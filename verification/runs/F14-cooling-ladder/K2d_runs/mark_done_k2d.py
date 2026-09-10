#!/usr/bin/env python3
"""mark_done_k2d.py -- K2d rule-4 completion instrument and clause-7 launch guard.

    python3 mark_done_k2d.py <case> [<case> ...]   # completion, per case
    python3 mark_done_k2d.py --guard <case_dir>    # clause 7, before a launch
    python3 mark_done_k2d.py --selftest            # mutation matrix

RUNG
----
K2d, campaign F14 -- the three-level realisation of the owner-approved K2a
rack-row module.  Registration:
`docs/campaigns/F14-cooling-ladder/K2d_PREREGISTRATION.md` (section 6.2, 6.3, 6.4).

EXIT MAP -- T3's convention, the canonical one (registration section 6.4)
    0  EXIT_OK       every named case is DONE / the guard permits the launch
    1  EXIT_FAIL     a case is NOT DONE / the guard REFUSES the launch
    2  EXIT_REFUSE   this instrument cannot decide -- a case, STATUS or log is
                     absent, or a name is not on the allow-list

THE EXIT CODE DOES NOT CARRY THE VERDICT and no record may read it as one.
T16c returned rc = 0 while every row read `NOT A RESULT`; T25R6c-R2 crashed to
1 after grading correctly.  The verdict is read from the printed lines.

WHAT THIS FILE DELIBERATELY IS NOT
----------------------------------
It does not grade.  It answers exactly two questions -- "may this case be
launched?" and "is this case finished?" -- and the comparator CALLS it rather
than reimplementing its clauses, so there is exactly one implementation of the
completion rule for this rung and no drift is possible.

THE SIX CLAUSES (standing rule 4, all of them, all-or-nothing)
--------------------------------------------------------------
  1  rc = 0 read from the case's STATUS file
  2  an `End` line in log.solve
  3  last written time directory == endTime from the case's own controlDict
  4  every required field present at endTime
  5  ExecutionTime count == round(endTime/deltaT); with SIMPLE's deltaT = 1
     that is == endTime.  Read deltaT from the case's controlDict, never assumed
  6  THE AGE GUARD: every field at endTime is NEWER than the case's own 0/T,
     because 0/T is touched last at launch and so dates the run that was
     allowed to produce the answer

A run that fails ANY clause is not done.  There is no partial credit and no
degradation: clause failures are printed and the case is NOT DONE.
"""

import os
import re
import shutil
import sys
import tempfile
import time

EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

HERE = os.path.dirname(os.path.abspath(__file__))

# ALLOW-LIST.  A name not here is REFUSED (exit 2) rather than guessed at.
# Widening an allow-list can never make a failing case pass -- the same ground
# the T23 wrapper extensions rest on.
CASES = ("K2d_L1", "K2d_L2", "K2d_L3")

# Required fields at endTime -- the thermal family set, with `phi` (Sanaa's
# approval 2026-09-06 aligned standing rule 4 with its enforcing instrument).
NEEDED = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi")

# The age-guard referent.  0/T is touched last at launch, so it dates the run.
AGE_REF = os.path.join("0", "T")

_TIMEDIR = re.compile(r"^\d+(\.\d+)?$")


# ---------------------------------------------------------------- primitives

def _read_status(case_dir):
    """STATUS.<case> beside the case dir, or STATUS inside it. REFUSE if absent."""
    name = os.path.basename(os.path.normpath(case_dir))
    for p in (os.path.join(os.path.dirname(os.path.normpath(case_dir)),
                           "STATUS.%s" % name),
              os.path.join(case_dir, "STATUS")):
        if os.path.isfile(p):
            with open(p) as fh:
                return p, fh.read()
    return None, None


def _status_field(text, key):
    m = re.search(r"(?:^|\s)%s\s*=\s*([^\s]+)" % re.escape(key), text)
    return m.group(1) if m else None


def _dict_num(case_dir, key, default=None):
    """Read a numeric entry from the case's OWN system/controlDict."""
    cd = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(cd):
        return default
    with open(cd) as fh:
        txt = fh.read()
    txt = re.sub(r"//.*?$", "", txt, flags=re.M)
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    m = re.search(r"(?:^|\s)%s\s+([0-9.eE+-]+)\s*;" % re.escape(key), txt)
    return float(m.group(1)) if m else default


def _time_dirs(case_dir):
    out = []
    for e in os.listdir(case_dir):
        if _TIMEDIR.match(e) and os.path.isdir(os.path.join(case_dir, e)):
            out.append(float(e))
    return sorted(out)


def _fmt_time(v):
    return str(int(v)) if float(v).is_integer() else repr(v)


# ------------------------------------------------------------------ clause 7

def launch_guard(case_dir, verbose=True):
    """CLAUSE 7 -- refuse to launch into a directory that is not unstarted.

    Returns True if the launch may proceed, False if it must not.

    A guard that has never been executed is a claim, not a guard, which is why
    --selftest drives BOTH directions of every limb on real paths.
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
                   "NOT unstarted. Results from an earlier run would be graded as "
                   "this one's." % (cd, "y" if len(existing) == 1 else "ies",
                                    ", ".join(_fmt_time(t) for t in existing[:5])))

    if not os.path.isdir(os.path.join(cd, "0.orig")):
        why.append("CLAUSE 7: %s has no 0.orig/ to arm from; build_k2d.py stages "
                   "into 0.orig and never creates 0/" % cd)

    # --- postProcessing limb, and it fires on CONTENT, not on the directory ---
    # A case whose time directories were cleaned while postProcessing/ survived
    # passes every limb above and is NOT unstarted.  On restart OpenFOAM does
    # not overwrite a function-object file -- it writes a SECOND one beside it
    # (T_in.dat AND T_in_0.dat), and both then match the glob the comparator
    # reads.  That is a WRONG NUMBER, not a crash: nothing fails and the value
    # is silently the wrong file's.  Reported by cfd 2026-09-10.
    # An EMPTY postProcessing/ is NOT a refusal -- hence "on content".
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
            why.append("CLAUSE 7: %s has a NON-EMPTY postProcessing/ (%s%s) -- this "
                       "case is NOT unstarted. A restart writes a SECOND function-"
                       "object file beside the first and BOTH match the comparator's "
                       "glob, which is a wrong number rather than a crash. MOVE it "
                       "aside with its path recorded, NEVER delete it."
                       % (cd, ", ".join(leftovers[:4]),
                          " ..." if len(leftovers) >= 5 else ""))

    if verbose:
        for w in why:
            print(w)
        if not why:
            print("CLAUSE 7: %s is unstarted -- launch permitted" % cd)
    return not why


# ------------------------------------------------------------- the six clauses

def check(case_dir):
    """Return (done, [reasons]).  `done` is False unless ALL SIX clauses hold."""
    why = []
    cd = os.path.normpath(case_dir)

    if not os.path.isdir(cd):
        return None, ["case directory %s does not exist" % cd]

    spath, stext = _read_status(cd)
    if stext is None:
        return None, ["no STATUS file for %s -- this instrument REFUSES rather "
                      "than assuming a run it cannot see" % cd]

    # clause 1 -- rc
    rc = _status_field(stext, "rc")
    if rc is None:
        return None, ["STATUS %s carries no rc= field" % spath]
    if rc != "0":
        why.append("STATUS is rc=%s, not rc=0 (%s)" % (rc, spath))

    # clause 2 -- End line
    logp = os.path.join(cd, "log.solve")
    if not os.path.isfile(logp):
        return None, ["no log.solve in %s" % cd]
    with open(logp, errors="replace") as fh:
        log = fh.read()
    if not re.search(r"^End\s*$", log, flags=re.M):
        why.append("log.solve has no End line")

    # clause 3 -- last written time == endTime
    end_t = _dict_num(cd, "endTime")
    if end_t is None:
        return None, ["cannot read endTime from %s/system/controlDict" % cd]
    times = [t for t in _time_dirs(cd) if t != 0.0]
    if not times:
        why.append("no time directory beyond 0")
    elif abs(times[-1] - end_t) > 1e-9:
        why.append("last written time %s != endTime %s"
                   % (_fmt_time(times[-1]), _fmt_time(end_t)))

    # clause 4 -- fields present at endTime
    end_dir = None
    if times and abs(times[-1] - end_t) <= 1e-9:
        for e in os.listdir(cd):
            if _TIMEDIR.match(e) and abs(float(e) - end_t) <= 1e-9:
                end_dir = os.path.join(cd, e)
                break
    if end_dir is None:
        why.append("no time directory at endTime %s, so no field can be checked"
                   % _fmt_time(end_t))
    else:
        missing = [f for f in NEEDED if not os.path.exists(os.path.join(end_dir, f))]
        if missing:
            why.append("fields missing at endTime: %s" % ", ".join(missing))

    # clause 5 -- ExecutionTime count.  deltaT READ, never assumed.
    dt = _dict_num(cd, "deltaT", 1.0)
    n_exec = len(re.findall(r"^ExecutionTime = ", log, flags=re.M))
    want = int(round(end_t / dt)) if dt else None
    if want is None:
        why.append("deltaT is zero or unreadable; clause 5 cannot be evaluated")
    elif n_exec != want:
        why.append("%d ExecutionTime lines != round(endTime/deltaT) = %d "
                   "(endTime %s, deltaT %s) -- a truncated or duplicated solver log"
                   % (n_exec, want, _fmt_time(end_t), _fmt_time(dt)))

    # clause 6 -- THE AGE GUARD
    ref = os.path.join(cd, AGE_REF)
    if not os.path.isfile(ref):
        why.append("age guard referent %s is absent, so the age of the fields "
                   "cannot be established -- and unestablished is not passing"
                   % os.path.join(cd, AGE_REF))
    elif end_dir is not None:
        t_ref = os.path.getmtime(ref)
        stale = []
        for f in NEEDED:
            p = os.path.join(end_dir, f)
            if os.path.exists(p) and os.path.getmtime(p) <= t_ref:
                stale.append(f)
        if stale:
            why.append("AGE GUARD: field(s) %s at endTime are NOT newer than the "
                       "case's own %s -- they predate the run allowed to produce "
                       "this answer" % (", ".join(stale), AGE_REF))

    return (not why), why


# ------------------------------------------------------------------- driver

def run(names, verbose=True):
    rc = EXIT_OK
    n_done = 0
    for name in names:
        base = os.path.basename(os.path.normpath(name))
        if base not in CASES:
            if verbose:
                print("REFUSE: %r is not on the K2d allow-list %s"
                      % (base, ", ".join(CASES)))
            return EXIT_REFUSE
        cd = name if os.path.isdir(name) else os.path.join(HERE, base)
        done, why = check(cd)
        if done is None:
            if verbose:
                print("REFUSE: %s" % base)
                for w in why:
                    print("            - %s" % w)
            return EXIT_REFUSE
        if done:
            n_done += 1
            if verbose:
                print("  DONE      %s" % base)
        else:
            rc = EXIT_FAIL
            if verbose:
                print("  NOT DONE  %s" % base)
                for w in why:
                    print("            - %s" % w)
    if verbose:
        print("%d/%d cases meet the strict completion rule" % (n_done, len(names)))
    return rc


# ------------------------------------------------------------------ selftest

def _mk_case(root, name, *, end=100, dt=1, fields=True, endline=True,
             rc="0", nexec=None, age_ok=True, timedir=True):
    """Build a synthetic case that passes every clause, then let callers break one."""
    cd = os.path.join(root, name)
    os.makedirs(os.path.join(cd, "system"), exist_ok=True)
    os.makedirs(os.path.join(cd, "0"), exist_ok=True)
    with open(os.path.join(cd, "system", "controlDict"), "w") as fh:
        fh.write("endTime %d;\ndeltaT %d;\n" % (end, dt))
    with open(os.path.join(cd, "0", "T"), "w") as fh:
        fh.write("0/T\n")
    time.sleep(0.02)
    if timedir:
        ed = os.path.join(cd, str(end))
        os.makedirs(ed, exist_ok=True)
        if fields:
            for f in NEEDED:
                with open(os.path.join(ed, f), "w") as fh:
                    fh.write("%s\n" % f)
    if not age_ok:
        # make 0/T newer than the fields: the exact defect the guard exists for
        time.sleep(0.02)
        with open(os.path.join(cd, "0", "T"), "w") as fh:
            fh.write("touched last\n")
    n = int(round(end / dt)) if nexec is None else nexec
    with open(os.path.join(cd, "log.solve"), "w") as fh:
        for _ in range(n):
            fh.write("ExecutionTime = 1.0 s  ClockTime = 1 s\n")
        if endline:
            fh.write("End\n")
    with open(os.path.join(root, "STATUS.%s" % name), "w") as fh:
        fh.write("case=%s\nrc=%s\nwall_s=1\nranks=1\n" % (name, rc))
    return cd


def selftest():
    """Mutation matrix.  A control arm that must stay silent and one corruption
    arm per limb that must fire.  Every arm is DRIVEN, not asserted about."""
    ok_all = True

    def arm(label, got, want):
        nonlocal ok_all
        good = (got == want)
        ok_all = ok_all and good
        print("  [%s] %s" % ("ok " if good else "BAD", label))
        return good

    root = tempfile.mkdtemp(prefix="k2d_selftest_")
    try:
        print("-- completion clauses --")
        _mk_case(root, "K2d_L1")
        arm("CONTROL: a clean case -> DONE",
            check(os.path.join(root, "K2d_L1"))[0], True)

        shutil.rmtree(os.path.join(root, "K2d_L1")); os.remove(os.path.join(root, "STATUS.K2d_L1"))
        _mk_case(root, "K2d_L1", rc="1")
        arm("clause 1: rc=1 -> NOT DONE",
            check(os.path.join(root, "K2d_L1"))[0], False)

        shutil.rmtree(os.path.join(root, "K2d_L1")); os.remove(os.path.join(root, "STATUS.K2d_L1"))
        _mk_case(root, "K2d_L1", endline=False)
        arm("clause 2: no End line -> NOT DONE",
            check(os.path.join(root, "K2d_L1"))[0], False)

        shutil.rmtree(os.path.join(root, "K2d_L1")); os.remove(os.path.join(root, "STATUS.K2d_L1"))
        _mk_case(root, "K2d_L1", timedir=False)
        arm("clause 3: no time dir beyond 0 -> NOT DONE",
            check(os.path.join(root, "K2d_L1"))[0], False)

        shutil.rmtree(os.path.join(root, "K2d_L1")); os.remove(os.path.join(root, "STATUS.K2d_L1"))
        _mk_case(root, "K2d_L1", fields=False)
        arm("clause 4: fields missing at endTime -> NOT DONE",
            check(os.path.join(root, "K2d_L1"))[0], False)

        shutil.rmtree(os.path.join(root, "K2d_L1")); os.remove(os.path.join(root, "STATUS.K2d_L1"))
        _mk_case(root, "K2d_L1", nexec=99)
        arm("clause 5: ExecutionTime count short by one -> NOT DONE",
            check(os.path.join(root, "K2d_L1"))[0], False)

        shutil.rmtree(os.path.join(root, "K2d_L1")); os.remove(os.path.join(root, "STATUS.K2d_L1"))
        _mk_case(root, "K2d_L1", age_ok=False)
        arm("clause 6: AGE GUARD, 0/T newer than the fields -> NOT DONE",
            check(os.path.join(root, "K2d_L1"))[0], False)

        shutil.rmtree(os.path.join(root, "K2d_L1")); os.remove(os.path.join(root, "STATUS.K2d_L1"))
        _mk_case(root, "K2d_L1")
        os.remove(os.path.join(root, "STATUS.K2d_L1"))
        arm("REFUSE: no STATUS -> cannot decide (None)",
            check(os.path.join(root, "K2d_L1"))[0], None)

        arm("REFUSE: name off the allow-list -> exit 2",
            run([os.path.join(root, "not_a_k2d_case")], verbose=False), EXIT_REFUSE)

        print("-- clause 7 launch guard, BOTH DIRECTIONS, on real paths --")
        g = os.path.join(root, "guard_clean")
        os.makedirs(os.path.join(g, "0.orig"), exist_ok=True)
        arm("CONTROL: clean case with 0.orig/ -> guard PERMITS",
            launch_guard(g, verbose=False), True)

        os.makedirs(os.path.join(g, "0"), exist_ok=True)
        arm("guard: a pre-existing 0/ -> guard REFUSES",
            launch_guard(g, verbose=False), False)
        shutil.rmtree(os.path.join(g, "0"))

        os.makedirs(os.path.join(g, "500"), exist_ok=True)
        arm("guard: a pre-existing time dir -> guard REFUSES",
            launch_guard(g, verbose=False), False)
        shutil.rmtree(os.path.join(g, "500"))

        shutil.rmtree(os.path.join(g, "0.orig"))
        arm("guard: no 0.orig/ to arm from -> guard REFUSES",
            launch_guard(g, verbose=False), False)
        os.makedirs(os.path.join(g, "0.orig"), exist_ok=True)

        pp = os.path.join(g, "postProcessing", "T_in", "0")
        os.makedirs(pp, exist_ok=True)
        arm("NEGATIVE CONTROL: EMPTY postProcessing/ -> guard PERMITS "
            "(the limb fires on CONTENT, not on the directory existing)",
            launch_guard(g, verbose=False), True)

        with open(os.path.join(pp, "T_in.dat"), "w") as fh:
            fh.write("# leftover\n")
        arm("guard: NON-EMPTY postProcessing/ -> guard REFUSES",
            launch_guard(g, verbose=False), False)

        arm("guard: the --guard CLI form both launchers call -> exit 1",
            main(["--guard", g]), EXIT_FAIL)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("\nSELFTEST %s" % ("PASS -- every arm fired as registered" if ok_all
                             else "FAIL -- an arm did not behave as registered"))
    return EXIT_OK if ok_all else EXIT_FAIL


def main(argv):
    if not argv:
        print(__doc__)
        return EXIT_REFUSE
    if argv[0] == "--selftest":
        return selftest()
    if argv[0] == "--guard":
        if len(argv) != 2:
            print("REFUSE: --guard takes exactly one case directory")
            return EXIT_REFUSE
        return EXIT_OK if launch_guard(argv[1]) else EXIT_FAIL
    return run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
