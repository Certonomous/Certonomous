#!/usr/bin/env python3
"""mark_done_k2f.py -- K2f rule-4 completion instrument and clause-7 launch guard.

    python3 mark_done_k2f.py <case> [<case> ...]   # completion, per case
    python3 mark_done_k2f.py --guard <case_dir>    # clause 7, before a launch
    python3 mark_done_k2f.py --selftest            # mutation matrix

RUNG
----
K2f, campaign F14 -- the rack-row module re-registered on a grading path that
can grade, after K2d was retired for a path that could not.  Registration:
`docs/campaigns/F14-cooling-ladder/K2f_PREREGISTRATION.md` (sections 9.2, 9.3, 9.5).

WHY THIS FILE EXISTS RATHER THAN A REUSE OF `mark_done_k2d.py`
--------------------------------------------------------------
K2d's instrument was NOT the defective one -- its builder and its comparator
were -- but its ALLOW-LIST at `mark_done_k2d.py:61` is
`("K2d_L1", "K2d_L2", "K2d_L3")` and a name off the list is REFUSED at exit 2.
Reusing it would force K2f to build under K2d's names, inviting exactly the
confusion that made K2d section 17.8 move a directory aside, or require editing
a file pinned to a retired registration.  The allow-list is therefore registered
in K2f section 9.2 and lives here, so builder, launcher and instrument agree by
construction.

EXIT MAP -- T3's convention (registration section 9.5)
    0  EXIT_OK       every named case is DONE / the guard permits the launch
    1  EXIT_FAIL     a case is NOT DONE / the guard REFUSES the launch
    2  EXIT_REFUSE   this instrument cannot decide -- a case, STATUS or log is
                     absent, or a name is not on the allow-list

THE EXIT CODE DOES NOT CARRY THE VERDICT and no record may read it as one.
T16c returned rc = 0 while every row read `NOT A RESULT`.

THE SIX CLAUSES (standing rule 4, all of them, all-or-nothing)
  1  rc = 0 read from the case's STATUS file
  2  an `End` line in log.solve
  3  last written time directory == endTime from the case's own controlDict
  4  every required field present at endTime
  5  ExecutionTime count == round(endTime/deltaT); deltaT read from the case's
     own controlDict, never assumed
  6  THE AGE GUARD: every field at endTime is NEWER than the case's own 0/T,
     because 0/T is touched last at launch and so dates the run that was
     allowed to produce the answer

A run that fails ANY clause is not done.  No partial credit, no degradation.

A NOTE ON CLAUSE 3 AND `writeInterval 500` (registration section 9.4)
--------------------------------------------------------------------
K2f writes six times per level instead of once, so a trip leaves a restart
point -- K2d's `writeInterval 3000` against `endTime 3000` is why a kill at 33 %
of L3 destroyed 100 % of 535.600 core-minutes.  Clause 3 is unaffected: it
requires the LAST written time to equal endTime, and with `purgeWrite 0` the
endTime write is still the last.  The intermediate directories are restart
points, not answers, and clause 4 reads fields at endTime alone.
"""

import os
import re
import shutil
import sys
import tempfile

EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

HERE = os.path.dirname(os.path.abspath(__file__))

# ALLOW-LIST -- registration section 9.2.  A name not here is REFUSED (exit 2)
# rather than guessed at.  Widening an allow-list can never make a failing case
# pass, which is the ground the T23 wrapper extensions rest on.
CASES = ("K2f_L1", "K2f_L2", "K2f_L3")

# Required fields at endTime -- the thermal family set, with `phi`
# (Sanaa's approval 2026-09-06 aligned standing rule 4 with its instrument).
NEEDED = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi")

# The age-guard referent.  0/T is touched last at launch, so it dates the run.
AGE_REF = os.path.join("0", "T")

_TIMEDIR = re.compile(r"^\d+(\.\d+)?$")


# ---------------------------------------------------------------- primitives

def _read_status(case_dir):
    """STATUS.<case> beside the case dir, or STATUS inside it. REFUSE if absent."""
    base = os.path.basename(os.path.normpath(case_dir))
    for p in (os.path.join(os.path.dirname(os.path.normpath(case_dir)),
                           "STATUS." + base),
              os.path.join(case_dir, "STATUS")):
        if os.path.exists(p):
            return open(p).read()
    return None


def _status_field(text, key):
    m = re.search(r"^%s=(.*)$" % re.escape(key), text, re.M)
    return m.group(1).strip() if m else None


def _dict_num(case_dir, key, default=None):
    """Read a numeric entry from the case's OWN controlDict. Never assumed."""
    p = os.path.join(case_dir, "system", "controlDict")
    if not os.path.exists(p):
        return default
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % re.escape(key),
                  open(p).read(), re.M)
    return float(m.group(1)) if m else default


def _time_dirs(case_dir):
    out = []
    if os.path.isdir(case_dir):
        for e in os.listdir(case_dir):
            if _TIMEDIR.match(e) and os.path.isdir(os.path.join(case_dir, e)):
                out.append(float(e))
    return sorted(out)


def _fmt_time(v):
    return str(int(v)) if float(v).is_integer() else repr(v)


# ------------------------------------------------------------------- clause 7

def launch_guard(case_dir, verbose=True):
    """CLAUSE 7 -- refuse to launch into a directory that is not unstarted.

    Returns True if the launch may proceed, False if it must not.
    A guard that has never been executed is a claim, not a guard, which is why
    --selftest drives BOTH directions of every limb on real paths, and why
    registration section 9.3 makes that demonstration a pre-freeze obligation.
    """
    why = []
    cd = os.path.normpath(case_dir)

    if not os.path.isdir(cd):
        why.append("CLAUSE 7: %s does not exist" % cd)
        if verbose:
            for w in why:
                print(w)
        return False

    if os.path.isdir(os.path.join(cd, "0")):
        why.append("CLAUSE 7: %s already has a 0/ -- this case is NOT unstarted. "
                   "0/ is armed from 0.orig/ AT LAUNCH and dates the run for the "
                   "age guard; a pre-existing 0/ destroys that referent." % cd)

    existing = [t for t in _time_dirs(cd) if t != 0.0]
    if existing:
        why.append("CLAUSE 7: %s already has time director%s %s -- this case is "
                   "NOT unstarted. Results from an earlier run would be graded "
                   "as this one's." % (cd, "y" if len(existing) == 1 else "ies",
                                       ", ".join(_fmt_time(t) for t in existing[:5])))

    if not os.path.isdir(os.path.join(cd, "0.orig")):
        why.append("CLAUSE 7: %s has no 0.orig/ to arm from; build_k2f.py stages "
                   "into 0.orig and never creates 0/" % cd)

    # --- postProcessing limb: fires on CONTENT, not on the directory ---------
    # K2f writes function-object series, so this limb is load-bearing here in a
    # way it was not in K2d, whose builder wrote no function objects at all.
    # On restart OpenFOAM does NOT overwrite a function-object file -- it writes
    # a SECOND one beside it, and BOTH match the comparator's glob.  That is a
    # WRONG NUMBER, not a crash.  An EMPTY postProcessing/ is not a refusal.
    pp = os.path.join(cd, "postProcessing")
    if os.path.isdir(pp):
        leftovers = []
        for dp, _dns, fns in os.walk(pp):
            for fn in fns:
                leftovers.append(os.path.relpath(os.path.join(dp, fn), cd))
                if len(leftovers) >= 5:
                    break
            if len(leftovers) >= 5:
                break
        if leftovers:
            why.append("CLAUSE 7: %s has a NON-EMPTY postProcessing/ (%s%s) -- "
                       "this case is NOT unstarted. A restart writes a SECOND "
                       "function-object file beside the first and BOTH match the "
                       "comparator's glob, which is a wrong number rather than a "
                       "crash. MOVE it aside with its path recorded, NEVER delete "
                       "it." % (cd, ", ".join(leftovers[:4]),
                                " ..." if len(leftovers) >= 5 else ""))

    if verbose:
        for w in why:
            print(w)
        if not why:
            print("CLAUSE 7: %s is unstarted -- launch permitted" % cd)
    return not why


# ------------------------------------------------------------- the six clauses

def check(case_dir):
    """Return (done, why[]).  done is None when the instrument cannot decide."""
    why = []
    cd = os.path.normpath(case_dir)
    if not os.path.isdir(cd):
        return None, ["no case directory %s -- this instrument REFUSES rather "
                      "than guessing" % cd]

    status = _read_status(cd)
    if status is None:
        return None, ["no STATUS file for %s -- this instrument REFUSES rather "
                      "than assuming a run happened" % cd]

    log = os.path.join(cd, "log.solve")
    if not os.path.exists(log):
        return None, ["no log.solve in %s -- REFUSE" % cd]
    text = open(log, errors="replace").read()

    # clause 1 -- rc
    rc = _status_field(status, "rc")
    if rc != "0":
        why.append("CLAUSE 1: rc=%s, not 0" % rc)

    # clause 2 -- End line
    if not re.search(r"^End\b", text, re.M):
        why.append("CLAUSE 2: no `End` line in log.solve")

    # clause 3 -- last written time == endTime
    end_time = _dict_num(cd, "endTime")
    if end_time is None:
        return None, ["cannot read endTime from %s/system/controlDict -- REFUSE"
                      % cd]
    times = [t for t in _time_dirs(cd) if t != 0.0]
    if not times:
        why.append("CLAUSE 3: no time directory beyond 0 in %s. A PARALLEL run "
                   "leaves its fields in processor*/<t>/ and the case root holds "
                   "none until reconstructPar has run." % cd)
        end_dir = None
    else:
        last = max(times)
        end_dir = os.path.join(cd, _fmt_time(last))
        if abs(last - end_time) > 1e-9:
            why.append("CLAUSE 3: last written time %s != endTime %s"
                       % (_fmt_time(last), _fmt_time(end_time)))

    # clause 4 -- fields present at endTime
    if end_dir is None:
        why.append("CLAUSE 4: no endTime directory, so no field can be present")
    else:
        missing = [f for f in NEEDED
                   if not os.path.exists(os.path.join(end_dir, f))]
        if missing:
            why.append("CLAUSE 4: missing field(s) at endTime: %s"
                       % ", ".join(missing))

    # clause 5 -- ExecutionTime count
    dt = _dict_num(cd, "deltaT", 1.0)
    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    want = int(round(end_time / dt)) if dt else None
    if want is not None and n_exec != want:
        why.append("CLAUSE 5: %d ExecutionTime lines, expected round(%s/%s) = %d"
                   % (n_exec, _fmt_time(end_time), _fmt_time(dt), want))

    # clause 6 -- THE AGE GUARD
    ref = os.path.join(cd, AGE_REF)
    if not os.path.exists(ref):
        why.append("CLAUSE 6: age guard referent %s is absent, so the age of the "
                   "fields cannot be established. UNMEASURED IS NOT PASSING."
                   % AGE_REF)
    elif end_dir is not None:
        t_ref = os.path.getmtime(ref)
        stale = [f for f in NEEDED
                 if os.path.exists(os.path.join(end_dir, f))
                 and os.path.getmtime(os.path.join(end_dir, f)) <= t_ref]
        if stale:
            why.append("CLAUSE 6 AGE GUARD: field(s) %s at endTime are NOT newer "
                       "than the case's own %s. They predate the run that was "
                       "allowed to produce them." % (", ".join(stale), AGE_REF))

    return (not why), why


def run(names, verbose=True):
    worst = EXIT_OK
    for name in names:
        base = os.path.basename(os.path.normpath(name))
        if base not in CASES:
            if verbose:
                print("REFUSE: %r is not on the K2f allow-list %s"
                      % (base, ", ".join(CASES)))
            return EXIT_REFUSE
        cd = name if os.path.isdir(name) else os.path.join(HERE, base)
        done, why = check(cd)
        if done is None:
            if verbose:
                print("REFUSE: %s" % base)
                for w in why:
                    print("    %s" % w)
            return EXIT_REFUSE
        if verbose:
            print("%s: %s" % (base, "DONE -- all six clauses" if done
                              else "NOT DONE"))
            for w in why:
                print("    %s" % w)
        if not done:
            worst = EXIT_FAIL
    return worst


# ------------------------------------------------------------------- selftest

def _mk_case(root, name, *, end=100, dt=1, fields=True, endline=True,
             rc="0", nexec=None, age_ok=True, timedir=True, interval=50):
    """Build a synthetic case on disk. Real paths, real mtimes -- no mocking."""
    import time as _t
    cd = os.path.join(root, name)
    os.makedirs(os.path.join(cd, "system"), exist_ok=True)
    os.makedirs(os.path.join(cd, "0"), exist_ok=True)
    open(os.path.join(cd, "0", "T"), "w").write("0\n")
    with open(os.path.join(cd, "system", "controlDict"), "w") as fh:
        fh.write("endTime %d;\ndeltaT %d;\nwriteInterval %d;\n"
                 % (end, dt, interval))
    n = nexec if nexec is not None else int(round(end / dt))
    with open(os.path.join(cd, "log.solve"), "w") as fh:
        for _ in range(n):
            fh.write("ExecutionTime = 1 s  ClockTime = 1 s\n")
        if endline:
            fh.write("End\n")
    open(os.path.join(root, "STATUS." + name), "w").write("rc=%s\n" % rc)
    if timedir:
        _t.sleep(0.01)
        td = os.path.join(cd, str(end))
        os.makedirs(td, exist_ok=True)
        if fields:
            for f in NEEDED:
                open(os.path.join(td, f), "w").write("x\n")
    if not age_ok:
        # make 0/T newer than the fields: the exact defect the guard exists for
        _t.sleep(0.01)
        open(os.path.join(cd, "0", "T"), "w").write("0\n")
    return cd


def selftest():
    ok_all = True

    def arm(label, got, want):
        nonlocal ok_all
        good = (got == want)
        ok_all = ok_all and good
        print("  [%s] %s" % ("ok " if good else "BAD", label))

    root = tempfile.mkdtemp(prefix="k2f_md_")
    try:
        print("-- the six clauses, CONTROL first then one corruption per clause --")
        _mk_case(root, "K2f_L1")
        arm("CONTROL: a complete case -> DONE (exit 0)",
            run([os.path.join(root, "K2f_L1")], verbose=False), EXIT_OK)

        shutil.rmtree(os.path.join(root, "K2f_L1"))
        _mk_case(root, "K2f_L1", rc="1")
        arm("clause 1: rc=1 -> NOT DONE",
            run([os.path.join(root, "K2f_L1")], verbose=False), EXIT_FAIL)

        shutil.rmtree(os.path.join(root, "K2f_L1"))
        _mk_case(root, "K2f_L1", endline=False)
        arm("clause 2: no End line -> NOT DONE",
            run([os.path.join(root, "K2f_L1")], verbose=False), EXIT_FAIL)

        shutil.rmtree(os.path.join(root, "K2f_L1"))
        _mk_case(root, "K2f_L1", timedir=False)
        arm("clause 3: no time directory (the PARALLEL trap) -> NOT DONE",
            run([os.path.join(root, "K2f_L1")], verbose=False), EXIT_FAIL)

        shutil.rmtree(os.path.join(root, "K2f_L1"))
        _mk_case(root, "K2f_L1", fields=False)
        arm("clause 4: fields missing at endTime -> NOT DONE",
            run([os.path.join(root, "K2f_L1")], verbose=False), EXIT_FAIL)

        shutil.rmtree(os.path.join(root, "K2f_L1"))
        _mk_case(root, "K2f_L1", nexec=99)
        arm("clause 5: 99 ExecutionTime lines for endTime 100 -> NOT DONE",
            run([os.path.join(root, "K2f_L1")], verbose=False), EXIT_FAIL)

        shutil.rmtree(os.path.join(root, "K2f_L1"))
        _mk_case(root, "K2f_L1", age_ok=False)
        arm("clause 6: AGE GUARD, 0/T newer than the fields -> NOT DONE",
            run([os.path.join(root, "K2f_L1")], verbose=False), EXIT_FAIL)

        print("-- writeInterval 500: intermediate time dirs must NOT break "
              "clause 3 (registration section 9.4) --")
        shutil.rmtree(os.path.join(root, "K2f_L1"))
        cd = _mk_case(root, "K2f_L1", end=3000, interval=500)
        for t in (500, 1000, 1500, 2000, 2500):
            os.makedirs(os.path.join(cd, str(t)), exist_ok=True)
        arm("five restart points below endTime -> still DONE "
            "(K2d's writeInterval 3000 is why 535.600 core-min vanished)",
            run([cd], verbose=False), EXIT_OK)
        # and the negative: a LATER time dir than endTime must fail clause 3
        os.makedirs(os.path.join(cd, "3500"), exist_ok=True)
        arm("a time dir ABOVE endTime -> NOT DONE (clause 3 is equality)",
            run([cd], verbose=False), EXIT_FAIL)

        print("-- REFUSALS: the instrument declines rather than guessing --")
        shutil.rmtree(os.path.join(root, "K2f_L1"))
        _mk_case(root, "K2f_L1")
        os.remove(os.path.join(root, "STATUS.K2f_L1"))
        arm("no STATUS -> REFUSE (exit 2), not NOT-DONE",
            run([os.path.join(root, "K2f_L1")], verbose=False), EXIT_REFUSE)
        arm("a name off the allow-list -> REFUSE (exit 2)",
            run([os.path.join(root, "K2d_L1")], verbose=False), EXIT_REFUSE)
        arm("K2d's own case names are NOT accepted here",
            run([os.path.join(root, "K2d_L3")], verbose=False), EXIT_REFUSE)

        print("-- clause 7 launch guard, BOTH DIRECTIONS, on real paths --")
        g = os.path.join(root, "guard")
        os.makedirs(os.path.join(g, "0.orig"), exist_ok=True)
        arm("CONTROL: clean case with 0.orig/ -> guard PERMITS",
            launch_guard(g, verbose=False), True)
        os.makedirs(os.path.join(g, "0"), exist_ok=True)
        arm("a pre-existing 0/ -> guard REFUSES",
            launch_guard(g, verbose=False), False)
        shutil.rmtree(os.path.join(g, "0"))
        os.makedirs(os.path.join(g, "1500"), exist_ok=True)
        arm("a pre-existing time dir -> guard REFUSES",
            launch_guard(g, verbose=False), False)
        shutil.rmtree(os.path.join(g, "1500"))
        shutil.rmtree(os.path.join(g, "0.orig"))
        arm("no 0.orig/ to arm from -> guard REFUSES",
            launch_guard(g, verbose=False), False)
        os.makedirs(os.path.join(g, "0.orig"), exist_ok=True)
        os.makedirs(os.path.join(g, "postProcessing", "T_in"), exist_ok=True)
        arm("NEGATIVE CONTROL: EMPTY postProcessing/ -> guard PERMITS "
            "(the limb fires on CONTENT, not on the directory)",
            launch_guard(g, verbose=False), True)
        open(os.path.join(g, "postProcessing", "T_in", "T_in.dat"), "w").close()
        arm("POPULATED postProcessing/ -> guard REFUSES (the restart collision "
            "writes a SECOND file and both match the comparator's glob)",
            launch_guard(g, verbose=False), False)
        arm("a directory that does not exist -> guard REFUSES",
            launch_guard(os.path.join(root, "nope"), verbose=False), False)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("\nSELFTEST %s" % ("PASS -- every arm fired as registered" if ok_all
                             else "FAIL -- an arm did not behave as registered"))
    return EXIT_OK if ok_all else EXIT_FAIL


def main(argv):
    if argv and argv[0] == "--selftest":
        return selftest()
    if argv and argv[0] == "--guard":
        if len(argv) != 2:
            print("REFUSE: --guard takes exactly one case directory")
            return EXIT_REFUSE
        return EXIT_OK if launch_guard(argv[1]) else EXIT_FAIL
    if not argv:
        print(__doc__)
        return EXIT_REFUSE
    return run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
