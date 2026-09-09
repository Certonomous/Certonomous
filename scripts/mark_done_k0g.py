#!/usr/bin/env python3
"""K0d completion certification -- the strict completion rule, in full.

Written 2026-08-25 from the FROZEN registration and from nothing else:
  docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION.md   (v1.1, blob 36b302f1)
  docs/campaigns/F14-cooling-ladder/K0d_PREREGISTRATION.md  (v1.5, blob e629f5c4, superseded but adopted by citation)

A case is DONE only if ALL SEVEN registered clauses hold (re-registration
section 7.2; superseded section 8.2 quoting T1b_L4_AMENDMENT.md section 7):

  1. STATUS.<case> exists and reports rc=0
  2. an "End" line in log.solve
  3. last written time == controlDict endTime
  4. the REGISTERED COMPLETION FIELD SET OF THE CASE'S OWN CLOSURE, all present
     at endTime -- PER CLOSURE, never a single tuple (see PER_CLOSURE_FIELDS)
  5. the ExecutionTime line count == the "Time =" line count (the ADAPTIVE-
     deltaT form of standing rule 4 clause 5, "n_exec == steps written", Sanaa
     2026-09-09 -- an internal-consistency check, NOT the count == endTime steady
     instantiation, which K0g's adjustable time step does not satisfy; see the
     clause-5 code comment)
  6. every field at endTime is NEWER than the case's own 0/T -- THE AGE GUARD,
     because 0/T is touched LAST at launch and so dates the run that was
     allowed to produce the answer (D438, L-143)
  7. the LAUNCH guard refuses a case in which 0 or any numeric time directory
     already exists.  Clause 7 is a PRE-launch condition, so it cannot be
     re-checked after a run; it is exposed as --launch-guard for the launcher
     to call BEFORE it starts a solver, and this file is the only place the
     rule is written down.

REFUSAL, NOT INFERENCE (re-registration section 7.2, final paragraph, binding on
the script author): "no exemption and no field substitution may be inferred at
grading time.  A case whose closure does not appear above has no registered
completion field set, and mark_done_k0g.py REFUSES (exit 2) rather than infer
one."  CLOSURE_OF_CASE below is the registered map and it is not extended by
this script under any circumstance.

This script NEVER retracts a marker for a plain (unextended) case: an existing
DONE.<case> is left alone.  For an EXTENDED case a failing extension has its
stale marker REMOVED with the reasons printed, which the registration requires
explicitly.

Exit codes:  0 all requested cases DONE
             1 at least one case is NOT DONE (the reasons are printed)
             2 REFUSAL -- an unregistered closure, or a structural precondition
               that means the question cannot be asked

Usage:
    python3 mark_done_k0g.py --root <K0g_runs dir> [case ...]
    python3 mark_done_k0g.py --root <dir> --launch-guard <case>
    python3 mark_done_k0g.py --selftest
"""
import argparse
import os
import re
import shutil
import sys
import tempfile

EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2

# --------------------------------------------------------------------------
# REGISTERED CONSTANTS.  Every one carries the clause that fixes it.  Nothing
# in this block is a choice made by this script.
# --------------------------------------------------------------------------

# K0g pre-registration section 5: FIVE authorised arms (L1+L2, two turbulent
# closures, plus C_lam the discrimination control).  L3 and the guard/sweep arms
# (B_hi, I_hi, M1_m_seed) are DEFINED-AND-NOT-AUTHORISED and are absent here.
CASES = ["M1_c", "M1_m", "M2_c", "M2_m", "C_lam"]

# K0g pre-registration section 5 (closures carried unchanged from K0f).
CLOSURE_OF_CASE = {
    "M1_c": "kOmegaSST", "M1_m": "kOmegaSST",
    "M2_c": "RNGkEpsilon", "M2_m": "RNGkEpsilon",
    "C_lam": "laminar",
}

# K0g pre-registration section 7.2, the TRANSIENT completion field set table.
# The per-closure sets are carried BYTE-FOR-BYTE from K0f's section 7.2, and
# TMean and UMean are ADDED: they are the fieldAverage outputs (avg2, the
# [40,60] s window) that K0g actually grades, so a run without them at endTime is
# not complete.  Like phi they are SOLVER-GENERATED and are never staged in 0/
# (build_k0g.py's preflight excludes them); they must be PRESENT at endTime.
PER_CLOSURE_FIELDS = {
    "kOmegaSST":   ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi",
                    "TMean", "UMean"),
    "RNGkEpsilon": ("T", "U", "p_rgh", "alphat", "nut", "k", "epsilon", "phi",
                    "TMean", "UMean"),
    "laminar":     ("T", "U", "p_rgh", "alphat", "phi", "TMean", "UMean"),
}

# K0g pre-registration section 7.1'/7.1''.  TRANSIENT: endTime is a PHYSICAL
# TIME in seconds, and the one registered extension carries it 60 -> 120 s.
REGISTERED_END_TIME = 60.0
REGISTERED_EXTENSION = 60             # one extension 60->120 s, a second is NOT authorised


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def registered_fields(case):
    """The completion field set of this case's own closure, or a REFUSAL.

    This function is the single point at which clause 4 is applied.  It does
    not fall back, does not substitute and does not infer."""
    closure = CLOSURE_OF_CASE.get(case)
    if closure is None:
        refuse(f"case {case!r} is not a registered K0d case; the registered ten "
               f"are {', '.join(CASES)}.  A case with no registered closure has "
               f"no registered completion field set (re-registration 7.2).")
    fields = PER_CLOSURE_FIELDS.get(closure)
    if fields is None:
        refuse(f"closure {closure!r} of case {case!r} has NO REGISTERED "
               f"COMPLETION FIELD SET.  Refusing rather than inferring one "
               f"(re-registration 7.2, binding on the script author).")
    return closure, fields


# --------------------------------------------------------------------------
# disk readers
# --------------------------------------------------------------------------
def field_path(tdir, field):
    """Return the path of `field` inside `tdir`, accepting the compressed form.

    writeCompression is UNREGISTERED (superseded AMENDMENT 5 section A5.13
    FINDING 14), which decides whether the completion reader must find T or
    T.gz.  Accepting EITHER is not a choice of the unregistered setting -- it
    reads the registered clause ("every field present"), which names fields and
    not filenames, under both possible settings.  It is recorded here so the
    reader is not later thought to have assumed one."""
    plain = os.path.join(tdir, field)
    if os.path.isfile(plain):
        return plain
    gz = os.path.join(tdir, field + ".gz")
    if os.path.isfile(gz):
        return gz
    return None


def numeric_times(d):
    return sorted((x for x in os.listdir(d)
                   if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)


def control_end_time(d):
    p = os.path.join(d, "system", "controlDict")
    if not os.path.isfile(p):
        return None
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", open(p).read(), re.M)
    return float(m.group(1)) if m else None


def status_rc(path):
    """The pool STATUS format: 'rc= wall= checkMesh_rc='."""
    if not os.path.isfile(path):
        return None, "no STATUS file (case never finished)"
    s = open(path, errors="replace").read()
    m = re.search(r"\brc=(\d+)", s)
    if not m:
        return None, f"STATUS is {s.strip()!r}, which states no rc"
    return int(m.group(1)), s.strip()


# --------------------------------------------------------------------------
# clause 7 -- the LAUNCH guard, which must be called BEFORE a solver starts
# --------------------------------------------------------------------------
def launch_guard(root, case):
    """Clause 7: refuse a case in which 0 or any numeric time directory already
    exists, so a stray write from an earlier process can neither be overwritten
    nor certified.  Returns a list of reasons to REFUSE the launch; empty means
    the launch may proceed."""
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return [f"no case directory {d}"]
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
def check(root, case):
    """Return (fails, info).  fails empty == every registered clause holds."""
    closure, need = registered_fields(case)          # may REFUSE (exit 2)
    info = dict(case=case, closure=closure, fields=need)
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return ["no case directory"], info
    fails = []

    # --- clause 1 -------------------------------------------------------
    # AN ABSENT `STATUS` IS A REFUSAL, NOT A VERDICT (K0g section R6).
    #
    # At K0d commit bf7e9428 this clause was the ONLY one of seven that failed
    # on `M1_c` and `M2_c`: End line, last time == endTime, every registered
    # field present for the case's own closure, full ExecutionTime count and
    # the age guard ALL passed, and the two cases are ungradeable anyway
    # because the launcher never captured an rc.  The log's End line is what
    # `rc=0` normally accompanies -- and that is an INFERENCE, not the
    # measurement the clause requires.  Writing `rc=0` from it would be
    # back-dating a measurement nobody took.
    #
    # So this is marked as a REFUSAL and carried out of `main()` as exit 2,
    # DISTINCT from exit 1 "this case is not done".  The distinction is the
    # point: NOT DONE is a fact about the case; a missing rc means the
    # INSTRUMENT CANNOT EVALUATE THE CLAUSE AT ALL, and under a detached queue
    # with nobody watching, the two must not read alike.
    rc, note = status_rc(os.path.join(root, f"STATUS.{case}"))
    if rc is None:
        info["status_absent"] = True
        return [note], info
    if rc != 0:
        fails.append(f"STATUS is {note!r}, not rc=0")

    # --- extension detection (re-registration 7.1: ONE extension registered)
    ext_status = os.path.join(root, f"STATUS.{case}.ext1")
    ext_log = os.path.join(d, "log.solve.ext1")
    extended = os.path.isfile(ext_status) or os.path.isfile(ext_log)
    info["extended"] = extended
    if os.path.isfile(os.path.join(root, f"STATUS.{case}.ext2")):
        fails.append("a SECOND extension is present; one extension of "
                     f"+{REGISTERED_EXTENSION} is registered and a second is not "
                     "authorised (re-registration 7.1)")

    # --- clause 2 -------------------------------------------------------
    logs = [os.path.join(d, "log.solve")]
    if extended:
        logs.append(ext_log)
        erc, enote = status_rc(ext_status)
        if erc is None:
            fails.append("extended case: " + enote)
        elif erc != 0:
            fails.append(f"extension STATUS is {enote!r}, not rc=0")
    n_exec = 0
    n_time = 0
    first_ext_time = None
    for i, log in enumerate(logs):
        if not os.path.isfile(log):
            fails.append(f"no {os.path.basename(log)}")
            continue
        body = open(log, errors="replace").read()
        if not re.search(r"^End\s*$", body, re.M):
            fails.append(f"{os.path.basename(log)} has no End line")
        n_exec += len(re.findall(r"^ExecutionTime", body, re.M))
        n_time += len(re.findall(r"^Time = ", body, re.M))
        if i == 1:
            m = re.search(r"^Time = ([0-9.eE+-]+)", body, re.M)
            if m:
                first_ext_time = float(m.group(1))
    info["n_exec"] = n_exec
    info["n_time"] = n_time

    # --- clause 3 -------------------------------------------------------
    et = control_end_time(d)
    if et is None:
        return fails + ["no system/controlDict, so endTime cannot be read"], info
    expected_end = et + (REGISTERED_EXTENSION if extended else 0)
    info["endTime"] = et
    info["expected_end"] = expected_end
    times = [float(t) for t in numeric_times(d)]
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        fails.append("no time directory beyond 0")
        return fails, info
    last = nonzero[-1]
    info["last_time"] = last
    if abs(last - expected_end) > 1e-9:
        fails.append(f"last written time {last:g} != endTime {expected_end:g}")

    # --- clause 5 -- TRANSIENT ADAPTATION OF STANDING RULE 4, FLAGGED --------
    # STANDING RULE 4's clause 5 reads "ExecutionTime count == endTime".  That
    # is the deltaT=1 STEADY instantiation (K0f ran 40 000 SIMPLE iterations at
    # deltaT 1, so #steps == endTime).  K0g is TRANSIENT with an ADJUSTABLE
    # time step (maxCo 2.0), so #steps is NOT endTime and the K0f clause cannot
    # transfer.  The transient-appropriate check is INTERNAL CONSISTENCY: the
    # solver logs one "Time = " line and one "ExecutionTime" line per step, so
    # their counts must be EQUAL and non-zero.  This adaptive form -- "adaptive-
    # deltaT runs use n_exec == steps written" -- is now CLAUDE.md STANDING RULE 4
    # clause 5 (Sanaa 2026-09-09), NO LONGER a lane proposal awaiting sign-off.
    # It is the IDENTICAL logic the verification supervisor audited in
    # mark_done_adaptive.py (@ 2ae36a1d), and it carries the heat-transfer
    # supervisor's explicit sign-off.  Because that audit (V-143) covered
    # mark_done_adaptive.py rather than THIS instrument, verification's explicit
    # confirmation for mark_done_k0g is being routed via the chief and is the
    # LAST GATE before this instrument is frozen.  Completion evidence for a
    # transient run rests on clause 3 (last time == endTime) and clause 6 (the
    # age guard); clause 5 here guards against a truncated/duplicated log.
    if n_exec < 1 or n_time < 1:
        fails.append(f"no time steps logged (ExecutionTime={n_exec}, "
                     f"Time-lines={n_time})")
    elif n_exec != n_time:
        fails.append(f"{n_exec} ExecutionTime lines != {n_time} 'Time =' lines "
                     f"(a truncated or duplicated solver log)")
    if extended and first_ext_time is not None and first_ext_time <= et:
        fails.append(f"first extension Time is {first_ext_time:g}, which is not "
                     f"AFTER the base endTime {et:g} (a restart must resume past "
                     f"it)")

    # --- clause 4 -------------------------------------------------------
    tdir = os.path.join(d, f"{last:g}")
    present = {f: field_path(tdir, f) for f in need}
    miss = [f for f in need if present[f] is None]
    if miss:
        fails.append(f"time {last:g} is missing {','.join(miss)} "
                     f"(registered {closure} set: {' '.join(need)})")

    # --- clause 6 -- THE AGE GUARD --------------------------------------
    t0 = field_path(os.path.join(d, "0"), "T")
    if t0 is None:
        fails.append("no 0/T, so the run's start cannot be dated and the age "
                     "guard cannot be applied")
    elif not miss:
        age0 = os.path.getmtime(t0)
        stale = [f for f in need if os.path.getmtime(present[f]) < age0]
        if stale:
            fails.append("time %g holds fields OLDER than 0/T (%s) -- not "
                         "written by this run (D438, L-143)"
                         % (last, ",".join(stale)))
        if extended:
            st = os.path.join(root, f"STATUS.{case}")
            if os.path.isfile(st):
                age_s = os.path.getmtime(st)
                stale2 = [f for f in need
                          if os.path.getmtime(present[f]) < age_s]
                if stale2:
                    fails.append("extended case: time %g holds fields older "
                                 "than STATUS.%s (%s)"
                                 % (last, case, ",".join(stale2)))
    return fails, info


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None,
                    help="the K0g_runs directory holding the case directories")
    ap.add_argument("--launch-guard", metavar="CASE", default=None,
                    help="apply clause 7 BEFORE launching CASE and exit")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("cases", nargs="*")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    if a.root is None:
        refuse("--root is required: this script does not guess where the run "
               "directory is.")
    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        refuse(f"no such run directory: {root}")

    if a.launch_guard:
        bad = launch_guard(root, a.launch_guard)
        if bad:
            print(f"LAUNCH REFUSED for {a.launch_guard} (clause 7):")
            for r in bad:
                print("   - " + r)
            return EXIT_REFUSE
        print(f"launch guard clear for {a.launch_guard}: no 0 and no numeric "
              f"time directory exists")
        return EXIT_OK

    cases = a.cases or CASES
    ok, bad, absent = [], {}, []
    for c in cases:
        fails, inf = check(root, c)
        if inf.get("status_absent"):
            absent.append(c)
        (ok.append(c) if not fails else bad.setdefault(c, fails))
    for c in ok:
        marker = os.path.join(root, f"DONE.{c}")
        if not os.path.exists(marker):
            open(marker, "w").write("strict completion rule met (all seven "
                                    "clauses, re-registration 7.2)\n")
    # a FAILING EXTENDED case has any stale marker REMOVED, with reasons printed
    for c in bad:
        marker = os.path.join(root, f"DONE.{c}")
        _, info = check(root, c)
        if info.get("extended") and os.path.exists(marker):
            os.remove(marker)
            print(f"  REMOVED stale DONE.{c} (extended case now fails)")
    print(f"{len(ok)}/{len(cases)} cases meet the strict completion rule")
    for c in sorted(bad):
        print(f"  NOT DONE  {c}")
        for r in bad[c]:
            print(f"            - {r}")
    # EVERY case is reported first, THEN the refusal is raised: refusing on the
    # first missing STATUS would hide the state of the other nine, and a
    # refusal that destroys the report it was about to make is a worse
    # instrument than the one it replaced.
    if absent:
        print()
        print("REFUSE: no STATUS file for " + ", ".join(sorted(absent)) + ".")
        print("  A missing rc is NOT a passing rc.  The completion rule is "
              "all-or-nothing precisely so that it cannot be satisfied by a "
              "plausible reconstruction, and this instrument INFERS NOTHING: "
              "it reports that it cannot evaluate clause 1 and stops.")
        print("  This is exit 2 (REFUSAL), not exit 1 (NOT DONE).")
        return EXIT_REFUSE
    return EXIT_OK if not bad else EXIT_NOTDONE


# --------------------------------------------------------------------------
# selftest -- planted controls.  Every clause is shown able to FIRE on a
# planted defect and able to STAY QUIET on the clean counterpart.  A clause
# never shown able to fire is not evidence (standing rule 3).
# --------------------------------------------------------------------------
def _synthetic(root, case, endtime=60, fields=None, break_clause=None,
               gzip_fields=False, n_steps=100):
    """Build a minimal on-disk TRANSIENT case that satisfies every clause, then
    break exactly one.  Times/paths are built numerically from `endtime`, never
    from a shared format constant (L-321).  The log carries one 'Time = ' line
    and one 'ExecutionTime' line PER STEP -- clause 5's transient form checks
    their EQUALITY, not a count against endTime (an adjustable-dt run has no
    fixed step count)."""
    import time as _time
    closure, need = registered_fields(case)
    fields = fields if fields is not None else need
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write(
        f"endTime {endtime};\ndeltaT 0.001;\nwriteInterval 20;\npurgeWrite 0;\n")
    z = os.path.join(d, "0")
    os.makedirs(z, exist_ok=True)
    open(os.path.join(z, "T"), "w").write("0/T\n")
    _time.sleep(0.02)
    last = endtime if break_clause != "clause3" else endtime - 20
    tdir = os.path.join(d, str(int(last)))
    os.makedirs(tdir, exist_ok=True)
    emit = [f for f in fields if not (break_clause == "clause4" and f == fields[-1])]
    for f in emit:
        if gzip_fields:
            # The `.gz` branch is exercised even though K0g registers
            # writeCompression off: a branch kept alive in code and dead in test
            # is believed the first time it is used, and `field_path` accepts
            # either form deliberately.
            import gzip as _gzip
            with _gzip.open(os.path.join(tdir, f + ".gz"), "wt") as fh:
                fh.write(f"{f} at {last}\n")
        else:
            open(os.path.join(tdir, f), "w").write(f"{f} at {last}\n")
    if break_clause == "clause6":
        old = os.path.getmtime(os.path.join(z, "T")) - 100
        for f in emit:
            os.utime(os.path.join(tdir, f + (".gz" if gzip_fields else "")),
                     (old, old))
    # one Time line and one ExecutionTime line per step; clause5 breaks equality
    body = "".join("Time = %g\nExecutionTime = %d s\n" % (0.001 * i, i)
                   for i in range(1, n_steps + 1))
    if break_clause == "clause5":
        body += "ExecutionTime = 999 s\n"          # one extra: n_exec != n_time
    if break_clause != "clause2":
        body += "End\n"
    open(os.path.join(d, "log.solve"), "w").write(body)
    rc = 0 if break_clause != "clause1" else 1
    open(os.path.join(root, f"STATUS.{case}"), "w").write(
        f"rc={rc} wall=1.0 checkMesh_rc=0\n")
    return d


def selftest():
    print("=" * 74)
    print("mark_done_k0g.py -- SELFTEST (planted controls)")
    print("=" * 74)
    fails = []

    def check_(label, cond, detail=""):
        print(f"  {'OK  ' if cond else 'FAIL'}  {label}"
              + (f"   [{detail}]" if detail else ""))
        if not cond:
            fails.append(label)

    tmp = tempfile.mkdtemp(prefix="k0d_md_")
    try:
        # the CLEAN control first: a clause never shown able to stay quiet
        # flags everything.
        _synthetic(tmp, "M1_m", break_clause=None)
        f, _ = check(tmp, "M1_m")
        check_("clean case satisfies all seven clauses", not f, str(f))

        for clause, label in (("clause1", "rc != 0"),
                              ("clause2", "no End line"),
                              ("clause3", "last time != endTime"),
                              ("clause4", "a registered field missing"),
                              ("clause5", "ExecutionTime count != Time-line count"),
                              ("clause6", "fields OLDER than 0/T (age guard)")):
            case = "M1_c"
            shutil.rmtree(os.path.join(tmp, case), ignore_errors=True)
            _synthetic(tmp, case, break_clause=clause)
            f, _ = check(tmp, case)
            check_(f"{clause} FIRES on a planted defect: {label}", bool(f),
                   "; ".join(f)[:90])

        # clause 4 is PER CLOSURE.  The kOmegaSST tuple must NOT be applied to
        # the RNGkEpsilon or laminar cases -- that is the exact defect the
        # per-closure table was written to remove.
        _synthetic(tmp, "M2_m", break_clause=None)
        f, info = check(tmp, "M2_m")
        check_("RNGkEpsilon case passes on ITS OWN set (has epsilon, no omega)",
               not f and "epsilon" in info["fields"] and "omega" not in info["fields"],
               str(info["fields"]))
        _synthetic(tmp, "C_lam", break_clause=None)
        f, info = check(tmp, "C_lam")
        check_("laminar case passes on ITS OWN 7-field set (no k/omega/nut; "
               "has TMean/UMean)",
               not f and len(info["fields"]) == 7
               and not ({"k", "omega", "nut"} & set(info["fields"]))
               and {"TMean", "UMean"} <= set(info["fields"]), str(info["fields"]))

        # every graded arm's completion set names the fieldAverage outputs
        check_("every closure's completion set names TMean and UMean (the "
               "avg2 [40,60] fields K0g grades)",
               all({"TMean", "UMean"} <= set(v)
                   for v in PER_CLOSURE_FIELDS.values()))
        # the field-presence assertion count, asserted rather than asserted-about
        n = sum(len(PER_CLOSURE_FIELDS[CLOSURE_OF_CASE[c]]) for c in CASES)
        check_("47 field-presence assertions over the five arms "
               "(2*10 kOmegaSST + 2*10 RNGkEpsilon + 1*7 laminar)", n == 47, str(n))
        check_("FIVE authorised arms (L1+L2 + C_lam control), not ten",
               len(CASES) == 5, str(len(CASES)))

        # clause 7, both directions (launch_guard checks only dirs, no closure)
        d = os.path.join(tmp, "guardcase")
        os.makedirs(os.path.join(d, "system"), exist_ok=True)
        check_("clause 7 stays quiet on a case with no 0 and no time dir",
               not launch_guard(tmp, "guardcase"))
        os.makedirs(os.path.join(d, "0"), exist_ok=True)
        check_("clause 7 FIRES when 0 already exists",
               bool(launch_guard(tmp, "guardcase")))
        os.makedirs(os.path.join(d, "8000"), exist_ok=True)
        check_("clause 7 FIRES when a numeric time dir already exists",
               any("numeric time" in r for r in launch_guard(tmp, "guardcase")))

        # --- THE TWO REGISTERED `.gz` ARMS (AMENDMENT 2 section A2.1c) ---
        # Registered as REQUIRED, not optional, on a rung whose registration
        # FORBIDS compression.  `field_path` accepts `T` or `T.gz`; that second
        # branch had never been executed by any selftest in this family --
        # eleven legacy mark_done_*.py scripts carry no `.gz` handling at all
        # and fail safe only by coincidence.  Failing safe by coincidence is
        # not the same as being correct.
        shutil.rmtree(os.path.join(tmp, "M2_c"), ignore_errors=True)
        _synthetic(tmp, "M2_c", break_clause=None, gzip_fields=True)
        f, _ = check(tmp, "M2_c")
        check_("GZIPPED clean case still satisfies all seven clauses",
               not f, str(f))
        shutil.rmtree(os.path.join(tmp, "C_lam"), ignore_errors=True)
        _synthetic(tmp, "C_lam", break_clause="clause6", gzip_fields=True)
        f, _ = check(tmp, "C_lam")
        check_("GZIPPED stale case: the AGE GUARD still FIRES",
               any("older" in r or "newer" in r or "0/T" in r for r in f),
               str(f))

        # the REFUSAL, exercised in a subprocess so exit 2 can be observed
        import subprocess
        r = subprocess.run([sys.executable, os.path.abspath(__file__),
                            "--root", tmp, "NOT_A_REGISTERED_CASE"],
                           capture_output=True, text=True)
        check_("REFUSES (exit 2) on a case with no registered closure",
               r.returncode == EXIT_REFUSE, f"rc={r.returncode}")

        # THE bf7e9428 CONFIGURATION, DRIVEN: six clauses pass and the STATUS
        # file is absent.  It must be exit 2 (REFUSAL), never exit 1
        # (NOT DONE) and above all never exit 0.
        _synthetic(tmp, "M2_m", break_clause=None)
        os.remove(os.path.join(tmp, "STATUS.M2_m"))
        r2 = subprocess.run([sys.executable, os.path.abspath(__file__),
                             "--root", tmp, "M2_m"],
                            capture_output=True, text=True)
        check_("REFUSES (exit 2) on an ABSENT STATUS, never infers rc=0",
               r2.returncode == EXIT_REFUSE and "no STATUS file" in r2.stdout,
               f"rc={r2.returncode}")
        # and the CLEAN counterpart of that same arm must NOT refuse
        r3 = subprocess.run([sys.executable, os.path.abspath(__file__),
                             "--root", tmp, "M1_m"],
                            capture_output=True, text=True)
        check_("...and STAYS QUIET when STATUS is present and reports rc=0",
               r3.returncode == EXIT_OK, f"rc={r3.returncode}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s) did not hold")
        for f in fails:
            print("   - " + f)
        return EXIT_NOTDONE
    print("SELFTEST PASSED: every clause was shown able to FIRE on a planted")
    print("defect and able to STAY QUIET on its clean counterpart.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
