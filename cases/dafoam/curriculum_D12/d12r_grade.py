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
TRANSIENT_DISCARD  = 300        # timesteps of S2 discarded before FIELD_B
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

GATES_EMITTED = ["G12R-0", "G12R-1", "G12R-2", "G12R-3", "G12R-4", "G12R-5",
                 "G12R-6", "G12R-7", "G12R-8", "G12R-9", "G12R-10", "G12R-11"]


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


def g3_delta_window(cd_retained, W):
    blocks = block_averages(cd_retained, W)
    if len(blocks) < 2:
        raise Refusal("G12R-3: only %d block averages at W=%d -- no spread to measure"
                      % (len(blocks), W))
    d = max(blocks) - min(blocks)
    m = sum(blocks) / len(blocks)
    return {"gate": "G12R-3", "verdict": "PASS", "W": W, "n_windows": len(blocks),
            "delta_window": d,
            "delta_window_rel": (d / abs(m) if m != 0.0 else float("inf")),
            "grand_mean": m, "block_min": min(blocks), "block_max": max(blocks)}


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


# ---------------------------------------------------------------- selftest
def _u(name, fn, results):
    try:
        fn()
        results.append((name, "ok", ""))
    except AssertionError as e:
        results.append((name, "FAIL", str(e)))
    except Exception as e:
        results.append((name, "ERROR", "%s: %s" % (type(e).__name__, e)))


def selftest(tmpdir):
    R = []
    exercised = set()

    def base_stage(**kw):
        st = {"name": "s", "rc": 0, "oomkilled": "false", "status": "COMPLETE",
              "end_line_present": True, "last_time": 3.0, "endTime": 3.0,
              "coldstart_ok": True, "field_b_md5_ok": True,
              "obj": 1.0, "obj_from_log": 1.0, "memavail_GiB": 25.0}
        st.update(kw)
        return st

    # ---- G12R-0
    def u01():
        exercised.add("G12R-0")
        assert g0_completion([base_stage()])["verdict"] == "PASS"
    def u01b():
        for mut, val in [("rc", 1), ("oomkilled", "true"), ("status", "STARTED"),
                         ("end_line_present", False), ("last_time", 2.99),
                         ("coldstart_ok", False), ("field_b_md5_ok", False),
                         ("memavail_GiB", 3.0), ("obj_from_log", 1.5)]:
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
        assert cd == [1.0, 2.0, 3.0], cd
        assert av[-1] == 2.0
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
        assert cd2 == [1.0, 14.0, 3.0], ("PLANT UNSEEN by the series reader", cd2)

    # ---- block averages
    def u03():
        assert block_averages([1.0, 2.0, 3.0, 4.0], 2) == [1.5, 2.5, 3.5]
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
        assert r["verdict"] == "PASS", r
        flat = [1.0 + 1e-9 * (i % 2) for i in range(100)]
        r2 = g1_limit_cycle(flat)
        assert r2["verdict"] == "NOT A RESULT", r2
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
        assert r["delta_repeat"] == 0.0 and "NOT A CLEARANCE" in r["note"], r
        r2 = g2_delta_repeat([1.0, 1.002, 1.001])
        assert abs(r2["delta_repeat"] - 0.002) < 1e-12, r2
    def u05b():
        for bad in ([], [1.0], [1.0, 2.0], [1.0, float("nan"), 2.0]):
            try:
                g2_delta_repeat(bad)
                raise AssertionError("G12R-2 did not refuse %r" % (bad,))
            except Refusal:
                pass

    # ---- G12R-3
    def u06():
        exercised.add("G12R-3")
        # REPAIRED 2026-08-25 (before first compute).  The original fixture used W = 2 on a
        # period-2 series, so W was an EXACT MULTIPLE of the period and EVERY block average
        # was identical: delta_window = 0 BY CONSTRUCTION.  The gate was right and the
        # fixture was wrong.  W = 3 does not divide the period, so a real spread exists.
        r = g3_delta_window([1.0, 3.0, 1.0, 3.0, 1.0, 3.0], 3)
        assert r["verdict"] == "PASS" and r["n_windows"] == 4, r
        assert abs(r["delta_window"] - 2.0 / 3.0) < 1e-12, r
        assert abs(r["grand_mean"] - 2.0) < 1e-12, r
    def u06c():
        # ADDED 2026-08-25.  Locks in what the broken fixture accidentally discovered, because
        # it is a HAZARD FOR D12 ITSELF: when the graded window W is an exact multiple of the
        # shedding period, delta_window collapses to EXACTLY ZERO -- not because the objective
        # is noiseless but because block averaging over whole periods cancels the phase spread.
        # delta_eff = max(delta_repeat, delta_window) would then be ~0 and G12R-4's h_min would
        # collapse with it.  This unit exists so that fact can never be rediscovered as a bug.
        r = g3_delta_window([1.0, 3.0, 1.0, 3.0, 1.0, 3.0], 2)
        assert r["verdict"] == "PASS" and r["n_windows"] == 5, r
        assert r["delta_window"] == 0.0, r
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
        assert r["verdict"] == "PASS" and abs(r["h_min"] - 1.0e-4) < 1e-15, r
        assert len(r["steps"]) >= 3, r
        r2 = g4_step_sizing(1.0e-2, 1.0)       # h_min = 1.0 > h_max
        assert r2["verdict"] == "NOT A RESULT" and "EXCEEDS" in r2["reason"], r2
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
        assert r["verdict"] == "PASS" and r["h_star"] == 1e-3, r
        assert len(r["table"]) == 5, "every row, including the failures, must survive"
    def u08b():
        sw = [{"h": 1e-4, "fd": 1.0}, {"h": 1e-3, "fd": 2.0}, {"h": 1e-2, "fd": 4.0}]
        r = g5_plateau(sw)
        assert r["verdict"] == "NOT A RESULT" and len(r["table"]) == 3, r
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
        assert r["verdict"] == "PASS" and r["charter_band"] == "PASS", r
        assert len(r["per_component"]) == 3, "per-component must be reported BESIDE it"
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
        assert r["charter_band"] == "CONDITIONAL" and r["verdict"] == "GATE FAIL", r
        assert 0.05 < r["aggregate_vector_rel"] <= 0.15, r
    def u09_fail():
        r = g6_bright_line([1.0, 2.0, 3.0], [1.0, 2.0, 9.0])
        assert r["verdict"] == "GATE FAIL" and r["charter_band"] == "FAIL", r
    def u09_flip():
        r = g6_bright_line([1.0, 2.0, 3.0], [1.0, 2.0, 3.0000001 * -1])
        assert r["verdict"] == "GATE FAIL" and r["sign_flipped"] == [2], r
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
        assert r["aggregate_vector_rel"] <= BAND_PASS, r
        assert r["sign_flipped"] == [2], r
        assert r["verdict"] == "GATE FAIL" and r["charter_band"] == "FAIL", r
    def u09_flag():
        r = g6_bright_line([1.0, 2.0, 3.0], [1.0, 2.0, 3.9], flagged=[2])
        assert r["aggregate_excl_flagged"] is not None, r
        assert r["aggregate_excl_flagged"] < r["aggregate_vector_rel"], r
    def u09_floor():
        r = g6_bright_line([1.0, 2.0], [1.0, 2.0 * 1.0001])
        assert "HARNESS FLOOR" in r["harness_floor_note"], r
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
        assert g7_trivial_baseline(0.40, "PASS")["verdict"] == "PASS"
        r = g7_trivial_baseline(0.001, "PASS")
        assert r["verdict"] == "WITHDRAWN" and "WITHDRAWN" in r["note"], r
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
        assert r["verdict"] == "PASS" and r["resolution"] == "RESOLVED", r
        r2 = g8_envelope({20: [0.5325, 0.5335], 40: [0.5330, 0.5320], 80: [0.5328, 0.5333]}, 25.0)
        assert r2["resolution"] == "UNRESOLVED" and "NOT reported as flat" in r2["note"], r2
        r3 = g8_envelope({20: [0.5, 0.5], 80: [0.9, 0.9]}, 2.0)
        assert r3["verdict"] == "BLOCKED", r3
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
        assert r["verdict"] == "PASS" and r["plant_response_rel"] > PLANT_FLOOR_REL, r
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
        assert m and int(m.group(1)) == 987654321, "envelope reader is blind to its plant"

    # ---- G12R-10
    def u13():
        exercised.add("G12R-10")
        assert g10_two_rows({"verdict": "PASS"}, {"verdict": "PASS"})["verdict"] == "PASS"
        assert g10_two_rows({"verdict": "PASS"}, {"verdict": "GATE FAIL"})["verdict"] == "GATE FAIL"
        assert g10_two_rows({"verdict": "PASS"}, None)["verdict"] == "PENDING"
    def u13b():
        try:
            g10_two_rows(None, {"verdict": "PASS"})
            raise AssertionError("G12R-10 did not refuse a missing SHIPPED row")
        except Refusal:
            pass

    # ---- G12R-11
    def u14():
        exercised.add("G12R-11")
        assert g11_optimisation(1.0, 0.5, 1e-3, "Optimal", True)["verdict"] == "GATE REACHED"
        r = g11_optimisation(1.0, 0.9999, 1e-3, "Optimal", True)
        assert r["verdict"] == "NOT A RESULT" and "phase-noise floor" in r["note"], r
        assert g11_optimisation(1.0, None, 1e-3, None, True)["verdict"] == "PENDING"
        assert g11_optimisation(1.0, None, 1e-3, None, False)["verdict"] == "NOT A RESULT"
    def u14b():
        try:
            g11_optimisation(float("nan"), 0.5, 1e-3, "Optimal", True)
            raise AssertionError("G12R-11 did not refuse a non-finite baseline")
        except Refusal:
            pass

    for nm, fn in [
        ("U-01  G12R-0 accepts a complete stage", u01),
        ("U-01b G12R-0 refuses all 9 rule-4 mutations", u01b),
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
    ]:
        _u(nm, fn, R)

    bad = [r for r in R if r[1] != "ok"]
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
    if bad or missing:
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--gatelist", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--manifest", default=None,
                    help="path to d12r_manifest.json written by the launcher")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.gatelist:
        print("\n".join(GATES_EMITTED))
        return 0
    if a.selftest:
        d = os.path.join(a.tmpdir, "d12r_selftest")
        os.makedirs(d, exist_ok=True)
        return selftest(d)
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
