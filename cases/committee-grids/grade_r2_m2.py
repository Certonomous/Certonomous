#!/usr/bin/env python3
"""
R2-M2 COMPARATOR -- the grading path for
`verification/campaign/RUNG2_CRM_M2_PREREGISTRATION.md`.

THIS FILE IS THE GRADING PATH. Rule 2: it is fixed at the pre-registration commit and the
driver verifies at run time that the file that ran IS the committed blob. It does NOT import
`grade_r2_m1.py` or `grade_r2_m0.py` -- those are frozen (rule 6) and are left exactly as
they are. It reuses M1's proven CONTROL STRUCTURE conceptually, not by import.

WHY M2 EXISTS, AND THE ONE CONTROL M1's COMPARATOR NEVER HAD
-----------------------------------------------------------
R2-M1's admission gate came back GATE FAIL not on the physics but on the RECORDING: B1
iterated CLEAN to Time = 50 (rc = 0, End line) -- the first compressible arm carried past
iteration 2 on this grid -- yet wrote NO field snapshot at endTime, because the driver
rewrote endTime alone and left writeInterval 120 > 50 steps under purgeWrite 1. Every
rule-4 field-at-endTime clause then failed on an ABSENCE.

M1's comparator could not have caught the absence with a live control, because none of M1's
arms ever wrote an endTime snapshot to read -- there was no non-zero for the reader to be
shown able to see. M2's whole reason for existing is to carry THE FIELD-AT-ENDTIME PLANT
(C12/C13): a reader shown able to see an endTime field snapshot AND to report its absence,
driven in the refusing direction on M1's REAL B1 arm (which reached endTime and wrote none).
That control speaks directly to the exact zero M1's GATE FAIL turned on.

THE GATES (registration section 7)
  R2M2-G0  reproduction control (B0). A PRECONDITION -- if it fails, nothing else stands.
  R2M2-G1  writer liveness, per launched arm (records == steps, exactly, per field).
  R2M2-G2  the warm start MAPS AND EXERCISES -> PASS, else BLOCKED (never GATE FAIL).
  R2M2-G3  ADMISSION -- the only admission gate, and THE ITEM VERDICT. B1 reaches endTime
           STRICTLY COMPLETE under all six clauses of rule 4. BLOCKED if G2 is BLOCKED.
  R2M2-G4  the planted controls fire AND the section-5 rehearsal DISCRIMINATES.

R2M2-G0 and R2M2-G4 can only turn a PASS or GATE FAIL INTO NOT A RESULT, never the reverse
(rule 5's ordering applied to a gate table).

EXIT CODES
  0  graded; the verdict is in the STATUS file (a GATE FAIL is still exit 0)
  2  REFUSED -- a planted control did not fire, or a fact needed for a verdict is absent
"""

import ast
import os
import re
import sys
import tempfile

# ---------------------------------------------------------------------------
# Registered constants. Changing any of these changes a gate and is a rule-2 event.
# ---------------------------------------------------------------------------

# The two REAL archived logs from the 2026-08-01 committee-grid numerics probe: same grid,
# same box, same day, one aborting and one clean. Positive and negative control (as M1).
CONTROL_ABORT_LOG = (
    "/home/ubuntu/certonomous-runs/dpw5-committee-probe/logs/"
    "hex_base_compressible_a2.11_solve.log"
)
CONTROL_CLEAN_LOG = (
    "/home/ubuntu/certonomous-runs/dpw5-committee-probe/logs/"
    "hex_base_incompressible_a2.11_solve.log"
)

# M1's REAL, graded B1 arm. It reached Time = 50 (rc = 0, End line) and wrote NO endTime
# snapshot -- verified at source 2026-09-06: B1/processor0/ holds only 0 and constant, and
# no serial 50/ exists. It is the negative case for the field-at-endTime plant (C13): the
# reader must report the endTime snapshot ABSENT on the exact real data whose absence was
# M1's GATE FAIL. Treated as a required archived control (as M1 requires its control logs);
# an absent path is REFUSED, never silently passed.
REAL_B1_ARM = (
    "/home/ubuntu/Certonomous/verification/runs/RUNG2_CRM_runs/"
    "M1_mechanism_and_warmstart/B1"
)

# The section-5 snapshot rehearsal record, which must DISCRIMINATE (registration G4).
REHEARSAL_TSV = (
    "/home/ubuntu/Certonomous/cases/committee-grids/R2_M2_SNAPSHOT_REHEARSAL.tsv"
)

THERMO_FRAME = "libfluidThermophysicalModels.so"
SIGFPE_MARK = "Floating point exception (8)"
REPRODUCTION_ABORT_TIME = 2       # R2M2-G0: B0 must abort at Time <= this
ADMISSION_ENDTIME = 50            # R2M2-G3: B1's admission bar
MINMAX_FIELDS = ("T", "p", "rho", "mag(U)")
# The field set present at endTime -- the field list M1's frozen comparator graded.
ENDTIME_FIELDS = ("T", "U", "p", "k", "omega", "nut", "alphat")
FO_NAME = "r2m2MinMax"

ARMS = ("B0", "B1")

RE_TIME = re.compile(r"^Time = ([0-9]+(?:\.[0-9]+)?)\s*$", re.M)
RE_EXECTIME = re.compile(r"^ExecutionTime = ", re.M)
RE_END = re.compile(r"^End\s*$", re.M)
RE_NANINF = re.compile(r"(?i)(?<![A-Za-z0-9_])[-+]?(nan|inf)(?![A-Za-z0-9_])")
RE_INTRASTEP = re.compile(r"^(pressureControl: p min|time step continuity errors)", re.M)


class Refusal(Exception):
    """Raised instead of returning a number this comparator cannot stand behind."""


def refuse(message):
    raise Refusal(message)


# ---------------------------------------------------------------------------
# THE READERS. Pure functions on text/paths, so every control below exercises the
# SAME code path the grade uses. A control on a different function is not a control.
# ---------------------------------------------------------------------------


def read_solve_log(text):
    """Facts only. This function makes no judgement and names no verdict."""
    times = [float(t) for t in RE_TIME.findall(text)]
    return {
        "time_headers": len(times),
        "last_time": times[-1] if times else None,
        "steps_completed": len(RE_EXECTIME.findall(text)),
        "end_line": bool(RE_END.search(text)),
        "sigfpe": text.count(SIGFPE_MARK),
        "thermo_frame": text.count(THERMO_FRAME),
        "nan_inf_tokens": len(RE_NANINF.findall(text)),
        "intrastep_lines": len(RE_INTRASTEP.findall(text)),
    }


def classify_arm_log(facts):
    """ABORTED / COMPLETED / INCOMPLETE. The one place these words are assigned."""
    if facts["sigfpe"] > 0 or facts["thermo_frame"] > 0:
        return "ABORTED"
    if facts["end_line"]:
        return "COMPLETED"
    return "INCOMPLETE"


def read_minmax(dat_path, field):
    """W1: how many DISTINCT times carry a record for `field`. Absent file reads 0.

    Reads 0 for an absent file DELIBERATELY, and the caller must not confuse that zero
    with a satisfied gate -- G1 compares it against steps_completed. Plant-verified C8.
    """
    if not os.path.isfile(dat_path):
        return 0
    times = set()
    with open(dat_path, "r", errors="replace") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1] == field:
                times.add(parts[0])
    return len(times)


def read_intrastep(text):
    """W2: intra-step solver lines. Written DURING a step, so they survive the abort."""
    return len(RE_INTRASTEP.findall(text))


def read_endtime_fields(case_dir, endtime, fields=ENDTIME_FIELDS):
    """THE FIELD-AT-ENDTIME READER -- the control M1's comparator never had.

    Returns the list of registered fields that exist in <case>/<endTime>/. An absent time
    directory, or a present-but-empty one, reads as [] DELIBERATELY: this is the exact
    reader whose zero M1's GATE FAIL turned on, and the caller must not confuse an empty
    list with a satisfied gate. It is plant-verified PRESENT and ABSENT (C12), and driven
    in the refusing direction on M1's real B1 arm (C13). completion_clauses() calls THIS
    function for the field-presence clause, so C12/C13 exercise the grade's own path.
    """
    time_dir = os.path.join(case_dir, _fmt_time(endtime))
    if not os.path.isdir(time_dir):
        return []
    return [f for f in fields if os.path.isfile(os.path.join(time_dir, f))]


def read_rc(arm_dir):
    """rc is captured inside the wrapper. An ABSENT rc is a refusal, never a zero."""
    path = os.path.join(arm_dir, "rc.txt")
    if not os.path.isfile(path):
        refuse("no rc.txt in %s -- an uncaptured rc is not a zero" % arm_dir)
    raw = open(path).read().strip()
    if not re.fullmatch(r"-?[0-9]+", raw):
        refuse("rc.txt in %s is not an integer: %r" % (arm_dir, raw))
    return int(raw)


def check_rc_consistency(rc, facts):
    """An rc=0 beside an aborting log is a lie by one of the two. Refuse, never pick."""
    if rc == 0 and classify_arm_log(facts) == "ABORTED":
        refuse("rc=0 beside a log carrying the abort signature -- irreconcilable")


def rehearsal_discriminates(text):
    """Reader for the section-5 rehearsal record. True iff it declares DISCRIMINATES and
    does not declare the negative. Plant-verified both directions in C14."""
    if "DOES_NOT_DISCRIMINATE" in text:
        return False
    return ("-- DISCRIMINATES" in text) or bool(
        re.search(r"^#.*\bDISCRIMINATES\b\s*$", text, re.M)
    )


def completion_clauses(case_dir, rc, facts, endtime):
    """Rule 4, all six clauses. Returns (bool, list-of-failed-clause-names).

    The field-presence clause goes through read_endtime_fields() -- the same reader the
    field-at-endTime plant drives -- so a passing plant is evidence about THIS path.
    """
    failed = []
    if rc != 0:
        failed.append("rc==0")
    if not facts["end_line"]:
        failed.append("End line")
    if facts["last_time"] is None or float(facts["last_time"]) != float(endtime):
        failed.append("last time == endTime")
    if facts["steps_completed"] != int(endtime):
        failed.append("ExecutionTime count == endTime")

    time_dir = os.path.join(case_dir, _fmt_time(endtime))
    present = read_endtime_fields(case_dir, endtime)
    present_paths = []
    for field in ENDTIME_FIELDS:
        if field in present:
            present_paths.append(os.path.join(time_dir, field))
        else:
            failed.append("field %s at endTime" % field)

    # THE AGE GUARD. `0/T` is touched last at launch (registration section 7 names 0/T as
    # the anchor, as M1's frozen comparator graded), so it dates the run that was allowed to
    # produce this answer. A field older than it is a leftover.
    zero_t = os.path.join(case_dir, "0", "T")
    if not os.path.isfile(zero_t):
        failed.append("age guard: 0/T absent")
    else:
        ref = os.path.getmtime(zero_t)
        for path in present_paths:
            if os.path.getmtime(path) <= ref:
                failed.append("age guard: %s not newer than 0/T" % os.path.basename(path))
    return (not failed), failed


def _fmt_time(value):
    value = float(value)
    return str(int(value)) if value == int(value) else repr(value)


def guard_run_root_absent(path):
    """Rule 4's guard: refuse a root that already holds a 0/ or a time directory."""
    if not os.path.isdir(path):
        return True
    for entry in os.listdir(path):
        if entry == "0" or re.fullmatch(r"[0-9]+(\.[0-9]+)?", entry):
            refuse("run root %s already holds %r -- a pre-existing field is not this run's"
                   % (path, entry))
    return True


def count_assert_nodes(source):
    """L-221/L-222 in the checking direction, done by AST not regex: parse the source and
    count `ast.Assert` nodes. A bare assert vanishes under `python -O`, so a guard built on
    one is not a guard. The AST catches asserts a line-anchored regex would miss (indented,
    multi-target, trailing). Detector planted-and-seen in C0."""
    return sum(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(source)))


def load(path, what):
    if not os.path.isfile(path):
        refuse("%s absent: %s" % (what, path))
    return open(path, "r", errors="replace").read()


# ---------------------------------------------------------------------------
# THE SELFTEST. It runs BEFORE anything is reported and REFUSES (exit 2) rather than
# degrading. Rule 3: a zero from a reader not shown able to see a non-zero is not
# evidence -- so every reader is driven in BOTH directions, and the GATE functions are
# driven in the REFUSING direction too (C10, C11).
# ---------------------------------------------------------------------------


def selftest(own_path):
    results = []

    def record(tag, ok, note):
        results.append((tag, bool(ok), note))

    # C0 -- the assert detector, planted, by AST parse.
    own_source = open(own_path).read()
    real = count_assert_nodes(own_source)
    seen = count_assert_nodes(own_source + "\nassert True\n")
    record("C0", real == 0 and seen == 1,
           "AST parse proves this comparator carries %d assert nodes and the detector sees "
           "a planted one (%d)" % (real, seen))

    # C1/C2 -- the two REAL archived logs, opposite outcomes, same reader.
    abort_facts = read_solve_log(load(CONTROL_ABORT_LOG, "archived ABORT control log"))
    clean_facts = read_solve_log(load(CONTROL_CLEAN_LOG, "archived CLEAN control log"))
    record("C1", classify_arm_log(abort_facts) == "ABORTED"
           and abort_facts["thermo_frame"] > 0
           and abort_facts["last_time"] == REPRODUCTION_ABORT_TIME,
           "archived abort log reads ABORTED at Time = %s, thermo frame seen %d times"
           % (abort_facts["last_time"], abort_facts["thermo_frame"]))
    record("C2", classify_arm_log(clean_facts) == "COMPLETED" and clean_facts["sigfpe"] == 0,
           "archived clean log reads COMPLETED with no abort signature")

    # C3 -- MUTATION: plant the abort signature into the CLEAN log; it must flip.
    mutated = load(CONTROL_CLEAN_LOG, "clean log") + "\n%s\n[0] #5  ? in %s\n" % (
        SIGFPE_MARK, THERMO_FRAME)
    record("C3", classify_arm_log(read_solve_log(mutated)) == "ABORTED",
           "abort signature planted into the clean log flips it to ABORTED")

    # C4 -- the NaN scan, both directions.
    record("C4", read_solve_log("Time = 1\nresidual = nan\n")["nan_inf_tokens"] > 0
           and read_solve_log("Time = 1\nresidual = 0.5\n")["nan_inf_tokens"] == 0,
           "planted nan fires the scan; unplanted stays silent")

    # C5 -- rc=0 beside an aborting log must be REFUSED, not resolved.
    try:
        check_rc_consistency(0, abort_facts)
        refused = False
    except Refusal:
        refused = True
    try:
        check_rc_consistency(0, clean_facts)
        allowed = True
    except Refusal:
        allowed = False
    record("C5", refused and allowed,
           "rc=0 beside a SIGFPE log REFUSED; rc=0 beside a clean log allowed")

    # C6 -- the age guard, both directions.
    record("C6", *_age_guard_control())

    # C7 -- the run-root guard, both directions.
    record("C7", *_root_guard_control())

    # C8 -- W1 (fieldMinMax reader), planted: N -> 0 -> N, on the SAME function G1 uses.
    with tempfile.TemporaryDirectory() as tmp:
        dat = os.path.join(tmp, "fieldMinMax.dat")
        with open(dat, "w") as handle:
            handle.write("# Field minima and maxima\n# Time\tfield\tmin\n")
            for step in (1, 2, 3):
                for field in MINMAX_FIELDS:
                    handle.write("%d\t%s\t0.0\t(0 0 0)\t0\t1.0\t(0 0 0)\t0\n" % (step, field))
        live = [read_minmax(dat, f) for f in MINMAX_FIELDS]
        os.rename(dat, dat + ".hidden")
        gone = [read_minmax(dat, f) for f in MINMAX_FIELDS]
        os.rename(dat + ".hidden", dat)
        back = [read_minmax(dat, f) for f in MINMAX_FIELDS]
    record("C8", live == [3] * 4 and gone == [0] * 4 and back == [3] * 4,
           "W1 reads %s live, %s absent, %s restored -- DISCRIMINATES" % (live, gone, back))

    # C9 -- W2 (intra-step reader), planted: N -> 0 -> N.
    live_text = ("Time = 1\npressureControl: p min -252762.6\n"
                 "time step continuity errors : sum local = 1\nExecutionTime = 1 s\n")
    scrubbed = "\n".join(l for l in live_text.splitlines()
                         if not RE_INTRASTEP.match(l)) + "\n"
    a, b, c = read_intrastep(live_text), read_intrastep(scrubbed), read_intrastep(live_text)
    record("C9", a == 2 and b == 0 and c == 2,
           "W2 reads %d live, %d scrubbed, %d restored -- DISCRIMINATES" % (a, b, c))

    # C10 -- THE WRITER GATE ITSELF, driven in the REFUSING direction.
    good = writer_gate(steps_completed=3, w1={f: 3 for f in MINMAX_FIELDS}, w2=3)
    short = writer_gate(steps_completed=3, w1={f: 1 for f in MINMAX_FIELDS}, w2=3)
    silent = writer_gate(steps_completed=3, w1={f: 0 for f in MINMAX_FIELDS}, w2=0)
    zero = writer_gate(steps_completed=0, w1={f: 0 for f in MINMAX_FIELDS}, w2=0)
    record("C10", good and not short and not silent and zero,
           "writer gate PASSES 3-of-3, FAILS 1-of-3 and 0-of-3, and PASSES a zero-step arm "
           "with zero records")

    # C11 -- THE COMPLETION RULE, driven in the refusing direction on a synthetic case.
    record("C11", *_completion_control())

    # C12 -- THE FIELD-AT-ENDTIME PLANT (synthetic), present -> absent, on the SAME reader
    #        completion_clauses uses. This is the control M1's comparator NEVER HAD.
    record("C12", *_field_at_endtime_control())

    # C13 -- THE FIELD-AT-ENDTIME PLANT ON M1's REAL B1 ARM (the refusing direction on real
    #        data). B1 reached endTime and wrote no snapshot; the reader must report ABSENT.
    record("C13", *_field_at_endtime_real_control())

    # C14 -- the section-5 rehearsal DISCRIMINATES (registration G4), reader planted both
    #        directions, then applied to the real committed record.
    good_txt = "# -- DISCRIMINATES\n# VERDICT: PASS\n"
    bad_txt = "# -- DOES_NOT_DISCRIMINATE\n# VERDICT: FAIL\n"
    reader_ok = rehearsal_discriminates(good_txt) and not rehearsal_discriminates(bad_txt)
    real_txt = load(REHEARSAL_TSV, "section-5 rehearsal record")
    record("C14", reader_ok and rehearsal_discriminates(real_txt),
           "rehearsal reader sees DISCRIMINATES and rejects the negative; the committed "
           "R2_M2_SNAPSHOT_REHEARSAL.tsv DISCRIMINATES")

    return results


def _age_guard_control():
    with tempfile.TemporaryDirectory() as tmp:
        case = os.path.join(tmp, "case")
        os.makedirs(os.path.join(case, "0"))
        os.makedirs(os.path.join(case, "50"))
        open(os.path.join(case, "0", "T"), "w").write("x")
        for field in ENDTIME_FIELDS:
            open(os.path.join(case, "50", field), "w").write("x")
        os.utime(os.path.join(case, "0", "T"), (1000, 1000))
        for field in ENDTIME_FIELDS:
            os.utime(os.path.join(case, "50", field), (2000, 2000))
        facts = {"end_line": True, "last_time": 50.0, "steps_completed": 50,
                 "sigfpe": 0, "thermo_frame": 0, "nan_inf_tokens": 0,
                 "time_headers": 50, "intrastep_lines": 50}
        fresh_ok, _ = completion_clauses(case, 0, facts, 50)
        os.utime(os.path.join(case, "0", "T"), (3000, 3000))   # touch 0/T FORWARD
        stale_ok, why = completion_clauses(case, 0, facts, 50)
    return (fresh_ok and not stale_ok
            and any("age guard" in w for w in why)), \
        "fields newer than 0/T PASS; 0/T touched forward FAILS on the age guard"


def _root_guard_control():
    with tempfile.TemporaryDirectory() as tmp:
        absent = os.path.join(tmp, "not_there")
        try:
            permitted = guard_run_root_absent(absent)
        except Refusal:
            permitted = False
        occupied = os.path.join(tmp, "occupied")
        os.makedirs(os.path.join(occupied, "0"))
        try:
            guard_run_root_absent(occupied)
            refused = False
        except Refusal:
            refused = True
    return (permitted and refused), "absent root permitted; occupied root REFUSED"


def _completion_control():
    with tempfile.TemporaryDirectory() as tmp:
        case = os.path.join(tmp, "case")
        os.makedirs(os.path.join(case, "0"))
        os.makedirs(os.path.join(case, "50"))
        open(os.path.join(case, "0", "T"), "w").write("x")
        for field in ENDTIME_FIELDS:
            path = os.path.join(case, "50", field)
            open(path, "w").write("x")
            os.utime(path, (2000, 2000))
        os.utime(os.path.join(case, "0", "T"), (1000, 1000))
        full = {"end_line": True, "last_time": 50.0, "steps_completed": 50, "sigfpe": 0,
                "thermo_frame": 0, "nan_inf_tokens": 0, "time_headers": 50,
                "intrastep_lines": 50}
        ok_all, _ = completion_clauses(case, 0, full, 50)
        short = dict(full, last_time=49.0)          # last time != endTime
        ok_short, why_short = completion_clauses(case, 0, short, 50)
        noend = dict(full, end_line=False)          # no End line
        ok_noend, why_noend = completion_clauses(case, 0, noend, 50)
        ok_rc, why_rc = completion_clauses(case, 1, full, 50)   # rc != 0
        short_steps = dict(full, steps_completed=49)            # ExecutionTime count off
        ok_steps, why_steps = completion_clauses(case, 0, short_steps, 50)
        os.remove(os.path.join(case, "50", "alphat"))
        ok_field, why_field = completion_clauses(case, 0, full, 50)
    good = (ok_all and not ok_short and not ok_noend and not ok_rc and not ok_steps
            and not ok_field
            and any("last time" in w for w in why_short)
            and any("End line" in w for w in why_noend)
            and any("rc==0" in w for w in why_rc)
            and any("ExecutionTime" in w for w in why_steps)
            and any("alphat" in w for w in why_field))
    return good, ("all six clauses together PASS; each of rc, End, last-time, "
                  "ExecutionTime-count and a missing field FAILS on its own clause")


def _field_at_endtime_control():
    """C12: the field-at-endTime reader, planted PRESENT then ABSENT, synthetic. Driven on
    read_endtime_fields -- the exact reader completion_clauses uses for the field clause."""
    with tempfile.TemporaryDirectory() as tmp:
        case = os.path.join(tmp, "case")
        os.makedirs(os.path.join(case, "50"))
        for field in ENDTIME_FIELDS:
            open(os.path.join(case, "50", field), "w").write("x")
        present = read_endtime_fields(case, 50)
        for field in ENDTIME_FIELDS:
            os.remove(os.path.join(case, "50", field))
        empty_dir = read_endtime_fields(case, 50)          # dir present, no fields
        os.rmdir(os.path.join(case, "50"))
        no_dir = read_endtime_fields(case, 50)             # dir absent entirely
    ok = (sorted(present) == sorted(ENDTIME_FIELDS)
          and empty_dir == [] and no_dir == [])
    return ok, ("field-at-endTime reader sees all %d fields PRESENT, then ABSENT for an "
                "empty time dir AND for a missing time dir -- DISCRIMINATES"
                % len(ENDTIME_FIELDS))


def _field_at_endtime_real_control():
    """C13: the field-at-endTime reader on M1's REAL B1 arm -- the refusing direction on
    real data. B1 reached Time = 50 and wrote NO endTime snapshot (M1's GATE FAIL); the
    reader MUST report the snapshot ABSENT there. This is the exact zero M1's gate turned
    on, and here it is a zero from a reader C12 just showed able to see a non-zero.

    A required archived control: an absent REAL_B1_ARM is REFUSED, not silently passed
    (as M1 requires its archived control logs)."""
    if not os.path.isdir(REAL_B1_ARM):
        refuse("REAL_B1_ARM absent: %s -- the field-at-endTime plant needs the real "
               "negative case it fires on" % REAL_B1_ARM)
    present = read_endtime_fields(REAL_B1_ARM, ADMISSION_ENDTIME)
    return present == [], ("M1's real B1 arm reached endTime and wrote no snapshot; the "
                           "field-at-endTime reader reports %d fields at %d/ -- ABSENT as "
                           "expected (the exact zero M1's GATE FAIL turned on)"
                           % (len(present), ADMISSION_ENDTIME))


# ---------------------------------------------------------------------------
# THE GATES.
# ---------------------------------------------------------------------------


def writer_gate(steps_completed, w1, w2):
    """R2M2-G1, one arm. `records == steps`, exactly, per field, on BOTH instruments.
    A zero-step arm satisfies it with zero records; a stepping arm that wrote fewer
    records FAILS. (Carried from R2M1-G1.)"""
    if steps_completed == 0:
        return all(v == 0 for v in w1.values()) and w2 == 0
    return all(w1[f] == steps_completed for f in MINMAX_FIELDS) and w2 >= steps_completed


def grade(root):
    """Reads the arms and returns (lines, status_fields). Names no verdict it did not
    measure, and never widens a gate to fit what it found."""
    lines, status = [], {}
    arm = {}

    for name in ARMS:
        case = os.path.join(root, name)
        state_path = os.path.join(case, "ARM_STATE.txt")
        state = open(state_path).read().strip() if os.path.isfile(state_path) else "LAUNCHED"
        if state == "BLOCKED":
            arm[name] = {"state": "BLOCKED"}
            continue
        facts = read_solve_log(load(os.path.join(case, "log.solve"), "%s log" % name))
        rc = read_rc(case)
        check_rc_consistency(rc, facts)
        dat = os.path.join(case, "postProcessing", FO_NAME, "0", "fieldMinMax.dat")
        arm[name] = {
            "state": "LAUNCHED", "rc": rc, "facts": facts, "case": case,
            "w1": {f: read_minmax(dat, f) for f in MINMAX_FIELDS},
            "w2": facts["intrastep_lines"],
            "class": classify_arm_log(facts),
        }

    # -- R2M2-G0, reproduction control. A PRECONDITION: if it fails, nothing else stands.
    b0 = arm["B0"]
    if b0["state"] == "BLOCKED":
        refuse("B0 is the reproduction control and it cannot be BLOCKED")
    g0 = (b0["rc"] == 136 and b0["class"] == "ABORTED"
          and b0["facts"]["thermo_frame"] > 0
          and b0["facts"]["last_time"] is not None
          and b0["facts"]["last_time"] <= REPRODUCTION_ABORT_TIME)
    status["R2M2_G0"] = "PASS" if g0 else "NOT A RESULT"
    lines.append("R2M2-G0: %s -- B0 rc=%s, class=%s, last Time=%s, thermo frames=%d"
                 % (status["R2M2_G0"], b0["rc"], b0["class"], b0["facts"]["last_time"],
                    b0["facts"]["thermo_frame"]))
    if not g0:
        lines.append("R2M2 VERDICT: NOT A RESULT -- the reproduction control did not "
                     "reproduce, so no conclusion is drawn from B1.")
        status["R2M2_VERDICT"] = "NOT A RESULT"
        return lines, status

    # -- R2M2-G1, writer liveness, PER ARM.
    g1_fail = []
    for name in ARMS:
        a = arm[name]
        if a["state"] == "BLOCKED":
            continue
        if not writer_gate(a["facts"]["steps_completed"], a["w1"], a["w2"]):
            g1_fail.append(name)
        lines.append("  %s COMPLETED_STEPS=%d W1=%s W2=%d"
                     % (name, a["facts"]["steps_completed"],
                        [a["w1"][f] for f in MINMAX_FIELDS], a["w2"]))
    status["R2M2_G1"] = "PASS" if not g1_fail else "GATE FAIL"
    lines.append("R2M2-G1: %s -- writer liveness%s"
                 % (status["R2M2_G1"],
                    "" if not g1_fail else " FAILED on: %s" % ", ".join(g1_fail)))

    # -- R2M2-G2, the warm start MAPS AND EXERCISES.
    b1 = arm["B1"]
    mapped = os.path.isfile(os.path.join(root, "B1", "WARMSTART_MAPPED"))
    status["R2M2_G2"] = "PASS" if (mapped and b1["state"] != "BLOCKED") else "BLOCKED"
    lines.append("R2M2-G2: %s -- warm-start map marker %s, arm state %s"
                 % (status["R2M2_G2"], "present" if mapped else "ABSENT", b1["state"]))

    # -- R2M2-G3, ADMISSION. The only admission gate, and the item verdict. B1's alone.
    if status["R2M2_G2"] != "PASS":
        status["R2M2_G3"] = "BLOCKED"
        lines.append("R2M2-G3: BLOCKED -- the warm start did not exercise, so the repaired "
                     "remedy STILL has not been tested. This is NOT a GATE FAIL.")
    else:
        ok, why = completion_clauses(b1["case"], b1["rc"], b1["facts"], ADMISSION_ENDTIME)
        clean = ok and b1["facts"]["sigfpe"] == 0 and b1["facts"]["nan_inf_tokens"] == 0
        status["R2M2_G3"] = "PASS" if clean else "GATE FAIL"
        why_all = list(why)
        if b1["facts"]["sigfpe"] > 0:
            why_all.append("signal 8 in log")
        if b1["facts"]["nan_inf_tokens"] > 0:
            why_all.append("nan/inf token in log")
        lines.append("R2M2-G3: %s -- B1 rc=%s last Time=%s%s"
                     % (status["R2M2_G3"], b1["rc"], b1["facts"]["last_time"],
                        "" if clean else "; failed clauses: %s"
                        % ", ".join(why_all or ["nan/sigfpe"])))
        if not clean:
            lines.append("  The failing clause above is the NEXT FINDING. The gate is NOT "
                         "widened, and no third remedy is licensed without a new "
                         "registration (registration section 9).")

    # -- the item verdict. R2M2-G3 carries it; G0 and the selftest can only turn it into
    #    NOT A RESULT, never the reverse.
    status["R2M2_VERDICT"] = status["R2M2_G3"]
    lines.append("R2M2 VERDICT: %s (carried by R2M2-G3, the admission gate)"
                 % status["R2M2_VERDICT"])
    if status["R2M2_VERDICT"] == "PASS":
        lines.append("  The compressible path is ADMITTED; Blocker 1 clears; M6SR's B5a may "
                     "relaunch. This moves NO CRM number: Rung 2 (a) stays BLOCKED on "
                     "binding ground (iii), the absent refinement triple.")
    lines.append("NO FORCE, DRAG, LIFT, MOMENT OR CRM CLAIM IS PRODUCED BY THIS PROBE.")
    return lines, status


def _run_selftest_report(own):
    try:
        results = selftest(own)
    except Refusal as exc:
        print("REFUSED: %s" % exc)
        return None
    return results


def main(argv):
    own = os.path.abspath(__file__)
    if "--selftest" in argv:
        results = _run_selftest_report(own)
        if results is None:
            return 2
        for tag, ok, note in results:
            print("%s %-4s %s" % ("PASS" if ok else "FAIL", tag, note))
        bad = [t for t, ok, _ in results if not ok]
        print("R2M2-G4: %s -- %d/%d controls fired."
              % ("PASS" if not bad else "NOT A RESULT",
                 len(results) - len(bad), len(results)))
        return 0 if not bad else 2

    if len(argv) < 2:
        print("usage: grade_r2_m2.py <run root> | --selftest")
        return 2
    root = argv[1]

    # THE SELFTEST RUNS FIRST AND UNCONDITIONALLY. Nothing is reported by a reader that
    # has not just been shown able to see both outcomes.
    results = _run_selftest_report(own)
    if results is None:
        return 2
    bad = [t for t, ok, _ in results if not ok]
    if bad:
        print("REFUSED: controls did not fire: %s" % ", ".join(bad))
        return 2

    try:
        lines, status = grade(root)
    except Refusal as exc:
        print("REFUSED: %s" % exc)
        return 2

    for line in lines:
        print(line)
    with open(os.path.join(root, "STATUS.R2_M2"), "a") as handle:
        for key, value in status.items():
            handle.write("%s=%s\n" % (key, value))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
