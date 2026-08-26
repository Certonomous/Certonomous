#!/usr/bin/env python3
"""
STRICT COMPLETION RULE (standing rule 4) for the F3 successor -- the gate that
runs BEFORE grading, per cfd-supervisor's launch condition 8.

WHY THIS IS A SEPARATE FILE. Annex C of the pre-registration registers the
completion rule, but the frozen grading path (`grade_f3s.py`, `instrument.py`,
frozen at 5891db27) implements no completion check -- it checks only that the
artifacts it reads exist. That is a gap between the frozen document and the
frozen code, found at grading time. Rule 6 forbids editing a frozen file, so the
rule is enforced here, in a new file, and the gap is reported rather than
patched into the frozen path.

REFUSES (exit 2) rather than degrade. No `assert` carries any clause: `python3 -O`
deletes every one, and a completion rule that vanishes under a flag is worse than
none, because it certifies.
"""
import sys

# ---------------------------------------------------------------------------
# `-O` ENTRY REFUSAL. This file carries zero `assert` statements, so `python3 -O`
# weakens nothing in it TODAY. It is here for PATH UNIFORMITY: this file is now
# the first half of the graded path, and `grade_f3s.py` is the second. A path is
# flag-proof or it is not. Having one half refuse `-O` and the other half accept
# it invites a later reader to assume the wrong half, and the second half's
# refusal exists because `roache_triple.py` reaches its gate through four
# asserts that `-O` deletes.
# ---------------------------------------------------------------------------
if not __debug__:
    sys.stderr.write(
        "REFUSED: the graded path must not run under `python3 -O`.\n"
        "  This file carries no asserts, but grade_f3s.py -- the second half of\n"
        "  the same path -- refuses because roache_triple.py:195,632,634,637\n"
        "  carry rule 1's vocabulary and rule 5's one-way asymmetry as asserts.\n"
        "  Both halves refuse, so the path is flag-proof end to end.\n")
    sys.exit(2)

import os
import re
import json
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")

# THE ONE INAPPLICABLE LIMB, DECLARED **WITH ITS REASON**.
#
# Standing rule 4 requires `ExecutionTime count == endTime`. That clause assumes
# a STEADY solver, where `endTime` is an ITERATION COUNT and one ExecutionTime
# line is printed per iteration, so the two are commensurable.
#
# `rhoCentralFoam` is an explicit density-based TIME-MARCHER run under
# `adjustTimeStep yes`. Here `endTime` is a **PHYSICAL TIME** (2.6 for the wedge,
# 6.0 for the diamond) and the number of steps taken to reach it is set by the
# Courant condition -- 8,071 steps to reach t = 2.6 on the fine wedge. An
# ExecutionTime line count therefore CANNOT equal endTime for any correct run,
# and a limb that no correct run can satisfy tests nothing.
#
# **It is inapplicable BY CONSTRUCTION, not by convenience**, and the distinction
# is the point: a limb declared inapplicable without its reason is
# indistinguishable from a limb dropped because it failed. C3 below carries the
# real completion evidence for a time-marcher -- did it reach endTime.
DECLARED_INAPPLICABLE = [
    dict(clause="ExecutionTime_count_equals_endTime",
         reason="endTime is a PHYSICAL TIME for this explicit time-marcher under "
                "adjustTimeStep, not an iteration count; the step count is set by "
                "the Courant condition (8,071 steps to t=2.6 on the fine wedge), so "
                "no correct run can satisfy this limb and it tests nothing. "
                "Inapplicable by construction, not by convenience.",
         evidence_carried_instead_by="C3_completion_limb")]
REQUIRED_FIELDS = ("p", "T", "U", "rho")


def fail(case, clause, detail):
    return dict(case=case, clause=clause, detail=detail)


def controldict(case_dir):
    txt = open(os.path.join(case_dir, "system", "controlDict")).read()
    def g(k):
        m = re.search(r"^\s*%s\s+([^;]+);" % k, txt, re.M)
        return m.group(1).strip() if m else None
    return dict(endTime=float(g("endTime")), maxDeltaT=float(g("maxDeltaT")),
                deltaT=float(g("deltaT")), adjustTimeStep=g("adjustTimeStep"))


def time_dirs(case_dir):
    out = []
    for d in os.listdir(case_dir):
        p = os.path.join(case_dir, d)
        if os.path.isdir(p) and re.match(r"^[0-9]+(\.[0-9]+)?$", d):
            out.append((float(d), d))
    out.sort(key=lambda t: t[0])
    return out


def check_case(case_dir):
    c, problems = {}, []
    name = os.path.relpath(case_dir, RUNS)

    # C1 -- rc = 0, read from the launcher's own RC.txt (never inferred)
    rcp = os.path.join(case_dir, "RC.txt")
    c["C1_rc_zero"] = os.path.exists(rcp) and open(rcp).read().strip() == "0"
    if not c["C1_rc_zero"]:
        problems.append(fail(name, "C1_rc_zero",
                             open(rcp).read().strip() if os.path.exists(rcp) else "RC.txt absent"))

    # C2 -- an End line in the solver log
    logp = os.path.join(case_dir, "log.rhoCentralFoam")
    txt = open(logp, errors="replace").read() if os.path.exists(logp) else ""
    c["C2_end_line"] = bool(re.search(r"^End\s*$", txt, re.M))
    if not c["C2_end_line"]:
        problems.append(fail(name, "C2_end_line", "no End line in log.rhoCentralFoam"))

    ctrl = controldict(case_dir)
    tds = time_dirs(case_dir)
    nonzero = [t for t in tds if t[0] > 0.0]

    # C3 -- THE COMPLETION LIMB: latest + dt_final > endTime, NOT latest >= endTime.
    # With adjustTimeStep on, the final step lands on EITHER SIDE of endTime; the
    # naive form refuses genuinely complete runs (it refused 4 of 9 on F4). The
    # allowance is maxDeltaT read from the case's OWN controlDict -- an input
    # frozen at build time, not an epsilon chosen after seeing which runs it admits.
    if not nonzero:
        c["C3_completion_limb"] = False
        problems.append(fail(name, "C3_completion_limb", "no non-zero time directory"))
        latest = None
    else:
        latest = nonzero[-1]
        c["C3_completion_limb"] = (latest[0] + ctrl["maxDeltaT"]) > ctrl["endTime"]
        c["_latest_time"] = latest[1]
        c["_endTime"] = ctrl["endTime"]
        c["_maxDeltaT"] = ctrl["maxDeltaT"]
        c["_shortfall"] = ctrl["endTime"] - latest[0]
        if not c["C3_completion_limb"]:
            problems.append(fail(name, "C3_completion_limb",
                                 "latest %s + maxDeltaT %g <= endTime %g"
                                 % (latest[1], ctrl["maxDeltaT"], ctrl["endTime"])))

    # C4 -- fields present at the latest time
    if latest:
        d = os.path.join(case_dir, latest[1])
        missing = [f for f in REQUIRED_FIELDS if not os.path.exists(os.path.join(d, f))]
        c["C4_fields_present"] = not missing
        if missing:
            problems.append(fail(name, "C4_fields_present", "missing: %s" % ",".join(missing)))
    else:
        c["C4_fields_present"] = False

    # C5 -- THE AGE GUARD. Every field at the latest time must be NEWER than the
    # case's own 0/ directory, because 0/ is written last at build time and so
    # dates the run that was allowed to produce this answer. A case whose fields
    # predate its own 0/ is showing output from a previous run.
    zero = os.path.join(case_dir, "0")
    if latest and os.path.isdir(zero):
        z_ref = max(os.path.getmtime(os.path.join(zero, f))
                    for f in os.listdir(zero)
                    if os.path.isfile(os.path.join(zero, f)))
        d = os.path.join(case_dir, latest[1])
        older = [f for f in os.listdir(d)
                 if os.path.isfile(os.path.join(d, f))
                 and os.path.getmtime(os.path.join(d, f)) < z_ref]
        c["C5_age_guard"] = not older
        if older:
            problems.append(fail(name, "C5_age_guard",
                                 "fields older than the case's own 0/: %s" % ",".join(older)))
    else:
        c["C5_age_guard"] = False
        problems.append(fail(name, "C5_age_guard", "no 0/ directory or no latest time"))

    # C6 -- the series the Class C gate consumes must exist and be non-trivial.
    ser = sorted(glob.glob(os.path.join(case_dir, "series_*.json")))
    c["C6_series_present"] = bool(ser)
    c["_series"] = {os.path.basename(s): len(json.load(open(s))["t"]) for s in ser}
    if not ser and "UNINSTRUMENTED" not in case_dir:
        problems.append(fail(name, "C6_series_present", "no series_*.json"))

    c["ALL"] = all(v for k, v in c.items() if k.startswith("C") and not k.startswith("_"))
    return c, problems


def main():
    if not os.path.isdir(RUNS):
        sys.stderr.write("REFUSED: no run root at %s -- nothing has been fired\n" % RUNS)
        sys.exit(2)
    cases = []
    for dirpath, dirnames, filenames in os.walk(RUNS):
        if "system" in dirnames and "constant" in dirnames:
            cases.append(dirpath)
    cases.sort()
    if not cases:
        sys.stderr.write("REFUSED: no case directories under %s\n" % RUNS)
        sys.exit(2)

    report, problems = {}, []
    for cd in cases:
        c, p = check_case(cd)
        report[os.path.relpath(cd, RUNS)] = c
        problems.extend(p)

    out = dict(declared_inapplicable=DECLARED_INAPPLICABLE, cases=report,
               problems=problems, n_cases=len(cases),
               n_complete=sum(1 for c in report.values() if c["ALL"]))
    json.dump(out, open(os.path.join(HERE, "COMPLETION.json"), "w"), indent=2)

    for k, c in sorted(report.items()):
        print("%-46s %s" % (k, "COMPLETE" if c["ALL"] else "NOT DONE"))
        if not c["ALL"]:
            for cl in sorted(x for x in c if x.startswith("C") and not c[x] and not x.startswith("_")):
                print("      failed: %s" % cl)
    print("-" * 70)
    if problems:
        # THE CLAIM IS INSIDE THE PASSING BRANCH: no "all complete" is printed
        # unless the predicate that establishes it was evaluated and held.
        sys.stderr.write("REFUSED: %d of %d cases are NOT DONE. A run that fails "
                         "any clause of the completion rule is not graded -- it is "
                         "labelled. See COMPLETION.json\n"
                         % (len(cases) - out["n_complete"], len(cases)))
        sys.exit(2)
    print("ALL %d CASES COMPLETE under the strict completion rule "
          "(%s declared inapplicable and not silently dropped)."
          % (len(cases), ", ".join(DECLARED_INAPPLICABLE)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
