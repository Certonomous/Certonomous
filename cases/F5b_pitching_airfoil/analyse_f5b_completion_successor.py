#!/usr/bin/env python3
"""F5b PHYSICS RUNG -- SUCCESSOR COMPARATOR, STAGE 1: the completion rule only.

WHAT THIS IS
------------
A SUCCESSOR comparator for the F5b physics rung, written fresh at a new path under
Sanaa's 2026-09-03 GO on "F5b -- OPTION 1" (successor comparator at a new path).

It SUPERSEDES nothing by overwriting.  The predecessor
`verification/runs/F5b_runs/analyse_f5b_physics.py` is EVIDENCE and is neither read at
run time, imported, copied, patched, edited, moved nor deleted by this file.  This file
was written against the FROZEN PRE-REGISTRATION
`verification/campaign/F5b_PHYSICS_PREREGISTRATION.md` sections 5 and 8, not against the
predecessor's source.

THE DEFECT IT REPAIRS  (L-321; VERIFICATION_CHARTER §2p.5)
---------------------------------------------------------
The predecessor resolved the endTime directory by STRING MATCH on a hand-written literal
`END_TIME_STR = "21.9440"` and looked for `case/21.9440/`.  OpenFOAM's float formatting
strips the trailing zero and wrote `case/21.944/`.  Completion clauses 4 (fields present)
and 6 (age guard) both keyed off that one string, both failed, and the rung graded
NOT A RESULT with the gate never evaluated -- while every required field sat on disk.

The repair is STRUCTURAL, never a corrected constant: the registered endTime is parsed as
a NUMBER, every candidate directory name is parsed as a NUMBER, and the match is made
between numbers.  `21.9440` and `21.944` parse to the same double, so the trailing zero
can never matter again -- and neither can the next endTime whose OpenFOAM rendering
differs from its registered spelling.  Where no candidate matches exactly, a SECOND,
NARROWER rule applies (the 6-significant-figure write quantum, §2p.5's "anchoring"), and
in BOTH rules the selection REFUSES unless exactly one candidate matches.  It never
chooses among several and never falls back to "the latest".

EXIT CODES (VERIFICATION_CHARTER §2ak, ruled 2026-09-03 at 5577cec9)
-------------------------------------------------------------------
    0   the completion rule was evaluated; the VERDICT is in the record, never in the code
    2   EXIT_REFUSE      -- a registered refusal: the instrument declines to judge
   70   EXIT_INSTRUMENT_ERROR (EX_SOFTWARE) -- an internal error.  A CRASH IS NOT A
        REFUSAL.  The record is emitted anyway, carrying the exception type, message,
        raise site and this file's own blob sha; the traceback goes to stderr.
    1   IS NOT USED BY THIS FILE.  A `1` from this process means the top-level handler
        itself failed -- the floor §2ak states honestly and does not paper over.

NO BARE `assert` APPEARS IN THIS FILE (L-332 / L-475: `python3 -O` deletes every one).
Every guard raises.  `--selftest` returns the same rc under `python3` and `python3 -O`,
and that invariance is itself one of the controls.

STAGE 1 SCOPE, DECLARED SO IT CANNOT BE MISTAKEN FOR MORE
---------------------------------------------------------
Clauses 1-8 of the frozen registration's section 5 completion rule.  The GATE bodies
(G1 area, G2 excursion, G3 admissibility) are NOT implemented here: they raise
NotImplementedError, exactly as the predecessor's own staged freeze did (registration
section 9, stage 1 / stage 2).  This instrument therefore cannot report A_L, C_L or any
gate quantity, by construction.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback

# ---------------------------------------------------------------- exit vocabulary
EXIT_OK = 0
EXIT_REFUSE = 2                 # §2ak: the majority convention, 51 of 53 definitions
EXIT_INSTRUMENT_ERROR = 70      # §2ak: EX_SOFTWARE.  A crash is not a refusal.

# ------------------------------------------------- constants, from the FROZEN prereg
# verification/campaign/F5b_PHYSICS_PREREGISTRATION.md sections 5 and 8.
# NOT ONE OF THESE IS CHANGED BY THIS SUCCESSOR.  The successor changes HOW the endTime
# directory is FOUND, never what is required of it, and never a gate, band, cap or label.
END_TIME_STR = "21.9440"                              # §5 clause 3, registered spelling
REQUIRED_FIELDS = ("U", "p", "k", "omega", "nut")     # §5 clause 4 (E2 initial_fields)
REPORTED_NOT_GATED_FIELDS = ("phi", "yPlus", "yPlus1")
PRELUDE_LOGS = ("log.blockMesh", "log.checkMesh", "log.potentialFoam")
PRELOOP_COURANT_LINES = 2                             # §5 clause 5, derived pimpleFoam.C
WALL_CAP_S = 4200.0                                   # §8 driver timeout
COST_CAP_CORE_MIN = 72.0                              # §8 RUN CAP
SIGNIFICANT_FIGURES = 6                               # OpenFOAM default time-name width

RE_END = re.compile(r"^End\b", re.M)
RE_TIME = re.compile(r"^Time = (\S+)", re.M)
RE_EXECTIME = re.compile(r"^ExecutionTime = ", re.M)
RE_COURANT = re.compile(r"^Courant Number mean: (\S+) max: (\S+)", re.M)
RE_MESH_COURANT = re.compile(r"^Mesh Courant Number mean:", re.M)
RE_TIME_DIR = re.compile(r"^[0-9]+(?:\.[0-9]*)?(?:[eE][-+]?[0-9]+)?$")


class Refusal(Exception):
    """A statement about the RUN, made by a working instrument.  Exits 2."""


class ControlFailure(Exception):
    """A planted control did not behave as registered.  Raised, never asserted."""


def refuse(reason):
    raise Refusal(reason)


def own_blob_sha():
    """This file's git blob sha, computed locally -- no subprocess, no repo assumed."""
    with open(os.path.abspath(__file__), "rb") as fh:
        body = fh.read()
    return hashlib.sha1(b"blob %d\x00" % len(body) + body).hexdigest()


# ===================================================================== THE REPAIR
def resolve_end_time_dir(case_dir, end_time_str=END_TIME_STR):
    """§2p.5: SELECT BY THE TIME WE NEED, and REFUSE if it is not uniquely present.

    Returns (path, rule, candidates) where `rule` is 'exact' or 'write-quantum'.
    Raises Refusal (-> exit 2) on zero matches and on any ambiguity.  It NEVER returns
    'the latest', never sorts, and never chooses among several.
    """
    if not os.path.isdir(case_dir):
        refuse("case directory absent: %s" % case_dir)
    try:
        target = float(end_time_str)
    except (TypeError, ValueError):
        refuse("registered endTime %r is not a number" % (end_time_str,))

    candidates = []
    for name in sorted(os.listdir(case_dir)):
        if not os.path.isdir(os.path.join(case_dir, name)):
            continue
        if not RE_TIME_DIR.match(name):
            continue                      # constant/, system/, polyMesh/ ... not times
        try:
            candidates.append((name, float(name)))
        except ValueError:
            continue

    exact = [n for n, v in candidates if v == target]
    if len(exact) == 1:
        return os.path.join(case_dir, exact[0]), "exact", candidates
    if len(exact) > 1:
        refuse("AMBIGUOUS: %d directories parse to endTime %s exactly: %r.  The reader "
               "declines rather than choosing one." % (len(exact), end_time_str, exact))

    # No exact parse-equality.  The only other admissible match is OpenFOAM's own
    # write quantum: a time name printed at %d significant figures carries at most half
    # a unit in its last printed place.  Anything wider would risk matching a directory
    # from a DIFFERENT write, so the guard stays narrow and still refuses on ambiguity.
    near = []
    for name, value in candidates:
        if value == 0.0:
            continue
        magnitude = abs(value)
        exponent = 0
        while magnitude >= 10.0:
            magnitude /= 10.0
            exponent += 1
        while magnitude < 1.0:
            magnitude *= 10.0
            exponent -= 1
        quantum = 0.5 * 10.0 ** (exponent - (SIGNIFICANT_FIGURES - 1))
        if abs(value - target) <= quantum:
            near.append(name)
    if len(near) == 1:
        return os.path.join(case_dir, near[0]), "write-quantum", candidates
    if len(near) > 1:
        refuse("AMBIGUOUS: %d directories fall inside the %d-significant-figure write "
               "quantum of endTime %s: %r.  The reader declines rather than choosing."
               % (len(near), SIGNIFICANT_FIGURES, end_time_str, near))
    refuse("NO directory under %s resolves to endTime %s.  Candidates on disk: %r.  "
           "The reader refuses; it does not fall back to the latest time."
           % (case_dir, end_time_str, [n for n, _ in candidates]))


# ============================================================ the completion rule
class Clauses(object):
    def __init__(self):
        self.rows = []

    def add(self, number, name, ok, detail):
        if not isinstance(ok, bool):
            raise ControlFailure("clause %s produced a non-boolean verdict %r"
                                 % (number, ok))
        self.rows.append({"clause": number, "name": name, "ok": ok, "detail": detail})

    @property
    def all_ok(self):
        return all(r["ok"] for r in self.rows)

    def failing(self):
        return [r["clause"] for r in self.rows if not r["ok"]]


def _read(path):
    try:
        with open(path, "r", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def _count_coefficient_rows(case_dir):
    """Data-row count under postProcessing/forceCoeffs1 -- a COUNT, never a value.

    This stage-1 instrument reads no coefficient COLUMN.  It refuses on a multiple
    match (a restart collision renames the file) rather than choosing one.
    """
    base = os.path.join(case_dir, "postProcessing", "forceCoeffs1")
    hits = []
    if os.path.isdir(base):
        for sub in sorted(os.listdir(base)):
            subdir = os.path.join(base, sub)
            if not os.path.isdir(subdir):
                continue
            for name in sorted(os.listdir(subdir)):
                if name.startswith("coefficient") and name.endswith(".dat"):
                    hits.append(os.path.join(subdir, name))
    if not hits:
        return None, "no coefficient*.dat under %s" % base
    if len(hits) > 1:
        refuse("%d coefficient files under %s: %r.  A restart collision renames the "
               "file; the reader refuses rather than choosing one." % (len(hits), base, hits))
    text = _read(hits[0])
    if text is None:
        refuse("coefficient file unreadable: %s" % hits[0])
    header_fields = None
    rows = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            header_fields = len(stripped.lstrip("#").split())
            continue
        fields = len(stripped.split())
        if header_fields is not None and fields != header_fields:
            refuse("coefficient row has %d fields against a %d-field header in %s"
                   % (fields, header_fields, hits[0]))
        rows += 1
    return rows, hits[0]


def check_completion(case_dir, record_path=None):
    """Clauses 1-8 of the frozen registration's section 5.  Refuses, never degrades."""
    comp = Clauses()
    record_path = record_path or os.path.join(os.path.dirname(case_dir.rstrip("/")),
                                              "record.json")
    log_path = os.path.join(case_dir, "log.pimpleFoam")
    log = _read(log_path)
    if log is None:
        refuse("log.pimpleFoam absent at %s -- nothing below can be checked" % log_path)

    # THE REPAIR, ON THE LOAD-BEARING PATH: clauses 4 and 6 both key off this.
    time_dir, rule, candidates = resolve_end_time_dir(case_dir)

    # clause 1 -- rc = 0 by the disclosed proxy.  L-320: the INDEPENDENT operand is
    # record.json's presence, and it is stated first because it is the one that carries
    # the load; the prelude End lines merely restate clause 2 on other logs.
    record_present = os.path.isfile(record_path)
    missing = [n for n in PRELUDE_LOGS if _read(os.path.join(case_dir, n)) is None]
    no_end = [n for n in PRELUDE_LOGS
              if n not in missing and not RE_END.search(_read(os.path.join(case_dir, n)))]
    comp.add(1, "rc = 0 (disclosed proxy)", bool(record_present and not missing and not no_end),
             "record.json present: %s (INDEPENDENT operand, L-320) | prelude logs "
             "missing: %s | prelude logs without End: %s | NO rc IS RECORDED ON DISK"
             % (record_present, missing or "none", no_end or "none"))

    # clause 2 -- an End line in log.pimpleFoam
    comp.add(2, "End line", bool(RE_END.search(log)),
             "log.pimpleFoam %s a final End line"
             % ("carries" if RE_END.search(log) else "DOES NOT carry"))

    # clause 3 -- last time == endTime, compared as NUMBERS
    times = RE_TIME.findall(log)
    last = times[-1] if times else None
    ok3 = False
    if last is not None:
        try:
            ok3 = float(last) == float(END_TIME_STR)
        except ValueError:
            ok3 = False
    comp.add(3, "last time == endTime", ok3,
             "last 'Time = ' %s   required %s   (%d Time lines; compared numerically, "
             "never as strings)" % (last, END_TIME_STR, len(times)))

    # clause 4 -- fields present, AT THE RESOLVED DIRECTORY
    have = sorted(os.listdir(time_dir))
    absent = [f for f in REQUIRED_FIELDS if f not in have]
    comp.add(4, "fields present", not absent,
             "%s  [resolved by the %s rule from candidates %r]\nrequired: %s\nmissing: "
             "%s\nreported, NOT gated: %s"
             % (time_dir, rule, [n for n, _ in candidates], list(REQUIRED_FIELDS),
                absent or "none",
                {f: (f in have) for f in REPORTED_NOT_GATED_FIELDS}))

    # clause 5 -- the four-way step count
    zero_dir = os.path.join(case_dir, "0")
    n_exec = len(RE_EXECTIME.findall(log))
    n_courant = len(RE_COURANT.findall(log))
    n_mesh_courant = len(RE_MESH_COURANT.findall(log))
    n_rows, coeff_note = _count_coefficient_rows(case_dir)
    n_steps = None
    if record_present:
        try:
            n_steps = json.loads(_read(record_path)).get("n_steps")
        except (ValueError, TypeError):
            n_steps = None
    ok5 = (isinstance(n_rows, int) and isinstance(n_steps, int)
           and n_exec == n_rows == n_steps
           and n_courant == n_steps + PRELOOP_COURANT_LINES)
    comp.add(5, "four-way step count", ok5,
             "count(ExecutionTime =) %s | coefficient data rows %s | record.json "
             "n_steps %s | count(^Courant Number mean:) %s (required n_steps + %d) | "
             "count(^Mesh Courant Number mean:) %s reported, anchored out of the count "
             "above | %s"
             % (n_exec, n_rows, n_steps, n_courant, PRELOOP_COURANT_LINES,
                n_mesh_courant, coeff_note))

    # clause 6 -- the age guard, AT THE RESOLVED DIRECTORY
    ok6, detail6 = False, "0/ absent at %s" % zero_dir
    if os.path.isdir(zero_dir):
        zero_entries = [(f, os.path.getmtime(os.path.join(zero_dir, f)))
                        for f in os.listdir(zero_dir)]
        if not zero_entries:
            detail6 = "0/ is empty -- the guard has no datum and cannot pass"
        else:
            argmax = max(zero_entries, key=lambda pair: pair[1])
            stale = [(f, os.path.getmtime(os.path.join(time_dir, f)))
                     for f in os.listdir(time_dir)
                     if os.path.getmtime(os.path.join(time_dir, f)) <= argmax[1]]
            ok6 = not stale
            detail6 = ("max(mtime) over the whole 0/ directory: %s at %.6f (max over the "
                       "DIRECTORY, so write order cannot defeat the guard)\nfiles at "
                       "endTime NOT strictly newer: %s\nreported, not gated: argmax is "
                       "0/nut: %s" % (argmax[0], argmax[1], stale or "none",
                                      argmax[0] == "nut"))
    comp.add(6, "age guard", ok6, detail6)

    # clause 7 -- the pre-existing-state guard is the LAUNCHER's, and is recorded as such
    comp.add(7, "pre-existing-state guard", True,
             "enforced at LAUNCH (registration section 3 assertion 1, defect D-1), not "
             "here.  This comparator records whose guard it is and does not claim it.")

    # clause 8 -- cap guard
    wall = None
    if record_present:
        try:
            wall = json.loads(_read(record_path)).get("wall_seconds")
        except (ValueError, TypeError):
            wall = None
    core_min = (wall / 60.0) if isinstance(wall, (int, float)) else None
    ok8 = (isinstance(wall, (int, float)) and wall <= WALL_CAP_S
           and core_min <= COST_CAP_CORE_MIN)
    comp.add(8, "cap guard", ok8,
             "wall_seconds %s <= %.0f s | core-minutes (1 rank) %s <= %.1f cap | AN "
             "OVERRUN STOPS THE RUN; IT DOES NOT GET A NEW BUDGET (rule 12)"
             % (wall, WALL_CAP_S,
                ("%.3f" % core_min) if core_min is not None else None, COST_CAP_CORE_MIN))
    return comp, time_dir, rule


# ------------------------------------------------------------------ stage 2 stubs
def grade_G1(*_a, **_k):
    raise NotImplementedError(
        "G1 (loop area A_L) is STAGE 2 and is not implemented in this successor. "
        "Stage 1 grades the completion rule only and cannot report a gate quantity.")


def grade_G2(*_a, **_k):
    raise NotImplementedError("G2 (C_L excursion) is STAGE 2; see grade_G1.")


def grade_G3(*_a, **_k):
    raise NotImplementedError("G3 (admissibility) is STAGE 2; see grade_G1.")


# ========================================================== planted controls (rule 3)
# Every control below drives the SHIPPED functions above.  None re-implements the
# comparison inside the test.  Two MUTATION controls (C-M1, C-M2) prove that dependency
# by replacing a shipped function and requiring the suite to go RED.
def _openfoam_time_name(value):
    """The FIXTURE's route to a time-directory name: FORMATTING from the number.

    L-321: the fixture must build the artifact by a DIFFERENT ROUTE than the reader
    resolves it.  The reader parses names into numbers; this formats a number into a
    name, the way OpenFOAM's own general float output does.  Their agreement therefore
    carries information.
    """
    text = "%.*g" % (SIGNIFICANT_FIGURES, value)
    return text


def _build_synthetic_case(root, time_name=None, n_steps=12, wall_seconds=1200.0,
                          drop_field=None, drop_record=False, blank_end_on=None,
                          last_time=None, extra_time_dir=None, stale_field=None,
                          no_time_dir=False, coeff_rows=None):
    """A synthetic run tree.  Nothing here reads F5b's artifacts."""
    case = os.path.join(root, "case")
    os.makedirs(case)
    end_value = float(END_TIME_STR)
    time_name = time_name if time_name is not None else _openfoam_time_name(end_value)

    zero = os.path.join(case, "0")
    os.makedirs(zero)
    for field in REQUIRED_FIELDS:
        with open(os.path.join(zero, field), "w") as fh:
            fh.write("0\n")
        os.utime(os.path.join(zero, field), (900.0, 900.0))
    os.utime(os.path.join(zero, "nut"), (1000.0, 1000.0))   # written last, as E2 writes

    if not no_time_dir:
        tdir = os.path.join(case, time_name)
        os.makedirs(tdir)
        for field in REQUIRED_FIELDS:
            if field == drop_field:
                continue
            path = os.path.join(tdir, field)
            with open(path, "w") as fh:
                fh.write("x\n")
            os.utime(path, (2000.0, 2000.0))
        if stale_field:
            os.utime(os.path.join(tdir, stale_field), (500.0, 500.0))
    if extra_time_dir:
        os.makedirs(os.path.join(case, extra_time_dir))

    for name in PRELUDE_LOGS:
        with open(os.path.join(case, name), "w") as fh:
            fh.write("" if name == blank_end_on else "End\n")

    shown_last = last_time if last_time is not None else time_name
    lines = []
    for step in range(n_steps):
        value = end_value * (step + 1) / n_steps
        stamp = shown_last if step == n_steps - 1 else "%.8g" % value
        lines.append("Time = %s" % stamp)
        lines.append("Courant Number mean: 0.1 max: 0.4")
        lines.append("ExecutionTime = %.2f s" % (step + 1))
    header = ["Courant Number mean: 0.0 max: 0.0", "Courant Number mean: 0.0 max: 0.0"]
    with open(os.path.join(case, "log.pimpleFoam"), "w") as fh:
        fh.write("\n".join(header + lines) + "\nEnd\n")

    pp = os.path.join(case, "postProcessing", "forceCoeffs1", "0")
    os.makedirs(pp)
    rows = n_steps if coeff_rows is None else coeff_rows
    with open(os.path.join(pp, "coefficient.dat"), "w") as fh:
        fh.write("# Time Cd Cl\n")
        for step in range(rows):
            fh.write("%g\t0.1\t0.2\n" % (end_value * (step + 1) / n_steps))

    if not drop_record:
        with open(os.path.join(root, "record.json"), "w") as fh:
            json.dump({"n_steps": n_steps, "wall_seconds": wall_seconds}, fh)
    return case


def _expect(condition, message):
    if not condition:
        raise ControlFailure(message)


def _subprocess_rc(args, env=None):
    merged = dict(os.environ)
    merged.update(env or {})
    proc = subprocess.run([sys.executable] + args, capture_output=True, text=True,
                          env=merged)
    return proc.returncode, proc.stdout, proc.stderr


def run_selftest():
    """Returns 0 if every control behaved as registered, EXIT_REFUSE otherwise."""
    me = os.path.abspath(__file__)
    fired = []
    root = tempfile.mkdtemp(prefix="f5b_succ_")
    try:
        # ---- C-N1  the clean tree: every clause must be able to PASS ---------------
        base = os.path.join(root, "N1")
        os.makedirs(base)
        case = _build_synthetic_case(base)
        comp, tdir, rule = check_completion(case)
        _expect(comp.all_ok, "C-N1 clean tree failed clauses %r -- a reader that cannot "
                             "pass a good tree cannot report a failure either" % (comp.failing(),))
        _expect(os.path.basename(tdir) == "21.944",
                "C-N1 resolved %r; OpenFOAM's own formatting of the registered endTime "
                "is '21.944'" % os.path.basename(tdir))
        _expect(rule == "exact", "C-N1 resolved by the %r rule, expected 'exact'" % rule)
        fired.append("C-N1 clean tree, endTime written as OpenFOAM writes it -> ALL PASS")

        # ---- C-P0  THE DEFECT ITSELF, planted --------------------------------------
        # The predecessor looked for the literal '21.9440'.  Both spellings must resolve.
        for spelling in ("21.9440", "21.944", "2.19440e+01"):
            sub = os.path.join(root, "P0_" + spelling)
            os.makedirs(sub)
            case = _build_synthetic_case(sub, time_name=spelling)
            comp, tdir, rule = check_completion(case)
            _expect(comp.all_ok,
                    "C-P0 spelling %r failed clauses %r -- the successor is still "
                    "string-locked" % (spelling, comp.failing()))
            _expect(os.path.basename(tdir) == spelling,
                    "C-P0 resolved %r, expected %r" % (os.path.basename(tdir), spelling))
        fired.append("C-P0 endTime spellings 21.9440 / 21.944 / 2.19440e+01 -> ALL "
                     "RESOLVE (the L-321 defect, planted and repaired)")

        # ---- C-P1  no endTime directory -> REFUSE with rc 2, never a crash ---------
        sub = os.path.join(root, "P1")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, no_time_dir=True)
        rc, out, err = _subprocess_rc([me, "--case", case])
        _expect(rc == EXIT_REFUSE,
                "C-P1 owed a REFUSAL (rc %d) and returned rc %d.  A crash is not a "
                "refusal (§2ak).  stderr tail: %r" % (EXIT_REFUSE, rc, err[-300:]))
        _expect("REFUSE" in out or "REFUSE" in err, "C-P1 refused without saying so")
        fired.append("C-P1 endTime directory absent -> rc 2 through the real entry point")

        # ---- C-P2  two directories inside the write quantum -> REFUSE, never choose -
        sub = os.path.join(root, "P2")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, time_name="21.944", extra_time_dir="21.94400")
        rc, _out, err = _subprocess_rc([me, "--case", case])
        _expect(rc == EXIT_REFUSE,
                "C-P2 ambiguity owed rc %d, got %d -- the reader chose instead of "
                "declining" % (EXIT_REFUSE, rc))
        fired.append("C-P2 two directories resolving to endTime -> rc 2, no choice made")

        # ---- C-P3  clause 4, each required field in turn ---------------------------
        for field in REQUIRED_FIELDS:
            sub = os.path.join(root, "P3_" + field)
            os.makedirs(sub)
            case = _build_synthetic_case(sub, drop_field=field)
            comp, _t, _r = check_completion(case)
            _expect(comp.failing() == [4],
                    "C-P3 dropping %s failed clauses %r, expected exactly [4]"
                    % (field, comp.failing()))
            _expect(field in comp.rows[3]["detail"],
                    "C-P3 clause 4 did not name the missing field %s" % field)
        fired.append("C-P3 each of %s removed in turn -> clause 4 only, field named"
                     % (list(REQUIRED_FIELDS),))

        # ---- C-P4  clause 6 age guard ----------------------------------------------
        sub = os.path.join(root, "P4")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, stale_field="U")
        comp, _t, _r = check_completion(case)
        _expect(6 in comp.failing(),
                "C-P4 back-dated an endTime field below max(mtime over 0/) and the age "
                "guard stayed green: failing %r" % (comp.failing(),))
        fired.append("C-P4 endTime field older than 0/ -> clause 6 fails")

        # ---- C-P5  clause 1's INDEPENDENT operand (L-320) --------------------------
        sub = os.path.join(root, "P5")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, drop_record=True)
        comp, _t, _r = check_completion(case)
        _expect(1 in comp.failing(),
                "C-P5 removed record.json -- the operand L-320 found had NEVER been "
                "falsified in a passing run -- and clause 1 stayed green")
        fired.append("C-P5 record.json absent -> clause 1 fails (L-320's load-bearing "
                     "operand, not the cheap one)")

        # ---- C-P6  clause 1's dependent operand, and clause 3, and clause 8 --------
        sub = os.path.join(root, "P6")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, blank_end_on="log.checkMesh")
        _expect(1 in check_completion(case)[0].failing(), "C-P6 prelude End not seen")
        sub = os.path.join(root, "P7")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, last_time="20.0000")
        _expect(3 in check_completion(case)[0].failing(), "C-P7 wrong last time not seen")
        sub = os.path.join(root, "P8")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, wall_seconds=WALL_CAP_S + 1.0)
        _expect(8 in check_completion(case)[0].failing(), "C-P8 cap overrun not seen")
        sub = os.path.join(root, "P9")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, coeff_rows=3)
        _expect(5 in check_completion(case)[0].failing(), "C-P9 step-count mismatch not seen")
        fired.append("C-P6/7/8/9 prelude End, last time, cap, step count -> each fails "
                     "its own clause")

        # ---- C-P10  a crash is NOT a refusal ---------------------------------------
        sub = os.path.join(root, "P10")
        os.makedirs(sub)
        case = _build_synthetic_case(sub)
        rc, out, err = _subprocess_rc([me, "--case", case, "--inject-instrument-error"])
        _expect(rc == EXIT_INSTRUMENT_ERROR,
                "C-P10 injected an internal error and got rc %d; §2ak requires %d, and "
                "requires it to differ from the refusal code %d"
                % (rc, EXIT_INSTRUMENT_ERROR, EXIT_REFUSE))
        _expect("instrument_error" in out,
                "C-P10 crashed without emitting its record -- §2ak's emission duty")
        _expect("Traceback" in err, "C-P10 emitted no traceback on stderr")
        fired.append("C-P10 injected internal error -> rc 70, record emitted, traceback "
                     "on stderr (a crash is not a refusal)")

        # ---- C-M1 / C-M2  the plants drive the SHIPPED code, proven by mutation ----
        # L-479's sibling finding: a checker whose entire check() could be deleted with
        # --selftest still reporting every plant fired.  These two controls make that
        # impossible to claim: replace a shipped function, require the suite to go RED.
        mutants = [
            ("C-M1", "check_completion",
             "lambda *a, **k: (_AllOk(), '/dev/null', 'exact')"),
            ("C-M2", "resolve_end_time_dir",
             "lambda *a, **k: ('/dev/null', 'exact', [])"),
        ]
        for tag, target, replacement in mutants:
            program = (
                "import importlib.util, sys\n"
                "spec = importlib.util.spec_from_file_location('m', %r)\n"
                "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
                "class _AllOk:\n"
                "    rows = [{'clause': i, 'name': 'x', 'ok': True, 'detail': ''} "
                "for i in range(1, 9)]\n"
                "    all_ok = True\n"
                "    def failing(self): return []\n"
                "m.__dict__['_AllOk'] = _AllOk\n"
                "m.%s = eval(%r, m.__dict__)\n"
                "sys.exit(m.run_selftest())\n" % (me, target, replacement))
            rc, _out, _err = _subprocess_rc(["-c", program])
            _expect(rc != 0,
                    "%s replaced the shipped %s() and the control suite STILL reported "
                    "green (rc 0).  The plants are not driving the shipped code."
                    % (tag, target))
            fired.append("%s shipped %s() replaced -> suite goes RED (rc %d)"
                         % (tag, target, rc))

        print("PLANTED CONTROLS -- every one drove the shipped code path")
        for line in fired:
            print("  FIRED  %s" % line)
        print("controls fired: %d" % len(fired))
        return EXIT_OK
    except ControlFailure as exc:
        print("CONTROL FAILURE: %s" % exc)
        print("This instrument's numbers are NOT evidence.  Nothing may be graded with it.")
        return EXIT_REFUSE
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ===================================================================== entry point
def _emit(record):
    print(json.dumps(record, indent=2, sort_keys=True))


def _run(argv):
    if "--selftest" in argv:
        return run_selftest()
    if "--case" not in argv:
        print("usage: %s --case <case_dir> [--record <record.json>] | --selftest"
              % os.path.basename(__file__))
        return EXIT_REFUSE
    case_dir = argv[argv.index("--case") + 1]
    record_path = argv[argv.index("--record") + 1] if "--record" in argv else None
    if "--inject-instrument-error" in argv:
        raise RuntimeError("INJECTED instrument error (control C-P10) -- this message "
                           "can only appear when --inject-instrument-error is passed")
    comp, time_dir, rule = check_completion(case_dir, record_path)
    verdict = "COMPLETION CLAUSES ALL HOLD" if comp.all_ok else "NOT A RESULT"
    _emit({
        "comparator": os.path.abspath(__file__),
        "comparator_blob_sha": own_blob_sha(),
        "stage": "1 -- completion rule only; gates G1/G2/G3 NOT implemented",
        "case": os.path.abspath(case_dir),
        "end_time_registered": END_TIME_STR,
        "end_time_dir_resolved": time_dir,
        "resolution_rule": rule,
        "clauses": comp.rows,
        "failing_clauses": comp.failing(),
        "verdict": verdict,
        "note": "A completion verdict is NOT a rung verdict.  The gate is unevaluated "
                "by construction at stage 1.",
    })
    return EXIT_OK


def main(argv):
    try:
        return _run(argv)
    except Refusal as exc:
        print("REFUSE: %s" % exc)
        sys.stderr.write("REFUSE: %s\n" % exc)
        return EXIT_REFUSE
    except NotImplementedError as exc:
        print("REFUSE: %s" % exc)
        sys.stderr.write("REFUSE: %s\n" % exc)
        return EXIT_REFUSE
    except BaseException as exc:                       # §2ak: emit, then exit 70
        tb = traceback.extract_tb(sys.exc_info()[2])
        site = tb[-1] if tb else None
        try:
            _emit({
                "comparator": os.path.abspath(__file__),
                "comparator_blob_sha": own_blob_sha(),
                "verdict": "NOT A RESULT",
                "instrument_error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "file": getattr(site, "filename", None),
                    "line": getattr(site, "lineno", None),
                },
                "note": "A CRASH IS NOT A REFUSAL (VERIFICATION_CHARTER §2ak).  The run "
                        "is NOT A RESULT and the instrument is a defect finding.",
            })
        finally:
            traceback.print_exc()
        return EXIT_INSTRUMENT_ERROR


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
