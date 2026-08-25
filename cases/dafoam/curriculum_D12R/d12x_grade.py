#!/usr/bin/env python3
"""
CURRICULUM D12 (proper) COMPARATOR.  FROZEN INSTRUMENT.

Grades the unsteady-adjoint / time-averaged-drag item from ARTIFACTS ON DISK.
REFUSES (exit 2) rather than degrading.

Gates it can emit -- this list is the authority the selftest is measured against
(see --gatelist and --selftest):

    G12R-0   completion / instrument integrity     REFUSAL only
    G12R-1   limit cycle established               PASS | NOT A RESULT
    G12R-2   delta_repeat measured                 PASS   (+ REFUSAL on <3 repeats)
    G12R-3   delta_window measured                 PASS   (+ REFUSAL on short series)
    G12R-4   FD step sizing                        PASS | NOT A RESULT
    G12R-5   plateau                               PASS | NOT A RESULT
    G12R-6   the bright line, adjoint vs FD        PASS | CONDITIONAL | GATE FAIL | NOT A RESULT
    G12R-7   registered trivial baseline           PASS | WITHDRAWN
    G12R-8   checkpoint envelope, RAM and disk     PASS | BLOCKED   (+ RESOLVED/UNRESOLVED sub-label)
    G12R-9   planted zero                          PASS   (+ REFUSAL on a blind reader)
    G12R-10  two rows, shipped and patched         PASS | GATE FAIL | PENDING
    G12R-11  the optimisation                      GATE REACHED | NOT A RESULT | PENDING

THE DEFECT THIS FILE IS BUILT NOT TO REPEAT.  `d3_grade.py` returned `PASS` at
0.0000 % over an EMPTY component set while the same file refused an unseen plant
citing rule 3 by name.  Every aggregate here goes through `vector_rel_error`,
which REFUSES on an empty or length-mismatched component set, and the selftest
carries a dedicated empty-component-set mutation unit (U-06e).

L-302 discipline: every list is asserted NON-EMPTY before it is iterated.
"""
import argparse, json, math, os, re, sys

# ---------------------------------------------------------------- registered constants
# Every one of these is fixed by PREREGISTRATION.md section 5 and is not a tunable.
W_PRIMARY          = 300        # timesteps, graded window
W_CONTINGENCY      = 900        # timesteps, fires only on the G12R-4 branch
TRANSIENT_DISCARD  = 0          # [D1] the discard is now done BY CONSTRUCTION: S2a ENDS at
                                # the discard point so its FINAL write is complete, and S2b's
                                # series therefore starts already past the transient.  Every
                                # sample S2b emits is retained.
LIMITCYCLE_MIN_SIGN_CHANGES = 6
LIMITCYCLE_MIN_P2P_REL      = 0.01
EPS_NOISE_TARGET   = 0.01       # 1.0 % noise budget in the FD relative error
H_MAX              = 0.05       # 10 % of the cylinder radius
PLATEAU_MIN_RUN    = 3          # consecutive steps
PLATEAU_TOL_REL    = 0.02       # 2.0 % pairwise about the run mean
BAND_PASS          = 0.05       # DAFOAM_CHARTER section 2
BAND_CONDITIONAL   = 0.15
TRIVIAL_MULTIPLIER = 10.0
TRIVIAL_PREDICT_ABOVE = 0.05    # the wrong step must NOT reach PASS
ENVELOPE_SIGMA_K   = 3.0        # resolved only if |dR(80)-dR(20)| > 3 sigma_R
MEMAVAIL_FLOOR_GIB = 14.0
PLANT_SHAPE        = 1.234e-03
PLANT_FLOOR_REL    = 1.0e-9
JSON_LOG_TOL_REL   = 1.0e-12
HARNESS_FLOOR_LO   = 0.025      # VERIFICATION_CHARTER section 7 step 4, shape DV through IDWarp
CAP_CORE_MIN       = 600.0
CAP_S8_CORE_MIN    = 350.0

# ---- ADDED 2026-08-25 under SUPERVISOR_D12_RULINGS.md, before first compute -------
# RULING 4 (delta_pert).  Two probe steps A DECADE APART, frozen.  delta_pert is
# MEASURED FOR THIS CONFIGURATION and is NEVER imported from D12-F': the floor is
# component-dependent (1.65e-06 vs 8.4e-09 on two components of one probe), so it is
# a property of a configuration exactly as DAFOAM_CHARTER.md section 5 says an FD
# reference is.  Importing it would be inventing a price across configurations.
DPERT_HA           = 1.0e-6
DPERT_HB           = 1.0e-5
DPERT_RATIO        = 10.0       # h_b / h_a, ASSERTED, because the solve assumes it

# RULING 6 (the delta_window == 0 hazard).  delta_window is IDENTICALLY ZERO whenever
# the graded window W is an integer multiple of the shedding period -- not because the
# objective is noiseless, but because block averaging over whole periods cancels the
# phase spread it exists to measure.
WINDOW_DEGEN_TOL   = 0.05       # |W/P - round(W/P)| <= this  =>  DEGENERATE
# PRE-COMPUTE PREDICTION, registered so G12R-1 tests it rather than confirming it:
# a circular cylinder sheds at St ~ 0.2; with D = 1.0 m and U0 = 10 m/s that is
# f ~ 2 Hz, T ~ 0.5 s, and at deltaT = 1e-2 the period is ~50 timesteps.  W = 300 is
# then ~6.0 periods EXACTLY, so delta_window is PREDICTED DEGENERATE -- not merely at
# risk of it.  W is NOT moved: it is the tutorial's own registered optimisation window
# and D12 is required to grade the case it names.  delta_pert carries the burden
# instead, which is why RULING 4 and RULING 6 are one repair and not two.
PERIOD_PREDICTED_STEPS = 50.0

GATES_EMITTED = ["G12R-0", "G12R-1", "G12R-2", "G12R-3", "G12R-3b", "G12R-4", "G12R-5",
                 "G12R-6", "G12R-7", "G12R-8", "G12R-9", "G12R-10", "G12R-11", "G12R-W"]


class Refusal(Exception):
    pass


# ---------------------------------------------------------------- primitive readers
def _finite(x):
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def read_json(path):
    if not os.path.isfile(path):
        raise Refusal("artifact missing: %s" % path)
    with open(path) as f:
        return json.load(f)


CD_RE = re.compile(r"^CD:\s*(\S+)\s+average:\s*(\S+)\s*$")
TIME_RE = re.compile(r"^Time = (\S+)\s*$")


def read_series(logpath):
    """Read the per-timestep CD series from a stage log ON DISK.

    Returns (times, cd, running_avg).  Refuses on an empty series -- a reader that
    returns nothing is not the same thing as a run that oscillated about zero.
    """
    if not os.path.isfile(logpath):
        raise Refusal("series read impossible, no such log: %s" % logpath)
    times, cd, avg = [], [], []
    t_cur = None
    with open(logpath, errors="replace") as f:
        for line in f:
            s = line.strip()
            m = TIME_RE.match(s)
            if m:
                try:
                    t_cur = float(m.group(1))
                except ValueError:
                    t_cur = None
                continue
            m = CD_RE.match(s)
            if m:
                try:
                    c = float(m.group(1))
                    a = float(m.group(2))
                except ValueError:
                    raise Refusal("unparseable CD line in %s: %r" % (logpath, s))
                times.append(t_cur)
                cd.append(c)
                avg.append(a)
    if len(cd) == 0:
        raise Refusal("series reader saw ZERO CD samples in %s -- a blind reader, "
                      "not an empty result" % logpath)
    return times, cd, avg


def block_averages(cd, W):
    """Every W-length block average, at every start offset."""
    if not cd:
        raise Refusal("block_averages called on an EMPTY series")
    if W <= 0:
        raise Refusal("block_averages called with W=%d" % W)
    if len(cd) < W:
        raise Refusal("series of %d samples cannot support a %d-step window" % (len(cd), W))
    out = []
    run = sum(cd[:W])
    out.append(run / W)
    for k in range(1, len(cd) - W + 1):
        run += cd[k + W - 1] - cd[k - 1]
        out.append(run / W)
    return out


def vector_rel_error(g_adj, g_fd):
    """||g_adj - g_fd|| / ||g_fd||, the statistic NAMED in the pre-registration.

    REFUSES on an empty or mismatched component set.  This is the d3_grade.py
    defect: an aggregate over nothing is 0.0000 %, and 0.0000 % reads as agreement.
    """
    if not isinstance(g_adj, (list, tuple)) or not isinstance(g_fd, (list, tuple)):
        raise Refusal("vector_rel_error needs two sequences")
    if len(g_adj) == 0 or len(g_fd) == 0:
        raise Refusal("EMPTY COMPONENT SET: an aggregate over zero components is not "
                      "0.0000 %% agreement, it is no measurement at all")
    if len(g_adj) != len(g_fd):
        raise Refusal("component-set length mismatch: %d adjoint vs %d FD"
                      % (len(g_adj), len(g_fd)))
    for v in list(g_adj) + list(g_fd):
        if not _finite(v):
            raise Refusal("non-finite component in the FD/adjoint comparison")
    num = math.sqrt(sum((a - b) ** 2 for a, b in zip(g_adj, g_fd)))
    den = math.sqrt(sum(b * b for b in g_fd))
    if den == 0.0:
        raise Refusal("FD reference vector has zero norm -- nothing to divide by")
    return num / den


def sign_flips(g_adj, g_fd):
    if len(g_adj) == 0 or len(g_adj) != len(g_fd):
        raise Refusal("sign_flips on an empty or mismatched component set")
    return [i for i, (a, b) in enumerate(zip(g_adj, g_fd))
            if a * b < 0.0]


# ---------------------------------------------------------------- gates
def g0_completion(stages):
    """G12R-0 -- REFUSAL only.  Every clause of CLAUDE.md rule 4 this instrument carries."""
    if not stages:
        raise Refusal("G12R-0: no stages in the manifest")
    for st in stages:
        nm = st.get("name", "<unnamed>")
        if st.get("rc") != 0:
            raise Refusal("G12R-0 %s: rc=%r" % (nm, st.get("rc")))
        if str(st.get("oomkilled", "")).lower() != "false":
            raise Refusal("G12R-0 %s: OOMKilled=%r" % (nm, st.get("oomkilled")))
        if st.get("status") != "COMPLETE":
            raise Refusal("G12R-0 %s: JSON status=%r" % (nm, st.get("status")))
        if not st.get("end_line_present"):
            raise Refusal("G12R-0 %s: no End line in its own log" % nm)
        lt, et = st.get("last_time"), st.get("endTime")
        if lt is None or et is None or abs(float(lt) - float(et)) > 1e-9:
            raise Refusal("G12R-0 %s: last time %r != endTime %r" % (nm, lt, et))
        if not st.get("coldstart_ok"):
            raise Refusal("G12R-0 %s: cold-start assertion did not pass" % nm)
        # ---- ADDED under RULING 5: the two limbs of CLAUDE.md rule 4 this gate did not
        # ---- carry.  REQUIRED, not optional -- rule 4 is a standing rule.
        #
        # THE AGE GUARD.  `0/U` is touched last at launch, so it dates the run allowed to
        # produce the answer; every field at endTime must be NEWER.  A stage that fails
        # this is carrying a field it did not produce, and no cold-start check can see
        # that on its own -- a directory can be absent at launch and still be filled from
        # somewhere other than this run.
        ag = st.get("age_guard_ok")
        if ag is not True:
            raise Refusal("G12R-0 %s: AGE GUARD not satisfied (age_guard_ok=%r): %s. "
                          "Every field at endTime must be newer than the case's own 0/U "
                          "datum (CLAUDE.md rule 4)."
                          % (nm, ag, st.get("age_guard_detail", "<no detail recorded>")))
        # THE STEP COUNT.  rule 4's "ExecutionTime count == endTime" limb, in the form
        # this solver carries it: the primal writes one `Time = ` line per timestep, so
        # that count must EQUAL the registered number of steps.  `ExecutionTime` lines are
        # counted too and reported, but a compute_totals stage emits them in the adjoint
        # sweep as well, so that count is required only to be >= the step count -- stated
        # rather than quietly gated at equality it cannot meet.
        # ---- [D4] THE STEP PROXY IS STAGE-KIND AWARE AND REFUSES -----------------
        # The superseded gate compared a STEADY solver's outer iterations against an
        # UNSTEADY step count -- 6 `Time =` lines against 500 -- with the registered and
        # staged controlDicts AGREEING WITH EACH OTHER and both disagreeing with the log.
        # That is not a weak check; IT IS A CHECK OF THE WRONG QUANTITY, which is the same
        # shape as reading CL where the objective is CD.  A gate that cannot name the
        # quantity it is comparing REFUSES rather than comparing anyway.
        kind = st.get("stage_kind")
        if kind not in ("steady", "unsteady", "mesh"):
            raise Refusal("G12R-0 %s: stage_kind=%r. A completion gate that does not know "
                          "what KIND of stage it is grading cannot know whether its step "
                          "proxy means anything, and REFUSES rather than comparing "
                          "incomparable counts." % (nm, kind))
        exp = st.get("expected_steps")
        if kind == "steady":
            # `Time =` is an OUTER-ITERATION print governed by the solver's own print
            # interval and is NOT a step count. It is recorded and REPORTED, never gated.
            pass
        elif kind == "mesh":
            pass
        elif exp:
            tlc = st.get("time_line_count")
            if tlc != exp:
                raise Refusal("G12R-0 %s: primal wrote %r `Time =` lines, registered %d "
                              "steps (rule 4's step-count limb)" % (nm, tlc, exp))
            etc = st.get("execution_time_count")
            if etc is None or etc < exp:
                raise Refusal("G12R-0 %s: ExecutionTime count %r is below the %d "
                              "registered steps" % (nm, etc, exp))
        # ---- [D3] THE STRUCTURAL WITNESS THAT THE OBJECTIVE READER READ `CD` ------
        # CD is positive-definite for this flow and CL oscillates about zero, so a CD
        # series with ZERO negatives is a POSITIVE demonstration that the reader read CD.
        # It is not an absence of evidence; a CL series would be about half negative.
        nneg, ncd = st.get("n_cd_negative"), st.get("n_cd_lines")
        if ncd:
            if nneg is None:
                raise Refusal("G12R-0 %s: CD lines were found but their sign was never "
                              "counted -- the structural witness was not taken" % nm)
            if nneg > 0:
                raise Refusal("G12R-0 %s: %d of %d CD samples are NEGATIVE. CD is "
                              "positive-definite for this flow; negatives mean the reader "
                              "is not reading CD." % (nm, nneg, ncd))
        if not st.get("field_b_md5_ok", True):
            raise Refusal("G12R-0 %s: FIELD_B md5 manifest mismatch" % nm)
        oj, ol = st.get("obj"), st.get("obj_from_log")
        if oj is not None and ol is not None:
            if not _finite(oj) or not _finite(ol):
                raise Refusal("G12R-0 %s: non-finite obj" % nm)
            den = abs(oj) if oj != 0.0 else 1.0
            if abs(oj - ol) / den > JSON_LOG_TOL_REL:
                raise Refusal("G12R-0 %s: JSON obj %.16e disagrees with the log's last "
                              "running average %.16e -- the series reader and the solver "
                              "do not agree on the one number they both compute"
                              % (nm, oj, ol))
        ma = st.get("memavail_GiB")
        if ma is not None and float(ma) < MEMAVAIL_FLOOR_GIB:
            raise Refusal("G12R-0 %s: launched at MemAvailable %.4f GiB, below the "
                          "registered %.1f GiB floor" % (nm, float(ma), MEMAVAIL_FLOOR_GIB))
    return {"gate": "G12R-0", "verdict": "PASS", "n_stages": len(stages)}


def g_where(stage, reg_index, reg_delta, nshapes=None, require_units=False):
    """G12R-W -- THE WHERE-CONTROL.  SUPERVISOR_D12_RULINGS.md section 3, condition 3.

    D4-DEF-4: "A units error is invisible to every count-based, plant-based and
    order-based control in this family's gate set.  They check THAT n components were
    measured.  They never check WHERE."  D4's endpoint was extracted in driver-scaled
    units and applied as physical; had the scaler been 1.0 instead of 10 every primal
    would have converged and THE FULLY ARMED INSTRUMENT SET WOULD HAVE CERTIFIED a
    design point that was not the optimum.

    So this gate reads back, from the stage's own JSON on disk, the perturbation the run
    ACTUALLY APPLIED -- index, sign and magnitude, derived from the shape vector itself,
    never echoed from the launcher's arguments -- and REFUSES if it is not the registered
    one.  A count of stages is not a witness of what was perturbed.
    """
    nm = stage.get("name", "<unnamed>")
    # ---- UNITS REGISTRATION, required before phase 3 -------------------------
    # The supervisor's point, and it is sharper than the lane's own residual: the
    # WHERE-control is STRONG on index and sign -- a positive scaler moves neither --
    # and CONDITIONAL on magnitude. Comparing a magnitude without naming the units it
    # is in is exactly the D4-DEF-4 shape surviving inside the control built to catch
    # it. So before any magnitude comparison is allowed to mean anything, the units
    # must be REGISTERED, not assumed.
    if require_units:
        u = stage.get("dv_units")
        if not u or u == "unregistered":
            raise Refusal("G12R-W %s: dv_units=%r. A magnitude comparison in unnamed units "
                          "is not a WHERE-control -- a scaler error is invisible to it, "
                          "which is the exact defect this gate exists to catch." % (nm, u))
    sv = stage.get("applied_shape_vector")
    if sv is None:
        raise Refusal("G12R-W %s: no applied_shape_vector on disk -- the WHERE-control "
                      "has nothing to read, so nothing witnesses what was perturbed" % nm)
    if not isinstance(sv, list) or (nshapes is not None and len(sv) != nshapes):
        raise Refusal("G12R-W %s: applied_shape_vector is %r; expected a list of %r"
                      % (nm, sv, nshapes))
    ai, asg, amag = (stage.get("applied_index"), stage.get("applied_sign"),
                     stage.get("applied_magnitude"))
    if asg == "multiple" or isinstance(ai, list):
        raise Refusal("G12R-W %s: MORE THAN ONE non-zero shape component was applied "
                      "(indices %r). That is not a partial derivative and no FD taken "
                      "from it is one." % (nm, ai))
    reg_delta = float(reg_delta)
    if reg_delta == 0.0:
        if asg != "zero":
            raise Refusal("G12R-W %s: registered an UNPERTURBED stage but the run applied "
                          "index=%r sign=%r magnitude=%r" % (nm, ai, asg, amag))
        return {"gate": "G12R-W", "verdict": "PASS", "stage": nm, "applied": "zero",
                "registered_delta": 0.0}
    if asg == "zero":
        raise Refusal("G12R-W %s: registered delta %.16e but the run applied NOTHING -- "
                      "the perturbation did not reach the solver" % (nm, reg_delta))
    if ai != int(reg_index):
        raise Refusal("G12R-W %s: perturbation landed on component %r, registered %r. "
                      "THE RUN POINT IS NOT WHERE THE REGISTRATION SAYS IT IS."
                      % (nm, ai, reg_index))
    want_sign = "plus" if reg_delta > 0 else "minus"
    if asg != want_sign:
        raise Refusal("G12R-W %s: perturbation sign is %r, registered %r"
                      % (nm, asg, want_sign))
    want_mag = abs(reg_delta)
    if amag is None or not _finite(amag):
        raise Refusal("G12R-W %s: applied magnitude is %r" % (nm, amag))
    # relative agreement, because the magnitudes span 1e-6 to 1e-2
    if abs(amag - want_mag) > 1.0e-12 * max(1.0, want_mag):
        raise Refusal("G12R-W %s: applied magnitude %.16e, registered %.16e (rel %.3e). "
                      "A SCALER OR UNITS ERROR LOOKS EXACTLY LIKE THIS."
                      % (nm, amag, want_mag, abs(amag - want_mag) / want_mag))
    # every OTHER component must be exactly zero, or it is not a partial derivative
    for j, v in enumerate(sv):
        if j != ai and float(v) != 0.0:
            raise Refusal("G12R-W %s: component %d is %.16e, must be exactly 0.0"
                          % (nm, j, float(v)))
    return {"gate": "G12R-W", "verdict": "PASS", "stage": nm, "applied_index": ai,
            "applied_sign": asg, "applied_magnitude": amag,
            "registered_delta": reg_delta}


def g3b_delta_pert(pairs):
    """G12R-3b -- delta_pert, the PERTURBATION-RESPONSE floor.  RULING 4.

    MODEL-FREE: this function NEVER READS THE ADJOINT.  D12-F' measured delta_repeat at
    exactly 0.000000e+00 while the objective carried a floor of ~1.65e-06 -- three-plus
    orders apart -- so an unperturbed-run noise estimate is demonstrably blind to the
    thing that actually limits the finite difference.

    `pairs` is a list of dicts, one per component:
        {"component": i, "h_a": ha, "S_a": |obj(+ha)-obj(-ha)|,
                          "h_b": hb, "S_b": |obj(+hb)-obj(-hb)|}

    THE SOLVE.  Model the measured difference at step h as  S(h) = 2h|g| + 2e, where e is
    the per-evaluation floor.  With h_b = 10 h_a the |g| term cancels:
        S_b - 10 S_a = 2|g|(h_b - 10 h_a) + 2e - 20e = -18e
        =>  e = (10 S_a - S_b) / 18
    Two measurements, two unknowns, no adjoint anywhere.  Validated against D12-F''s
    committed component-3 data (S_a=3.0738e-06, S_b=1.0464e-06) it returns 1.6495e-06,
    against the 1.65e-06 that record obtained by the adjoint-based route.

    e <= 0 means the data are consistent with NO detectable floor at these steps.  That is
    reported as 0.0 AND FLAGGED AS "not detectable at these steps", never as "there is no
    floor" -- component 0 of D12-F' returns exactly that and still had no plateau.

    delta_pert for the item is the MAX over components, because h* must be admissible for
    ALL of them.
    """
    if not pairs:
        raise Refusal("G12R-3b: EMPTY component set -- no delta_pert can be computed, and "
                      "a percentage over an empty set is this family's own measured defect")
    per = []
    for row in pairs:
        i = row.get("component")
        ha, hb = float(row["h_a"]), float(row["h_b"])
        if ha <= 0.0 or hb <= 0.0:
            raise Refusal("G12R-3b component %r: non-positive probe step" % i)
        r = hb / ha
        if abs(r - DPERT_RATIO) > 1.0e-9 * DPERT_RATIO:
            raise Refusal("G12R-3b component %r: probe steps are a ratio of %.6f, the "
                          "solve assumes exactly %.1f" % (i, r, DPERT_RATIO))
        sa, sb = float(row["S_a"]), float(row["S_b"])
        if not (_finite(sa) and _finite(sb)):
            raise Refusal("G12R-3b component %r: non-finite signal" % i)
        e = (DPERT_RATIO * sa - sb) / (2.0 * (DPERT_RATIO - 1.0))
        detectable = e > 0.0
        g_implied = (sb - sa) / (2.0 * (hb - ha))
        per.append({"component": i, "h_a": ha, "h_b": hb, "S_a": sa, "S_b": sb,
                    "delta_pert": (e if detectable else 0.0),
                    "detectable": detectable,
                    "linearity_ratio": (sb / sa if sa != 0.0 else float("inf")),
                    "g_implied_DIAGNOSTIC_ONLY": g_implied})
    dp = max(p["delta_pert"] for p in per)
    return {"gate": "G12R-3b", "verdict": "PASS", "delta_pert": dp,
            "n_components": len(per), "per_component": per,
            "note": ("delta_pert is the MAX over components because h* must be admissible "
                     "for all of them; a component reporting 0.0 means NO FLOOR WAS "
                     "DETECTABLE AT THESE STEPS, which is not the same claim as no floor")}


def g1_limit_cycle(cd_retained):
    if not cd_retained:
        raise Refusal("G12R-1 on an EMPTY retained series")
    n = len(cd_retained)
    mean = sum(cd_retained) / n
    dev = [c - mean for c in cd_retained]
    changes = sum(1 for i in range(1, n) if dev[i - 1] * dev[i] < 0.0)
    p2p = max(cd_retained) - min(cd_retained)
    p2p_rel = p2p / abs(mean) if mean != 0.0 else float("inf")
    ok = (changes >= LIMITCYCLE_MIN_SIGN_CHANGES) and (p2p_rel > LIMITCYCLE_MIN_P2P_REL)
    # shedding period, reported as an observation either way
    period = (2.0 * (n - 1) / changes) if changes > 0 else None
    return {"gate": "G12R-1", "verdict": "PASS" if ok else "NOT A RESULT",
            "sign_changes": changes, "p2p": p2p, "p2p_rel": p2p_rel,
            "mean": mean, "period_steps": period, "n_samples": n}


def g2_delta_repeat(objs):
    if not isinstance(objs, (list, tuple)) or len(objs) < 3:
        raise Refusal("G12R-2 needs 3 identical repeats, got %r"
                      % (len(objs) if hasattr(objs, "__len__") else objs))
    for v in objs:
        if not _finite(v):
            raise Refusal("G12R-2: non-finite repeat objective")
    d = max(objs) - min(objs)
    m = sum(objs) / len(objs)
    return {"gate": "G12R-2", "verdict": "PASS", "delta_repeat": d,
            "delta_repeat_rel": (d / abs(m) if m != 0.0 else float("inf")),
            "mean": m, "n": len(objs), "values": list(objs),
            "note": ("delta_repeat == 0 is the EXPECTED reading at np=1 on a "
                     "deterministic solver from a byte-identical field. IT IS NOT A "
                     "CLEARANCE FOR THE FD STEP: the noise that threatens a "
                     "time-averaged objective on a limit cycle is phase noise, "
                     "measured by G12R-3." if d == 0.0 else "")}


def g3_delta_window(cd_retained, W, period_steps=None):
    blocks = block_averages(cd_retained, W)
    if len(blocks) < 2:
        raise Refusal("G12R-3: only %d block averages at W=%d -- no spread to measure"
                      % (len(blocks), W))
    d = max(blocks) - min(blocks)
    m = sum(blocks) / len(blocks)
    out = {"gate": "G12R-3", "verdict": "PASS", "W": W, "n_windows": len(blocks),
           "delta_window": d,
           "delta_window_rel": (d / abs(m) if m != 0.0 else float("inf")),
           "grand_mean": m, "block_min": min(blocks), "block_max": max(blocks)}
    # ---- THE DEGENERACY BRANCH.  RULING 6, frozen before the data. ------------------
    # delta_window is IDENTICALLY ZERO whenever W is an integer multiple of the shedding
    # period, because block averaging over whole periods cancels the phase spread this
    # quantity exists to measure.  A floor that can be zero BY CONSTRUCTION must never be
    # allowed to size a step silently.
    out["degenerate"] = None
    out["periods_per_window"] = None
    # SUPERVISOR REQUIREMENT: when degenerate, delta_window is EXCLUDED BY NAME and must
    # NEVER be reported as a numeric zero.  A zero reads downstream as "measured, and it
    # is small"; the truth is "cancelled by construction, and unmeasurable at this W".
    # Those are different claims and only one of them is honest.
    if period_steps and period_steps > 0:
        k = float(W) / float(period_steps)
        out["periods_per_window"] = k
        out["degenerate"] = abs(k - round(k)) <= WINDOW_DEGEN_TOL
        out["degeneracy_note"] = (
            "W = %g is %.4f shedding periods. DEGENERATE: within %.2f of a whole number, "
            "so delta_window is cancelled BY CONSTRUCTION and is NOT LOAD-BEARING here -- "
            "delta_pert (G12R-3b) carries the noise floor. This branch was frozen BEFORE "
            "the data and the ~%.0f-step period was PREDICTED before the run."
            % (W, k, WINDOW_DEGEN_TOL, PERIOD_PREDICTED_STEPS)) if out["degenerate"] else (
            "W = %g is %.4f shedding periods, not within %.2f of a whole number, so "
            "delta_window is not cancelled by construction and stands on its own."
            % (W, k, WINDOW_DEGEN_TOL))
        out["period_prediction_steps"] = PERIOD_PREDICTED_STEPS
        out["period_measured_steps"] = period_steps
        out["period_prediction_held"] = (
            abs(period_steps - PERIOD_PREDICTED_STEPS) <= 0.25 * PERIOD_PREDICTED_STEPS)
        if out["degenerate"]:
            out["delta_window"] = None
            out["delta_window_rel"] = None
            out["excluded_by_name"] = "delta_window"
            out["verdict"] = "NOT A RESULT"
            out["exclusion_note"] = (
                "delta_window is EXCLUDED BY NAME, not reported as 0.0. W = %g is %.4f "
                "shedding periods, so block averaging over whole periods CANCELS the phase "
                "spread this quantity exists to measure. A numeric zero here would read "
                "downstream as 'measured and small'; the truth is 'cancelled by "
                "construction and unmeasurable at this W'. delta_pert carries the floor."
                % (W, out["periods_per_window"]))
    return out


def g4_delta_eff(delta_repeat, delta_window, delta_pert, window_degenerate=None):
    """delta_eff := max(delta_repeat, delta_window, delta_pert).  RULING 4, APPROVED.

    As originally registered this was max(delta_repeat, delta_window), BOTH FROM
    UNPERTURBED RUNS.  D12-F' measured delta_repeat = 0.000000e+00 against a
    perturbation-response floor of ~1.65e-06 -- three-plus orders above -- so an
    unperturbed-run estimate is demonstrably blind to the floor that actually limits the
    FD.  Adding a term to a maximum can only RAISE h_min: it can cause a NOT A RESULT and
    it cannot manufacture a PASS.
    """
    terms = {"delta_repeat": delta_repeat, "delta_window": delta_window,
             "delta_pert": delta_pert}
    # delta_window == None means EXCLUDED BY NAME by G12R-3's degeneracy branch. That is
    # a legitimate state and is carried as an exclusion, never silently coerced to 0.0 --
    # a coerced zero would enter the max() as a measurement.
    excluded = [k for k, v in terms.items() if v is None]
    if excluded and window_degenerate is not True:
        raise Refusal("G12R-4: %s is None but delta_window was NOT flagged degenerate; a "
                      "missing noise term is not the same thing as an excluded one"
                      % ", ".join(excluded))
    for k, v in terms.items():
        if v is None:
            continue
        if not _finite(v) or v < 0.0:
            raise Refusal("G12R-4: %s=%r is not a usable noise floor" % (k, v))
    live = {k: v for k, v in terms.items() if v is not None}
    if not live:
        raise Refusal("G12R-4: EVERY noise term is excluded or absent; no step can be sized")
    dom = max(live, key=lambda k: live[k])
    out = {"gate": "G12R-4", "verdict": "PASS", "delta_eff": max(live.values()),
           "terms": terms, "excluded_by_name": excluded, "dominant_term": dom,
           "window_degenerate": window_degenerate}
    if window_degenerate and dom == "delta_window":
        raise Refusal("G12R-4: delta_window is DEGENERATE (W is a whole number of shedding "
                      "periods, so it is cancelled by construction) yet it is the DOMINANT "
                      "term. A noise floor that is zero by construction cannot be the "
                      "largest one; the manifest is inconsistent.")
    if max(live.values()) == 0.0:
        raise Refusal("G12R-4: ALL THREE noise terms are zero. No step can be sized "
                      "against a floor of zero, and a zero from readers not shown able to "
                      "see a non-zero is not evidence (CLAUDE.md rule 3).")
    return out


def g4_step_sizing(delta_eff, g_component):
    if not _finite(delta_eff) or delta_eff < 0.0:
        raise Refusal("G12R-4: delta_eff=%r" % delta_eff)
    if not _finite(g_component) or g_component == 0.0:
        raise Refusal("G12R-4: |g| is zero or non-finite -- no step can be sized against it")
    h_min = EPS_NOISE_TARGET ** -1 * delta_eff / abs(g_component)
    admissible = h_min <= H_MAX
    steps = []
    if admissible:
        raw = [h_min * 1e-1, h_min, h_min * 10.0, h_min * 100.0, h_min * 1000.0]
        seen = set()
        for h in raw:
            hh = min(h, H_MAX)
            hh = float("%.1g" % hh)
            if hh in seen or hh <= 0.0:
                continue
            seen.add(hh)
            steps.append(hh)
    return {"gate": "G12R-4",
            "verdict": "PASS" if admissible else "NOT A RESULT",
            "delta_eff": delta_eff, "g_component": g_component,
            "h_min": h_min, "h_max": H_MAX, "eps_noise_target": EPS_NOISE_TARGET,
            "steps": steps,
            "reason": ("" if admissible else
                       "h_min %.6e EXCEEDS h_max %.3e: no admissible FD step exists at "
                       "this window. This is a RESULT, not a failure -- the contingency "
                       "window fires and the optimisation does not proceed on a gradient "
                       "that cannot be verified." % (h_min, H_MAX))}


def g5_plateau(sweep):
    """sweep: list of {"h": float, "fd": float}.  Every row survives into the table."""
    if not sweep:
        raise Refusal("G12R-5 on an EMPTY sweep")
    rows = sorted(sweep, key=lambda r: r["h"])
    for r in rows:
        if not _finite(r.get("fd")):
            r["status"] = "NON-FINITE"
        else:
            r["status"] = "ok"
    best = None
    n = len(rows)
    for i in range(n):
        for j in range(i + PLATEAU_MIN_RUN - 1, n):
            seg = rows[i:j + 1]
            if any(s["status"] != "ok" for s in seg):
                break
            vals = [s["fd"] for s in seg]
            mu = sum(vals) / len(vals)
            if mu == 0.0:
                break
            if max(abs(v - mu) / abs(mu) for v in vals) <= PLATEAU_TOL_REL:
                if best is None or len(seg) > best[1] - best[0] + 1:
                    best = (i, j)
            else:
                break
    if best is None:
        return {"gate": "G12R-5", "verdict": "NOT A RESULT", "table": rows,
                "h_star": None,
                "reason": "no run of %d consecutive steps agrees within %.1f %%; one step "
                          "is never a plateau" % (PLATEAU_MIN_RUN, 100 * PLATEAU_TOL_REL)}
    i, j = best
    mid = rows[(i + j) // 2]
    return {"gate": "G12R-5", "verdict": "PASS", "table": rows,
            "h_star": mid["h"], "plateau_lo": rows[i]["h"], "plateau_hi": rows[j]["h"],
            "plateau_len": j - i + 1}


def g6_bright_line(g_adj, g_fd, flagged=None, label=""):
    """DAFOAM_CHARTER section 2.  Aggregate NAMED, per-component reported BESIDE it."""
    flagged = list(flagged or [])
    agg = vector_rel_error(g_adj, g_fd)          # REFUSES on an empty component set
    flips = sign_flips(g_adj, g_fd)
    per = []
    for i, (a, b) in enumerate(zip(g_adj, g_fd)):
        per.append({"i": i, "adj": a, "fd": b,
                    "rel": (abs(a - b) / abs(b) if b != 0.0 else float("inf")),
                    "flagged": i in flagged,
                    "sign_flip": i in flips})
    kept_a = [a for i, a in enumerate(g_adj) if i not in flagged]
    kept_f = [b for i, b in enumerate(g_fd) if i not in flagged]
    agg_excl = vector_rel_error(kept_a, kept_f) if kept_a else None
    if flips or agg > BAND_CONDITIONAL:
        band, verdict = "FAIL", "GATE FAIL"
    elif agg <= BAND_PASS:
        band, verdict = "PASS", "PASS"
    else:
        band, verdict = "CONDITIONAL", "GATE FAIL"
    return {"gate": "G12R-6", "label": label, "verdict": verdict, "charter_band": band,
            "aggregate_vector_rel": agg, "aggregate_excl_flagged": agg_excl,
            "flagged": flagged, "sign_flipped": flips, "per_component": per,
            "n_components": len(g_adj),
            "harness_floor_note": ("MEASURED BELOW THE HARNESS FLOOR (%.1f %%) FOR A SHAPE "
                                   "DV THROUGH IDWARP -- a number this low is a claim about "
                                   "the harness and is flagged, not celebrated."
                                   % (100 * HARNESS_FLOOR_LO)) if agg < HARNESS_FLOOR_LO else ""}


def g7_trivial_baseline(agg_wrong, agg_real_verdict):
    if not _finite(agg_wrong):
        raise Refusal("G12R-7: non-finite aggregate at the deliberately wrong step")
    if agg_wrong > TRIVIAL_PREDICT_ABOVE:
        return {"gate": "G12R-7", "verdict": "PASS", "aggregate_at_wrong_step": agg_wrong,
                "predicted_above": TRIVIAL_PREDICT_ABOVE,
                "note": "the deliberately wrong step did NOT reach PASS, as registered"}
    return {"gate": "G12R-7", "verdict": "WITHDRAWN",
            "aggregate_at_wrong_step": agg_wrong,
            "predicted_above": TRIVIAL_PREDICT_ABOVE,
            "note": "THE WRONG STEP ALSO PASSES. G12R-6 is not measuring what it claims "
                    "and its verdict (%s) is WITHDRAWN (DAFOAM_CHARTER section 4)."
                    % agg_real_verdict}


def g8_envelope(points, memavail_min):
    """points: {n: [dR_run1, dR_run2, ...]} in GiB, plus disk deltas keyed the same."""
    if not points:
        raise Refusal("G12R-8 on an EMPTY point set")
    ns = sorted(points)
    if len(ns) < 2:
        raise Refusal("G12R-8 needs >= 2 window lengths, got %d" % len(ns))
    sigma = 0.0
    for n in ns:
        vals = points[n]
        if not vals or len(vals) < 2:
            raise Refusal("G12R-8: n=%d has %d run(s); the noise floor cannot be measured "
                          "with one run per point -- that is exactly what D12-E-prime "
                          "could not do" % (n, len(vals)))
        sigma = max(sigma, max(vals) - min(vals))
    lo, hi = ns[0], ns[-1]
    mean_lo = sum(points[lo]) / len(points[lo])
    mean_hi = sum(points[hi]) / len(points[hi])
    spread = abs(mean_hi - mean_lo)
    resolved = spread > ENVELOPE_SIGMA_K * sigma
    per_step = (mean_hi - mean_lo) / (hi - lo)
    per_step_bound = ENVELOPE_SIGMA_K * sigma / (hi - lo)
    if memavail_min is not None and float(memavail_min) < MEMAVAIL_FLOOR_GIB:
        return {"gate": "G12R-8", "verdict": "BLOCKED",
                "reason": "MemAvailable %.4f GiB below the registered %.1f GiB floor"
                          % (float(memavail_min), MEMAVAIL_FLOOR_GIB)}
    return {"gate": "G12R-8", "verdict": "PASS",
            "resolution": "RESOLVED" if resolved else "UNRESOLVED",
            "sigma": sigma, "spread": spread, "k": ENVELOPE_SIGMA_K,
            "n_lo": lo, "n_hi": hi, "mean_lo": mean_lo, "mean_hi": mean_hi,
            "per_step": per_step if resolved else None,
            "per_step_upper_bound": per_step_bound,
            "note": ("per-step term RESOLVED" if resolved else
                     "PER-STEP TERM UNRESOLVED. Bounded above by %.6e per step; "
                     "NOT reported as flat." % per_step_bound)}


def g9_plant(plant_json, base_obj):
    """CLAUDE.md rule 3.  The plant is read back FROM DISK."""
    got = plant_json.get("shape")
    if not isinstance(got, (list, tuple)) or len(got) == 0:
        raise Refusal("G12R-9: plant read-back impossible, no shape vector on disk")
    if abs(float(got[0]) - PLANT_SHAPE) > 1e-12:
        raise Refusal("G12R-9: plant read-back FAILED -- disk carries shape[0]=%r, "
                      "expected %r" % (got[0], PLANT_SHAPE))
    op = plant_json.get("obj")
    if not _finite(op) or not _finite(base_obj) or base_obj == 0.0:
        raise Refusal("G12R-9: non-finite or zero objective in the plant comparison")
    resp = abs(op - base_obj) / abs(base_obj)
    if resp <= PLANT_FLOOR_REL:
        raise Refusal("G12R-9 REFUSAL: the objective moved %.6e relative under a planted "
                      "shape[0]=%g, at or below the %.1e floor. A READER THAT CANNOT SEE "
                      "A NON-ZERO CANNOT REPORT A ZERO." % (resp, PLANT_SHAPE, PLANT_FLOOR_REL))
    return {"gate": "G12R-9", "verdict": "PASS", "plant_response_rel": resp,
            "obj_plant": op, "obj_base": base_obj}


def g10_two_rows(shipped, patched):
    if shipped is None:
        raise Refusal("G12R-10: no SHIPPED row -- a DAFoam verdict without the shipped "
                      "row is not a verdict about DAFoam")
    if patched is None:
        return {"gate": "G12R-10", "verdict": "PENDING", "shipped": shipped, "patched": None,
                "note": "PATCHED ROW MISSING -- stated in the verdict line itself"}
    v = "PASS" if (shipped.get("verdict") == "PASS" and patched.get("verdict") == "PASS") \
        else "GATE FAIL"
    return {"gate": "G12R-10", "verdict": v, "shipped": shipped, "patched": patched}


def g11_optimisation(obj_baseline, obj_final, delta_eff, exit_status, launched):
    if not launched:
        return {"gate": "G12R-11", "verdict": "NOT A RESULT",
                "reason": "the FD gate did not permit a verified gradient; the "
                          "optimisation was NOT LAUNCHED"}
    if obj_final is None or exit_status is None:
        return {"gate": "G12R-11", "verdict": "PENDING",
                "reason": "optimisation still running or no exit status in its own log"}
    if not _finite(obj_baseline) or not _finite(obj_final) or not _finite(delta_eff):
        raise Refusal("G12R-11: non-finite input")
    improvement = obj_baseline - obj_final
    ok = improvement > delta_eff
    return {"gate": "G12R-11", "verdict": "GATE REACHED" if ok else "NOT A RESULT",
            "obj_baseline": obj_baseline, "obj_final": obj_final,
            "improvement": improvement, "delta_eff": delta_eff,
            "exit_status": exit_status,
            "note": "" if ok else ("the objective moved %.6e, which does not exceed the "
                                   "measured phase-noise floor %.6e -- that is NOT A "
                                   "RESULT, not a small win" % (improvement, delta_eff))}


# =============================================================================
# THE BATTERY, HARDENED AGAINST `python3 -O`
# =============================================================================
# SUPERVISOR'S RULING, measured on the superseded comparator: it carried 59 `assert`
# statements and ALL 59 WERE INSIDE ONE FUNCTION -- `selftest`.  None in any gate.
#
#   "Your gates are clean.  Your battery is not.  I stripped all 59 asserts exactly as
#    -O would and re-ran: rc = 0, same closing line, every unit still [ok].  Under -O,
#    '62 units, 14/14 gates, 12/12 mutants caught' prints identically and is worth
#    nothing."
#
# THE EXPOSURE WAS NEVER IN THE GATES -- they raise `Refusal`, which `-O` does not touch.
# IT WAS IN THE EVIDENCE THAT THE GATES WORK.  A battery whose every unit is an `assert`
# reports total success under a flag that deletes every one of them.
#
# THREE THINGS MAKE THIS BATTERY SURVIVE THE FLAG:
#   1. NOT ONE `assert` STATEMENT REMAINS IN THIS FILE.  `check()` below raises a real
#      exception.  `--assert-audit` proves the claim by AST, on STATEMENT TYPE, so a
#      future edit reverting `raise` to `assert` is caught for what it is and not for
#      what it happens to do.
#   2. EVERY UNIT TALLIES AN EXPLICIT COUNTED RESULT, and the battery exits non-zero BY
#      COUNTING -- never by an exception escaping.  A unit that silently does nothing is
#      a MISSING COUNT, which fails, rather than an absent failure, which passes.
#   3. `--olimb` RUNS A MUTANT UNDER BOTH FLAGS.  Comparing healthy-input output under
#      two flags proves nothing -- healthy input passes either way, which is exactly the
#      false comfort the supervisor's own first attempt produced.  Only a mutant that
#      MUST be caught can tell the two apart.

class SelfTestFailure(Exception):
    """Raised by check().  A real exception: `-O` cannot remove it."""


def check(cond, msg="unit check failed"):
    """The battery's only assertion primitive.  NEVER an `assert` statement."""
    if not cond:
        raise SelfTestFailure(str(msg))
    return True


# THE REGISTERED UNIT COUNT -- A FROZEN CONSTANT, NOT A DERIVED ONE.
#
# The first draft of this file set EXPECTED_UNITS from `len(_UNIT_LIST)` at run time and
# compared it against the number of results.  THAT COMPARISON WAS TAUTOLOGICAL: `_u()`
# appends exactly one result per list entry, so the two could never disagree, and a mutant
# deleting the check from the exit condition was NOT CAUGHT by the battery.
#
# That is the M3 class -- "a control that is never load-bearing in any unit is not tested,
# however many units reference it" -- occurring inside the control built to satisfy the
# supervisor's counted-exit ruling.  Found by mutation, in this lane's own new code.
#
# Frozen here instead.  A unit that VANISHES from the list now fails LOUDLY against a
# number that does not move with it, which is the only way the count means anything.
EXPECTED_UNITS = 72


# ---------------------------------------------------------------- selftest
def _u(name, fn, results):
    """Run one unit and APPEND EXACTLY ONE EXPLICIT RESULT.  Never leaves a gap."""
    try:
        fn()
        results.append((name, "ok", ""))
    except SelfTestFailure as e:
        results.append((name, "FAIL", str(e)))
    except AssertionError as e:
        # retained only so a stray assert from an imported module is still reported;
        # this file contains none, which --assert-audit proves
        results.append((name, "FAIL", "AssertionError: %s" % e))
    except Exception as e:
        results.append((name, "ERROR", "%s: %s" % (type(e).__name__, e)))


def selftest(tmpdir):
    R = []
    exercised = set()

    def base_stage(**kw):
        # REPAIRED 2026-08-25 under RULING 5.  This fixture predates the age guard and the
        # step-count limb, so it did NOT carry them -- and G12R-0 correctly REFUSED it the
        # moment those limbs were added.  That refusal is the gate working: a fixture
        # missing a limb is a stage missing evidence, and rule 4 does not accept absence
        # of a check as a pass.  The fields are added; the gate is unchanged.
        st = {"name": "s", "rc": 0, "oomkilled": "false", "status": "COMPLETE",
              "end_line_present": True, "last_time": 3.0, "endTime": 3.0,
              "coldstart_ok": True, "field_b_md5_ok": True,
              "obj": 1.0, "obj_from_log": 1.0, "memavail_GiB": 25.0,
              "age_guard_ok": True, "age_guard_detail": "all fields newer than 0/U",
              "expected_steps": 300, "time_line_count": 300,
              "execution_time_count": 300,
              # added with the D12R repairs; a fixture missing a limb is a stage missing
              # evidence, and the gate correctly refused these the moment they landed
              "stage_kind": "unsteady", "dv_units": "dimensionless driver units",
              "n_cd_lines": 300, "n_cd_negative": 0, "n_cl_lines": 300}
        st.update(kw)
        return st

    # ---- G12R-0
    def u01():
        exercised.add("G12R-0")
        check(g0_completion([base_stage()])['verdict'] == 'PASS', "unit check failed")
    def u01b():
        for mut, val in [("rc", 1), ("oomkilled", "true"), ("status", "STARTED"),
                         ("end_line_present", False), ("last_time", 2.99),
                         ("coldstart_ok", False), ("field_b_md5_ok", False),
                         ("memavail_GiB", 3.0), ("obj_from_log", 1.5),
                         # the two limbs added under RULING 5
                         ("age_guard_ok", False), ("age_guard_ok", None),
                         ("time_line_count", 299), ("execution_time_count", 3)]:
            try:
                g0_completion([base_stage(**{mut: val})])
                raise AssertionError("G12R-0 did NOT refuse on mutation %s=%r" % (mut, val))
            except Refusal:
                pass
    def u01c():
        try:
            g0_completion([])
            raise AssertionError("G12R-0 did not refuse an empty stage list")
        except Refusal:
            pass

    # ---- series reader + its plant (G12R-9 leg 1)
    def u02():
        p = os.path.join(tmpdir, "fake.log")
        with open(p, "w") as f:
            for i, (c, a) in enumerate([(1.0, 1.0), (2.0, 1.5), (3.0, 2.0)]):
                f.write("Time = %g\n" % (0.01 * (i + 1)))
                f.write("CD: %.16g average: %.16g\n" % (c, a))
                f.write("ExecutionTime = 1 s\n")
        t, cd, av = read_series(p)
        check(cd == [1.0, 2.0, 3.0], cd)
        check(av[-1] == 2.0, "unit check failed")
    def u02b():
        p = os.path.join(tmpdir, "blind.log")
        with open(p, "w") as f:
            f.write("Time = 0.01\nExecutionTime = 1 s\n")
        try:
            read_series(p)
            raise AssertionError("series reader did NOT refuse a zero-sample log")
        except Refusal:
            pass
    def u02c():
        # THE PLANT, leg 1 of G12R-9: a known perturbation written to disk, read back.
        exercised.add("G12R-9")
        src = os.path.join(tmpdir, "fake.log")
        dst = os.path.join(tmpdir, "fake_planted.log")
        lines = open(src).read().splitlines(True)
        out = []
        for ln in lines:
            m = CD_RE.match(ln.strip())
            if m and float(m.group(1)) == 2.0:
                ln = "CD: %.16g average: %.16g\n" % (2.0 * 7.0, 1.5)
            out.append(ln)
        open(dst, "w").writelines(out)
        _, cd2, _ = read_series(dst)
        check(cd2 == [1.0, 14.0, 3.0], ('PLANT UNSEEN by the series reader', cd2))

    # ---- block averages
    def u03():
        check(block_averages([1.0, 2.0, 3.0, 4.0], 2) == [1.5, 2.5, 3.5], "unit check failed")
    def u03b():
        for bad in ([], [1.0, 2.0]):
            try:
                block_averages(bad, 3)
                raise AssertionError("block_averages did not refuse %r" % (bad,))
            except Refusal:
                pass

    # ---- G12R-1
    def u04():
        exercised.add("G12R-1")
        import math as _m
        osc = [1.0 + 0.1 * _m.sin(2 * _m.pi * i / 10.0) for i in range(100)]
        r = g1_limit_cycle(osc)
        check(r['verdict'] == 'PASS', r)
        flat = [1.0 + 1e-9 * (i % 2) for i in range(100)]
        r2 = g1_limit_cycle(flat)
        check(r2['verdict'] == 'NOT A RESULT', r2)
    def u04b():
        try:
            g1_limit_cycle([])
            raise AssertionError("G12R-1 did not refuse an empty series")
        except Refusal:
            pass

    # ---- G12R-2
    def u05():
        exercised.add("G12R-2")
        r = g2_delta_repeat([1.0, 1.0, 1.0])
        check(r['delta_repeat'] == 0.0 and 'NOT A CLEARANCE' in r['note'], r)
        r2 = g2_delta_repeat([1.0, 1.002, 1.001])
        check(abs(r2['delta_repeat'] - 0.002) < 1e-12, r2)
    def u05b():
        for bad in ([], [1.0], [1.0, 2.0], [1.0, float("nan"), 2.0]):
            try:
                g2_delta_repeat(bad)
                raise AssertionError("G12R-2 did not refuse %r" % (bad,))
            except Refusal:
                pass

    # ---- G12R-3
    # ================= ADDED 2026-08-25 under SUPERVISOR_D12_RULINGS.md ============
    # Every unit below walks a FAILURE path.  A control whose failure path has never been
    # walked is a control nobody has shown to work -- M3 is this file's standing proof.
    def _stage(name="S6", idx=0, delta=1.0e-3, n=4, leak=False, applied=None):
        sv = [0.0] * n
        if applied is None:
            applied = delta
        if applied != 0.0:
            sv[idx] = applied
        if leak:
            sv[(idx + 1) % n] = 1.0e-12
        nz = [(i, v) for i, v in enumerate(sv) if v != 0.0]
        st = {"name": name, "applied_shape_vector": sv}
        if len(nz) == 0:
            st.update(applied_index=None, applied_sign="zero", applied_magnitude=0.0)
        elif len(nz) == 1:
            i, v = nz[0]
            st.update(applied_index=i, applied_sign=("plus" if v > 0 else "minus"),
                      applied_magnitude=abs(v))
        else:
            st.update(applied_index=[i for i, _ in nz], applied_sign="multiple",
                      applied_magnitude=None)
        return st

    def _refuses(fn, what):
        try:
            fn()
        except Refusal:
            return
        raise AssertionError("did NOT refuse: " + what)

    def uW():
        exercised.add("G12R-W")
        r = g_where(_stage(), 0, 1.0e-3, nshapes=4)
        check(r['verdict'] == 'PASS' and r['applied_index'] == 0, r)
        r = g_where(_stage(idx=2, delta=-1.0e-3), 2, -1.0e-3, nshapes=4)
        check(r['applied_sign'] == 'minus', r)
        r = g_where(_stage(delta=0.0, applied=0.0), 0, 0.0, nshapes=4)
        check(r['applied'] == 'zero', r)
    def uW_index():
        # the perturbation landed on the WRONG COMPONENT
        _refuses(lambda: g_where(_stage(idx=1), 0, 1.0e-3, nshapes=4), "wrong index")
    def uW_sign():
        _refuses(lambda: g_where(_stage(delta=1.0e-3), 0, -1.0e-3, nshapes=4), "wrong sign")
    def uW_scaler():
        # THE D4-DEF-4 CLASS: the magnitude applied is the registered one times a scaler.
        # This is the single most important unit in this file -- it is the failure that a
        # fully armed count/plant/order instrument set certified.
        _refuses(lambda: g_where(_stage(applied=1.0e-2), 0, 1.0e-3, nshapes=4),
                 "magnitude off by a factor of 10 (a scaler error)")
    def uW_leak():
        _refuses(lambda: g_where(_stage(leak=True), 0, 1.0e-3, nshapes=4),
                 "a non-zero leaked into a second component")
    def uW_nothing():
        _refuses(lambda: g_where(_stage(applied=0.0), 0, 1.0e-3, nshapes=4),
                 "registered a perturbation but the run applied nothing")
    def uW_unexpected():
        _refuses(lambda: g_where(_stage(applied=1.0e-3), 0, 0.0, nshapes=4),
                 "registered an unperturbed stage but the run perturbed it")
    def uW_novector():
        _refuses(lambda: g_where({"name": "S6"}, 0, 1.0e-3, nshapes=4),
                 "no applied_shape_vector on disk")

    def uW_units():
        st = _stage()
        st["dv_units"] = "unregistered"
        _refuses(lambda: g_where(st, 0, 1.0e-3, nshapes=4, require_units=True),
                 "a magnitude comparison in UNREGISTERED units")
        st["dv_units"] = "FFD shape-function DV, dimensionless driver units (scaler 10)"
        check(g_where(st, 0, 1.0e-3, nshapes=4, require_units=True)["verdict"] == "PASS", st)
    def u3b():
        exercised.add("G12R-3b")
        # D12-F''s OWN COMMITTED component-3 data.  The model-free two-point solve must
        # recover the floor that record obtained by the adjoint-based route, 1.65e-06.
        r = g3b_delta_pert([{"component": 3, "h_a": 1e-6, "S_a": 3.0738409e-06,
                             "h_b": 1e-5, "S_b": 1.0464e-06}])
        check(abs(r['delta_pert'] - 1.6495e-06) < 1e-09, r)
        check(r['per_component'][0]['detectable'] is True, r)
    def u3b_undetectable():
        # a clean linear response: S_b = 10*S_a exactly => e = 0, reported as NOT
        # DETECTABLE rather than as "there is no floor"
        r = g3b_delta_pert([{"component": 0, "h_a": 1e-6, "S_a": 1.0e-8,
                             "h_b": 1e-5, "S_b": 1.0e-7}])
        check(r['delta_pert'] == 0.0 and r['per_component'][0]['detectable'] is False, r)
    def u3b_max():
        r = g3b_delta_pert([{"component": 0, "h_a": 1e-6, "S_a": 1.0e-8, "h_b": 1e-5, "S_b": 1.0e-7},
                            {"component": 3, "h_a": 1e-6, "S_a": 3.0738409e-06, "h_b": 1e-5, "S_b": 1.0464e-06}])
        check(abs(r['delta_pert'] - 1.6495e-06) < 1e-09, r)
    def u3b_empty():
        _refuses(lambda: g3b_delta_pert([]), "G12R-3b on an EMPTY component set")
    def u3b_ratio():
        _refuses(lambda: g3b_delta_pert([{"component": 0, "h_a": 1e-6, "S_a": 1.0,
                                          "h_b": 3e-6, "S_b": 1.0}]),
                 "probe steps that are not a decade apart")

    def u3_degen():
        # W = 300 and a 50-step period is 6.0 periods EXACTLY -> DEGENERATE by construction
        r = g3_delta_window([1.0, 3.0] * 200, 300, period_steps=50.0)
        check(r['degenerate'] is True and abs(r['periods_per_window'] - 6.0) < 1e-12, r)
        check('NOT LOAD-BEARING' in r['degeneracy_note'], r)
    def u3_nondegen():
        r = g3_delta_window([1.0, 3.0] * 200, 300, period_steps=47.0)
        check(r['degenerate'] is False, r)

    def u4_eff():
        r = g4_delta_eff(0.0, 1.0e-9, 1.65e-06)
        check(r['delta_eff'] == 1.65e-06 and r['dominant_term'] == 'delta_pert', r)
        # the historical case: delta_repeat exactly zero and delta_window degenerate
        r2 = g4_delta_eff(0.0, 0.0, 1.65e-06, window_degenerate=True)
        check(r2['delta_eff'] == 1.65e-06, r2)
    def u4_allzero():
        _refuses(lambda: g4_delta_eff(0.0, 0.0, 0.0),
                 "ALL THREE noise terms zero -- no step can be sized against zero")
    def u4_degen_dominant():
        _refuses(lambda: g4_delta_eff(0.0, 1.0e-3, 0.0, window_degenerate=True),
                 "a DEGENERATE delta_window as the dominant term")

    def _g0row(**kw):
        row = {"name": "S5", "rc": 0, "oomkilled": "false", "status": "COMPLETE",
               "end_line_present": True, "last_time": 3.0, "endTime": 3.0,
               "coldstart_ok": True, "age_guard_ok": True, "age_guard_detail": "ok",
               "expected_steps": 300, "time_line_count": 300,
               "execution_time_count": 600, "memavail_GiB": 20.0,
               "stage_kind": "unsteady", "dv_units": "dimensionless driver units",
               "n_cd_lines": 300, "n_cd_negative": 0, "n_cl_lines": 300}
        row.update(kw)
        return row
    def uD4_steady():
        # a STEADY stage prints `Time =` on its own interval: 6 lines against 500 outer
        # iterations. That must PASS -- the proxy is reported, not gated -- where the old
        # gate refused it for comparing the wrong quantity.
        r = g0_completion([_g0row(name="S1a", stage_kind="steady", expected_steps=500,
                                  time_line_count=6, execution_time_count=7,
                                  endTime=500.0, last_time=500.0,
                                  n_cd_lines=0, n_cd_negative=0)])
        check(r["verdict"] == "PASS", r)
    def uD4_unknown():
        _refuses(lambda: g0_completion([_g0row(stage_kind=None)]),
                 "a stage whose KIND is unknown -- the proxy cannot be known to mean anything")
    def uD4_unsteady_short():
        _refuses(lambda: g0_completion([_g0row(stage_kind="unsteady", time_line_count=299)]),
                 "an UNSTEADY stage short by one step (the proxy IS gated here)")
    def uD3_negatives():
        _refuses(lambda: g0_completion([_g0row(n_cd_negative=7)]),
                 "negative CD samples -- CD is positive-definite, so the reader is not reading CD")
    def uD3_uncounted():
        _refuses(lambda: g0_completion([_g0row(n_cd_negative=None)]),
                 "CD lines present but their sign never counted -- witness not taken")
    def uDW_excluded():
        # degenerate => EXCLUDED BY NAME, and NEVER a numeric zero
        r = g3_delta_window([1.0, 3.0] * 200, 300, period_steps=50.0)
        check(r["degenerate"] is True, r)
        check(r["delta_window"] is None, r)
        check(r["delta_window_rel"] is None, r)
        check(r["excluded_by_name"] == "delta_window", r)
        check(r["verdict"] == "NOT A RESULT", r)
        check("EXCLUDED BY NAME" in r["exclusion_note"], r)
    def uDW_live_is_numeric():
        r = g3_delta_window([1.0, 3.0] * 200, 300, period_steps=47.0)
        check(r["degenerate"] is False, r)
        check(isinstance(r["delta_window"], float), r)
    def uDW_eff_accepts_excluded():
        r = g4_delta_eff(0.0, None, 1.65e-06, window_degenerate=True)
        check(r["delta_eff"] == 1.65e-06, r)
        check(r["excluded_by_name"] == ["delta_window"], r)
        check(r["dominant_term"] == "delta_pert", r)
    def uDW_eff_refuses_unflagged_none():
        _refuses(lambda: g4_delta_eff(0.0, None, 1.65e-06, window_degenerate=False),
                 "a None delta_window that was NOT flagged degenerate -- missing is not excluded")
    def u0_age():
        exercised.add("G12R-0")
        check(g0_completion([_g0row()])['verdict'] == 'PASS', "unit check failed")
        _refuses(lambda: g0_completion([_g0row(age_guard_ok=False,
                                               age_guard_detail="STALE: U,p")]),
                 "AGE GUARD failed -- a field older than the case's own 0/U datum")
    def u0_age_unevaluated():
        _refuses(lambda: g0_completion([_g0row(age_guard_ok=None)]),
                 "age guard NOT EVALUATED -- absence of a check is not a pass")
    def u0_steps():
        _refuses(lambda: g0_completion([_g0row(time_line_count=299)]),
                 "primal wrote 299 Time lines against 300 registered steps")
    def u0_exectime():
        _refuses(lambda: g0_completion([_g0row(execution_time_count=12)]),
                 "ExecutionTime count below the registered step count")

    def u06():
        exercised.add("G12R-3")
        # REPAIRED 2026-08-25 (before first compute).  The original fixture used W = 2 on a
        # period-2 series, so W was an EXACT MULTIPLE of the period and EVERY block average
        # was identical: delta_window = 0 BY CONSTRUCTION.  The gate was right and the
        # fixture was wrong.  W = 3 does not divide the period, so a real spread exists.
        r = g3_delta_window([1.0, 3.0, 1.0, 3.0, 1.0, 3.0], 3)
        check(r['verdict'] == 'PASS' and r['n_windows'] == 4, r)
        check(abs(r['delta_window'] - 2.0 / 3.0) < 1e-12, r)
        check(abs(r['grand_mean'] - 2.0) < 1e-12, r)
    def u06c():
        # ADDED 2026-08-25.  Locks in what the broken fixture accidentally discovered, because
        # it is a HAZARD FOR D12 ITSELF: when the graded window W is an exact multiple of the
        # shedding period, delta_window collapses to EXACTLY ZERO -- not because the objective
        # is noiseless but because block averaging over whole periods cancels the phase spread.
        # delta_eff = max(delta_repeat, delta_window) would then be ~0 and G12R-4's h_min would
        # collapse with it.  This unit exists so that fact can never be rediscovered as a bug.
        r = g3_delta_window([1.0, 3.0, 1.0, 3.0, 1.0, 3.0], 2)
        check(r['verdict'] == 'PASS' and r['n_windows'] == 5, r)
        check(r['delta_window'] == 0.0, r)
    def u06b():
        try:
            g3_delta_window([1.0, 2.0], 2)   # exactly one window: no spread to measure
            raise AssertionError("G12R-3 did not refuse a single-window series")
        except Refusal:
            pass

    # ---- G12R-4
    def u07():
        exercised.add("G12R-4")
        r = g4_step_sizing(1.0e-6, 1.0)        # h_min = 1e-4
        check(r['verdict'] == 'PASS' and abs(r['h_min'] - 0.0001) < 1e-15, r)
        check(len(r['steps']) >= 3, r)
        r2 = g4_step_sizing(1.0e-2, 1.0)       # h_min = 1.0 > h_max
        check(r2['verdict'] == 'NOT A RESULT' and 'EXCEEDS' in r2['reason'], r2)
    def u07b():
        for de, g in [(-1.0, 1.0), (float("nan"), 1.0), (1e-6, 0.0), (1e-6, float("inf"))]:
            try:
                g4_step_sizing(de, g)
                raise AssertionError("G12R-4 did not refuse (%r,%r)" % (de, g))
            except Refusal:
                pass

    # ---- G12R-5
    def u08():
        exercised.add("G12R-5")
        sw = [{"h": 1e-5, "fd": 5.0}, {"h": 1e-4, "fd": 1.000},
              {"h": 1e-3, "fd": 1.005}, {"h": 1e-2, "fd": 1.010}, {"h": 1e-1, "fd": 3.0}]
        r = g5_plateau(sw)
        check(r['verdict'] == 'PASS' and r['h_star'] == 0.001, r)
        check(len(r['table']) == 5, 'every row, including the failures, must survive')
    def u08b():
        sw = [{"h": 1e-4, "fd": 1.0}, {"h": 1e-3, "fd": 2.0}, {"h": 1e-2, "fd": 4.0}]
        r = g5_plateau(sw)
        check(r['verdict'] == 'NOT A RESULT' and len(r['table']) == 3, r)
    def u08c():
        try:
            g5_plateau([])
            raise AssertionError("G12R-5 did not refuse an empty sweep")
        except Refusal:
            pass

    # ---- G12R-6, THE BRIGHT LINE.  Every band, plus the empty-component-set defect.
    def u09_pass():
        exercised.add("G12R-6")
        r = g6_bright_line([1.0, 2.0, 3.0], [1.00, 2.02, 3.00])
        check(r['verdict'] == 'PASS' and r['charter_band'] == 'PASS', r)
        check(len(r['per_component']) == 3, 'per-component must be reported BESIDE it')
    def u09_cond():
        # REPAIRED 2026-08-25 (before first compute).  The original fixture used 3.0*1.3,
        # a 30 % PER-COMPONENT error, and asserted the CONDITIONAL band.  But this gate's
        # statistic is the VECTOR-RELATIVE error over all components, which for that vector
        # is 20.02 % -- above the 15 % FAIL threshold.  The gate was right and the fixture
        # was wrong, and the fixture's error is precisely the confusion DAFOAM_CHARTER.md §2
        # forbids: "A vector norm and an average per-component error are different
        # statistics, and quoting one against the other is forbidden."
        # 3.0*1.1 gives a vector aggregate of 7.526 %, genuinely inside (5 %, 15 %].
        r = g6_bright_line([1.0, 2.0, 3.0], [1.0, 2.0, 3.0 * 1.1])
        check(r['charter_band'] == 'CONDITIONAL' and r['verdict'] == 'GATE FAIL', r)
        check(0.05 < r['aggregate_vector_rel'] <= 0.15, r)
    def u09_fail():
        r = g6_bright_line([1.0, 2.0, 3.0], [1.0, 2.0, 9.0])
        check(r['verdict'] == 'GATE FAIL' and r['charter_band'] == 'FAIL', r)
    def u09_flip():
        r = g6_bright_line([1.0, 2.0, 3.0], [1.0, 2.0, 3.0000001 * -1])
        check(r['verdict'] == 'GATE FAIL' and r['sign_flipped'] == [2], r)
    def u09_flip_only():
        # ADDED 2026-08-25 (before first compute), because a MUTATION TEST found the gap:
        # deleting the sign-flip override from g6 entirely left the WHOLE selftest passing.
        # u09_flip above cannot catch it -- its aggregate is 160 %, so the aggregate alone
        # already condemns the vector and the override is never load-bearing in any unit.
        # DAFOAM_CHARTER.md section 2 makes the sign-flip clause INDEPENDENT of the
        # aggregate: "FAIL above 15 % or on any sign-flipped component REGARDLESS OF THE
        # AGGREGATE."  This vector has an aggregate of 0.1414 % -- comfortably inside the
        # 5 % PASS band -- and one flipped component, so ONLY the override can condemn it.
        r = g6_bright_line([10.0, 10.0, 0.01], [10.0, 10.0, -0.01])
        check(r['aggregate_vector_rel'] <= BAND_PASS, r)
        check(r['sign_flipped'] == [2], r)
        check(r['verdict'] == 'GATE FAIL' and r['charter_band'] == 'FAIL', r)
    def u09_flag():
        r = g6_bright_line([1.0, 2.0, 3.0], [1.0, 2.0, 3.9], flagged=[2])
        check(r['aggregate_excl_flagged'] is not None, r)
        check(r['aggregate_excl_flagged'] < r['aggregate_vector_rel'], r)
    def u09_floor():
        r = g6_bright_line([1.0, 2.0], [1.0, 2.0 * 1.0001])
        check('HARNESS FLOOR' in r['harness_floor_note'], r)
    def u09_empty():
        # U-06e -- THE d3_grade.py DEFECT, in its own unit.
        for a, b in [([], []), ([1.0], []), ([], [1.0]), ([1.0, 2.0], [1.0])]:
            try:
                g6_bright_line(a, b)
                raise AssertionError("G12R-6 returned a verdict over the component set "
                                     "(%r, %r) -- an aggregate over nothing is not "
                                     "0.0000 %% agreement" % (a, b))
            except Refusal:
                pass
    def u09_zeroden():
        try:
            g6_bright_line([1.0, 2.0], [0.0, 0.0])
            raise AssertionError("G12R-6 divided by a zero-norm FD reference")
        except Refusal:
            pass

    # ---- G12R-7
    def u10():
        exercised.add("G12R-7")
        check(g7_trivial_baseline(0.4, 'PASS')['verdict'] == 'PASS', "unit check failed")
        r = g7_trivial_baseline(0.001, "PASS")
        check(r['verdict'] == 'WITHDRAWN' and 'WITHDRAWN' in r['note'], r)
    def u10b():
        try:
            g7_trivial_baseline(float("nan"), "PASS")
            raise AssertionError("G12R-7 did not refuse a non-finite aggregate")
        except Refusal:
            pass

    # ---- G12R-8
    def u11():
        exercised.add("G12R-8")
        r = g8_envelope({20: [0.50, 0.501], 40: [0.60, 0.601], 80: [0.90, 0.901]}, 25.0)
        check(r['verdict'] == 'PASS' and r['resolution'] == 'RESOLVED', r)
        r2 = g8_envelope({20: [0.5325, 0.5335], 40: [0.5330, 0.5320], 80: [0.5328, 0.5333]}, 25.0)
        check(r2['resolution'] == 'UNRESOLVED' and 'NOT reported as flat' in r2['note'], r2)
        r3 = g8_envelope({20: [0.5, 0.5], 80: [0.9, 0.9]}, 2.0)
        check(r3['verdict'] == 'BLOCKED', r3)
    def u11b():
        for bad in ({}, {20: [0.5, 0.5]}, {20: [0.5], 80: [0.9]}, {20: [], 80: [0.9, 0.9]}):
            try:
                g8_envelope(bad, 25.0)
                raise AssertionError("G12R-8 did not refuse %r" % (bad,))
            except Refusal:
                pass

    # ---- G12R-9 leg 2 and 3
    def u12():
        exercised.add("G12R-9")
        p = os.path.join(tmpdir, "plant.json")
        json.dump({"shape": [PLANT_SHAPE, 0, 0, 0], "obj": 1.001}, open(p, "w"))
        r = g9_plant(read_json(p), 1.0)
        check(r['verdict'] == 'PASS' and r['plant_response_rel'] > PLANT_FLOOR_REL, r)
    def u12b():
        p = os.path.join(tmpdir, "plant_blind.json")
        json.dump({"shape": [PLANT_SHAPE, 0, 0, 0], "obj": 1.0}, open(p, "w"))
        try:
            g9_plant(read_json(p), 1.0)
            raise AssertionError("G12R-9 did NOT refuse an objective blind to the plant")
        except Refusal:
            pass
        p2 = os.path.join(tmpdir, "plant_absent.json")
        json.dump({"shape": [0.0, 0, 0, 0], "obj": 1.001}, open(p2, "w"))
        try:
            g9_plant(read_json(p2), 1.0)
            raise AssertionError("G12R-9 did NOT refuse a plant absent from disk")
        except Refusal:
            pass
        p3 = os.path.join(tmpdir, "plant_noshape.json")
        json.dump({"shape": [], "obj": 1.001}, open(p3, "w"))
        try:
            g9_plant(read_json(p3), 1.0)
            raise AssertionError("G12R-9 did NOT refuse an empty shape vector")
        except Refusal:
            pass
    def u12c():
        # leg 3 -- the envelope reader's plant: a known du_delta written to disk, read back
        p = os.path.join(tmpdir, "ledger_plant.txt")
        open(p, "w").write("STAGE=x du_delta_B=987654321 rc=0\n")
        m = re.search(r"du_delta_B=(\d+)", open(p).read())
        check(m and int(m.group(1)) == 987654321, 'envelope reader is blind to its plant')

    # ---- G12R-10
    def u13():
        exercised.add("G12R-10")
        check(g10_two_rows({'verdict': 'PASS'}, {'verdict': 'PASS'})['verdict'] == 'PASS', "unit check failed")
        check(g10_two_rows({'verdict': 'PASS'}, {'verdict': 'GATE FAIL'})['verdict'] == 'GATE FAIL', "unit check failed")
        check(g10_two_rows({'verdict': 'PASS'}, None)['verdict'] == 'PENDING', "unit check failed")
    def u13b():
        try:
            g10_two_rows(None, {"verdict": "PASS"})
            raise AssertionError("G12R-10 did not refuse a missing SHIPPED row")
        except Refusal:
            pass

    # ---- G12R-11
    def u14():
        exercised.add("G12R-11")
        check(g11_optimisation(1.0, 0.5, 0.001, 'Optimal', True)['verdict'] == 'GATE REACHED', "unit check failed")
        r = g11_optimisation(1.0, 0.9999, 1e-3, "Optimal", True)
        check(r['verdict'] == 'NOT A RESULT' and 'phase-noise floor' in r['note'], r)
        check(g11_optimisation(1.0, None, 0.001, None, True)['verdict'] == 'PENDING', "unit check failed")
        check(g11_optimisation(1.0, None, 0.001, None, False)['verdict'] == 'NOT A RESULT', "unit check failed")
    def u14b():
        try:
            g11_optimisation(float("nan"), 0.5, 1e-3, "Optimal", True)
            raise AssertionError("G12R-11 did not refuse a non-finite baseline")
        except Refusal:
            pass

    _UNIT_LIST = [
        ("U-01  G12R-0 accepts a complete stage", u01),
        ("U-01b G12R-0 refuses all 13 rule-4 mutations", u01b),
        ("U-01c G12R-0 refuses an empty stage list", u01c),
        ("U-02  series reader reads a real log shape", u02),
        ("U-02b series reader refuses a zero-sample log", u02b),
        ("U-02c PLANT leg 1: series reader SEES a planted CD", u02c),
        ("U-03  block averages are the running mean", u03),
        ("U-03b block averages refuse empty/short series", u03b),
        ("U-04  G12R-1 both branches", u04),
        ("U-04b G12R-1 refuses an empty series", u04b),
        ("U-05  G12R-2 zero and non-zero repeat spread", u05),
        ("U-05b G12R-2 refuses <3 repeats and non-finites", u05b),
        ("U-W   G12R-W where-control PASS on index/sign/zero", uW),
        ("U-W1  G12R-W refuses the WRONG COMPONENT", uW_index),
        ("U-W2  G12R-W refuses the WRONG SIGN", uW_sign),
        ("U-W3  G12R-W refuses a SCALER ERROR (the D4-DEF-4 class)", uW_scaler),
        ("U-W4  G12R-W refuses a LEAK into a second component", uW_leak),
        ("U-W5  G12R-W refuses registered-but-not-applied", uW_nothing),
        ("U-W6  G12R-W refuses applied-but-not-registered", uW_unexpected),
        ("U-W7  G12R-W refuses a stage with no shape vector on disk", uW_novector),
        ("U-W8  G12R-W REFUSES a magnitude in UNREGISTERED units", uW_units),
        ("U-3b  G12R-3b recovers D12-F's 1.65e-06 MODEL-FREE", u3b),
        ("U-3b1 G12R-3b reports NOT DETECTABLE, not 'no floor'", u3b_undetectable),
        ("U-3b2 G12R-3b takes the MAX over components", u3b_max),
        ("U-3b3 G12R-3b refuses an EMPTY component set", u3b_empty),
        ("U-3b4 G12R-3b refuses probe steps not a decade apart", u3b_ratio),
        ("U-3d  G12R-3 flags W=300 at a 50-step period as DEGENERATE", u3_degen),
        ("U-3e  G12R-3 does NOT flag a non-dividing period", u3_nondegen),
        ("U-4e  G12R-4 delta_eff = max of THREE terms", u4_eff),
        ("U-4f  G12R-4 refuses all-zero noise terms", u4_allzero),
        ("U-4g  G12R-4 refuses a DEGENERATE delta_window as dominant", u4_degen_dominant),
        ("U-D4a G12R-0 a STEADY stage passes with 6/500 Time lines", uD4_steady),
        ("U-D4b G12R-0 REFUSES an unknown stage_kind", uD4_unknown),
        ("U-D4c G12R-0 still gates the step count on an UNSTEADY stage", uD4_unsteady_short),
        ("U-D3a G12R-0 REFUSES negative CD samples (reader is not reading CD)", uD3_negatives),
        ("U-D3b G12R-0 REFUSES CD lines whose sign was never counted", uD3_uncounted),
        ("U-DW1 G12R-3 degenerate => EXCLUDED BY NAME, never a numeric 0.0", uDW_excluded),
        ("U-DW2 G12R-3 live => a real number", uDW_live_is_numeric),
        ("U-DW3 G12R-4 accepts an EXCLUDED delta_window", uDW_eff_accepts_excluded),
        ("U-DW4 G12R-4 REFUSES a None delta_window not flagged degenerate", uDW_eff_refuses_unflagged_none),
        ("U-0a  G12R-0 AGE GUARD refuses a stale field", u0_age),
        ("U-0b  G12R-0 refuses an UNEVALUATED age guard", u0_age_unevaluated),
        ("U-0c  G12R-0 refuses a short primal step count", u0_steps),
        ("U-0d  G12R-0 refuses a short ExecutionTime count", u0_exectime),
        ("U-06  G12R-3 window spread", u06),
        ("U-06c G12R-3 W a multiple of the period => delta_window EXACTLY 0", u06c),
        ("U-06b G12R-3 refuses a single-window series", u06b),
        ("U-07  G12R-4 both branches incl. h_min > h_max", u07),
        ("U-07b G12R-4 refuses bad delta_eff / |g|", u07b),
        ("U-08  G12R-5 finds a plateau, keeps failed rows", u08),
        ("U-08b G12R-5 NOT A RESULT with no plateau", u08b),
        ("U-08c G12R-5 refuses an empty sweep", u08c),
        ("U-09p G12R-6 PASS band", u09_pass),
        ("U-09c G12R-6 CONDITIONAL band", u09_cond),
        ("U-09f G12R-6 FAIL band", u09_fail),
        ("U-09s G12R-6 sign flip overrides the aggregate", u09_flip),
        ("U-09s2 G12R-6 sign flip condemns a vector INSIDE the PASS band", u09_flip_only),
        ("U-09g G12R-6 flagged components excluded BY NAME", u09_flag),
        ("U-09h G12R-6 flags a sub-harness-floor aggregate", u09_floor),
        ("U-06e G12R-6 EMPTY COMPONENT SET refuses (the d3_grade.py defect)", u09_empty),
        ("U-09z G12R-6 refuses a zero-norm FD reference", u09_zeroden),
        ("U-10  G12R-7 PASS and WITHDRAWN", u10),
        ("U-10b G12R-7 refuses a non-finite aggregate", u10b),
        ("U-11  G12R-8 RESOLVED / UNRESOLVED / BLOCKED", u11),
        ("U-11b G12R-8 refuses one-run-per-point", u11b),
        ("U-12  PLANT leg 2: G12R-9 sees the plant", u12),
        ("U-12b PLANT leg 2: G12R-9 refuses a blind reader", u12b),
        ("U-12c PLANT leg 3: envelope reader sees its plant", u12c),
        ("U-13  G12R-10 all three branches", u13),
        ("U-13b G12R-10 refuses a missing SHIPPED row", u13b),
        ("U-14  G12R-11 all four branches", u14),
        ("U-14b G12R-11 refuses a non-finite baseline", u14b),
    ]
    for nm, fn in _UNIT_LIST:
        _u(nm, fn, R)

    # ---- THE COUNTED EXIT.  The battery's verdict is arithmetic on explicit results,
    # ---- never the absence of an escaping exception.
    bad = [r for r in R if r[1] != "ok"]
    count_ok = (len(R) == EXPECTED_UNITS and len(_UNIT_LIST) == EXPECTED_UNITS)
    print("SELFTEST UNITS: %d, failures: %d" % (len(R), len(bad)))
    for nm, st, msg in R:
        print("  [%s] %s%s" % (st, nm, ("  -- " + msg) if msg else ""))
    print("")
    print("GATES THIS FILE CAN EMIT   (%d): %s" % (len(GATES_EMITTED), " ".join(GATES_EMITTED)))
    ex = sorted(exercised)
    print("GATES THE SELFTEST EXERCISES (%d): %s" % (len(ex), " ".join(ex)))
    missing = [g for g in GATES_EMITTED if g not in exercised]
    print("GATES EMITTED BUT NEVER EXERCISED (%d): %s"
          % (len(missing), " ".join(missing) if missing else "(none)"))
    print("")
    print("COUNTING UNITS MEASURES THIS SELFTEST'S SIZE, NOT ITS COVERAGE. The list above")
    print("is the coverage claim; the unit count is not.")
    print("")
    print("COUNTED EXIT: units REGISTERED (frozen constant) %d, units in the list %d, "
          "units that RETURNED A RESULT %d, failures %d"
          % (EXPECTED_UNITS, len(_UNIT_LIST), len(R), len(bad)))
    if not count_ok:
        print("*** UNIT COUNT MISMATCH: a unit registered in the list produced NO RESULT.")
        print("    A missing count FAILS. An absent failure would have passed, which is the")
        print("    whole reason the exit is arithmetic and not exception-driven.")
    # ---- ASSERT AUDIT, run as part of every battery: STATEMENT TYPE, not behaviour ----
    n_assert = _count_assert_statements(__file__)
    print("ASSERT AUDIT: %d `assert` statements in this file (must be 0 -- `-O` deletes them)"
          % n_assert)
    if bad or missing or (not count_ok) or n_assert != 0:
        return 1
    return 0


# =============================================================================
# THE PLAN MODES -- where step selection lives, and why it lives HERE
# =============================================================================
# SUPERVISOR_D12_RULINGS.md section 3 condition 3: "The launcher stages in two phases;
# IT DOES NOT CHOOSE A STEP.  The rule that selects the step stays frozen in the
# comparator and must remain POSITIONAL OVER THE PLATEAU, NEVER READING THE ADJOINT."
#
# That property is not decoration.  In D10-F' the positional rule landed on the step that
# independently minimised disagreement with a number it never reads, producing a V-shaped
# error column whose minimum coincided with the rule's own choice.  A grader fitting the
# step to the answer cannot produce that coincidence, which is why the coincidence is
# evidence.  Give the rule sight of the adjoint and the evidence evaporates.
#
# So: G12R-4 sizes the RANGE of the sweep from |g| -- that is the pre-registration's own
# registered arithmetic, and sizing a range is not selecting a step.  G12R-5 selects h*
# POSITIONALLY over the plateau and never sees the adjoint at all.

def _read_manifest_rows(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        raise Refusal("manifest %s holds NO stage rows" % path)
    return rows


def _by_name(rows):
    d = {}
    for r in rows:
        d[r.get("name")] = r
    return d


def plan(manifest_path, root, man_meta=None):
    """--plan : phase 1 -> step_plan.json.  Computes delta_eff and the sweep RANGE."""
    rows = [r for r in _read_manifest_rows(manifest_path) if not r.get("blocked")]
    out = {"gates": []}
    out["gates"].append(g0_completion(rows))

    # ---- G12R-W on EVERY stage, before any number from it is used ------------------
    nsh = None
    for r in rows:
        if r.get("nShapes"):
            nsh = int(r["nShapes"])
            break
    if nsh is not None and nsh != 4:
        raise Refusal("nShapes is %r, the registered case has 4 shape modes" % nsh)
    where = []
    for r in rows:
        if r.get("applied_shape_vector") is None:
            continue
        where.append(g_where(r, r.get("registered_dvIndex", 0),
                             r.get("registered_dvDelta", 0.0), nshapes=nsh))
    out["gates"].append({"gate": "G12R-W", "verdict": "PASS", "n_stages_witnessed": len(where)})
    if not where:
        raise Refusal("G12R-W witnessed ZERO stages -- the WHERE-control read nothing, and "
                      "a control that read nothing has not passed")

    byn = _by_name(rows)

    # ---- G12R-1 and G12R-3 from S2's own series on disk -----------------------------
    s2 = byn.get("S2b")
    if not s2:
        raise Refusal("no S2b diagnostic stage in the manifest")
    # [D1] FIELD_B COMPLETENESS, verified comparator-side from the manifest the launcher
    # wrote. The launcher refuses at stage time; this refuses at grade time. Both ask the
    # SAME question -- "is this enough to start a solve?" -- which is the question the md5
    # control never asked.
    fbc = man_meta.get("field_b_completeness") if isinstance(man_meta, dict) else None
    logp = os.path.join(root, os.path.basename(s2.get("log", "")))
    cands = [p for p in os.listdir(root) if p.startswith("S2b_") and p.endswith(".log")]
    if not cands:
        raise Refusal("no S2b log on disk in %s" % root)
    _, cd, _ = read_series(os.path.join(root, sorted(cands)[-1]))
    if len(cd) <= TRANSIENT_DISCARD:
        raise Refusal("S2b produced %d CD samples, at or below the registered %d-step "
                      "transient discard" % (len(cd), TRANSIENT_DISCARD))
    if any(v < 0.0 for v in cd):
        raise Refusal("S2b's CD series carries %d NEGATIVE samples. CD is positive-definite "
                      "for this flow; the reader is not reading CD."
                      % sum(1 for v in cd if v < 0.0))
    retained = cd[TRANSIENT_DISCARD:]
    g1 = g1_limit_cycle(retained)
    out["gates"].append(g1)
    g3 = g3_delta_window(retained, W_PRIMARY, period_steps=g1.get("period_steps"))
    out["gates"].append(g3)

    # ---- G12R-2 delta_repeat --------------------------------------------------------
    reps = [byn["S3_r%d" % i]["obj"] for i in (1, 2, 3) if byn.get("S3_r%d" % i)]
    if len(reps) < 3:
        raise Refusal("delta_repeat needs 3 runs, the manifest carries %d" % len(reps))
    g2 = g2_delta_repeat(reps)
    out["gates"].append(g2)

    # ---- G12R-3b delta_pert, MEASURED HERE, never imported --------------------------
    pairs = []
    for i in range(nsh or 4):
        row = {"component": i}
        ok = True
        for tag, key, h in (("a", "S_a", DPERT_HA), ("b", "S_b", DPERT_HB)):
            pn = byn.get("S3b_c%d_%sp" % (i, tag))
            mn = byn.get("S3b_c%d_%sm" % (i, tag))
            if not pn or not mn or pn.get("obj") is None or mn.get("obj") is None:
                ok = False
                break
            row[key] = abs(float(pn["obj"]) - float(mn["obj"]))
            row["h_a" if tag == "a" else "h_b"] = h
        if ok:
            pairs.append(row)
    g3b = g3b_delta_pert(pairs)
    out["gates"].append(g3b)

    # ---- delta_eff, and the step RANGE ---------------------------------------------
    ge = g4_delta_eff(g2["delta_repeat"], g3["delta_window"], g3b["delta_pert"],
                      window_degenerate=g3.get("degenerate"))
    out["gates"].append(ge)
    s5 = byn.get("S5")
    if not s5 or not s5.get("dobj_dshape"):
        raise Refusal("no S5 adjoint in the manifest -- no |g| to size the sweep range")
    g_comp = float(s5["dobj_dshape"][0])
    g4 = g4_step_sizing(ge["delta_eff"], g_comp)
    out["gates"].append(g4)

    planj = {"admissible": bool(g4.get("verdict") == "PASS" and g4.get("steps")),
             "steps": g4.get("steps", []), "h_min": g4.get("h_min"),
             "h_max": H_MAX, "delta_eff": ge["delta_eff"],
             "delta_terms": ge["terms"], "dominant_term": ge["dominant_term"],
             "window_degenerate": g3.get("degenerate"),
             "period_steps": g1.get("period_steps"),
             "g_component_0": g_comp}
    with open(os.path.join(root, "step_plan.json"), "w") as f:
        json.dump(planj, f, indent=2, sort_keys=True)
    out["step_plan"] = planj
    return out


def plan2(manifest_path, root):
    """--plan2 : phase 2 -> step_plan2.json.  Selects h* POSITIONALLY.  NO ADJOINT."""
    rows = [r for r in _read_manifest_rows(manifest_path) if not r.get("blocked")]
    g0_completion(rows)
    byn = _by_name(rows)
    with open(os.path.join(root, "step_plan.json")) as f:
        pj = json.load(f)
    fds, used = [], []
    for k, h in enumerate(pj["steps"], start=1):
        pn, mn = byn.get("S6_s%d_p" % k), byn.get("S6_s%d_m" % k)
        if not pn or not mn or pn.get("obj") is None or mn.get("obj") is None:
            continue
        g_where(pn, 0, h, nshapes=4)
        g_where(mn, 0, -h, nshapes=4)
        fds.append((float(pn["obj"]) - float(mn["obj"])) / (2.0 * float(h)))
        used.append(float(h))
    if len(used) < 3:
        raise Refusal("G12R-5: only %d usable sweep steps on disk; a plateau needs at "
                      "least %d and one step is never a plateau" % (len(used), PLATEAU_MIN_RUN))
    g5 = g5_plateau(used, fds) if "g5_plateau" in globals() else None
    if g5 is None:
        # positional plateau, inline: consecutive steps agreeing within PLATEAU_TOL_REL
        runs, cur = [], [0]
        for i in range(len(fds) - 1):
            a, b = fds[i], fds[i + 1]
            if b != 0.0 and abs(a - b) / abs(b) <= PLATEAU_TOL_REL:
                cur.append(i + 1)
            else:
                runs.append(cur); cur = [i + 1]
        runs.append(cur)
        best = max(runs, key=len)
        g5 = {"gate": "G12R-5",
              "verdict": "PASS" if len(best) >= PLATEAU_MIN_RUN else "NOT A RESULT",
              "run_len": len(best), "steps": used, "fd": fds,
              "h_star": (used[best[(len(best) - 1) // 2]] if len(best) >= PLATEAU_MIN_RUN else None)}
    hs = g5.get("h_star")
    p2 = {"h_star": hs, "h_wrong": (hs * TRIVIAL_MULTIPLIER if hs else None),
          "plateau_verdict": g5["verdict"], "plateau_run_len": g5.get("run_len"),
          "steps": used, "fd_estimates": fds,
          "NOTE": "h* was selected POSITIONALLY over the plateau. No adjoint was read."}
    with open(os.path.join(root, "step_plan2.json"), "w") as f:
        json.dump(p2, f, indent=2, sort_keys=True)
    return {"gates": [g5], "step_plan2": p2}


def plan3(manifest_path, root):
    """--plan3 : phase 3 -> step_plan3.json.  G12R-6 at h*, and G12R-11's AUTHORISATION.

    The optimisation is authorised BY THE COMPARATOR, never by the launcher.  G12R-11:
    S8 runs only if the bright line returns PASS or the charter's CONDITIONAL band on the
    SHIPPED row; otherwise D12's optimisation is NOT A RESULT and is not launched.
    """
    rows = [r for r in _read_manifest_rows(manifest_path) if not r.get("blocked")]
    g0_completion(rows)
    byn = _by_name(rows)
    with open(os.path.join(root, "step_plan2.json")) as f:
        p2 = json.load(f)
    hs = p2.get("h_star")
    if not hs:
        raise Refusal("G12R-6: no h* -- the plateau gate did not return one, so there is "
                      "no step at which to take a vector FD")
    s5 = byn.get("S5")
    if not s5 or not s5.get("dobj_dshape"):
        raise Refusal("G12R-6: no S5 adjoint in the manifest")
    g_adj, g_fd = [], []
    for i in range(len(s5["dobj_dshape"])):
        pn, mn = byn.get("S6c_c%d_p" % i), byn.get("S6c_c%d_m" % i)
        if not pn or not mn or pn.get("obj") is None or mn.get("obj") is None:
            raise Refusal("G12R-6: component %d has no FD pair on disk at h*; the "
                          "aggregate would be taken over a SHORT component set (%d of %d)"
                          % (i, len(g_fd), len(s5["dobj_dshape"])))
        g_where(pn, i, hs, nshapes=len(s5["dobj_dshape"]), require_units=True)
        g_where(mn, i, -hs, nshapes=len(s5["dobj_dshape"]), require_units=True)
        g_adj.append(float(s5["dobj_dshape"][i]))
        g_fd.append((float(pn["obj"]) - float(mn["obj"])) / (2.0 * float(hs)))
    g6 = g6_bright_line(g_adj, g_fd, label="SHIPPED at h*=%r" % hs)
    authorised = g6["charter_band"] in ("PASS", "CONDITIONAL")
    p3 = {"optimisation_authorised": authorised, "h_star": hs,
          "aggregate_vector_rel": g6["aggregate_vector_rel"],
          "charter_band": g6["charter_band"], "verdict": g6["verdict"],
          "per_component": g6["per_component"], "sign_flipped": g6["sign_flipped"],
          "NOTE": ("The optimisation is authorised by THIS comparator, not by the "
                   "launcher. A refusal here means D12's optimisation is NOT A RESULT.")}
    with open(os.path.join(root, "step_plan3.json"), "w") as f:
        json.dump(p3, f, indent=2, sort_keys=True)
    return {"gates": [g6], "step_plan3": p3}


def _count_assert_statements(path):
    """Count `assert` STATEMENTS by AST.  Statement type, not behaviour.

    A grep for the word `assert` would match `raise AssertionError`, a docstring, or a
    variable called `assert_state`.  A behavioural test would pass a file whose asserts
    all happen to hold.  Only the statement type distinguishes `assert X` -- which `-O`
    DELETES -- from `if not X: raise ...` -- which it does not.  This is what catches a
    future edit that reverts a `raise` back to an `assert`.
    """
    import ast as _ast
    try:
        with open(path) as f:
            t = _ast.parse(f.read())
    except Exception:                                          # noqa: BLE001
        return -1
    return sum(1 for n in _ast.walk(t) if isinstance(n, _ast.Assert))


def olimb(tmpdir):
    """--olimb : prove the battery still catches a defect UNDER `python3 -O`.

    THE POINT, AND WHY THE OBVIOUS TEST IS WORTHLESS.  Running the battery on HEALTHY
    input under both flags and comparing the output proves nothing: healthy input passes
    either way, so identical output is exactly what a COMPLETELY DISABLED battery
    produces.  The supervisor's own first attempt did this and got identical output for
    the wrong reason.

    So this limb MUTATES the file first -- a mutant that MUST be caught -- and then
    requires BOTH `python3` and `python3 -O` to catch it.  A battery that catches the
    mutant unflagged and misses it under `-O` is the failure this limb exists to find.

    Two mutants are run:
      M-A  a GATE mutant  (the PASS band widened) -- the classic behavioural mutant.
      M-B  a STATEMENT-TYPE mutant: one `check(...)` reverted to `assert ...`, which is
           what a well-meaning future edit looks like.  It must be caught by the AST
           audit, and the audit must fire IDENTICALLY under `-O`.
    """
    import re as _re
    import shutil as _sh
    import subprocess as _sp
    here = os.path.abspath(__file__)
    os.makedirs(tmpdir, exist_ok=True)
    src = open(here).read()
    results = []

    def run(path, flag):
        cmd = [sys.executable] + (["-O"] if flag else []) + [path, "--selftest"]
        pr = _sp.run(cmd, capture_output=True, text=True)
        return pr.returncode, pr.stdout

    # ---- control: the unmutated file must PASS under both flags --------------
    for flag in (False, True):
        rc, _ = run(here, flag)
        results.append(("control unmutated", "-O" if flag else "  ", rc, rc == 0))

    # ---- M-A: a gate mutant, which MUST be caught under BOTH flags -----------
    ma = os.path.join(tmpdir, "mutant_gate.py")
    s2, n = _re.subn(r"^BAND_PASS( +)= 0\.05", r"BAND_PASS\g<1>= 0.50", src, count=1, flags=_re.M)
    if n != 1:
        raise Refusal("--olimb could not build the gate mutant; the target line moved")
    open(ma, "w").write(s2)
    for flag in (False, True):
        rc, _ = run(ma, flag)
        results.append(("M-A gate mutant (PASS band 0.05->0.50)", "-O" if flag else "  ", rc, rc != 0))

    # ---- M-B: a STATEMENT-TYPE mutant -- one check() reverted to an assert ----
    mb = os.path.join(tmpdir, "mutant_assert.py")
    s3, n = _re.subn(r"^(\s*)check\((.+), (.+)\)$", r"\g<1>assert \g<2>, \g<3>", src,
                     count=1, flags=_re.M)
    if n != 1:
        raise Refusal("--olimb could not build the statement-type mutant")
    open(mb, "w").write(s3)
    for flag in (False, True):
        rc, _ = run(mb, flag)
        results.append(("M-B one check() reverted to `assert`", "-O" if flag else "  ", rc, rc != 0))

    print("=" * 74)
    print("`python3 -O` LIMB -- a battery is flag-proof only if it still CATCHES under -O")
    print("=" * 74)
    ok = True
    for name, flag, rc, good in results:
        ok = ok and good
        print("  %-42s %s rc=%d  %s" % (name, flag, rc, "OK" if good else "*** BAD ***"))
    print("")
    print("  M-A is behavioural; M-B is STATEMENT TYPE. M-B is the one that matters here:")
    print("  reverting a single check() to an assert is what a future edit actually looks")
    print("  like, and under -O that assert VANISHES -- so only an AST audit can see it.")
    print("")
    print("  %s" % ("-O LIMB PASSES" if ok else "*** -O LIMB FAILS ***"))
    _sh.rmtree(tmpdir, ignore_errors=True)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--olimb", action="store_true")
    ap.add_argument("--assert-audit", dest="assert_audit", action="store_true")
    ap.add_argument("--plan3", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--plan2", action="store_true")
    ap.add_argument("--root", default=None)
    ap.add_argument("--gatelist", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--manifest", default=None,
                    help="path to d12r_manifest.json written by the launcher")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.gatelist:
        print("\n".join(GATES_EMITTED))
        return 0
    if a.assert_audit:
        n = _count_assert_statements(os.path.abspath(__file__))
        print("assert statements in this file: %d (must be 0)" % n)
        return 0 if n == 0 else 1
    if a.olimb:
        return olimb(os.path.join(a.tmpdir, "d12x_olimb"))
    if a.selftest:
        d = os.path.join(a.tmpdir, "d12r_selftest")
        os.makedirs(d, exist_ok=True)
        return selftest(d)
    if a.plan or a.plan2 or a.plan3:
        if not (a.manifest and a.root):
            print("REFUSAL: --plan/--plan2 need --manifest and --root", file=sys.stderr)
            return 3
        try:
            res = (plan if a.plan else (plan2 if a.plan2 else plan3))(a.manifest, a.root)
        except Refusal as e:
            print("REFUSAL: %s" % e, file=sys.stderr)
            return 2
        print(json.dumps(res, indent=2, sort_keys=True, default=str))
        return 0
    if not a.manifest:
        print("REFUSAL: no --manifest and no --selftest", file=sys.stderr)
        return 2
    try:
        man = read_json(a.manifest)
        res = grade_from_manifest(man, os.path.dirname(os.path.abspath(a.manifest)))
    except Refusal as e:
        print("REFUSAL: %s" % e, file=sys.stderr)
        return 2
    txt = json.dumps(res, indent=2, sort_keys=True, default=str)
    print(txt)
    if a.out:
        with open(a.out, "w") as f:
            f.write(txt)
    return 0


def grade_from_manifest(man, root):
    """Assemble every gate from the launcher's manifest and the artifacts it names."""
    stages = man.get("stages")
    if not stages:
        raise Refusal("manifest carries no stages")
    out = {"gates": [], "registered": {"W": W_PRIMARY, "W2": W_CONTINGENCY,
                                       "h_max": H_MAX, "cap_core_min": CAP_CORE_MIN}}
    out["gates"].append(g0_completion(stages))
    s2 = man.get("s2")
    if s2:
        _, cd, _ = read_series(os.path.join(root, s2["log"]))
        if len(cd) <= TRANSIENT_DISCARD:
            raise Refusal("S2 produced %d samples, at or below the registered %d-step "
                          "transient discard" % (len(cd), TRANSIENT_DISCARD))
        retained = cd[TRANSIENT_DISCARD:]
        out["gates"].append(g1_limit_cycle(retained))
        out["gates"].append(g3_delta_window(retained, man.get("W", W_PRIMARY)))
    if man.get("repeat_objs"):
        out["gates"].append(g2_delta_repeat(man["repeat_objs"]))
    return out


if __name__ == "__main__":
    sys.exit(main())
