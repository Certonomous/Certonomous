#!/usr/bin/env python3
"""Turn T4 STATUS files into DONE markers under the STRICT COMPLETION RULE.

CLAUDE.md rule 4, all of it, all-or-nothing:

  1. STATUS.<case> EXISTS and reports rc=0
  2. log.solve carries an `End` line
  3. the last written time == endTime from the case's own system/controlDict
  4. every registered field is present at that time
     (T U p_rgh alphat nut k omega -- the thermal family's set)
  5. the ExecutionTime line count == endTime
  6. THE AGE GUARD: every field at endTime is NEWER than the case's own 0/T,
     because 0/T is touched LAST at launch and so dates the run that was
     allowed to produce the answer (L-143, D438)

REFUSAL, NOT INFERENCE.  An ABSENT STATUS file is NOT DONE.  It is never read
as a pass, never defaulted, never back-filled.  This is the consumer side of
the defect that made K0d's L1 pair NOT DONE forever: the launcher never wrote
an rc, and the right answer was to refuse rather than to infer rc=0 from an
`End` line.  An `End` line is what rc=0 normally accompanies; it is not the
measurement the clause requires.

THE CAP-STOP IS DECIDED FROM THE WITNESS, NOT FROM rc.  Measured on this box
(GNU coreutils 9.4): a child that genuinely exits 124 is indistinguishable
from a wall-clock expiry, and 137 is both a --kill-after expiry and an OOM
kill.  So this script reads `capped=`, which run_one_t4.sh derives from
measured wall_s against the registered timeout_s, and reports a capped run as
CAPPED (rule 12: an overrun stops the run, it does not get a new budget) and
an uncapped non-zero rc as a CRASH (a finding, needing triage).  A STATUS file
with no `capped=` field is itself a refusal: it was not written by the
registered launcher.

Exit codes:  0 all requested cases DONE
             1 at least one NOT DONE (an ordinary, reportable outcome)
             2 REFUSAL -- a structural precondition failed
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

CASES = ("T4_IJ_c", "T4_IJ_m", "T4_IJ_f")
NEEDED = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega")

EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def control_end_time(case):
    p = os.path.join(HERE, case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict for %s -- endTime is unknowable, and a "
               "completion rule that guesses its own target is not a rule" % case)
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", open(p).read(), re.M)
    if not m:
        refuse("controlDict for %s states no endTime" % case)
    return float(m.group(1))


def read_status(case):
    """(fields_dict_or_None, reason). An absent file is None -- never a pass."""
    p = os.path.join(HERE, "STATUS.%s" % case)
    if not os.path.isfile(p):
        return None, "no STATUS file (case never finished, or was fired by a launcher that writes none)"
    txt = open(p).read()
    d = dict(re.findall(r"^([a-z_]+)=(.*)$", txt, re.M))
    if "rc" not in d:
        return None, "STATUS exists but states no rc: %r" % txt.strip()
    if "capped" not in d:
        return None, ("STATUS exists but carries no `capped` witness: %r -- it was "
                      "not written by run_one_t4.sh, and rc alone cannot separate a "
                      "cap-stop from a crash (124 and 137 are both ambiguous)" % txt.strip())
    return d, ""


def check(case):
    """Return a list of failures. Empty list == DONE."""
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
            fails.append("CAPPED: rc=%s at wall_s=%s against the registered "
                         "timeout_s=%s -- the run reached its registered cap and "
                         "was stopped. An overrun does not get a new budget "
                         "(CLAUDE.md rule 12); this case is NOT A RESULT, not a "
                         "candidate for re-launch at a larger cap."
                         % (rc, st.get("wall_s", "?"), st.get("timeout_s", "?")))
        else:
            fails.append("CRASH: rc=%s at wall_s=%s, BELOW the registered "
                         "timeout_s=%s, so this is not a cap-stop. A crash is a "
                         "FINDING until triage says otherwise "
                         "(SUPERVISION_CHARTER.md section 3)."
                         % (rc, st.get("wall_s", "?"), st.get("timeout_s", "?")))

    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"]
    body = open(log, errors="replace").read()

    if not re.search(r"^End\s*$", body, re.M):
        fails.append("log.solve has no End line")

    et = control_end_time(case)

    times = sorted((float(x) for x in os.listdir(d)
                    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        fails.append("no time directory beyond 0 -- the solver wrote no fields")
        return fails
    last = nonzero[-1]
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))

    tdir = os.path.join(d, ("%g" % last))
    miss = [f for f in NEEDED if not os.path.isfile(os.path.join(tdir, f))]
    if miss:
        fails.append("time %g is missing %s" % (last, ",".join(miss)))
        return fails

    n_exec = len(re.findall(r"^ExecutionTime", body, re.M))
    if n_exec != int(et):
        fails.append("%d ExecutionTime lines, expected %d" % (n_exec, int(et)))

    # ---- clause 6: THE AGE GUARD ------------------------------------------
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
            refuse("%r is not one of the three registered T4 cases: %s"
                   % (c, " ".join(CASES)))
    rc = EXIT_OK
    for case in want:
        fails = check(case)
        if fails:
            rc = EXIT_NOTDONE
            print("NOT DONE  %-10s - %s" % (case, "; ".join(fails)))
        else:
            marker = os.path.join(HERE, "DONE.%s" % case)
            if not os.path.exists(marker):
                open(marker, "w").write("done\n")
            print("DONE      %-10s" % case)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
