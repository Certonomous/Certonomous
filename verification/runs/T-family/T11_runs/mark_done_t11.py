#!/usr/bin/env python3
"""Turn T11 STATUS files into DONE markers under the STRICT COMPLETION RULE.

CLAUDE.md rule 4, all-or-nothing:
  1. STATUS.<case> EXISTS and reports rc=0
  2. log.solve carries an `End` line
  3. the last written time == endTime from the case's own controlDict
  4. the registered field is present at that time (T -- this rung is pure
     conduction and solves for nothing else)
  5. the ExecutionTime line count == endTime/deltaT.  NOTE THE GENERALISATION:
     the steady rungs write `count == endTime` only because their deltaT is 1.
     T11 is TRANSIENT with deltaT = 1e-4, so the clause is the same clause --
     one ExecutionTime line per timestep -- expressed for a case whose timestep
     is not unity.
  6. THE AGE GUARD: every field at endTime NEWER than the case's own 0/T.

AN ABSENT STATUS FILE IS NOT DONE, NEVER AN INFERENCE.  A missing `capped`
field is itself a refusal: rc alone cannot separate a cap-stop from a crash
(124 and 137 are both ambiguous on this box, measured).

Exit: 0 all DONE, 1 at least one NOT DONE, 2 REFUSAL.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = ("T11_PW_c", "T11_PW_m", "T11_PW_f")
NEEDED = ("T",)
EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def dict_num(case, key):
    p = os.path.join(HERE, case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict for %s -- a completion rule that guesses "
               "its own target is not a rule" % case)
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % key, open(p).read(), re.M)
    if not m:
        refuse("controlDict for %s states no %s" % (case, key))
    return float(m.group(1))


def read_status(case):
    p = os.path.join(HERE, "STATUS.%s" % case)
    if not os.path.isfile(p):
        return None, "no STATUS file (case never finished, or was fired by a launcher that writes none)"
    txt = open(p).read()
    d = dict(re.findall(r"^([a-z_]+)=(.*)$", txt, re.M))
    if "rc" not in d:
        return None, "STATUS exists but states no rc: %r" % txt.strip()
    if "capped" not in d:
        return None, ("STATUS carries no `capped` witness: %r -- not written by "
                      "run_one_t11.sh, and rc alone cannot separate a cap-stop "
                      "from a crash" % txt.strip())
    return d, ""


def check(case):
    d = os.path.join(HERE, case)
    fails = []
    if not os.path.isdir(d):
        return ["no case directory"]
    st, why = read_status(case)
    if st is None:
        return [why]
    rc = int(st["rc"])
    if rc != 0:
        if st["capped"] == "yes":
            fails.append("CAPPED: rc=%s at wall_s=%s against timeout_s=%s -- the "
                         "run reached its registered cap and was stopped. An "
                         "overrun does not get a new budget (rule 12); NOT A "
                         "RESULT, not a candidate for a larger cap."
                         % (rc, st.get("wall_s"), st.get("timeout_s")))
        else:
            fails.append("CRASH: rc=%s at wall_s=%s, BELOW timeout_s=%s, so not a "
                         "cap-stop. A crash is a FINDING until triage says "
                         "otherwise." % (rc, st.get("wall_s"), st.get("timeout_s")))
    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"]
    body = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", body, re.M):
        fails.append("log.solve has no End line")

    et = dict_num(case, "endTime")
    dt = dict_num(case, "deltaT")
    times = sorted((float(x) for x in os.listdir(d)
                    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        return fails + ["no time directory beyond 0 -- the solver wrote no fields"]
    last = nonzero[-1]
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))
    tdir = os.path.join(d, ("%g" % last))
    miss = [f for f in NEEDED if not os.path.isfile(os.path.join(tdir, f))]
    if miss:
        return fails + ["time %g is missing %s" % (last, ",".join(miss))]

    n_exec = len(re.findall(r"^ExecutionTime", body, re.M))
    want = int(round(et / dt))
    if n_exec != want:
        fails.append("%d ExecutionTime lines, expected %d (endTime %g / deltaT %g)"
                     % (n_exec, want, et, dt))

    ref = os.path.join(d, "0", "T")
    if not os.path.isfile(ref):
        fails.append("no 0/T, so the run cannot be dated and the age guard "
                     "cannot be evaluated")
    else:
        age = os.path.getmtime(ref)
        stale = [f for f in NEEDED
                 if os.path.getmtime(os.path.join(tdir, f)) < age]
        if stale:
            fails.append("time %g holds fields OLDER than 0/T (%s) -- not "
                         "written by this run" % (last, ",".join(stale)))
    return fails


def main(argv):
    want = [a for a in argv[1:] if not a.startswith("-")] or list(CASES)
    for c in want:
        if c not in CASES:
            refuse("%r is not a registered T11 case: %s" % (c, " ".join(CASES)))
    rc = EXIT_OK
    for case in want:
        fails = check(case)
        if fails:
            rc = EXIT_NOTDONE
            print("NOT DONE  %-10s - %s" % (case, "; ".join(fails)))
        else:
            m = os.path.join(HERE, "DONE.%s" % case)
            if not os.path.exists(m):
                open(m, "w").write("done\n")
            print("DONE      %-10s" % case)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
