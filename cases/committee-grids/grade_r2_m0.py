#!/usr/bin/env python3
"""Comparator for RUNG 2 / R2-M0 -- the CRM (DPW5 L1.T hex) compressible admission probe.

Registered by `verification/campaign/RUNG2_CRM_M0_PREREGISTRATION.md`, Amendment 1.
The grading path is fixed at that document's commit; this file is hashed against its
committed blob at grading time and the run refuses on mismatch.

THIS FILE LAUNCHES NOTHING. It reads logs and case directories and grades them.

Design constraints, each from a rule or a lesson and each carried by an executable check:

  * rule 3  -- planted controls. Every reader is shown able to see BOTH outcomes before it
               is allowed to report either. `--selftest` is that demonstration and it runs
               against the two REAL archived 2026-08-01 logs, not against synthetic text.
  * rule 4  -- strict completion, all six clauses including the age guard.
  * L-382 / "setsid parent returns zero" -- `setsid timeout cmd` exits 0 for every outcome,
               so an rc of 0 beside a log that shows signal 8 is a captured-outside-the-wrapper
               defect. This comparator REFUSES that combination rather than grading it.
  * "stale pycache inverts mutation tests" -- no bytecode is written by the selftest path.
  * ZERO `assert` statements. `python3 -O` strips `assert`, so a guard built on one is a guard
               that vanishes in production. `count_assert_nodes()` proves the absence by AST,
               with the detector itself planted first.

Exit codes:
    0  graded, or selftest passed
    2  REFUSED -- a control did not fire, or an input is inconsistent. Never a grade.
"""

import ast
import os
import re
import sys
import tempfile

# ---------------------------------------------------------------------------
# Registered constants. Changing any of these changes the grade and is a freeze
# violation unless it lands as a dated amendment to the pre-registration.
# ---------------------------------------------------------------------------

# The two REAL archived logs from the 2026-08-01 committee-grid numerics probe,
# on the same grid, the same box and the same day. They are this comparator's
# positive and negative controls for R2-G3.
CONTROL_ABORT_LOG = (
    "/home/ubuntu/certonomous-runs/dpw5-committee-probe/logs/"
    "hex_base_compressible_a2.11_solve.log"
)
CONTROL_CLEAN_LOG = (
    "/home/ubuntu/certonomous-runs/dpw5-committee-probe/logs/"
    "hex_base_incompressible_a2.11_solve.log"
)

# R2-G0's registered signature of the known abort.
THERMO_FRAME = "libfluidThermophysicalModels.so"
SIGFPE_MARK = "Floating point exception (8)"
ABORT_AT_TIME = 2

# R2-G1's registered admission bar.
ADMISSION_ENDTIME = 50

# Fields required present at endTime (rule 4 clause 4) for this compressible probe.
REQUIRED_FIELDS = ("T", "U", "p", "k", "omega", "nut", "alphat")

RE_TIME = re.compile(r"^Time = ([0-9]+(?:\.[0-9]+)?)\s*$", re.M)
RE_EXECTIME = re.compile(r"^ExecutionTime = ", re.M)
RE_END = re.compile(r"^End\s*$", re.M)
RE_NANINF = re.compile(r"(?i)(?<![A-Za-z0-9_])[-+]?(nan|inf)(?![A-Za-z0-9_])")


class Refusal(Exception):
    """Raised instead of returning a number the comparator cannot stand behind."""


def refuse(message):
    raise Refusal(message)


# ---------------------------------------------------------------------------
# The readers. Pure functions on text, so the controls exercise the SAME code
# path the grade uses -- a control on a different function is not a control.
# ---------------------------------------------------------------------------


def read_solve_log(text):
    """Read one solver log. Returns the facts; makes no judgement."""
    times = [float(t) for t in RE_TIME.findall(text)]
    return {
        "time_headers": len(times),
        "last_time": times[-1] if times else None,
        "exec_time_count": len(RE_EXECTIME.findall(text)),
        "end_line": bool(RE_END.search(text)),
        "sigfpe": text.count(SIGFPE_MARK),
        "thermo_frame": text.count(THERMO_FRAME),
        "nan_inf_tokens": len(RE_NANINF.findall(text)),
    }


def classify_arm_log(facts):
    """ABORTED / COMPLETED / INCOMPLETE. The one place the words are assigned."""
    if facts["sigfpe"] > 0 or facts["thermo_frame"] > 0:
        return "ABORTED"
    if facts["end_line"]:
        return "COMPLETED"
    return "INCOMPLETE"


def read_rc(arm_dir):
    """rc MUST be captured inside the wrapper. Absent rc is a refusal, not a zero."""
    path = os.path.join(arm_dir, "rc.txt")
    if not os.path.isfile(path):
        refuse(
            "no rc.txt in the arm directory. rc must be captured INSIDE the detached "
            "wrapper -- `setsid timeout cmd` exits 0 for every outcome, so an rc taken "
            "around the setsid line is not this run's rc."
        )
    with open(path, "r") as handle:
        raw = handle.read().strip()
    if not re.fullmatch(r"-?[0-9]+", raw):
        refuse("rc.txt does not contain a bare integer")
    return int(raw)


def check_rc_consistency(rc, facts):
    """The setsid trap, made executable.

    An rc of 0 beside a log carrying signal 8 does not mean the run succeeded; it
    means the rc was captured around the wrong process. Refuse rather than grade.
    """
    if rc == 0 and (facts["sigfpe"] > 0 or facts["thermo_frame"] > 0):
        refuse(
            "rc=0 beside a log carrying the SIGFPE signature. This is the "
            "setsid-parent-returns-zero defect, not a successful run."
        )
    return True


def read_endtime(case_dir):
    path = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(path):
        refuse("no system/controlDict, so endTime cannot be read from the case itself")
    with open(path, "r") as handle:
        text = handle.read()
    found = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", text, re.M)
    if not found:
        refuse("controlDict carries no endTime entry")
    return float(found.group(1))


def fmt_time(value):
    """OpenFOAM writes 50, not 50.0. Match the directory name it actually creates."""
    if value == int(value):
        return str(int(value))
    return repr(value)


def completion_clauses(case_dir, rc, facts, endtime):
    """Rule 4, all six clauses, reported individually so a failure names itself."""
    time_dir = os.path.join(case_dir, fmt_time(endtime))
    zero_T = os.path.join(case_dir, "0", "T")

    clauses = {}
    clauses["c1_rc_zero"] = rc == 0
    clauses["c2_end_line"] = facts["end_line"]
    clauses["c3_last_time_is_endtime"] = facts["last_time"] == endtime
    clauses["c5_exectime_count"] = facts["exec_time_count"] == int(endtime)

    if not os.path.isdir(time_dir):
        clauses["c4_fields_present"] = False
        clauses["c6_age_guard"] = False
        return clauses, time_dir

    present = [
        field
        for field in REQUIRED_FIELDS
        if os.path.isfile(os.path.join(time_dir, field))
    ]
    clauses["c4_fields_present"] = len(present) == len(REQUIRED_FIELDS)

    # THE AGE GUARD. `0/T` is touched last at launch, so it dates the run that was
    # allowed to produce this answer. Every field at endTime must be NEWER than it.
    if not os.path.isfile(zero_T):
        clauses["c6_age_guard"] = False
        return clauses, time_dir
    zero_mtime = os.path.getmtime(zero_T)
    newer = [
        field
        for field in present
        if os.path.getmtime(os.path.join(time_dir, field)) > zero_mtime
    ]
    clauses["c6_age_guard"] = (
        len(present) == len(REQUIRED_FIELDS) and len(newer) == len(present)
    )
    return clauses, time_dir


def guard_run_root_absent(path):
    """Refuse a launch into a root that already exists. Called BEFORE compute."""
    if os.path.exists(path):
        refuse(
            "the registered run root already exists. A guard refuses a case where 0 "
            "or a time directory could pre-date the run."
        )
    return True


# ---------------------------------------------------------------------------
# The `assert`-freedom proof. The detector is planted before it is trusted.
# ---------------------------------------------------------------------------


def count_assert_nodes(source_text):
    tree = ast.parse(source_text)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))


def prove_assert_free(own_path):
    """Plant the detector, watch it fire, then read this file with it."""
    planted = count_assert_nodes("assert True\nx = 1\n")
    if planted != 1:
        refuse(
            "the assert-detector did not see a planted `assert` (saw %d, expected 1). "
            "A detector not shown able to see one cannot report its absence." % planted
        )
    control = count_assert_nodes("x = 1\n")
    if control != 0:
        refuse("the assert-detector reported an assert in source that has none")
    with open(own_path, "r") as handle:
        own = count_assert_nodes(handle.read())
    if own != 0:
        refuse(
            "this comparator contains %d `assert` statement(s). `python3 -O` strips "
            "them, so such a guard vanishes in production." % own
        )
    return True


# ---------------------------------------------------------------------------
# R2-G3 -- the acceptance test. Runnable today, against the real archived logs,
# with no solve. If the reader cannot see both outcomes, R2-M0 must not launch.
# ---------------------------------------------------------------------------


def load(path, what):
    if not os.path.isfile(path):
        refuse("the %s control log is not on disk, so the control cannot fire" % what)
    with open(path, "r", errors="replace") as handle:
        return handle.read()


def selftest():
    results = []

    # -- Control 0: the comparator proves its own guards survive `python3 -O`.
    prove_assert_free(os.path.abspath(__file__))
    results.append(("C0  assert-free proved, detector planted and seen", True))

    # -- Control 1 (POSITIVE): the real archived ABORT log must read as ABORTED at
    #    Time = 2 with the thermophysical frame present. This is R2-G0's signature.
    abort_text = load(CONTROL_ABORT_LOG, "abort")
    abort_facts = read_solve_log(abort_text)
    abort_ok = (
        classify_arm_log(abort_facts) == "ABORTED"
        and abort_facts["last_time"] == ABORT_AT_TIME
        and abort_facts["thermo_frame"] > 0
        and abort_facts["sigfpe"] > 0
        and not abort_facts["end_line"]
    )
    results.append(("C1  archived ABORT log reads ABORTED at Time = 2, thermo frame seen",
                    abort_ok))

    # -- Control 2 (NEGATIVE): the real archived CLEAN log, same grid, same box, same
    #    day, must read as COMPLETED with no abort signature at all. The reader has to
    #    FLIP between two real artifacts, not merely fire on one.
    clean_text = load(CONTROL_CLEAN_LOG, "clean")
    clean_facts = read_solve_log(clean_text)
    clean_ok = (
        classify_arm_log(clean_facts) == "COMPLETED"
        and clean_facts["sigfpe"] == 0
        and clean_facts["thermo_frame"] == 0
        and clean_facts["end_line"]
        and clean_facts["last_time"] == 200.0
        and clean_facts["exec_time_count"] == 200
        and clean_facts["nan_inf_tokens"] == 0
    )
    results.append(("C2  archived CLEAN log reads COMPLETED, no abort signature", clean_ok))

    # -- Control 3 (MUTATION): plant the abort signature INTO the clean log. The
    #    classification must flip. This proves C2's negative is caused by the absence
    #    of those bytes and not by something incidental to that file.
    mutated = clean_text + "\n" + SIGFPE_MARK + "\n" + THERMO_FRAME + "\n"
    mutated_ok = classify_arm_log(read_solve_log(mutated)) == "ABORTED"
    results.append(("C3  abort signature planted into the clean log -> flips to ABORTED",
                    mutated_ok))

    # -- Control 4 (MUTATION): the NaN/inf scan R2-G1 names must fire on a planted
    #    token and must not fire on the unplanted control.
    nan_planted = read_solve_log(clean_text + "\nbounding k, min nan max nan\n")
    nan_ok = nan_planted["nan_inf_tokens"] > 0 and clean_facts["nan_inf_tokens"] == 0
    results.append(("C4  NaN token planted -> scan fires; unplanted -> silent", nan_ok))

    # -- Control 5: the rc-consistency guard must refuse the setsid trap and must
    #    permit an honest rc=0 beside a clean log.
    trap_refused = False
    try:
        check_rc_consistency(0, abort_facts)
    except Refusal:
        trap_refused = True
    honest_allowed = check_rc_consistency(0, clean_facts)
    results.append(("C5  rc=0 beside a SIGFPE log REFUSED; rc=0 beside a clean log allowed",
                    trap_refused and honest_allowed))

    # -- Control 6: THE AGE GUARD, shown able to fail. A synthetic case whose endTime
    #    fields are newer than `0/T` passes; touch `0/T` forward and it must fail.
    age_pass, age_fail = _age_guard_control()
    results.append(("C6  age guard: fields newer than 0/T PASS; 0/T touched forward FAIL",
                    age_pass and not age_fail))

    # -- Control 7: the run-root guard refuses an existing root and permits an absent one.
    root_ok = _root_guard_control()
    results.append(("C7  run-root guard refuses an existing root, permits an absent one",
                    root_ok))

    for label, ok in results:
        print("%-4s %s" % ("PASS" if ok else "FAIL", label))
    failed = [label for label, ok in results if not ok]
    if failed:
        print("R2-G3: NOT A RESULT -- %d control(s) did not fire." % len(failed))
        return 2
    print("R2-G3: PASS -- %d/%d controls fired." % (len(results), len(results)))
    return 0


def _age_guard_control():
    with tempfile.TemporaryDirectory() as root:
        case = os.path.join(root, "case")
        os.makedirs(os.path.join(case, "0"))
        os.makedirs(os.path.join(case, "system"))
        os.makedirs(os.path.join(case, str(ADMISSION_ENDTIME)))
        with open(os.path.join(case, "system", "controlDict"), "w") as handle:
            handle.write("endTime %d;\n" % ADMISSION_ENDTIME)
        zero_T = os.path.join(case, "0", "T")
        with open(zero_T, "w") as handle:
            handle.write("0\n")
        for field in REQUIRED_FIELDS:
            with open(os.path.join(case, str(ADMISSION_ENDTIME), field), "w") as handle:
                handle.write("x\n")
        facts = {
            "end_line": True,
            "last_time": float(ADMISSION_ENDTIME),
            "exec_time_count": ADMISSION_ENDTIME,
            "sigfpe": 0,
            "thermo_frame": 0,
            "nan_inf_tokens": 0,
            "time_headers": ADMISSION_ENDTIME,
        }
        endtime = read_endtime(case)

        # Deterministic mtimes: fields at t=2000, 0/T at t=1000 -> fields are newer.
        os.utime(zero_T, (1000, 1000))
        for field in REQUIRED_FIELDS:
            os.utime(os.path.join(case, str(ADMISSION_ENDTIME), field), (2000, 2000))
        good, _ = completion_clauses(case, 0, facts, endtime)

        # Now touch 0/T forward past the fields. The age guard must fail.
        os.utime(zero_T, (3000, 3000))
        bad, _ = completion_clauses(case, 0, facts, endtime)
        return good["c6_age_guard"], bad["c6_age_guard"]


def _root_guard_control():
    with tempfile.TemporaryDirectory() as root:
        existing = os.path.join(root, "already_here")
        os.makedirs(existing)
        refused = False
        try:
            guard_run_root_absent(existing)
        except Refusal:
            refused = True
        permitted = guard_run_root_absent(os.path.join(root, "not_here"))
        return refused and permitted


# ---------------------------------------------------------------------------


def grade(arm_dirs):
    """Grade R2-G0 and R2-G1 over the arm directories. NOT reached before launch."""
    verdicts = {}
    for arm_dir in arm_dirs:
        name = os.path.basename(os.path.normpath(arm_dir))
        log_path = os.path.join(arm_dir, "log.solve")
        facts = read_solve_log(load(log_path, "arm %s" % name))
        rc = read_rc(arm_dir)
        check_rc_consistency(rc, facts)
        state = classify_arm_log(facts)
        endtime = read_endtime(arm_dir)
        clauses, _ = completion_clauses(arm_dir, rc, facts, endtime)
        verdicts[name] = {
            "state": state,
            "rc": rc,
            "last_time": facts["last_time"],
            "nan_inf_tokens": facts["nan_inf_tokens"],
            "complete": all(clauses.values()),
            "clauses": clauses,
        }

    a0 = verdicts.get("A0")
    if a0 is None:
        refuse("A0, the reproduction control, is absent. R2-G0 cannot be read.")
    g0 = (
        a0["state"] == "ABORTED"
        and a0["rc"] == 136
        and a0["last_time"] is not None
        and a0["last_time"] <= ABORT_AT_TIME
    )
    if not g0:
        print("R2-G0: NOT A RESULT -- A0 did not reproduce the registered abort.")
        print("R2-M0 VERDICT: NOT A RESULT")
        return 0

    admitted = [
        name
        for name, v in verdicts.items()
        if name != "A0"
        and v["state"] == "COMPLETED"
        and v["rc"] == 0
        and v["complete"]
        and v["nan_inf_tokens"] == 0
        and v["last_time"] == float(ADMISSION_ENDTIME)
    ]
    print("R2-G0: PASS -- A0 reproduced the abort at Time = %s." % fmt_time(a0["last_time"]))
    if admitted:
        print("R2-G1: PASS -- %d arm(s) reached Time = %d." % (len(admitted), ADMISSION_ENDTIME))
        print("R2-M0 VERDICT: PASS")
    else:
        print("R2-G1: GATE FAIL -- no arm reached Time = %d." % ADMISSION_ENDTIME)
        print("R2-M0 VERDICT: GATE FAIL")
    return 0


def main(argv):
    if len(argv) >= 2 and argv[1] == "--selftest":
        return selftest()
    if len(argv) >= 3 and argv[1] == "--guard-absent":
        guard_run_root_absent(argv[2])
        print("run root ABSENT as registered")
        return 0
    if len(argv) >= 3 and argv[1] == "--grade":
        return grade(argv[2:])
    print(__doc__)
    print("usage: grade_r2_m0.py --selftest | --guard-absent <path> | --grade <arm_dir>...")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Refusal as exc:
        print("REFUSED: %s" % exc)
        sys.exit(2)
