#!/usr/bin/env python3
"""T25R6a GRADER -- G-T6a, THE WALL-COST GATE.

FROZEN AT THE PRE-REGISTRATION COMMIT, BEFORE ANY CASE DIRECTORY EXISTS.
Registration: docs/campaigns/T-family/T25R6a_PREREGISTRATION.md v1.0.

WHY THIS GRADER READS WALL TIME AND NOT ITERATIONS
--------------------------------------------------
T25R5's GT5_VERDICT.json recorded, of its own registered gate:

    "THE GATE METRIC IS ANTI-CORRELATED WITH WALL COST.  C5 has the WORST
     eligible gate metric (2.94x) and the BEST wall factor (13.56x) ... G-T5 as
     registered rewards the wrong quantity, and that is the lane's error."

G-T6a is therefore computed from ExecutionTime alone.  Iteration counts are
parsed, reported, and GATE NOTHING.

WHAT Sigma CAP IS, AND IS NOT  (prereg 4.2, 2.3)
------------------------------------------------
Sigma CAP is the ladder's x4 TIMEOUT ALLOWANCE under the assumption that each
arm's 40-step RAMP wall factor holds for the whole run.  It is NOT a prediction
of ladder cost and NOT a measurement of anything at step 11,800.  The assumption
is UNMEASURED and this rung does not test it.  A PASS authorises no ladder
launch.  Every verdict this grader writes carries that sentence.

DEFAULT-DENY, IN THE REGISTERED ORDER (prereg section 10)
---------------------------------------------------------
  1. the frozen-blob check on the delegated comparator      (prereg 6.1, 7.5)
  2. the PLANTED-ZERO control                               (rule 3, prereg 6.1)
  3. the P-4 reproduction control on B0                     (prereg 6.3)
  4. rule 4 completion, all conjuncts, with the AGE GUARD   (rule 4, prereg 6.2)
  5. the equivalence control                                (prereg 6.4)
  6. ONLY THEN is a wall factor eligible to enter Sigma CAP (prereg 7.1)

A failure at 1 or 2 is a REFUSAL (exit 2) and issues no verdict at all: a zero
from a reader not shown able to see a non-zero is not evidence.  A failure at
3-5 is NOT A RESULT (exit 4).  The grader REFUSES rather than degrades.

NO ROACHE TRIPLE IS FORMED (prereg 6.5).  These levels carry WALL COST
measurements of a transient at 40 steps, not a solution functional at
convergence, so rule 5's machinery does not apply and is not invoked.  No
observed order and no GCI is computed, quoted or derivable from this rung.

    python3 grade_t25R6a.py --grade
    python3 grade_t25R6a.py --selftest
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXIT_PASS = 0
EXIT_REFUSE = 2
EXIT_GATE_FAIL = 3
EXIT_NOT_A_RESULT = 4

# --- THE CASES.  Module-level literals ON PURPOSE: scripts/check_comparator_freeze.py
# --- derives a comparator's marker scope from string constants in its own source
# --- (D471.1).  A grader whose source names no marker in its tree is reported
# --- AMBIGUOUS-SCOPE and gets NO freeze verdict.  These are also the names
# --- mark_done_t25R6a.py writes DONE.<CASE> markers for.
CASES = ["B0_L1", "C5_L1", "B0_L3", "C5_L3"]
LEVELS = ["L1", "L3"]

# --- FROZEN: the delegated planted-zero / equivalence comparator.  Already
# --- committed and frozen by T25R5; this grader verifies the BLOB rather than
# --- asserting the freeze in prose (prereg 6.1).
COMPARATOR = os.path.join(
    os.path.dirname(HERE), "T25R5_LINSOLVER_runs", "compare_arms_t25R5.py")
COMPARATOR_BLOB = "736bd0d9e03c898c1ca991cfc1b8fec8e0058b39"

# --- FROZEN AT PREREG 2.1 step 3: the ladder price table,
# --- T25R5_PREREGISTRATION.md:58-66, from T25R4 A1.1's formula with M = 4.0.
LADDER = [("S1", "L1", 7526.4), ("S2", "L2", 20151.3), ("S3", "L3", 41815.5),
          ("T2", "L2", 40302.7), ("T4", "L2", 80605.3), ("W30", "L2", 40302.7)]
LADDER_POINT = [1881.6, 5037.8, 10453.9, 10075.7, 20151.3, 10075.7]
CAP_MARGIN_M = 4.0                # A1.1.  Sigma CAP / 4 == Sigma POINT exactly.
CEILING = 20000.0                 # core-min.  SANAA'S, reaffirmed 2026-09-03.  HARD.
LADDER_TOTAL = 230704.0           # published; the table re-sums to 230703.9
REQUIRED_UNIFORM_FACTOR = LADDER_TOTAL / CEILING          # 11.5352

# --- FROZEN AT PREREG 7.1: C5's L2 wall factor is NOT re-measured here.
# --- 516.15 / 38.07 from GT5_VERDICT.json (B0 exec_s / C5 exec_s).
F_C5_L2 = 516.15 / 38.07          # 13.5579

# --- FROZEN AT PREREG 6.3.  Exact integers admit NO tolerance; the ExecutionTime
# --- band is +/-10 %, set from the MEASURED contended/alone ratio 1.085 with
# --- margin.  Source: P3_SCORE.json.rows.
REPRO = {
    "B0_L1": dict(n_all=1200, n_feas=931,  sum_feas=28821,  pinned=275, exec_s=131.28),
    "B0_L3": dict(n_all=1200, n_feas=1111, sum_feas=366954, pinned=96,  exec_s=989.39),
}
EXEC_BAND = 0.10

# --- FROZEN AT T25R5 PREREG 3.2, carried unchanged: per-level feasibility
# --- thresholds.  REPORTED HERE, GATING NOTHING (prereg 7.1).
FEAS = {"L1": 4.500e-07, "L2": 6.500e-07, "L3": 1.000e-06}

# --- FROZEN AT PREREG 8.2: the hard per-run caps, set by the team at ~3x each
# --- run's own estimate (Sanaa 2026-09-03 18:00Z item 2).  These timeouts are
# --- what makes a slower-than-hoped C5 MEASURABLE rather than censored: the
# --- smallest measurable wall factor is 131.28/396 = 0.3315 at L1 and
# --- 989.39/2970 = 0.3331 at L3, i.e. this rung can measure a C5 three times
# --- SLOWER than the baseline (prereg 7.3).
TIMEOUT_S = {"L1": 396.0, "L3": 2970.0}
CAP_PER_RUN = {"L1": 13.20, "L3": 99.00}          # core-min at 2 ranks
RUNG_CEILING_CORE_MIN = 230.0
POINT_ESTIMATE = 40.111                            # prereg 8.5: THE denominator
USD_PER_CORE_H = 0.0513

STEPS = 40
ENDTIME = 0.8
RANKS = 2

FIELDS = {"coolant": ["T", "U", "p_rgh", "alphat", "nut", "k", "omega"],
          "module": ["T"]}

SOLVE = re.compile(r"^\S*(?:PCG|DIC|GAMG)\S*:\s+Solving for p_rgh, "
                   r"Initial residual = ([-\d.eE+]+), Final residual = ([-\d.eE+]+), "
                   r"No Iterations (\d+)")
TIME_RE = re.compile(r"^Time = ([\d.eE+-]+)")
EXEC_RE = re.compile(r"^ExecutionTime = ([\d.]+) s\s+ClockTime = (\d+) s")

NOT_A_LADDER_PRICE = (
    "Sigma CAP is the ladder's x4 TIMEOUT ALLOWANCE under the assumption that "
    "the 40-step RAMP wall factor holds for the whole run.  40 steps is 0.34 % "
    "of the shortest ladder run and it is the ramp, not the soak.  It is NOT a "
    "prediction of ladder cost.  The assumption is UNMEASURED and this rung "
    "does not test it (prereg 4.2).  NO LADDER LAUNCHES ON THIS RESULT.")


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def git_blob(path):
    """The sha1 git would give this file's blob, computed locally.  No subprocess:
    a freeze check that shells out can be defeated by PATH."""
    data = open(path, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def check_comparator_freeze():
    """PREREG 6.1 / 7.5.  The planted-zero and equivalence limbs are delegated to
    an already-frozen comparator; VERIFY the blob rather than assert the freeze."""
    if not os.path.isfile(COMPARATOR):
        refuse("the delegated comparator is absent: %s" % COMPARATOR)
    got = git_blob(COMPARATOR)
    if got != COMPARATOR_BLOB:
        refuse("compare_arms_t25R5.py is NOT the registered blob.\n"
               "  registered %s\n  on disk    %s\n"
               "  The planted-zero and equivalence limbs are delegated to that "
               "file; a changed comparator is an unfrozen grading path."
               % (COMPARATOR_BLOB, got))
    print("  ok   delegated comparator is the registered blob %s" % COMPARATOR_BLOB[:12])
    return True


def load_comparator():
    import importlib.util
    spec = importlib.util.spec_from_file_location("cmp_t25R5", COMPARATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------
# logs
# ----------------------------------------------------------------------------

def read_log(path, max_steps=STEPS):
    if not os.path.isfile(path):
        return None
    solves, step, ends = [], 0, 0
    exec_at, clock_at = {}, {}
    for ln in open(path, errors="replace"):
        if TIME_RE.match(ln):
            step += 1
            continue
        if ln.startswith("End"):
            ends += 1
        if step > max_steps:
            continue
        m = EXEC_RE.match(ln)
        if m:
            if step >= 1:
                exec_at[step] = float(m.group(1))
                clock_at[step] = float(m.group(2))
            continue
        m = SOLVE.match(ln)
        if m and step >= 1:
            solves.append((float(m.group(1)), float(m.group(2)), int(m.group(3))))
    last = max(exec_at) if exec_at else None
    return dict(solves=solves, steps=min(step, max_steps), end_lines=ends,
                exec_s=(exec_at[last] if last else None),
                clock_s=(clock_at[last] if last else None),
                n_exec_lines=len(exec_at))


def feas_stats(solves, level):
    thr = FEAS[level]
    f = [x for x in solves if x[0] > thr]
    return dict(n_all=len(solves), n=len(f), total=sum(x[2] for x in f),
                mean=(sum(x[2] for x in f) / len(f)) if f else None,
                pinned=sum(1 for x in solves if x[2] >= 1000),
                min_final=(min(x[1] for x in solves) if solves else None))


# ----------------------------------------------------------------------------
# rule 4 -- ALL conjuncts, level-aware
# ----------------------------------------------------------------------------

def _num(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def rule4(case_dir, case, log):
    """PREREG 6.2.  Returns (ok, [failures]).

    Deliberately NOT the T25R5 shape: grade_t25R5.py's rule4 hardcoded '_L2' in
    the rc filename -- the same defect shape D3.3 disclosed in
    compare_arms_t25R5.py, where a caller comparing C4 against B0_L1 compared two
    different meshes.  The case name is an argument here."""
    bad = []

    rcf = os.path.join(case_dir, ".rc.%s.legA" % case)
    if not os.path.isfile(rcf):
        bad.append("rc file absent (%s)" % os.path.basename(rcf))
    else:
        rc = open(rcf).read().strip()
        if rc != "0":
            bad.append("rc != 0 (%s)%s" % (rc, "  [124 = CAP STOP]" if rc == "124" else ""))

    if log is None:
        bad.append("no log.solve.legA")
        return False, bad
    if log["end_lines"] < 1:
        bad.append("no End line")

    # clause 5: a STEP-COUNT identity, not a time-value identity.  At deltaT 0.02
    # endTime 0.8 is 40 counts.  Reading rule 4's shorthand literally would fail
    # every case with deltaT != 1 (see T20_LC_c: endTime 4500, deltaT 6, 750).
    if log["n_exec_lines"] != STEPS:
        bad.append("ExecutionTime count %d != registered step count %d"
                   % (log["n_exec_lines"], STEPS))
    if log["steps"] != STEPS:
        bad.append("Time lines %d != registered step count %d" % (log["steps"], STEPS))

    p0 = os.path.join(case_dir, "processor0")
    if not os.path.isdir(p0):
        bad.append("no processor0/")
        return (not bad), bad
    tdirs = [d for d in os.listdir(p0) if _num(d) and abs(float(d) - ENDTIME) <= 1e-6]
    if len(tdirs) != 1:
        bad.append("t=%g field dir: %d found" % (ENDTIME, len(tdirs)))
        return (not bad), bad

    import glob
    procs = sorted(glob.glob(os.path.join(case_dir, "processor*")))

    # clause 4: fields present, per region
    for region, names in FIELDS.items():
        for nm in names:
            hits = [p for p in procs
                    if os.path.isfile(os.path.join(p, tdirs[0], region, nm))]
            if len(hits) != len(procs):
                bad.append("field %s/%s present in %d of %d processor dirs"
                           % (region, nm, len(hits), len(procs)))

    # clause 6: THE AGE GUARD.  0/module/T is touched LAST at launch and so dates
    # the run allowed to produce the answer.
    ref = os.path.join(case_dir, "0", "module", "T")
    if not os.path.isfile(ref):
        bad.append("no 0/module/T to date the run against -- AGE GUARD UNEVALUABLE")
    else:
        t0 = os.path.getmtime(ref)
        old = [f for f in glob.glob(os.path.join(case_dir, "processor*", tdirs[0], "*", "*"))
               if os.path.isfile(f) and os.path.getmtime(f) <= t0]
        if old:
            bad.append("AGE GUARD: %d field(s) NOT newer than 0/module/T" % len(old))

    return (not bad), bad


# ----------------------------------------------------------------------------
# the gate arithmetic
# ----------------------------------------------------------------------------

def sigma_cap(factors):
    """PREREG 7.1.  Sigma over the six ladder runs of CAP(run) / f(level(run))."""
    rows, tot = [], 0.0
    for name, lvl, cap in LADDER:
        f = factors[lvl]
        v = cap / f
        rows.append(dict(run=name, level=lvl, cap=cap, factor=round(f, 4),
                         core_min=round(v, 2)))
        tot += v
    return tot, rows


def print_no_roache():
    print("\n  ROACHE (rule 5) -- NOT INVOKED, AND THAT IS A REGISTERED DECISION.")
    print("  These levels carry WALL COST measurements of a transient at 40 steps,")
    print("  not a solution functional at convergence.  NO observed order and NO GCI")
    print("  is computed, quoted or derivable from this rung.  A successor reading a")
    print("  grid-convergence claim off these levels gets NOT A RESULT (prereg 6.5).")


# ----------------------------------------------------------------------------
# grade
# ----------------------------------------------------------------------------

def grade():
    print("T25R6a -- G-T6a, THE WALL-COST GATE")
    print("=" * 74)

    print("\n[1] FROZEN-BLOB CHECK ON THE DELEGATED COMPARATOR (prereg 6.1/7.5)")
    check_comparator_freeze()
    cmp_mod = load_comparator()

    out = dict(rung="T25R6a", gate="G-T6a", ceiling=CEILING,
               ceiling_source="T25R4 A1.3; reaffirmed by Sanaa 2026-09-03 16:00Z",
               required_uniform_factor=round(REQUIRED_UNIFORM_FACTOR, 4),
               f_C5_L2_frozen=round(F_C5_L2, 4),
               what_sigma_cap_is_not=NOT_A_LADDER_PRICE,
               roache="NOT INVOKED -- no grid claim, no order, no GCI (prereg 6.5)",
               cost_basis=("REPORTED-BY-OWNER; dollars DERIVED at $%.4f/core-h, NOT "
                           "MEASURED -- this box cannot read its own billing "
                           "(COMPUTE_BUDGET_CHARTER section 5)" % USD_PER_CORE_H))

    print("\n[2] PLANTED-ZERO CONTROL (rule 3) -- BEFORE ANY REAL COMPARISON")
    for base in ("B0_L1", "B0_L3"):
        d = os.path.join(HERE, base)
        if not os.path.isdir(d):
            refuse("%s absent; the planted-zero control has nothing to plant into, "
                   "and a verdict without it is not evidence." % base)
        if cmp_mod.planted_control(d) is not True:
            refuse("PLANTED-ZERO CONTROL FAILED on %s -- the reader cannot see a "
                   "known non-zero, so a zero it reports is not evidence." % base)
        print("  ok   %s: plant %.6e K recovered; it is ABOVE the E1 threshold "
              "%.3e K, so this proves THE GATE CAN FIRE, not merely that the "
              "reader can read." % (base, cmp_mod.PLANT, cmp_mod.E1_T_K))

    logs, stats = {}, {}
    for case in CASES:
        lvl = "L1" if case.endswith("_L1") else "L3"
        d = os.path.join(HERE, case)
        if not os.path.isdir(d):
            refuse("%s absent -- the rung is not complete and is not graded." % case)
        lg = read_log(os.path.join(d, "log.solve.legA"))
        if lg is None:
            refuse("%s: no log.solve.legA" % case)
        logs[case] = lg
        stats[case] = feas_stats(lg["solves"], lvl)

    print("\n[3] P-4 REPRODUCTION CONTROL (prereg 6.3)")
    integers_ok, repro = True, {}
    for case in ("B0_L1", "B0_L3"):
        e, s = REPRO[case], stats[case]
        miss = []
        for k, got in (("n_all", s["n_all"]), ("n_feas", s["n"]),
                       ("sum_feas", s["total"]), ("pinned", s["pinned"])):
            if got != e[k]:
                miss.append("%s %s != %s" % (k, got, e[k]))
        lo, hi = e["exec_s"] * (1 - EXEC_BAND), e["exec_s"] * (1 + EXEC_BAND)
        in_band = lo <= logs[case]["exec_s"] <= hi
        repro[case] = dict(integers="EXACT" if not miss else "MISS: " + "; ".join(miss),
                           exec_s=logs[case]["exec_s"], target_exec_s=e["exec_s"],
                           band=[round(lo, 2), round(hi, 2)], exec_in_band=in_band)
        if miss:
            integers_ok = False
            print("  MISS %s integers: %s" % (case, "; ".join(miss)))
        else:
            print("  ok   %s integers EXACT (%d/%d feasible, sum %d, pinned %d)"
                  % (case, s["n"], s["n_all"], s["total"], s["pinned"]))
        print("       %s ExecutionTime %.2f s vs T25R5 %.2f s, band [%.2f, %.2f]: %s"
              % (case, logs[case]["exec_s"], e["exec_s"], lo, hi,
                 "IN BAND" if in_band else "OUT OF BAND"))
        if not in_band:
            print("       >> DISCLOSED MACHINE-STATE CHANGE (prereg 6.3).  G-T6a is")
            print("          NOT voided -- this rung's factors are ratios taken")
            print("          within its own batch -- but EVERY comparison of this")
            print("          rung's factors against C4's T25R5 numbers IS VOID.")
    out["repro"] = repro
    out["cross_campaign_comparison_valid"] = all(
        repro[c]["exec_in_band"] for c in ("B0_L1", "B0_L3"))

    if not integers_ok:
        out["verdict"] = "NOT A RESULT"
        out["ground"] = ("P-4 integer reproduction MISSED.  The computation is not "
                         "the same computation; determinism is the premise every "
                         "other number rests on (prereg 6.3).")
        return finish(out, EXIT_NOT_A_RESULT)

    print("\n[4] RULE 4 COMPLETION, ALL CONJUNCTS, WITH THE AGE GUARD (prereg 6.2)")
    censored, r4 = {}, {}
    for case in CASES:
        ok, bad = rule4(os.path.join(HERE, case), case, logs[case])
        r4[case] = bad
        rcf = os.path.join(HERE, case, ".rc.%s.legA" % case)
        capped = os.path.isfile(rcf) and open(rcf).read().strip() == "124"
        censored[case] = capped
        print("  %-8s %s%s" % (case, "COMPLETE" if ok else "; ".join(bad),
                               "   [CENSORED: cap stop]" if capped else ""))
    out["rule4"], out["censored"] = r4, censored

    bad_not_censored = [c for c in CASES if r4[c] and not censored[c]]
    if bad_not_censored:
        out["verdict"] = "NOT A RESULT"
        out["ground"] = ("rule 4 incomplete on %s, and not by a cap stop"
                         % ", ".join(bad_not_censored))
        return finish(out, EXIT_NOT_A_RESULT)
    if any(censored[c] for c in ("B0_L1", "B0_L3")):
        out["verdict"] = "NOT A RESULT"
        out["ground"] = ("a BASELINE run cap-stopped; the wall-factor denominator "
                         "is censored and no factor can be formed from it "
                         "(prereg 7.3).")
        return finish(out, EXIT_NOT_A_RESULT)

    print("\n[5] EQUIVALENCE CONTROL (prereg 6.4) -- a solver change that moves the")
    print("    answer is a defect, not a speed-up")
    equiv, equiv_ok = {}, True
    for lvl in LEVELS:
        r = cmp_mod.compare(os.path.join(HERE, "C5_%s" % lvl),
                            os.path.join(HERE, "B0_%s" % lvl))
        equiv["C5_%s" % lvl] = str(r)
        if r is not True and r != 0:
            equiv_ok = False
    out["equivalence"] = equiv
    if not equiv_ok:
        out["verdict"] = "NOT A RESULT"
        out["ground"] = "the equivalence control FIRED (prereg 6.4)"
        return finish(out, EXIT_NOT_A_RESULT)

    print("\n[6] WALL FACTORS -- MEASURED (prereg 7.1).  The iteration counts below")
    print("    are REPORTED AND GATE NOTHING (prereg 3.1, 7.1).")
    factors, bounds = {"L2": F_C5_L2}, {}
    for lvl in LEVELS:
        b, a = logs["B0_%s" % lvl], logs["C5_%s" % lvl]
        if censored["C5_%s" % lvl]:
            f = b["exec_s"] / TIMEOUT_S[lvl]
            bounds[lvl] = f
            factors[lvl] = f
            print("  %s  CENSORED: C5 cap-stopped at %.0f s.  UPPER BOUND f < %.4f"
                  % (lvl, TIMEOUT_S[lvl], f))
        else:
            f = b["exec_s"] / a["exec_s"]
            factors[lvl] = f
            print("  %s  B0 %.2f s / C5 %.2f s  ->  wall factor %.4f"
                  % (lvl, b["exec_s"], a["exec_s"], f))
    print("  L2  FROZEN from T25R5 (516.15 / 38.07)  ->  %.4f" % F_C5_L2)
    for case in CASES:
        s = stats[case]
        print("     reported, gating nothing: %-8s feasible %d/%d, sum %d, pinned "
              "%d, mean %s" % (case, s["n"], s["n_all"], s["total"], s["pinned"],
                               "n/a" if s["mean"] is None else "%.4f" % s["mean"]))
    out["wall_factors"] = {k: round(v, 4) for k, v in factors.items()}
    out["censored_bounds"] = {k: round(v, 4) for k, v in bounds.items()}
    out["iterations_reported_gating_nothing"] = {
        c: {k: stats[c][k] for k in ("n_all", "n", "total", "pinned")} for c in CASES}

    print("\n[7] G-T6a -- SIGMA CAP AGAINST SANAA'S 20,000 CORE-MIN CEILING")
    tot, rows = sigma_cap(factors)
    for r in rows:
        print("     %-4s %s  CAP %9.1f / %7.4f = %9.2f core-min"
              % (r["run"], r["level"], r["cap"], r["factor"], r["core_min"]))
    print("     %-4s      %28s %9.2f core-min" % ("SUM", "", tot))
    print("\n     Sigma CAP(C5) = %.1f core-min   ceiling %.0f   ratio x%.4f"
          % (tot, CEILING, tot / CEILING))
    print("     Sigma POINT equivalent (Sigma CAP / M, M = %.1f) = %.1f core-min"
          % (CAP_MARGIN_M, tot / CAP_MARGIN_M))
    print("     >> THE CEILING IS REGISTERED ON SIGMA CAP, NOT ON POINT (T25R4")
    print("        A1.3, A1.4 step 4).  The POINT figure is printed because a desk")
    print("        item that omits it misrepresents the evidence (prereg 2.3a).")
    out["sigma_cap"] = round(tot, 1)
    out["sigma_cap_rows"] = rows
    out["ratio_to_ceiling"] = round(tot / CEILING, 4)
    out["sigma_point_equivalent"] = round(tot / CAP_MARGIN_M, 1)
    out["sigma_point_usd_derived"] = round(tot / CAP_MARGIN_M / 60.0 * USD_PER_CORE_H, 2)

    p = {}
    p["P-1 f(L3) < f(L2)"] = "WINS" if factors["L3"] < factors["L2"] else "LOSES"
    p["P-2 f(L3)/f(L2) > 0.4606"] = (
        "WINS" if factors["L3"] / factors["L2"] > 0.4606 else "LOSES")
    p["P-3 f(L3) >= 7.0029"] = "WINS" if factors["L3"] >= 7.0029 else "LOSES"
    out["predictions"] = p
    print("\n     REGISTERED PREDICTIONS (frozen before any arm existed):")
    for k, v in p.items():
        print("       %-32s %s" % (k, v))

    if any(censored.values()):
        if tot > CEILING:
            out["verdict"] = "GATE FAIL"
            out["ground"] = ("CENSORED, and the bound still breaches: Sigma CAP at "
                             "the upper bound is %.1f > %.0f.  A bound that fails "
                             "is a decision (prereg 7.3)." % (tot, CEILING))
            print("\n  G-T6a: GATE FAIL on a CENSORED BOUND (prereg 7.3).")
            return finish(out, EXIT_GATE_FAIL)
        out["verdict"] = "NOT A RESULT"
        out["ground"] = ("the measurement is CENSORED, and a censored run can never "
                         "produce a PASS (prereg 7.3).  Bound: Sigma CAP < %.1f" % tot)
        print("\n  G-T6a: NOT A RESULT -- CENSORED.  A censored run cannot PASS.")
        return finish(out, EXIT_NOT_A_RESULT)

    if tot <= CEILING:
        out["verdict"] = "PASS"
        out["ground"] = ("Sigma CAP(C5) = %.1f <= %.0f ON 40-STEP RAMP ARITHMETIC."
                         % (tot, CEILING))
        rc = EXIT_PASS
        print("\n  G-T6a: PASS -- %.1f <= %.0f core-min." % (tot, CEILING))
        print("  >> ON RAMP ARITHMETIC ONLY.  " + NOT_A_LADDER_PRICE)
    else:
        out["verdict"] = "GATE FAIL"
        out["ground"] = ("Sigma CAP(C5) = %.1f > %.0f, a x%.4f breach."
                         % (tot, CEILING, tot / CEILING))
        rc = EXIT_GATE_FAIL
        print("\n  G-T6a: GATE FAIL -- %.1f > %.0f core-min, a x%.4f breach."
              % (tot, CEILING, tot / CEILING))
        print("  >> THE RUNG REPORTS THE MEASURED NUMBER AND STOPS (prereg 7.4).")
        print("     Before ANY escalation, re-run the section 2 ARITHMETIC")
        print("     SELF-CHECK against this number -- Sanaa 2026-09-03 18:00Z item")
        print("     4 makes that a precondition, not a courtesy -- and carry its")
        print("     two qualifications with it (prereg 2.3).")
        print("     A widening request is a DESK ITEM FOR SANAA.  No agent at any")
        print("     level decides it.  This registration pre-registers NO widening.")

    print_no_roache()
    return finish(out, rc)


def finish(out, rc, name="T25R6a_VERDICT.json"):
    out["exit"] = rc
    out["registration"] = "docs/campaigns/T-family/T25R6a_PREREGISTRATION.md v1.0"
    out["sanaa_rulings"] = [
        "etc/sessions/2026-09-03T1600Z_sanaa_five_rulings.md item 4 (bc185687) "
        "-- the 20,000 ceiling stands, no widening on an optimistic reading",
        "etc/sessions/2026-09-03T1800Z_sanaa_compute_envelope.md items 2 and 4 "
        "-- per-run cap at ~3x the team's own estimate; arithmetic self-check "
        "before any escalation"]
    out["ceiling_is_hard"] = ("20,000 core-min stands.  This rung pre-registers NO "
                              "widening and grants none; a widening request is a "
                              "desk item for Sanaa (prereg 7.4).")
    out["envelope_note"] = ("The $1,000 benchmark-ladder envelope (Sanaa 18:00Z "
                            "item 1) covers Rungs 0-3 and is NOT this rung's "
                            "funding basis.  T25 is not inside it (prereg 1.3).")
    out["rung_cap_core_min"] = RUNG_CEILING_CORE_MIN
    out["point_estimate_core_min"] = POINT_ESTIMATE
    p = os.path.join(HERE, name)
    json.dump(out, open(p, "w"), indent=2, sort_keys=True)
    print("\n  written %s" % p)
    print("  VERDICT: %s" % out.get("verdict", "(none)"))
    return rc


# ----------------------------------------------------------------------------
# selftest -- planted controls on the grader's own arithmetic
# ----------------------------------------------------------------------------

def selftest():
    fails = [0]

    def chk(what, ok):
        print("  %-66s %s" % (what, "ok" if ok else "FAIL"))
        if not ok:
            fails[0] += 1

    print("T25R6a GRADER SELFTEST")
    print("-" * 76)

    chk("the ladder table re-sums to 230703.9",
        abs(sum(c for _, _, c in LADDER) - 230703.9) < 0.05)
    chk("CAP = 4.0 x POINT for every one of the six rows",
        all(abs(c[2] / p - CAP_MARGIN_M) < 1e-4
            for c, p in zip(LADDER, LADDER_POINT)))
    chk("the required uniform wall factor is 11.5352",
        abs(REQUIRED_UNIFORM_FACTOR - 11.5352) < 5e-5)
    chk("C5's frozen L2 factor is 13.5579", abs(F_C5_L2 - 13.5579) < 5e-5)

    # PLANTED CONTROL ON THE GATE ARITHMETIC: C4's published factors must
    # reproduce 24,709.3 and the gate must BREACH on them.
    t24, _ = sigma_cap({"L1": 9.67, "L2": 11.37, "L3": 5.24})
    chk("C4's published 2-dp factors reproduce Sigma CAP 24709.3",
        abs(t24 - 24709.3) < 0.1)
    chk("...and the gate BREACHES on them at x1.2355",
        t24 > CEILING and abs(t24 / CEILING - 1.2355) < 5e-4)
    chk("...and its POINT equivalent is 6177.3, INSIDE the ceiling (prereg 2.3a)",
        abs(t24 / CAP_MARGIN_M - 6177.3) < 0.5 and t24 / CAP_MARGIN_M < CEILING)

    # H1 / H2: the ceiling must sit BETWEEN the registered brackets, or the
    # measurement could not be decisive and the registration is a formality.
    h1, _ = sigma_cap({"L1": F_C5_L2, "L2": F_C5_L2, "L3": F_C5_L2})
    h2, _ = sigma_cap({"L1": F_C5_L2 * 0.8509, "L2": F_C5_L2, "L3": F_C5_L2 * 0.4606})
    chk("H1 (no decay) = 17016.2 and FITS", abs(h1 - 17016.2) < 0.5 and h1 < CEILING)
    chk("H2 (C4-like decay) = 20724.9 and BREACHES",
        abs(h2 - 20724.9) < 1.0 and h2 > CEILING)
    chk("THE CEILING SITS BETWEEN THE TWO REGISTERED BRACKETS", h1 < CEILING < h2)

    piv, _ = sigma_cap({"L1": F_C5_L2 * 0.8509, "L2": F_C5_L2, "L3": 7.0029})
    chk("the P-3 pivot f(L3) = 7.0029 puts Sigma CAP on the ceiling",
        abs(piv - CEILING) < 1.5)

    # A MUTATION MUST FLIP THE ANSWER.  A selftest that only confirms is not a test.
    mut, _ = sigma_cap({"L1": F_C5_L2, "L2": F_C5_L2, "L3": F_C5_L2 * 0.30})
    chk("a mutated L3 factor (x0.30) DRIVES THE GATE FROM FIT TO BREACH",
        h1 < CEILING < mut)

    # the frozen-blob check must actually refuse
    if os.path.isfile(COMPARATOR):
        chk("the delegated comparator on disk IS the registered blob",
            git_blob(COMPARATOR) == COMPARATOR_BLOB)
    else:
        chk("the delegated comparator is on disk", False)
    real = COMPARATOR_BLOB
    globals()["COMPARATOR_BLOB"] = "0" * 40
    try:
        check_comparator_freeze()
        r = None
    except SystemExit as e:
        r = e.code
    globals()["COMPARATOR_BLOB"] = real
    chk("a WRONG registered blob REFUSES (exit 2)", r == EXIT_REFUSE)

    # rule 4 clause 5 is a STEP-COUNT identity, not a time-value identity
    chk("the registered step count is 40 at endTime 0.8 (deltaT 0.02)",
        STEPS == 40 and ENDTIME == 0.8)

    # the caps, and the censoring headroom they buy (prereg 7.3, 8.2)
    chk("per-run caps are ~3x their own estimates (13.20 / 99.00 core-min)",
        abs(CAP_PER_RUN["L1"] - 13.20) < 1e-9 and abs(CAP_PER_RUN["L3"] - 99.00) < 1e-9)
    chk("caps and timeouts agree at 2 ranks",
        all(abs(TIMEOUT_S[l] * RANKS / 60.0 - CAP_PER_RUN[l]) < 0.01 for l in LEVELS))
    chk("the smallest measurable wall factor is < 0.34 at BOTH levels, so a C5 "
        "3x SLOWER than baseline is still MEASURED, not censored",
        131.28 / TIMEOUT_S["L1"] < 0.34 and 989.39 / TIMEOUT_S["L3"] < 0.34)
    chk("the rung ceiling is 230 core-min and covers the four caps plus staging",
        RUNG_CEILING_CORE_MIN >= 2 * CAP_PER_RUN["L1"] + 2 * CAP_PER_RUN["L3"] + 1.333)
    chk("230 core-min derives $0.1966 at $0.0513/core-h",
        abs(RUNG_CEILING_CORE_MIN / 60.0 * USD_PER_CORE_H - 0.1966) < 5e-4)
    chk("the largest single-run estimate is far below the $150 escalation trigger",
        32.980 / 60.0 * USD_PER_CORE_H < 150.0)

    # every case name must be a literal in this source, or check_comparator_freeze
    # cannot scope this grader's markers and reports AMBIGUOUS-SCOPE.
    src = open(os.path.abspath(__file__), errors="replace").read()
    chk("every case name appears as a literal string in this source",
        all(('"%s"' % c) in src for c in CASES))

    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails[0] else "FAIL", fails[0]))
    return 0 if not fails[0] else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--grade" in sys.argv:
        sys.exit(grade())
    print(__doc__)
    sys.exit(EXIT_REFUSE)
