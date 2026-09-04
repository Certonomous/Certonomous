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

WHAT THE AGE GUARD GATES  (clause 6; repaired 2026-09-04)
---------------------------------------------------------
CLAUDE.md rule 4 states the age guard over FIELDS: "every field at endTime NEWER than the
case's own `0/T`".  An earlier draft of this file gated every ENTRY returned by
`os.listdir(endTime)`.  F5b is a PITCHING airfoil -- a moving-mesh case -- and its real
endTime directory holds eleven entries of which two are DIRECTORIES (`polyMesh/`,
`uniform/`) and four are non-required fields (`Uf`, `meshPhi`, `phi`, `yPlus`).  A restart,
a mesh reuse or a `polyMesh` carried from an earlier write leaves one of those older than
`0/` while every required field is perfect -- and the run then graded NOT A RESULT on a
mesh directory.  Clause 6 now gates the REQUIRED FIELDS PRESENT and nothing else; every
other entry is REPORTED with its staleness and gates nothing, the same discipline clause 4
already applied to REPORTED_NOT_GATED_FIELDS.  The predicate is printed in the clause
detail so a reader can see exactly what was gated.  `age_guard_partition()` is the shipped
function that makes the split, and control C-M5 replaces it with the old gate-everything
behaviour and requires the suite to go RED.

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
def write_quantum(value, significant_figures=SIGNIFICANT_FIGURES):
    """Half a unit in the last printed place of `value` at `significant_figures` digits.

    A SHIPPED function, not a test helper: `resolve_end_time_dir` calls it, and it is a
    separate function precisely so a control can MUTATE it.  Narrow it to zero and the
    write-quantum match branch dies; widen it and the branch matches a directory from a
    DIFFERENT write.  Controls C-M3 and C-M4 do exactly those two things and require the
    suite to go RED, so the quantum is load-bearing in both directions.
    """
    if value == 0.0:
        return 0.0
    magnitude = abs(value)
    exponent = 0
    while magnitude >= 10.0:
        magnitude /= 10.0
        exponent += 1
    while magnitude < 1.0:
        magnitude *= 10.0
        exponent -= 1
    return 0.5 * 10.0 ** (exponent - (significant_figures - 1))


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
        quantum = write_quantum(value)
        # `quantum > 0.0` is not decoration: a zero quantum must admit NOTHING, not fall
        # back to exact equality (which the branch above has already decided).
        if quantum > 0.0 and abs(value - target) <= quantum:
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
def age_guard_partition(time_dir, required=REQUIRED_FIELDS):
    """Split the endTime directory into what clause 6 GATES and what it only REPORTS.

    A SHIPPED function; control C-M5 replaces it with the old gate-every-entry behaviour
    and requires the suite to go RED.

    GATED    -- the required fields that are PRESENT on disk.  CLAUDE.md rule 4: "every
                field at endTime NEWER than the case's own 0/T".  Fields, not entries.
    REPORTED -- every other entry: non-required fields (Uf, meshPhi, phi, yPlus) and
                DIRECTORIES (polyMesh/, uniform/), which a moving-mesh case such as this
                pitching airfoil writes inside its time directories.  Their mtimes are
                printed beside the verdict and gate NOTHING.
    ABSENT   -- required fields not on disk.  Their absence is CLAUSE 4's finding; clause 6
                cannot date a file that is not there, and must not double-count it.

    Returns (gated, reported, absent), each a sorted list of names.
    """
    entries = sorted(os.listdir(time_dir))
    present = set(entries)
    gated = [f for f in required if f in present]
    absent = [f for f in required if f not in present]
    reported = [e for e in entries if e not in set(required)]
    return gated, reported, absent


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

            def _mtime(name):
                return os.path.getmtime(os.path.join(time_dir, name))

            gated6, reported6, absent6 = age_guard_partition(time_dir)
            stale = [(f, _mtime(f)) for f in gated6 if _mtime(f) <= argmax[1]]
            ok6 = not stale
            reported_ages = {e: ("NOT strictly newer (%.6f)" % _mtime(e))
                             if _mtime(e) <= argmax[1] else "newer" for e in reported6}
            detail6 = (
                "PREDICATE: this clause gates the REQUIRED FIELDS PRESENT at endTime and "
                "NOTHING ELSE -- CLAUDE.md rule 4 states the age guard over FIELDS "
                "('every field at endTime NEWER than the case's own 0/T'), not over every "
                "entry that happens to sit in the directory.\n"
                "max(mtime) over the whole 0/ directory: %s at %.6f (max over the "
                "DIRECTORY, so write order cannot defeat the guard)\n"
                "GATED (required fields present): %s\n"
                "gated fields NOT strictly newer: %s\n"
                "required fields ABSENT -- clause 4's finding, not datable here: %s\n"
                "REPORTED, NOT GATED (non-required entries, including the polyMesh/ and "
                "uniform/ directories a moving-mesh case writes at each write and a "
                "restart or mesh reuse can leave stale without touching the physics): %s\n"
                "reported, not gated: argmax is 0/nut: %s"
                % (argmax[0], argmax[1], gated6, stale or "none", absent6 or "none",
                   reported_ages or "no non-required entries", argmax[0] == "nut"))
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


# The endTime directory of the REAL F5b physics run holds ELEVEN entries --
# `U Uf k meshPhi nut omega p phi polyMesh/ uniform/ yPlus` -- of which two are
# DIRECTORIES and only five are required fields.  A fixture that writes the five required
# fields ALONE is CLEANER THAN ITS SUBJECT, and a control tree simpler than the artifact it
# will grade cannot see a defect that lives in the extra entries.  These two tuples exist
# so the fixture is shaped like the thing it grades.  They are FIXTURE shape, taken from a
# directory listing, NOT constants from the registration: nothing below is required of a
# run, and no clause is keyed to them.
FIXTURE_EXTRA_FILES = ("Uf", "meshPhi", "phi", "yPlus")
FIXTURE_EXTRA_DIRS = ("polyMesh", "uniform")


def _build_synthetic_case(root, time_name=None, n_steps=12, wall_seconds=1200.0,
                          drop_field=None, drop_record=False, blank_end_on=None,
                          last_time=None, extra_time_dir=None, stale_field=None,
                          no_time_dir=False, coeff_rows=None, stale_extra=None):
    """A synthetic run tree, shaped like the real one.  Nothing here reads F5b's artifacts.

    `stale_extra` back-dates NON-REQUIRED entries (files or directories) inside the endTime
    directory below 0/'s argmax; `stale_field` back-dates a REQUIRED field.  The two knobs
    are separate because clause 6 must answer them differently.
    """
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
        # the non-required company the real directory keeps: four extra fields and two
        # DIRECTORIES, all newer than 0/ unless a control back-dates one.
        for name in FIXTURE_EXTRA_FILES:
            path = os.path.join(tdir, name)
            with open(path, "w") as fh:
                fh.write("x\n")
            os.utime(path, (2000.0, 2000.0))
        for name in FIXTURE_EXTRA_DIRS:
            sub_dir = os.path.join(tdir, name)
            os.makedirs(sub_dir)
            inner = os.path.join(sub_dir, "points" if name == "polyMesh" else "time")
            with open(inner, "w") as fh:
                fh.write("x\n")
            os.utime(inner, (2000.0, 2000.0))
            os.utime(sub_dir, (2000.0, 2000.0))   # after its contents, or the write wins
        if stale_field:
            os.utime(os.path.join(tdir, stale_field), (500.0, 500.0))
        for name in (stale_extra or ()):
            os.utime(os.path.join(tdir, name), (500.0, 500.0))
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


def run_selftest(include_mutations=True):
    """Returns 0 if every control behaved as registered, EXIT_REFUSE otherwise.

    `include_mutations=False` is used ONLY by the mutation controls' own child processes,
    which re-enter this suite with one shipped function replaced.  Without it a mutation
    that survives the planted controls would reach the mutation block and spawn a further
    generation of itself without bound -- measured, not feared: C-M4 (a WIDENED write
    quantum) did exactly that on 2026-09-04 and the suite never returned.  The flag is a
    PARAMETER, never an environment variable, so no ambient setting can make a top-level
    `--selftest` skip the mutation controls and still print green: `--selftest` from the
    command line always takes the default.
    """
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

        # ---- C-P2  EXACT-branch ambiguity -> REFUSE, never choose --------------------
        # CORRECTED 2026-09-04.  This control's earlier comment claimed it exercised "two
        # directories inside the write quantum".  IT DOES NOT, and never did: '21.944' and
        # '21.94400' parse to the IDENTICAL double, so `exact` holds two names and the
        # EXACT-branch refusal fires.  The write-quantum branches are a different code path
        # and had NO control at all; they are C-P2b, C-P2c and C-P2d below.  The refusal
        # BRANCH is now asserted, not just the exit code, so this control can no longer be
        # mistaken for coverage it does not provide.
        sub = os.path.join(root, "P2")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, time_name="21.944", extra_time_dir="21.94400")
        rc, out, err = _subprocess_rc([me, "--case", case])
        _expect(rc == EXIT_REFUSE,
                "C-P2 ambiguity owed rc %d, got %d -- the reader chose instead of "
                "declining" % (EXIT_REFUSE, rc))
        _expect("parse to endTime" in (out + err),
                "C-P2 refused, but NOT by the exact-parse-equality branch it exists to "
                "cover: %r" % ((out + err)[-300:],))
        fired.append("C-P2 two directories parsing to endTime EXACTLY -> rc 2 by the "
                     "exact branch, no choice made")

        # ---- C-P2b  WRITE-QUANTUM-branch ambiguity -> REFUSE, and BY THAT BRANCH -----
        # 21.94401 and 21.94399 both sit 1e-5 from 21.9440 -- inside the 5e-5 quantum --
        # and NEITHER parses equal to it, so the exact branch is empty and the second,
        # narrower refusal fires.  Before 2026-09-04 no control reached it.
        sub = os.path.join(root, "P2b")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, time_name="21.94401", last_time=END_TIME_STR,
                                     extra_time_dir="21.94399")
        # IN-PROCESS first.  A control that only ever asserts a SUBPROCESS's exit code is
        # blind to any mutation of this module -- the child re-reads the file from disk --
        # so the branch assertion is made here, where C-M3/C-M4 can reach it.
        try:
            bad = resolve_end_time_dir(case)
            raise ControlFailure(
                "C-P2b: two directories inside the write quantum and the reader CHOSE "
                "%r instead of declining" % (bad[0],))
        except Refusal as exc:
            _expect("significant-figure write" in str(exc),
                    "C-P2b refused, but not by the WRITE-QUANTUM branch -- the exact "
                    "branch or the no-candidate branch answered instead: %s" % exc)
        rc, out, err = _subprocess_rc([me, "--case", case])
        _expect(rc == EXIT_REFUSE,
                "C-P2b write-quantum ambiguity owed rc %d, got %d" % (EXIT_REFUSE, rc))
        _expect("significant-figure write" in (out + err),
                "C-P2b refused end-to-end, but not by the WRITE-QUANTUM branch: %r"
                % ((out + err)[-300:],))
        fired.append("C-P2b two directories inside the write quantum, neither exact -> "
                     "rc 2 BY THE WRITE-QUANTUM BRANCH (previously uncovered)")

        # ---- C-P2c  WRITE-QUANTUM MATCH -- the branch that RESOLVES -------------------
        # The narrower half of the repair.  A directory named 21.94401 against a registered
        # 21.9440: no parse equality, one candidate inside the quantum, so it resolves and
        # the rule is 'write-quantum'.  C-N1 and C-P0 can never produce this -- all three
        # of C-P0's spellings parse to the identical double and resolve by 'exact'.
        sub = os.path.join(root, "P2c")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, time_name="21.94401", last_time=END_TIME_STR)
        try:
            path2c, rule2c, _cands = resolve_end_time_dir(case)
        except Refusal as exc:
            raise ControlFailure(
                "C-P2c: a directory 1e-5 from endTime %s -- INSIDE the %d-significant-"
                "figure write quantum -- did not resolve at all: %s"
                % (END_TIME_STR, SIGNIFICANT_FIGURES, exc))
        _expect(rule2c == "write-quantum",
                "C-P2c resolved by the %r rule; the write-quantum branch was meant to "
                "answer and did not" % (rule2c,))
        _expect(os.path.basename(path2c) == "21.94401",
                "C-P2c resolved %r, expected '21.94401'" % os.path.basename(path2c))
        comp, _t, rule2c_full = check_completion(case)
        _expect(comp.all_ok,
                "C-P2c write-quantum resolution reached the clauses and they failed %r"
                % (comp.failing(),))
        _expect(rule2c_full == "write-quantum",
                "C-P2c: check_completion reported rule %r" % (rule2c_full,))
        fired.append("C-P2c one directory inside the write quantum, none exact -> RESOLVES "
                     "by the write-quantum rule and all clauses pass (previously uncovered)")

        # ---- C-P2d  the quantum stays NARROW -----------------------------------------
        # 21.9445 is 5e-4 from the registered endTime -- TEN quanta away, a DIFFERENT
        # write.  It must not be adopted.  This is the other direction of C-P2c: together
        # they pin the quantum's value, not merely the existence of the branch.
        sub = os.path.join(root, "P2d")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, time_name="21.9445", last_time=END_TIME_STR)
        # IN-PROCESS, for the same reason as C-P2b: a subprocess re-reads the clean file
        # and would report a widened quantum as green.
        try:
            adopted = resolve_end_time_dir(case)
            raise ControlFailure(
                "C-P2d adopted %r by the %r rule.  21.9445 is 5e-4 from endTime %s -- TEN "
                "write quanta, a DIFFERENT write -- and the guard is no longer narrow."
                % (os.path.basename(adopted[0]), adopted[1], END_TIME_STR))
        except Refusal:
            pass
        rc, out, err = _subprocess_rc([me, "--case", case])
        _expect(rc == EXIT_REFUSE,
                "C-P2d adopted a directory 5e-4 from endTime %s end-to-end (rc %d)"
                % (END_TIME_STR, rc))
        _expect("does not fall back to the latest" in (out + err),
                "C-P2d refused, but not by the no-candidate branch: %r"
                % ((out + err)[-300:],))
        fired.append("C-P2d a directory ten write quanta away -> rc 2, NOT adopted (the "
                     "quantum's value is pinned in both directions)")

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
        fired.append("C-P4 endTime REQUIRED field older than 0/ -> clause 6 fails")

        # ---- C-P4b  clause 6 gates FIELDS, not every entry ---------------------------
        # THE DEFECT THIS REPAIRS.  F5b is a PITCHING airfoil; its real endTime directory
        # carries polyMesh/ and uniform/ beside the fields, and a restart or a mesh reuse
        # leaves one of them older than 0/ while every required field is perfect.  Gating
        # on them manufactures a NOT A RESULT out of a sound run.  The fixture now builds
        # that company (FIXTURE_EXTRA_FILES / FIXTURE_EXTRA_DIRS), so this control can see
        # it -- a tree simpler than its subject could not.
        sub = os.path.join(root, "P4b")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, stale_extra=("polyMesh", "meshPhi"))
        comp, _t, _r = check_completion(case)
        _expect(comp.failing() == [],
                "C-P4b back-dated polyMesh/ (a DIRECTORY) and meshPhi -- NEITHER is a "
                "required field, and all five required fields are present and newer -- and "
                "the completion rule failed clauses %r.  CLAUDE.md rule 4's age guard is "
                "about FIELDS." % (comp.failing(),))
        detail6 = comp.rows[5]["detail"]
        _expect("polyMesh" in detail6 and "meshPhi" in detail6,
                "C-P4b clause 6 passed but did not REPORT the stale non-gated entries; "
                "not gated is not the same as not shown")
        # ...and the guard must still BITE when a required field is stale in that same
        # company, or the repair has merely disabled clause 6.
        sub = os.path.join(root, "P4c")
        os.makedirs(sub)
        case = _build_synthetic_case(sub, stale_extra=("polyMesh",), stale_field="omega")
        _expect(6 in check_completion(case)[0].failing(),
                "C-P4c a stale REQUIRED field alongside a stale polyMesh/ and clause 6 "
                "stayed green -- the repair disabled the guard instead of narrowing it")
        fired.append("C-P4b/C-P4c stale polyMesh/ + meshPhi -> clause 6 PASSES and reports "
                     "them; a stale required field beside them -> clause 6 still FAILS")

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
        # C-M3/C-M4/C-M5 added 2026-09-04: a control that never enters its branch is a
        # memory of a guard, not a guard.  Each of the three breaks ONE branch of the
        # repair and requires the suite to go RED, which is what makes C-P2b/C-P2c/C-P2d
        # and C-P4b coverage rather than decoration.
        mutants = [] if not include_mutations else [
            ("C-M1", "check_completion",
             "lambda *a, **k: (_AllOk(), '/dev/null', 'exact')"),
            ("C-M2", "resolve_end_time_dir",
             "lambda *a, **k: ('/dev/null', 'exact', [])"),
            # the write quantum narrowed to nothing: the MATCH branch can never fire
            ("C-M3", "write_quantum", "lambda *a, **k: 0.0"),
            # the write quantum widened: it adopts a directory from a DIFFERENT write
            ("C-M4", "write_quantum", "lambda *a, **k: 1.0"),
            # clause 6 back to gating EVERY entry -- the defect itself, replanted
            ("C-M5", "age_guard_partition",
             "lambda d, *a, **k: (sorted(os.listdir(d)), [], [])"),
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
                # include_mutations=False: the child re-enters the PLANTED controls with one
                # shipped function replaced, and must NOT re-enter this mutation block --
                # a surviving mutant would otherwise spawn its own generation without bound.
                "sys.exit(m.run_selftest(include_mutations=False))\n"
                % (me, target, replacement))
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
        print("mutation controls: %s"
              % ("INCLUDED" if include_mutations
                 else "NOT re-entered -- this is a nested mutation child, not a top-level "
                      "selftest, and its green says nothing about the mutation controls"))
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
