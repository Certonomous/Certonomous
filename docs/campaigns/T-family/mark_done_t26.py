#!/usr/bin/env python3
"""
T26 COMPLETION INSTRUMENT -- the strict completion rule, and CLAUSE 7.

REGISTERED PATH: T26_PREREGISTRATION.md:803 registers this file at
`docs/campaigns/T-family/mark_done_t26.py`.  It is NOT written under
`verification/runs/T-family/T26_runs/`, because :106 makes the ABSENCE of that
directory the rule-2 pre-compute condition of the whole registration.

THE STRICT COMPLETION RULE (CLAUDE.md rule 4; registration :587-601).  A level
is DONE only if EVERY clause holds.  Any failure -> NOT DONE, no marker:

  1  rc = 0, read from STATUS.<level> which the launcher writes from the
     solver's own `$?` captured INSIDE the wrapper.  An ABSENT STATUS is a
     REFUSAL (exit 2), never an rc inferred from an End line.
  2  log.solve carries an `End` line.
  3  the last written time == endTime from the level's OWN system/controlDict.
  4  the registered fields are present at endTime:
       fluid:  T U p_rgh alphat nut k omega phi   (`phi` per Sanaa 2026-09-06,
               aligning CLAUDE.md rule 4 with mark_done_t3.py:34)
       core, housing, duct:  T p                  (registration :594)
  5  the ExecutionTime line count == round(endTime / deltaT).  deltaT is READ
     from the controlDict, not assumed: at the registered `deltaT 1` this is
     endTime, the historical unit-step case (clause-5, Sanaa 2026-09-09).
  6  THE AGE GUARD: every field at endTime is NEWER, by st_mtime, than that
     level's OWN 0/fluid/T -- which launch_t26.sh touches LAST at launch, so it
     dates the run that was allowed to produce the answer (L-143, D438).

  7  THE LAUNCH GUARD -- `--launch-guard <case>`.  REFUSES a case in which `0/`
     or any numeric time directory already exists.

CLAUSE 7 IS ALIVE, AND THAT IS THE POINT OF THIS FILE.
The heat-transfer supervisor landed a finding on 2026-09-10: clause 7 is
DEFINED in seven K0-family instruments and CALLED BY ZERO LAUNCHERS, because
every builder created `0/` itself, so "refuse if 0/ exists" could never fire on
a legitimate launch.  Seven dead levers.  This is the eighth definition and it
is NOT dead:

  * `build_t26.py` stages into `0.orig/` and NEVER creates `0/`.
  * `launch_t26.sh` calls `mark_done_t26.py --launch-guard` BEFORE `cp -r
    0.orig 0` (call site CS-1, registration :647).
  * `orchestrate_t26.py` calls it SYNCHRONOUSLY, on this side of the fork,
    BEFORE `Popen` (call site CS-2, :648) -- because the orchestrator sends the
    launcher's stdout to DEVNULL and never waits, so a refusal printed inside
    the launcher would go to a discarded pipe and the level would be recorded
    as launched.
  * The rule is written down ONCE, here.  It is CALLED, never reimplemented
    (CLAUDE.md rule 14: a lesson is not applied until EVERY call site asserts
    it, so both sites call and `--selftest` drives BOTH).

`--selftest` drives clause 7 THROUGH THE REAL LAUNCHER AS A SUBPROCESS, in the
three arms the registration fixes at :655-661, and arm C is the one that makes
arm B evidence:
    A  clean case (only 0.orig/)            -> guard passes, launcher proceeds
    B  same case with 0/ pre-created        -> launcher REFUSES, exit 2,
                                               `CLAUSE 7` in its output, and
                                               NOTHING is Popen'd
    C  NEGATIVE CONTROL: guard forced clear, -> the dirty case LAUNCHES
       same dirty case, same launcher
Without arm C, arm B's refusal could be caused by anything in the launcher.
With it, the refusal is attributable to the guard and to nothing else.

NO `assert` STATEMENT IN THIS FILE (L-332): `python3 -O` deletes them, and a
guard that vanishes under -O is not a guard.  --selftest checks its own AST.

Usage:  python3 mark_done_t26.py [LEVEL ...] [--root DIR]
        python3 mark_done_t26.py --launch-guard CASE_DIR
        python3 mark_done_t26.py --selftest

Exit codes:  0 all requested levels DONE  /  the launch guard PASSED
             1 at least one level NOT DONE (a reportable physics outcome)
             2 REFUSAL -- STATUS absent, structural precondition failed, or
               THE LAUNCH GUARD REFUSED
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..",
                                    "verification", "runs", "T-family", "T26_runs"))
LEVELS = ("L1", "L2", "L3")
FLUID_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi")
SOLID_FIELDS = ("T", "p")
SOLID_REGIONS = ("core", "housing", "duct")
AGE_REF = os.path.join("0", "fluid", "T")        # touched LAST by launch_t26.sh
# INFRASTRUCTURE (L-342 / Sanaa's rule d4d0c29d: a bookkeeping failure
# invalidates the bookkeeping, never the physics artifacts).  Absent -> NOT
# MEASURED, disclosed, and the grade PROCEEDS.  `capped` is NOT a conjunct.
INFRA = ("wall_s", "timeout_s", "ranks", "core_min", "capped", "checkmesh_rc",
         "started_utc", "ended_utc", "solver_path", "note")

EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# ===========================================================================
# CLAUSE 7 -- THE LAUNCH GUARD.  One definition, two call sites, both live.
# ===========================================================================
def launch_guard(case_dir, verbose=True):
    """Return a list of refusal reasons; EMPTY means the case may be launched.

    A case is launchable only if it is UNSTARTED.  `0/` or any numeric time
    directory already present means either a previous run's state is still
    there -- in which case the age guard of clause 6 cannot date this run --
    or another process is mid-launch.  Either way this is a refusal, and a
    refusal STOPS THE LEVEL SET; it does not skip a level (registration :650).
    """
    why = []
    if not os.path.isdir(case_dir):
        return ["CLAUSE 7: no case directory %s" % case_dir]
    if os.path.exists(os.path.join(case_dir, "0")):
        why.append("CLAUSE 7: %s already has a 0/ -- the age guard of clause 6 "
                   "dates the run from 0/fluid/T, and a 0/ this launch did not "
                   "create cannot date it" % case_dir)
    for name in sorted(os.listdir(case_dir)):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", name) and float(name) > 0:
            if os.path.isdir(os.path.join(case_dir, name)):
                why.append("CLAUSE 7: %s already has time directory %s -- this "
                           "case has already run" % (case_dir, name))
    if not os.path.isdir(os.path.join(case_dir, "0.orig")):
        why.append("CLAUSE 7: %s has no 0.orig/ to arm from; build_t26.py stages "
                   "into 0.orig and never creates 0/" % case_dir)
    if verbose:
        for w in why:
            print(w)
    return why


# ===========================================================================
# clauses 1-6
# ===========================================================================
def _control_dict(case):
    p = os.path.join(case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict in %s -- endTime is unknowable" % case)
    txt = open(p, errors="replace").read()
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", txt, re.M)
    if not m:
        refuse("controlDict in %s states no endTime" % case)
    et = float(m.group(1))
    d = re.search(r"^\s*deltaT\s+([0-9.eE+-]+)\s*;", txt, re.M)
    dt = float(d.group(1)) if d else 1.0
    if dt <= 0:
        refuse("controlDict in %s states deltaT %g" % (case, dt))
    return et, dt


def _read_status(root, level):
    p = os.path.join(root, "STATUS.%s" % level)
    if not os.path.isfile(p):
        refuse("no STATUS.%s -- the solver's exit status was never recorded. An "
               "absent STATUS is NOT inferred from an End line; it is refused." % level)
    txt = open(p, errors="replace").read()
    d = dict(re.findall(r"^([A-Za-z_]+)=(.*)$", txt, re.M))
    if "rc" not in d or not re.fullmatch(r"-?\d+", d["rc"].strip()):
        refuse("STATUS.%s carries no integer rc: %r" % (level, txt.strip()))
    return d, [k for k in INFRA if k not in d]


def check(root, level):
    """Return (physics failures, infrastructure NOT MEASURED)."""
    case = os.path.join(root, level)
    if not os.path.isdir(case):
        refuse("no case directory %s" % case)
    st, nm = _read_status(root, level)
    fails = []

    # --- clause 1: rc ------------------------------------------------------
    rc = int(st["rc"])
    if rc != 0:
        capped = st.get("capped")
        if capped == "yes":
            fails.append("CAPPED (rc=%d, wall_s=%s >= timeout_s=%s): the HANG GUARD "
                         "expired. Registration :737 names it a hang guard and NOT a "
                         "budget cap -- Sanaa's exemption (:716) suspends the cap-stop "
                         "for this rung, so this is a hang finding, not a spend stop."
                         % (rc, st.get("wall_s"), st.get("timeout_s")))
        elif capped == "no":
            fails.append("CRASH (rc=%d at wall_s=%s below timeout_s=%s): a finding "
                         "until triage says otherwise"
                         % (rc, st.get("wall_s"), st.get("timeout_s")))
        else:
            fails.append("CRASH (rc=%d) -- capped witness NOT MEASURED, hang-stop vs "
                         "crash undetermined" % rc)

    # --- clause 2 and 5: the log ------------------------------------------
    log = os.path.join(case, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"], nm
    n_end = n_exec = 0
    with open(log, errors="replace") as fh:          # streamed, never loaded whole
        for line in fh:
            if line.startswith("ExecutionTime"):
                n_exec += 1
            elif line.rstrip() == "End":
                n_end += 1
    if n_end == 0:
        fails.append("log.solve has no End line")

    # --- clause 3: last time == endTime -----------------------------------
    et, dt = _control_dict(case)
    times = sorted((float(x) for x in os.listdir(case)
                    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)
                    and os.path.isdir(os.path.join(case, x))), key=float)
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        return fails + ["no time directory beyond 0 -- the solver wrote no fields"], nm
    last = nonzero[-1]
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))
    tdir = os.path.join(case, "%g" % last)

    # --- clause 4: the registered field set, fluid AND every solid region --
    need = [os.path.join("fluid", f) for f in FLUID_FIELDS]
    for reg in SOLID_REGIONS:
        need += [os.path.join(reg, f) for f in SOLID_FIELDS]
    miss = [f for f in need if not os.path.isfile(os.path.join(tdir, f))]
    if miss:
        return fails + ["time %g is missing %s" % (last, ",".join(miss))], nm

    # --- clause 5: ExecutionTime count == round(endTime / deltaT) ---------
    want = int(round(et / dt))
    if n_exec != want:
        fails.append("%d ExecutionTime lines, expected round(endTime %g / deltaT %g) = %d"
                     % (n_exec, et, dt, want))

    # --- clause 6: THE AGE GUARD ------------------------------------------
    ref = os.path.join(case, AGE_REF)
    if not os.path.isfile(ref):
        fails.append("no %s, so the run cannot be dated and the age guard cannot "
                     "be evaluated" % AGE_REF)
    else:
        age = os.path.getmtime(ref)
        stale = [f for f in need if os.path.getmtime(os.path.join(tdir, f)) < age]
        if stale:
            fails.append("time %g holds fields OLDER than %s (%s) -- not written by "
                         "this run" % (last, AGE_REF, ",".join(stale)))
    return fails, nm


# ===========================================================================
# selftest
# ===========================================================================
def _forge(root, level, rc="0", end=40, deltaT=1, n_exec=None, with_end=True,
           stale=False, status=True, infra=True, missing_field=None,
           short_time=False, capped="no"):
    """A synthetic level shaped exactly like a finished run, in a scratch root."""
    import time
    case = os.path.join(root, level)
    os.makedirs(os.path.join(case, "system"), exist_ok=True)
    os.makedirs(os.path.join(case, "0", "fluid"), exist_ok=True)
    open(os.path.join(case, "system", "controlDict"), "w").write(
        "endTime %d;\ndeltaT %g;\n" % (end, deltaT))
    ref = os.path.join(case, AGE_REF)
    open(ref, "w").write("x\n")
    t0 = time.time() - 100
    os.utime(ref, (t0, t0))
    written = end - 1 if short_time else end
    tdir = os.path.join(case, str(written))
    need = [os.path.join("fluid", f) for f in FLUID_FIELDS]
    for reg in SOLID_REGIONS:
        need += [os.path.join(reg, f) for f in SOLID_FIELDS]
    for f in need:
        if f == missing_field:
            continue
        p = os.path.join(tdir, f)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write("y\n")
        if stale:
            os.utime(p, (t0 - 100, t0 - 100))
    n = int(round(end / deltaT)) if n_exec is None else n_exec
    open(os.path.join(case, "log.solve"), "w").write(
        "ExecutionTime = 1 s\n" * n + ("End\n" if with_end else ""))
    if status:
        lines = ["case=%s" % level, "rc=%s" % rc]
        if infra:
            wall = 600 if capped == "yes" else 10
            lines += ["wall_s=%d" % wall, "ranks=8", "core_min=1.333", "timeout_s=600",
                      "capped=%s" % capped, "checkmesh_rc=0", "started_utc=x",
                      "ended_utc=y", "solver_path=/x", "note=clean"]
        open(os.path.join(root, "STATUS.%s" % level), "w").write("\n".join(lines) + "\n")
    return case


def selftest():
    import ast
    import shutil
    import subprocess
    import tempfile
    global ROOT
    print("mark_done_t26.py --selftest")
    print("=" * 74)
    fails = []
    level = LEVELS[0]

    print("\n(i) CLAUSES 1-6, each driven BOTH ways in a scratch root")

    def expect(name, want_code, want_marker, **kw):
        global ROOT
        tmp = tempfile.mkdtemp(prefix="t26_md_")
        try:
            _forge(tmp, level, **kw)
            ROOT = tmp
            try:
                code = main([level])
            except SystemExit as e:
                code = e.code
            marker = os.path.exists(os.path.join(tmp, "DONE.%s" % level))
            ok = (code == want_code) and (marker == want_marker)
            print("  [%s] %-58s -> exit %s, marker %s"
                  % ("ok " if ok else "BAD", name, code, marker))
            if not ok:
                fails.append(name)
        finally:
            ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "verification",
                                                "runs", "T-family", "T26_runs"))
            shutil.rmtree(tmp, ignore_errors=True)

    expect("CONTROL: clean forged level -> DONE, marker written", 0, True)
    expect("c1 rc=1, capped=no -> NOT DONE (CRASH)", 1, False, rc="1")
    expect("c1 rc=124, capped=yes -> NOT DONE (hang guard, NOT a budget cap)", 1, False,
           rc="124", capped="yes")
    expect("c1 rc=1, capped witness ABSENT -> NOT DONE, hang-vs-crash undetermined",
           1, False, rc="1", infra=False)
    expect("c2 no End line -> NOT DONE", 1, False, with_end=False)
    expect("c3 last time != endTime -> NOT DONE", 1, False, short_time=True)
    expect("c4 a registered fluid field missing -> NOT DONE", 1, False,
           missing_field=os.path.join("fluid", "phi"))
    expect("c4 a registered SOLID field missing -> NOT DONE", 1, False,
           missing_field=os.path.join("housing", "T"))
    expect("c5 ExecutionTime count short -> NOT DONE", 1, False, n_exec=39)
    # THE FIRST DRAFT OF THIS ARM PASSED NO n_exec, so _forge derived
    # round(40/0.5) = 80 lines and the forged case was GENUINELY COMPLETE.
    # mark_done correctly returned DONE and the selftest correctly called the
    # ARM bad. The instrument was right and the test input was wrong; recorded
    # rather than silently fixed.
    expect("c5 deltaT 0.5: 80 lines needed, 40 given -> NOT DONE", 1, False,
           deltaT=0.5, n_exec=40)
    expect("c5 deltaT 0.5 with 80 lines -> DONE", 0, True, deltaT=0.5, n_exec=80)
    expect("c6 AGE GUARD: fields OLDER than 0/fluid/T -> NOT DONE", 1, False, stale=True)
    expect("absent STATUS -> REFUSE exit 2, no marker", 2, False, status=False)
    expect("every infrastructure field absent -> still DONE, NOT MEASURED disclosed",
           0, True, infra=False)

    print("\n(ii) CLAUSE 7 -- THE LAUNCH GUARD, AS A FUNCTION")
    tmp = tempfile.mkdtemp(prefix="t26_g_")
    try:
        clean = os.path.join(tmp, "clean")
        os.makedirs(os.path.join(clean, "0.orig"))
        w = launch_guard(clean, verbose=False)
        ok = (w == [])
        print("  [%s] clean case (only 0.orig/) -> guard passes (%d reasons)"
              % ("ok " if ok else "BAD", len(w)))
        fails.append("guard clean") if not ok else None

        dirty = os.path.join(tmp, "dirty0")
        os.makedirs(os.path.join(dirty, "0.orig"))
        os.makedirs(os.path.join(dirty, "0"))
        w = launch_guard(dirty, verbose=False)
        ok = bool(w) and any("0/" in x for x in w)
        print("  [%s] case with 0/ present -> guard REFUSES: %s"
              % ("ok " if ok else "BAD", (w[0][:66] + "...") if w else "NOTHING"))
        fails.append("guard 0/") if not ok else None

        dt = os.path.join(tmp, "dirtyT")
        os.makedirs(os.path.join(dt, "0.orig"))
        os.makedirs(os.path.join(dt, "500"))
        w = launch_guard(dt, verbose=False)
        ok = bool(w) and any("500" in x for x in w)
        print("  [%s] case with time directory 500/ -> guard REFUSES"
              % ("ok " if ok else "BAD"))
        fails.append("guard time") if not ok else None

        no_orig = os.path.join(tmp, "noorig")
        os.makedirs(no_orig)
        w = launch_guard(no_orig, verbose=False)
        ok = bool(w) and any("0.orig" in x for x in w)
        print("  [%s] case with no 0.orig/ -> guard REFUSES" % ("ok " if ok else "BAD"))
        fails.append("guard 0.orig") if not ok else None

        # THE CLI FORM, which is what the launchers actually call
        for name, d, want in (("clean", clean, 0), ("dirty", dirty, EXIT_REFUSE)):
            r = subprocess.run([sys.executable, os.path.abspath(__file__),
                                "--launch-guard", d], capture_output=True, text=True)
            ok = r.returncode == want and (want == 0 or "CLAUSE 7" in r.stdout + r.stderr)
            print("  [%s] CLI --launch-guard on the %s case -> exit %d (wanted %d)"
                  % ("ok " if ok else "BAD", name, r.returncode, want))
            fails.append("cli guard " + name) if not ok else None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n(iii) CLAUSE 7 IS REACHABLE THROUGH THE REAL LAUNCHER -- three arms,")
    print("      registration :655-661.  ARM C IS WHAT MAKES ARM B EVIDENCE.")
    launcher = os.path.join(HERE, "launch_t26.sh")
    if not os.path.isfile(launcher):
        print("  [BAD] launch_t26.sh is absent -- clause 7 has NO live call site, which")
        print("        is exactly the seven-dead-levers defect this file exists to avoid")
        fails.append("no launcher")
    else:
        r = subprocess.run(["bash", launcher, "--selftest-clause7"],
                           capture_output=True, text=True)
        for ln in r.stdout.splitlines():
            if ln.startswith("  ["):
                print(ln)
        if r.returncode != 0:
            fails.append("launcher clause-7 selftest exit %d" % r.returncode)
        if "ARM C" not in r.stdout:
            fails.append("launcher selftest did not run arm C (the negative control)")

    print("\n(iv) NO `assert` STATEMENT IN THIS FILE (L-332: -O strips them)")
    n_assert = sum(isinstance(x, ast.Assert)
                   for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] AST assert count = %d (the counter sees a planted assert: %d)"
          % ("ok " if ok else "BAD", n_assert, planted))
    if not ok:
        fails.append("ast")

    print("\n" + "=" * 74)
    print("SELFTEST %s (%d failed)%s"
          % ("PASS" if not fails else "FAIL", len(fails),
             "" if not fails else ": " + "; ".join(sorted(set(fails)))))
    return EXIT_OK if not fails else EXIT_NOTDONE


# ===========================================================================
def main(argv):
    global ROOT
    if "--selftest" in argv:
        return selftest()
    if "--launch-guard" in argv:
        i = argv.index("--launch-guard")
        if i + 1 >= len(argv):
            refuse("--launch-guard needs a case directory")
        why = launch_guard(os.path.abspath(argv[i + 1]))
        if why:
            print("LAUNCH GUARD REFUSED: %d reason(s). A refusal STOPS THE LEVEL SET; "
                  "it does not skip a level (registration :650)." % len(why))
            return EXIT_REFUSE
        print("CLAUSE 7 launch guard PASSED for %s" % os.path.abspath(argv[i + 1]))
        return EXIT_OK
    if "--root" in argv:
        i = argv.index("--root")
        ROOT = os.path.abspath(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    want = [a for a in argv if not a.startswith("-")] or list(LEVELS)
    for lv in want:
        if lv not in LEVELS:
            refuse("%r is not a registered T26 level: %s" % (lv, " ".join(LEVELS)))
    rc = EXIT_OK
    for lv in want:
        f, nm = check(ROOT, lv)
        infra = ("  [infrastructure NOT MEASURED: %s -- disclosed, grade proceeds]"
                 % ",".join(nm)) if nm else ""
        if f:
            rc = EXIT_NOTDONE
            print("NOT DONE  %-4s - %s%s" % (lv, "; ".join(f), infra))
        else:
            marker = os.path.join(ROOT, "DONE.%s" % lv)
            if not os.path.exists(marker):
                open(marker, "w").write("strict completion rule met, clauses 1-6%s\n" % infra)
            print("DONE      %-4s%s" % (lv, infra))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
