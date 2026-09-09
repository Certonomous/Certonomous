#!/usr/bin/env python3
"""Adaptive-`deltaT` strict-completion instrument for the F14 / thermal family.

DRAFT -- NOT FROZEN, NOT COMMITTED, NOT YET GRADED WITH.  Built for the
heat-transfer supervisor's SUPERVISION-CHARTER-§3 diff-read and for the
verification supervisor's implementation audit.  Nothing here launches a solver.

=== WHAT THIS IS, AND WHAT IT REUSES UNCHANGED ===

The strict completion rule (CLAUDE.md rule 4) is all-or-nothing:
  1. rc = 0
  2. exactly one OpenFOAM `End` line in the solver log
  3. last written time == controlDict endTime
  4. every registered field present at endTime
  5. the STEP-COUNT conjunct  <-- the ONLY clause this instrument changes
  6. the age guard: every field at endTime NEWER than the case's own 0/T
 (7. the PRE-launch guard: refuse a case in which 0 or a numeric time dir
     already exists -- exposed as --launch-guard, mirroring mark_done_k0g.py)

Clauses 1-4 and the age guard are carried, byte-for-byte in LOGIC, from the
FROZEN fixed-`deltaT` instruments this family already trusts:
  * verification/runs/T-family/T3_runs/mark_done_t3.py   (clauses 2,3,4,6)
  * verification/runs/T-family/T23_runs/mark_done_t23.py (clause 1 rc-DERIVE
    path for a queue-CLOBBERED STATUS; L-342; Sanaa's rule 2026-08-26
    "bookkeeping never voids physics"; the "REFUSE, never degrade" discipline)
Nothing in clauses 1-4 or the age guard is weakened.  A defect planted on each
of them fires; the clean counterpart stays quiet (--selftest).

=== CLAUSE 5, THE ONE DIFFERENCE: THE ADAPTIVE STEP-COUNT FORM ===

The fixed-`deltaT` clause 5 reads `ExecutionTime` count == `round(endTime/deltaT)`
(T1b_L4_AMENDMENT.md §12, Sanaa-approved 2026-09-09 -- the "clause-5"
generalization of the historical `int(endTime)` unit-step form).  §12.3 places
ADAPTIVE-`deltaT` (variable-step) runs OUT of that form's scope: their step count
is NOT `round(endTime/deltaT)` because the step size varies with the Courant
number.  Their registered check is

        n_exec == n_time_written                 (T1b_L4_AMENDMENT.md §12.3)

which this instrument implements as an EQUALITY between two counts read from the
SOLVER LOG:
    n_exec = number of `ExecutionTime` lines   (one emitted at the END of a step)
    n_time = number of `Time = ` lines         (one emitted at the START of a step)
A transient PIMPLE/SIMPLE solver emits exactly one of each per time step, so on a
sound run the two counts are EQUAL and non-zero; a truncated or restart-replayed
log breaks the equality.  This is precisely the transient check the K0g draft
(scripts/mark_done_k0g.py, clause 5) already applies, and this file factors that
logic into a single shared core (`adaptive_step_check`) so both instruments call
ONE checked implementation (rule 14: additive, one call site of truth).

    ----------------------------------------------------------------------
    WHAT `n_time_written` MEANS, AND WHY IT IS A LOG COUNT, NOT A DIRECTORY COUNT
    ----------------------------------------------------------------------
    §12.3 is CORRECT and needs no amendment.  It specifies a STEP-COUNT check
    (line 672: "step-count check"; line 673: `n_exec == n_time_written`, worked
    example K2bU3R3's `995 == 995`), and this instrument implements EXACTLY that:
    both counts are read from the solver LOG (`ExecutionTime` lines / `Time = `
    lines, one of each per time step).  The word "directories" appears NOWHERE
    against `n_time_written` in the frozen amendment (verified by grep of
    T1b_L4_AMENDMENT.md: "director" occurs only on unrelated launch-guard/history
    lines 4, 31, 349, 354-355).

    A "number of time DIRECTORIES written" reading of `n_time_written` was an
    error in the BUILD BRIEF to this instrument, not in §12.3, and it is rejected
    here because it would INVERT the verdict on the actual K2bU3R3_D59 run:
      * the run took 995 time steps (995 `ExecutionTime`, 995 `Time = ` lines)
      * `writeControl adjustableRunTime; writeInterval 20;` with endTime 80 wrote
        exactly FOUR time directories on disk: 20, 40, 60, 80.
    So a directory reading gives `995 == 4 => NOT DONE`, against §12.3's codified
    `995 == 995` PASS and every frozen instrument's clause-5 intent
    (mark_done_t3.py:11-13, mark_done_k0g.py:278-286: "no silently skipped
    iterations, no restart that replayed part of the run").  `writeInterval`
    DECOUPLES on-disk directories from steps, so a directory count can never
    serve as the step count of an adaptive run.  `n_time_written` is therefore
    the LOG step count (`Time = ` lines) -- the only reading under which K2bU3R3
    gives 995 == 995 and under which clause 5 means what §12.3 wrote it to mean.
    ----------------------------------------------------------------------

FAIL-CLOSED ON NON-ADAPTIVE CASES.  The adaptive form is only correct for a
genuine `adjustTimeStep yes` run.  `adaptive_step_check` REFUSES (exit 2) if the
case's own controlDict does not set `adjustTimeStep` on -- it does NOT silently
accept, and it does NOT fall back to the fixed-`deltaT` count.  A fixed-`deltaT`
case must be graded by the fixed-`deltaT` instrument, never by this one.

NO `assert` in the module body (L-332).  A missing controlDict, a missing STATUS,
or a non-adaptive case is a REFUSAL (exit 2), never an inference (K0d L1).

Exit codes:  0 all requested cases DONE
             1 at least one case is NOT DONE (reasons printed)
             2 REFUSAL (a structural precondition means the question cannot be
               asked: no controlDict, no STATUS, or the case is not adaptive)

Usage:
    python3 mark_done_adaptive.py --preset k2bu3r3 [--root DIR]
    python3 mark_done_adaptive.py --root DIR --case NAME --fields "T U ..." \
            --log log.solve --status STATUS.NAME [--age-ref 0/T] [--rc-policy derive]
    python3 mark_done_adaptive.py --root DIR --launch-guard CASE
    python3 mark_done_adaptive.py --selftest
"""
import argparse
import os
import re
import sys

EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2

# The thermal-family completion tuple (CLAUDE.md rule 4, phi added Sanaa
# 2026-09-06).  A single-region RAS kOmegaSST transient case.
THERMAL_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi")


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------------------------------------------------------------------------
# controlDict readers (a completion rule that guesses its own target is not a
# rule -- mark_done_t23.py)
# --------------------------------------------------------------------------
def _controldict_path(root, case):
    p = os.path.join(root, case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict for %s -- a completion rule that guesses "
               "its own target is not a rule" % case)
    return p


def control_num(cd_path, key):
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % key, open(cd_path).read(), re.M)
    if not m:
        refuse("controlDict %s states no %s" % (cd_path, key))
    return float(m.group(1))


def is_adjust_time_step(cd_path):
    """True iff the case's OWN controlDict sets adjustTimeStep on.  Absent or
    off => False (this instrument then REFUSES upstream in clause 5)."""
    m = re.search(r"^\s*adjustTimeStep\s+(\w+)\s*;", open(cd_path).read(), re.M)
    return bool(m) and m.group(1).lower() in ("yes", "on", "true", "1")


# --------------------------------------------------------------------------
# THE ADAPTIVE CLAUSE-5 CORE -- the single shared implementation
# --------------------------------------------------------------------------
def adaptive_step_check(body, cd_path):
    """Clause 5 for an adaptive-`deltaT` run.  FAIL-CLOSED.

    Returns (fails, n_exec, n_time).  REFUSES (exit 2) -- never returns -- if the
    case is NOT adjustTimeStep, because the adaptive equality is only meaningful
    for a variable-step run and this instrument must not silently accept a
    fixed-step case it was not asked to grade.

    n_exec := count of `ExecutionTime` lines (one per step, emitted at step END)
    n_time := count of `Time = ` lines       (one per step, emitted at step START)
    A sound transient run has n_exec == n_time >= 1.  See the module docstring on
    why `n_time_written` is the LOG step count and NOT the filesystem directory
    count (writeInterval decouples directories from steps)."""
    if not is_adjust_time_step(cd_path):
        refuse("clause 5 (adaptive form) was applied to a case whose controlDict "
               "does NOT set adjustTimeStep on. The adaptive n_exec==n_time check "
               "is only valid for a variable-step run; a fixed-deltaT case must be "
               "graded by the fixed-deltaT instrument (round(endTime/deltaT)). "
               "Refusing rather than silently accepting (fail-closed).")
    n_exec = len(re.findall(r"^ExecutionTime", body, re.M))
    n_time = len(re.findall(r"^Time = ", body, re.M))
    fails = []
    if n_exec < 1 or n_time < 1:
        fails.append("no time steps logged (ExecutionTime=%d, Time-lines=%d)"
                     % (n_exec, n_time))
    elif n_exec != n_time:
        fails.append("%d ExecutionTime lines != %d 'Time =' lines (a truncated "
                     "or restart-replayed solver log; adaptive clause 5)"
                     % (n_exec, n_time))
    return fails, n_exec, n_time


# --------------------------------------------------------------------------
# disk readers (field_path accepts T or T.gz -- carried from mark_done_k0g.py)
# --------------------------------------------------------------------------
def field_path(tdir, field):
    plain = os.path.join(tdir, field)
    if os.path.isfile(plain):
        return plain
    gz = plain + ".gz"
    if os.path.isfile(gz):
        return gz
    return None


def numeric_times(d):
    return sorted((x for x in os.listdir(d)
                   if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)


def read_status(root, case, status_name):
    """STATUS file inside the case directory.  Absent => REFUSE (K0d L1: an
    absent STATUS is never inferred from an End line).  Tolerant of both the
    newline form (STATUS.<case>) and the single-line space-separated queue form
    (`launcher_rc=0 end=... note=...`)."""
    p = os.path.join(root, case, status_name)
    if not os.path.isfile(p):
        refuse("no %s -- the run's own record was never written. An absent STATUS "
               "is not inferred from an End line (K0d L1); it is refused." % status_name)
    txt = open(p, errors="replace").read()
    return dict(re.findall(r"([A-Za-z_]\w*)=(\S+)", txt))


# --------------------------------------------------------------------------
# clause 7 -- the PRE-launch guard (mirrors mark_done_k0g.py.launch_guard)
# --------------------------------------------------------------------------
def launch_guard(root, case):
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return ["no case directory %s" % d]
    bad = []
    if os.path.isdir(os.path.join(d, "0")):
        bad.append("a '0' directory already exists")
    stray = [t for t in numeric_times(d) if float(t) > 0]
    if stray:
        bad.append("numeric time directories already exist: " + ",".join(stray))
    return bad


# --------------------------------------------------------------------------
# clauses 1-6
# --------------------------------------------------------------------------
def check(root, case, fields, age_ref, log_name, status_name, rc_policy):
    """Return (fails, notes).  fails empty => every clause holds.

    rc_policy:
      'read'   -- clause 1 requires an integer rc= key in STATUS reading 0
                  (the mark_done_t3.py form).
      'derive' -- STATUS carries no true rc (queue-clobbered: only launcher_rc);
                  rc is DERIVED FROM THE LOG exactly as mark_done_t23.py does
                  (End==1, FOAM FATAL==0, last time==endTime), launcher_rc is
                  NEVER accepted as rc, and every line says rc_source (L-342;
                  bookkeeping never voids physics, Sanaa 2026-08-26)."""
    fails, notes = [], []
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return ["no case directory"], notes

    st = read_status(root, case, status_name)        # may REFUSE (exit 2)

    log = os.path.join(d, log_name)
    if not os.path.isfile(log):
        return fails + ["no %s" % log_name], notes
    body = open(log, errors="replace").read()

    n_end = len(re.findall(r"^End\s*$", body, re.M))
    n_fatal = len(re.findall(r"FOAM FATAL", body))

    cd = _controldict_path(root, case)
    et = control_num(cd, "endTime")
    times = [float(t) for t in numeric_times(d)]
    nonzero = [t for t in times if t > 0]
    last = nonzero[-1] if nonzero else None

    # --- CLAUSE 1: rc -----------------------------------------------------
    if rc_policy == "read":
        rc_source = "READ-FROM-STATUS"
        if not re.fullmatch(r"-?\d+", st.get("rc", "")):
            fails.append("STATUS carries no integer rc key (%r); rc_policy=read "
                         "requires one" % st)
        elif int(st["rc"]) != 0:
            fails.append("CRASH/CAP: STATUS rc=%s -- a crash is a FINDING until "
                         "triage says otherwise" % st["rc"])
    else:  # derive (mark_done_t23.py logic, verbatim in intent)
        rc_source = "DERIVED-FROM-LOG"
        if "rc" in st and re.fullmatch(r"-?\d+", st["rc"]):
            # a true rc IS present even under a derive preset: read it, do not
            # discard evidence.
            rc_source = "READ-FROM-STATUS"
            if int(st["rc"]) != 0:
                fails.append("CRASH/CAP: STATUS rc=%s" % st["rc"])
        else:
            why = ("STATUS carries launcher_rc=%s, the exit status of the LAUNCH "
                   "ARGV and NOT the solver rc; it is NOT accepted as rc"
                   % st["launcher_rc"]) if "launcher_rc" in st else \
                  "STATUS carries no rc key at all"
            notes.append("CLAUSE 1 (rc=0) UNEVALUABLE FROM STATUS: " + why)
            notes.append("CLAUSE 1 DERIVED from %s: End lines=%d (want 1), "
                         "FOAM FATAL=%d (want 0), last time=%s (want %g)"
                         % (log_name, n_end, n_fatal,
                            "none" if last is None else "%g" % last, et))
            if n_end != 1 or n_fatal != 0 or last is None or abs(last - et) > 1e-9:
                fails.append("rc CANNOT BE DERIVED as 0: End lines=%d, FOAM "
                             "FATAL=%d, last time=%s vs endTime %g"
                             % (n_end, n_fatal,
                                "none" if last is None else "%g" % last, et))

    # --- CLAUSE 2: exactly one End line -----------------------------------
    if n_end != 1:
        fails.append("%s carries %d End lines, expected exactly 1" % (log_name, n_end))
    if n_fatal:
        fails.append("%s carries %d FOAM FATAL occurrences" % (log_name, n_fatal))

    # --- CLAUSE 3: last written time == endTime ---------------------------
    if last is None:
        return fails + ["no time directory beyond 0 -- the solver wrote no fields"], notes
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))

    # --- CLAUSE 4: registered fields present at endTime -------------------
    tdir = os.path.join(d, "%g" % last)
    present = {f: field_path(tdir, f) for f in fields}
    miss = [f for f in fields if present[f] is None]
    if miss:
        return fails + ["time %g is missing %s" % (last, ",".join(miss))], notes

    # --- CLAUSE 5: THE ADAPTIVE STEP-COUNT FORM (shared core) -------------
    step_fails, n_exec, n_time = adaptive_step_check(body, cd)   # may REFUSE
    fails += step_fails
    notes.append("adaptive clause 5: n_exec=%d, n_time(log 'Time =')=%d, "
                 "time directories on disk (NOT the step count)=%d"
                 % (n_exec, n_time, len(nonzero)))

    # --- CLAUSE 6: THE AGE GUARD ------------------------------------------
    ref = os.path.join(d, *age_ref)
    if not os.path.isfile(ref):
        fails.append("no %s, so the run cannot be dated and the age guard cannot "
                     "be evaluated" % os.path.join(*age_ref))
    else:
        age = os.path.getmtime(ref)
        stale = [f for f in fields if os.path.getmtime(present[f]) < age]
        if stale:
            fails.append("time %g holds fields OLDER than %s (%s) -- not written "
                         "by this run (D438, L-143)"
                         % (last, os.path.join(*age_ref), ",".join(stale)))

    notes.append("rc_source=%s" % rc_source)
    return fails, notes


# --------------------------------------------------------------------------
# presets
# --------------------------------------------------------------------------
PRESETS = {
    # K2bU3R3_D59: buoyantBoussinesqPimpleFoam, adjustTimeStep, dt0 0.005,
    # endTime 80, RAS kOmegaSST.  STATUS is the queue-CLOBBERED form (only
    # launcher_rc), so rc is DERIVED FROM THE LOG (mark_done_t23.py; L-342).
    "k2bu3r3": dict(
        default_root="verification/runs/F14-cooling-ladder/K2b_runs",
        case="K2bU3R3_D59",
        fields=THERMAL_FIELDS,
        age_ref=("0", "T"),
        log_name="log.buoyantBoussinesqPimpleFoam",
        status_name="STATUS.queue.K2bU3R3",
        rc_policy="derive",
    ),
}


def run_case(root, case, fields, age_ref, log_name, status_name, rc_policy):
    fails, notes = check(root, case, fields, age_ref, log_name, status_name, rc_policy)
    for n in notes:
        print("NOTE      %-14s - %s" % (case, n))
    if fails:
        print("NOT DONE  %-14s - %s" % (case, "; ".join(fails)))
        return EXIT_NOTDONE
    marker = os.path.join(root, "DONE.%s" % case)
    if not os.path.exists(marker):
        open(marker, "w").write("strict completion rule met (adaptive clause 5)\n")
    print("DONE      %-14s" % case)
    return EXIT_OK


# --------------------------------------------------------------------------
# selftest -- planted controls.  Every clause is shown able to FIRE on a
# planted defect and STAY QUIET on the clean counterpart (standing rule 3).
# The fail-closed non-adaptive REFUSAL is exercised in-process (SystemExit).
# --------------------------------------------------------------------------
def _synthetic(root, case, n_steps=100, endtime=80.0, dt0=0.005, adjust=True,
               break_clause=None, launcher_only=True):
    import time as _time
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write(
        "application buoyantBoussinesqPimpleFoam;\n"
        "endTime %g;\ndeltaT %g;\nwriteControl adjustableRunTime;\n"
        "writeInterval 20.0;\nadjustTimeStep %s;\nmaxCo 2.0;\n"
        % (endtime, dt0, "yes" if adjust else "no"))
    z = os.path.join(d, "0")
    os.makedirs(z, exist_ok=True)
    open(os.path.join(z, "T"), "w").write("0/T\n")
    _time.sleep(0.02)
    last = endtime if break_clause != "clause3" else endtime - 20
    tdir = os.path.join(d, "%g" % last)
    os.makedirs(tdir, exist_ok=True)
    emit = [f for f in THERMAL_FIELDS
            if not (break_clause == "clause4" and f == THERMAL_FIELDS[-1])]
    for f in emit:
        q = os.path.join(tdir, f)
        open(q, "w").write("%s at %g\n" % (f, last))
        if break_clause == "clause6":
            old = os.path.getmtime(os.path.join(z, "T")) - 100
            os.utime(q, (old, old))
    # one 'Time =' and one 'ExecutionTime' line per step (variable dt values)
    body = "".join("Time = %g\nExecutionTime = %d s  ClockTime = %d s\n"
                   % (dt0 * i, i, i) for i in range(1, n_steps + 1))
    if break_clause == "clause5":
        body += "ExecutionTime = 999 s\n"          # n_exec != n_time
    n_end = {"clause2": 0, "clause2b": 2}.get(break_clause, 1)
    body += "End\n" * n_end
    if break_clause == "clause1fatal":
        body += "--> FOAM FATAL ERROR: planted\n"
    open(os.path.join(d, "log.buoyantBoussinesqPimpleFoam"), "w").write(body)
    # STATUS: the queue-clobbered form by default (launcher_rc only)
    if launcher_only:
        s = "launcher_rc=0 end=2026-09-07T19:19:03Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc\n"
    else:
        s = "rc=%s wall=1.0\n" % (1 if break_clause == "clause1read" else 0)
    open(os.path.join(d, "STATUS.%s" % case), "w").write(s)
    return d


def selftest():
    import tempfile
    import shutil
    import ast
    import io
    import contextlib
    print("=" * 74)
    print("mark_done_adaptive.py -- SELFTEST (planted controls)")
    print("=" * 74)
    fails = []
    F, AGE, LOG = THERMAL_FIELDS, ("0", "T"), "log.buoyantBoussinesqPimpleFoam"
    CASE = "K2bU3R3_D59"

    def drive(label, want_rc, want_marker, rc_policy="derive", status="STATUS.%s" % CASE, **kw):
        tmp = tempfile.mkdtemp(prefix="adapt_md_")
        try:
            _synthetic(tmp, CASE, **kw)
            buf = io.StringIO()
            code = None
            try:
                with contextlib.redirect_stdout(buf):
                    code = run_case(tmp, CASE, F, AGE, LOG, status, rc_policy)
            except SystemExit as e:
                code = e.code
            marker = os.path.exists(os.path.join(tmp, "DONE.%s" % CASE))
            ok = (code == want_rc and marker == want_marker)
            print("  [%s] %-62s -> exit %s, DONE %s"
                  % ("ok " if ok else "FAIL", label, code, marker))
            if not ok:
                fails.append(label)
                print(buf.getvalue())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # CLEAN control first (a clause never shown able to stay quiet flags all).
    drive("CLEAN clobbered-STATUS adaptive case -> DONE (rc DERIVED)", EXIT_OK, True)
    # clause-by-clause planted defects
    drive("clause1: FOAM FATAL in log -> rc NOT derivable -> NOT DONE",
          EXIT_NOTDONE, False, break_clause="clause1fatal")
    drive("clause2: no End line -> NOT DONE", EXIT_NOTDONE, False, break_clause="clause2")
    drive("clause2: two End lines -> NOT DONE", EXIT_NOTDONE, False, break_clause="clause2b")
    drive("clause3: last time != endTime -> NOT DONE", EXIT_NOTDONE, False, break_clause="clause3")
    drive("clause4: a registered field missing -> NOT DONE", EXIT_NOTDONE, False, break_clause="clause4")
    drive("clause5: n_exec != n_time (log truncation) -> NOT DONE", EXIT_NOTDONE, False, break_clause="clause5")
    drive("clause6: fields OLDER than 0/T (age guard) -> NOT DONE", EXIT_NOTDONE, False, break_clause="clause6")
    # rc-policy 'read' path, both directions
    drive("rc_policy=read, STATUS rc=0 -> DONE", EXIT_OK, True,
          rc_policy="read", launcher_only=False)
    drive("rc_policy=read, STATUS rc=1 -> NOT DONE (CRASH)", EXIT_NOTDONE, False,
          rc_policy="read", launcher_only=False, break_clause="clause1read")

    # THE FAIL-CLOSED REFUSAL: a NON-adaptive case must REFUSE (exit 2), never
    # be silently accepted and never fall back to the fixed-deltaT count.
    tmp = tempfile.mkdtemp(prefix="adapt_md_")
    try:
        _synthetic(tmp, CASE, adjust=False)
        buf = io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(buf):
                code = run_case(tmp, CASE, F, AGE, LOG, "STATUS.%s" % CASE, "derive")
        except SystemExit as e:
            code = e.code
        ok = (code == EXIT_REFUSE and "adjustTimeStep" in buf.getvalue())
        print("  [%s] FAIL-CLOSED: non-adjustTimeStep case -> REFUSE (exit 2)"
              % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("fail-closed-refusal")
            print(buf.getvalue())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # absent STATUS -> REFUSE (never inferred from an End line, K0d L1)
    tmp = tempfile.mkdtemp(prefix="adapt_md_")
    try:
        _synthetic(tmp, CASE)
        os.remove(os.path.join(tmp, CASE, "STATUS.%s" % CASE))
        buf = io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(buf):
                code = run_case(tmp, CASE, F, AGE, LOG, "STATUS.%s" % CASE, "derive")
        except SystemExit as e:
            code = e.code
        ok = (code == EXIT_REFUSE and "no STATUS" in buf.getvalue())
        print("  [%s] absent STATUS -> REFUSE (exit 2), never inferred"
              % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("absent-status-refusal")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # clause 7 (launch guard), both directions
    tmp = tempfile.mkdtemp(prefix="adapt_md_")
    try:
        gd = os.path.join(tmp, "g", "system")
        os.makedirs(gd, exist_ok=True)
        ok = not launch_guard(tmp, "g")
        print("  [%s] clause 7 stays quiet: no 0, no time dir" % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("guard-quiet")
        os.makedirs(os.path.join(tmp, "g", "0"), exist_ok=True)
        ok = bool(launch_guard(tmp, "g"))
        print("  [%s] clause 7 FIRES: 0 already exists" % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("guard-fires-0")
        os.makedirs(os.path.join(tmp, "g", "40"), exist_ok=True)
        ok = any("numeric time" in r for r in launch_guard(tmp, "g"))
        print("  [%s] clause 7 FIRES: a numeric time dir exists" % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("guard-fires-time")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # no `assert` in the module body (L-332), asserted rather than asserted-about
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (planted control: %d)"
          % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")

    print()
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    for f in fails:
        print("   - " + f)
    return EXIT_OK if not fails else EXIT_NOTDONE


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--case", default=None)
    ap.add_argument("--preset", choices=sorted(PRESETS), default=None)
    ap.add_argument("--fields", default=None, help="space-separated field list")
    ap.add_argument("--age-ref", default="0/T", help="path under case dir, '/'-joined")
    ap.add_argument("--log", default="log.solve")
    ap.add_argument("--status", default=None, help="STATUS file name in the case dir")
    ap.add_argument("--rc-policy", choices=("derive", "read"), default="derive")
    ap.add_argument("--launch-guard", metavar="CASE", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root

    if a.preset:
        p = PRESETS[a.preset]
        root = os.path.abspath(a.root) if a.root else os.path.join(here, p["default_root"])
        if a.launch_guard:
            bad = launch_guard(root, a.launch_guard)
            if bad:
                print("LAUNCH REFUSED for %s (clause 7):" % a.launch_guard)
                for r in bad:
                    print("   - " + r)
                return EXIT_REFUSE
            print("launch guard clear for %s" % a.launch_guard)
            return EXIT_OK
        return run_case(root, p["case"], p["fields"], p["age_ref"],
                        p["log_name"], p["status_name"], p["rc_policy"])

    if a.root is None:
        refuse("--root is required (or use --preset); this script does not guess "
               "where the run directory is.")
    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        refuse("no such run directory: %s" % root)

    if a.launch_guard:
        bad = launch_guard(root, a.launch_guard)
        if bad:
            print("LAUNCH REFUSED for %s (clause 7):" % a.launch_guard)
            for r in bad:
                print("   - " + r)
            return EXIT_REFUSE
        print("launch guard clear for %s" % a.launch_guard)
        return EXIT_OK

    if not a.case:
        refuse("--case is required when no --preset is given")
    fields = tuple(a.fields.split()) if a.fields else THERMAL_FIELDS
    status = a.status
    if status is None:
        refuse("--status is required: the run's own record file name is not guessed")
    age_ref = tuple(a.age_ref.split("/"))
    return run_case(root, a.case, fields, age_ref, a.log, status, a.rc_policy)


if __name__ == "__main__":
    sys.exit(main())
