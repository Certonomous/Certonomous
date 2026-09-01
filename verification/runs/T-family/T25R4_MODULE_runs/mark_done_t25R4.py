#!/usr/bin/env python3
"""T25R3 COMPLETION MARKER -- the ONLY place rule 4 is decided.

Registration: docs/campaigns/T-family/T25R3_PREREGISTRATION.md §9, v1.1.

CLAUDE.md rule 4 is ALL-OR-NOTHING: a run is DONE only if every conjunct holds.
There is no partial completion, no "converged enough", and no conjunct that can
be waived because the others look good.  This file decides it and NOTHING ELSE
REIMPLEMENTS IT -- a second implementation is a second answer.

WHAT IS NEW HERE AND WHY IT HAD TO BE, versus mark_done_t25R2.py: T25R3 runs in
TWO CHAINED LEGS (§6.3), because chtMultiRegionFoam reads ONE scalar `deltaT`
from controlDict and the registered schedule has two segments.  So:

  * conjuncts 1, 2 and 5 are evaluated PER LEG and must hold on BOTH;
  * conjunct 3 is evaluated on the PAIR -- leg A must end at 70, leg B at 900;
  * conjunct 6, the age guard, spans EVERY written time of BOTH legs against
    ONE reference, `0/module/T`, which the LAUNCHER touches last at LEG A's
    launch and which therefore dates the run allowed to produce the answer;
  * the launch guard -- refusing a case where `0` or a time directory already
    exists -- APPLIES TO LEG A ONLY, because at leg B's launch time
    directories exist BY DESIGN.  That exception is registered in §6.3 BEFORE
    compute; discovering it afterwards would have been indistinguishable from
    defeating the guard.

⚠ THE FIELD TUPLE IS THE THING MOST LIKELY TO SILENTLY DESTROY THE SPEND.
chtMultiRegionFoam SOLVES for enthalpy `h` and WRITES temperature `T`.  `h` is
never written to disk.  Registering `h` as a required field would make conjunct
4 unsatisfiable on every run forever -- the K0d defect (registering `omega`
against a solver that writes `epsilon`) with the roles swapped.  The tuple below
is §9.2's and was MEASURED against what T25R2_L1 actually wrote at t = 900.

    python3 mark_done_t25R3.py --selftest
    python3 mark_done_t25R3.py --mark <case_dir> <run_id>

NOTHING HERE LAUNCHES A SOLVER.
"""

import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXIT_REFUSE = 2

# ------------------------------------------------------------- §9.2, MEASURED
FIELDS = {
    "module": ("T", "p"),
    "coolant": ("T", "U", "p", "p_rgh", "alphat", "nut", "k", "omega"),
}
# NOT `h`  -- solved for, never written.
# NOT `epsilon` -- the model is kOmegaSST, so the second field is `omega`.
# `Qdot`, `phi`, `rho` ARE written and are NOT required; `phi` is separately
# asserted at the leg boundary because leg B's restart reads it.

T_END = 900.0
LEG_A_END = 70.0
WRITE_INTERVAL = 5.0
WRITE_TIMES = tuple(i * WRITE_INTERVAL
                    for i in range(int(T_END / WRITE_INTERVAL) + 1))   # 181

# §6.1 -- (leg-A steps, leg-B steps).  A STEP-COUNT identity, not a time-value
# identity: `endTime` is a time and these are counts of `ExecutionTime` lines.
STEPS = {
    "S1": (3500, 8300), "S2": (3500, 8300), "S3": (3500, 8300),
    "T2": (7000, 16600), "T4": (14000, 33200), "W30": (3500, 8300),
}
# §12.3 -- POINT and HARD CAP in core-minutes at the registered 2 ranks.
POINT = {"S1": 76.2, "S2": 171.5, "S3": 385.8,
         "T2": 342.9, "T4": 685.9, "W30": 313.8}
CAP = {"S1": 305.0, "S2": 686.0, "S3": 1543.0,
       "T2": 1372.0, "T4": 2744.0, "W30": 1255.0}
RANKS = 2
RATE_USD_PER_CORE_H = 0.0513


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# ==========================================================================
# THE CONJUNCTS
# ==========================================================================


TIME_NAME_TOL = 1.0e-6


def _tdir(case, t):
    """Locate a written time directory BY NUMERIC VALUE, not by name.

    FORCED BY MEASUREMENT.  OpenFOAM accumulates `value_ += deltaT_`; on T25R3's
    S1 the drift reached 1.39e-10 s at t = 900 and Time::setControls() raised
    timePrecision from 12 to 17, so the directories are named
    `900.00000000013904` and `70.00000000000321`.  172 of 181 names drifted.
    A `"%g" % 900` lookup finds nothing, and S1 -- complete and correct, every
    field on disk -- was marked NOT DONE by this very check.  THE RUN WAS FINE;
    THE READER WAS BROKEN.  Returns None when absent, so the caller reports a
    missing field rather than crashing."""
    best = None
    for e in os.listdir(case):
        if not os.path.isdir(os.path.join(case, e)):
            continue
        try:
            v = float(e)
        except ValueError:
            continue
        if abs(v - t) <= TIME_NAME_TOL and (best is None or abs(v - t) < best[0]):
            best = (abs(v - t), os.path.join(case, e))
    return best[1] if best else None


def _log(case, leg):
    return os.path.join(case, "log.solve.%s" % leg)


def _rc(case, run, leg):
    """CONJUNCT 1.  The rc is READ FROM A FILE THE WRAPPER WROTE, never
    inferred from a log and never taken from the launcher.

    `setsid timeout cmd` exits 0 for EVERY outcome, so an rc captured AROUND the
    setsid line is a constant zero wearing the costume of a measurement.  The
    launcher captures rc INSIDE the detached wrapper and writes it here."""
    p = os.path.join(case, ".rc.%s.%s" % (run, leg))
    if not os.path.isfile(p):
        return None, "no %s -- the solver rc was NOT RECORDED. An rc that was " \
            "not written down is not an rc, and a launcher rc is never " \
            "accepted in its place (setsid returns 0 for every outcome)" % p
    s = open(p).read().strip()
    if not re.fullmatch(r"-?\d+", s):
        return None, "%s holds %r, which is not an integer rc" % (p, s)
    return int(s), None


def _log_facts(case, leg):
    p = _log(case, leg)
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    times = re.findall(r"^Time = ([0-9.eE+-]+)\s*$", txt, re.M)
    return dict(
        ends=len(re.findall(r"^End\s*$", txt, re.M)),
        fatal=len(re.findall(r"FOAM FATAL", txt)),
        exec_lines=len(re.findall(r"^ExecutionTime = ", txt, re.M)),
        last_time=float(times[-1]) if times else None,
        exec_s=(float(re.findall(r"^ExecutionTime = ([0-9.eE+-]+) s", txt, re.M)[-1])
                if re.findall(r"^ExecutionTime = ([0-9.eE+-]+) s", txt, re.M)
                else None),
    )


def _written_times(case):
    out = []
    for e in os.listdir(case):
        if os.path.isdir(os.path.join(case, e)) and re.fullmatch(
                r"\d+(\.\d+)?", e):
            out.append((float(e), e))
    return sorted(out)


def evaluate(case, run):
    """-> (done: bool, rows: [(conjunct, ok, detail)])."""
    rows = []
    if run not in STEPS:
        refuse("%r is not one of the six registered runs of §2 -- the run set "
               "is CLOSED and this marker grades nothing outside it" % run)

    # ---- CONJUNCT 1: rc = 0 on BOTH legs, recorded not inferred ----
    ok1, det1 = True, []
    for leg in ("legA", "legB"):
        rc, err = _rc(case, run, leg)
        if err:
            ok1 = False
            det1.append("%s: %s" % (leg, err))
        else:
            det1.append("%s rc = %d" % (leg, rc))
            if rc != 0:
                ok1 = False
    rows.append(("1 rc=0, BOTH legs, RECORDED", ok1, "; ".join(det1)))

    # ---- CONJUNCT 2: exactly one End per leg, zero FOAM FATAL ----
    facts = {leg: _log_facts(case, leg) for leg in ("legA", "legB")}
    ok2, det2 = True, []
    for leg in ("legA", "legB"):
        f = facts[leg]
        if f is None:
            ok2 = False
            det2.append("%s: no %s" % (leg, _log(case, leg)))
            continue
        det2.append("%s End=%d FATAL=%d" % (leg, f["ends"], f["fatal"]))
        if f["ends"] != 1 or f["fatal"] != 0:
            ok2 = False
    rows.append(("2 exactly 1 `End` per leg, 0 FOAM FATAL", ok2, "; ".join(det2)))

    # ---- CONJUNCT 3: last time == endTime, on the PAIR ----
    wt = _written_times(case)
    last = wt[-1][0] if wt else None
    okA = facts["legA"] is not None and facts["legA"]["last_time"] is not None \
        and abs(facts["legA"]["last_time"] - LEG_A_END) < 1e-9
    ok3 = okA and last is not None and abs(last - T_END) < 1e-9
    rows.append(("3 leg A ends at %g, run ends at %g" % (LEG_A_END, T_END), ok3,
                 "legA log last Time = %s ; last written time dir = %s ; "
                 "%d time dirs" % (
                     facts["legA"]["last_time"] if facts["legA"] else None,
                     last, len(wt))))

    # ---- CONJUNCT 4: the registered field tuple at t = 900 ----
    missing = []
    tail = _tdir(case, T_END)
    for region, names in FIELDS.items():
        for nm in names:
            if tail is None or not os.path.isfile(os.path.join(tail, region, nm)):
                missing.append("%s/%s" % (region, nm))
    ok4 = not missing
    rows.append(("4 fields at t=%g (module T,p; coolant T,U,p,p_rgh,alphat,"
                 "nut,k,omega -- NOT h, NOT epsilon)" % T_END, ok4,
                 "missing: %s" % (", ".join(missing) if missing else "NONE")))

    # ---- CONJUNCT 5: ExecutionTime count per leg == the REGISTERED count ----
    ok5, det5 = True, []
    for leg, want in zip(("legA", "legB"), STEPS[run]):
        f = facts[leg]
        got = f["exec_lines"] if f else None
        det5.append("%s %s/%d" % (leg, got, want))
        if got != want:
            ok5 = False
    rows.append(("5 ExecutionTime line count == registered steps, per leg",
                 ok5, "; ".join(det5)))

    # ---- CONJUNCT 6: THE AGE GUARD ----
    ref = os.path.join(case, "0", "module", "T")
    if not os.path.isfile(ref):
        rows.append(("6 age guard vs 0/module/T", False,
                     "the reference %s does not exist -- the age guard is "
                     "UNEVALUABLE and an unevaluable guard is a FAILED guard, "
                     "never a passed one" % ref))
        ok6, tight, nchecked = False, None, 0
    else:
        t0 = os.path.getmtime(ref)
        tight, older, nchecked = None, [], 0
        for tv, tname in wt:
            if tv == 0.0:
                continue
            for region, names in FIELDS.items():
                for nm in names:
                    p = os.path.join(case, tname, region, nm)
                    if not os.path.isfile(p):
                        continue
                    nchecked += 1
                    m = os.path.getmtime(p) - t0
                    if tight is None or m < tight:
                        tight = m
                    if m <= 0:
                        older.append(p)
        ok6 = (not older) and nchecked > 0 and tight is not None and tight > 0
        rows.append(("6 age guard: every field newer than 0/module/T", ok6,
                     "%d field files checked across %d written times and both "
                     "regions; tightest margin %s s; OLDER than reference: %s"
                     % (nchecked, len(wt) - 1,
                        ("%+.3f" % tight) if tight is not None else "n/a",
                        ", ".join(older) if older else "NONE")))

    # ---- registered structural checks that are NOT rule 4 conjuncts ----
    n_expected = len(WRITE_TIMES)
    rows.append(("* write count == %d registered times" % n_expected,
                 len(wt) == n_expected, "%d present" % len(wt)))
    phi70 = os.path.join(_tdir(case, LEG_A_END) or "", "coolant", "phi")
    rows.append(("* leg boundary: %g/coolant/phi present for leg B's restart"
                 % LEG_A_END, os.path.isfile(phi70), phi70))

    done = all(ok for _, ok, _ in rows[:6])
    return done, rows


def cost(case, run):
    facts = {leg: _log_facts(case, leg) for leg in ("legA", "legB")}
    tot = 0.0
    parts = []
    for leg in ("legA", "legB"):
        f = facts[leg]
        if f is None or f["exec_s"] is None:
            return None, ["%s: no ExecutionTime to cost from" % leg]
        cm = f["exec_s"] * RANKS / 60.0
        tot += cm
        parts.append("%s %.3f core-min (ExecutionTime %.2f s x %d ranks)"
                     % (leg, cm, f["exec_s"], RANKS))
    parts.append("TOTAL %.3f core-min" % tot)
    parts.append("POINT %.1f -> RATIO actual/predicted = %.3f"
                 % (POINT[run], tot / POINT[run]))
    parts.append("HARD CAP %.0f -> %.1f%% used, %.1f core-min unspent"
                 % (CAP[run], 100.0 * tot / CAP[run], CAP[run] - tot))
    parts.append("DOLLARS %.4f USD at $%.4f/core-h -- *** DERIVED, NOT "
                 "MEASURED ***; cost_basis = REPORTED-BY-OWNER, this box "
                 "cannot read its own billing"
                 % (tot / 60.0 * RATE_USD_PER_CORE_H, RATE_USD_PER_CORE_H))
    if tot > CAP[run]:
        parts.append("*** OVER CAP. Rule 12: an overrun STOPS the run; it does "
                     "not get a new budget. ***")
    return tot, parts


def mark(case, run):
    done, rows = evaluate(case, run)
    out = ["=" * 74,
           "%s -- RULE 4, decided here and reimplemented nowhere else" % run,
           "=" * 74]
    for name, ok, det in rows:
        out.append("  %-4s %s" % ("ok" if ok else "FAIL", name))
        out.append("        %s" % det)
    out.append("")
    out.append("  MARKER VERDICT: %s" %
               ("DONE -- all six conjuncts hold."
                if done else
                "NOT DONE -- rule 4 is ALL-OR-NOTHING and at least one "
                "conjunct failed. This run produced no gradable content."))
    tot, parts = cost(case, run)
    out.append("")
    out.append("COST -- rule 12. The unit is CORE-MINUTES (wall s x ranks / 60).")
    for p in parts:
        out.append("  " + p)
    txt = "\n".join(out)
    print(txt)
    with open(os.path.join(case, "COMPLETION.%s.txt" % run), "w") as fh:
        fh.write(txt + "\n")
    return 0 if done else 1


# ==========================================================================
# SELFTEST -- every conjunct driven BOTH WAYS.  A marker that has only ever
# been shown to say DONE has not been shown to be able to say anything else.
# ==========================================================================

def _forge(root, run="S1", **bad):
    case = os.path.join(root, run)
    a, b = STEPS[run]
    for leg, n, endt in (("legA", a, LEG_A_END), ("legB", b, T_END)):
        if bad.get("no_log") == leg:
            continue
        lines = ["Time = %g" % endt]
        lines += ["ExecutionTime = %.2f s  ClockTime = 1 s" % (i + 1)
                  for i in range(n - (1 if bad.get("short_steps") == leg else 0))]
        if bad.get("fatal") == leg:
            lines.append("--> FOAM FATAL ERROR:")
        lines.append("End")
        if bad.get("two_ends") == leg:
            lines.append("End")
        os.makedirs(case, exist_ok=True)
        open(_log(case, leg), "w").write("\n".join(lines) + "\n")
        if bad.get("no_rc") != leg:
            open(os.path.join(case, ".rc.%s.%s" % (run, leg)), "w").write(
                "%d\n" % (1 if bad.get("rc1") == leg else 0))
    # the reference `0/module/T`, touched FIRST
    for region, names in FIELDS.items():
        for nm in names:
            p = os.path.join(case, "0", region, nm)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write("x\n")
    ref = os.path.join(case, "0", "module", "T")
    os.utime(ref, (1000.0, 1000.0))
    times = WRITE_TIMES if not bad.get("missing_time") else \
        tuple(t for t in WRITE_TIMES if t != bad["missing_time"])
    for t in times:
        if t == 0.0:
            continue
        for region, names in FIELDS.items():
            for nm in names:
                if bad.get("drop_field") == "%s/%s" % (region, nm) and t == T_END:
                    continue
                p = os.path.join(case, "%g" % t, region, nm)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w").write("y\n")
                stamp = 500.0 if bad.get("stale") and t == T_END else 2000.0
                os.utime(p, (stamp, stamp))
    p = os.path.join(case, "%g" % LEG_A_END, "coolant", "phi")
    if not bad.get("no_phi"):
        open(p, "w").write("z\n")
        os.utime(p, (2000.0, 2000.0))
    return case


def selftest():
    fails = [0]

    def chk(name, cond):
        print("  %-4s %s" % ("ok" if cond else "FAIL", name))
        if not cond:
            fails[0] += 1

    tmp = tempfile.mkdtemp(prefix="t25R3md_")
    try:
        c = _forge(tmp, "S1")
        done, rows = evaluate(c, "S1")
        chk("POSITIVE: a complete two-leg run is DONE on all six conjuncts", done)
        for i, (name, ok, det) in enumerate(rows[:6]):
            chk("  conjunct %d holds on the clean case" % (i + 1), ok)

        print("\n  -- and now EVERY conjunct driven the OTHER way --")
        cases = [
            ("1 rc=1 on leg B fails", dict(rc1="legB"), 0),
            ("1 an UNRECORDED rc fails (setsid returns 0 for everything)",
             dict(no_rc="legA"), 0),
            ("2 a FOAM FATAL on leg A fails", dict(fatal="legA"), 1),
            ("2 TWO `End` lines in one leg fails", dict(two_ends="legB"), 1),
            ("2 a MISSING leg log fails", dict(no_log="legB"), 1),
            ("5 one step short on leg B fails", dict(short_steps="legB"), 4),
            ("4 a dropped coolant/omega at t=900 fails",
             dict(drop_field="coolant/omega"), 3),
            ("4 a dropped module/p at t=900 fails",
             dict(drop_field="module/p"), 3),
            ("6 a field OLDER than 0/module/T fails the age guard",
             dict(stale=True), 5),
        ]
        for label, bad, idx in cases:
            root = tempfile.mkdtemp(prefix="t25R3md_", dir=tmp)
            cc = _forge(root, "S1", **bad)
            d, rr = evaluate(cc, "S1")
            chk("NEGATIVE: %s" % label, (not d) and (not rr[idx][1]))

        root = tempfile.mkdtemp(prefix="t25R3md_", dir=tmp)
        cc = _forge(root, "S1", missing_time=300.0)
        d, rr = evaluate(cc, "S1")
        chk("NEGATIVE: a missing written time is caught by the write-count "
            "check", not rr[6][1])
        root = tempfile.mkdtemp(prefix="t25R3md_", dir=tmp)
        cc = _forge(root, "S1", no_phi=True)
        d, rr = evaluate(cc, "S1")
        chk("NEGATIVE: a missing 70/coolant/phi is caught -- leg B's restart "
            "reads it and would have started from the wrong state",
            not rr[7][1])

        print("\n  -- the field tuple, asserted against the K0d defect shape --")
        chk("`h` is NOT in the required tuple (the solver writes T, not h)",
            "h" not in FIELDS["coolant"] and "h" not in FIELDS["module"])
        chk("`epsilon` is NOT in the required tuple (kOmegaSST writes omega)",
            "epsilon" not in FIELDS["coolant"])
        chk("`omega` IS required on the coolant", "omega" in FIELDS["coolant"])
        chk("the solid tuple does NOT demand U/k/omega/p_rgh, which a solid "
            "region never writes",
            not ({"U", "k", "omega", "p_rgh"} & set(FIELDS["module"])))
        chk("a run id outside the closed set of six REFUSES",
            _refuses(lambda: evaluate(c, "S9")))

        print("\n  -- cost, rule 12 --")
        tot, parts = cost(c, "S1")
        chk("cost is core-minutes = ExecutionTime x ranks / 60, and ranks is "
            "the registered 2", tot is not None and tot > 0)
        chk("the cost report names its dollars DERIVED, NOT MEASURED",
            any("DERIVED, NOT MEASURED" in p for p in parts))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails[0] else "FAIL",
                                         fails[0]))
    return 0 if not fails[0] else 1


def _refuses(fn):
    try:
        fn()
    except SystemExit as e:
        return e.code == EXIT_REFUSE
    return False


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--mark" in argv:
        i = argv.index("--mark")
        return mark(argv[i + 1], argv[i + 2])
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
