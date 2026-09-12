#!/usr/bin/env python3
"""check_clause_demonstrated.py v1.1 - the executable check shipping with L-529.

THE PROPOSITION UNDER TEST
--------------------------
A grader clause can be IMPLEMENTED, look green, and be UNSATISFIABLE BY ITS REAL
PRODUCER. Its green is then the ABSENCE OF A READING, not a reading: the clause
has only ever been satisfied by fixtures the check itself wrote, and no artifact
the real producer can emit will ever satisfy it. From the outside that is
indistinguishable from a clause that passed.

L-529's operative test is TWO questions, both answered by EXECUTION:

    (a) Has this guard ever been SHOWN TO FIRE, on a planted condition it must
        catch?
    (b) Can anything ACTUALLY MAKE IT PASS - a real artifact from the real
        producer, not a fixture the check itself wrote?

This file makes (b) executable. It takes a NAMED grader clause, LOCATES it in the
grader by `ast` (never by import, never by transcription), derives the clause's
own patterns FROM THE GRADER'S SOURCE, then reads the REAL PRODUCER ARTIFACTS off
disk and asks whether any non-fixture artifact satisfies it.

THE PAID EXAMPLE, WHICH IS THIS FILE'S NEGATIVE CONTROL
------------------------------------------------------
`grade_r5d.py:296` implements rule-4 clause 5 as `n_exec == write_iter`, where
`n_exec` counts `ExecutionTime = ` lines in `log.frozen`. The producer,
`kCorrectiveFrozenFoam.C`, emits that string at ONE source line, `:192`, and its
outer `while (runTime.loop())` at `:106` CLOSES AT `:166` - so the emit is
outside the loop and every producible run emits it exactly ONCE, while
`write_iter` is the settle iteration and runs into the thousands. Measured here
over the two registered 27-case populations: n_exec is 1 on 54 of 54, and 0 of 54
satisfy the clause. The value 120 - the only value ever seen to match a write
iteration - occurs on this box ONLY under `grading_scratch/selftest/`.

THREE VERDICTS, NEVER TWO, AND NEVER MERGED
-------------------------------------------
    DEMONSTRATED       a NAMED non-fixture artifact satisfies the clause
    NOT-DEMONSTRATED   enough non-fixture artifacts were READ to say that none
                       of them does - a finding about the clause
    HALF-DEMONSTRATED  the clause was located but the population could not be
    / COULD-NOT-RUN    read, or was too small to speak for, or consisted only of
                       fixtures. NOT a pass and NOT a finding.

Collapsing the third into either of the other two is the defect, not a
simplification: "no real artifact satisfies it" and "no real artifact was read"
are the two states L-529 says a reader must never have to tell apart afterwards.

THE VERDICT IS UNUTTERABLE WITHOUT ITS POPULATION
-------------------------------------------------
This is the structural repair that `scripts/check_bar_above_floor.py` v1.1
carries, and it is copied here as discipline rather than as code. The clean
sentence is built by ONE function that takes the population counts as arguments
and REFUSES if the screened count is zero or if no witness artifact is named. An
empty population is rc=3: a check that read nothing is not a pass. v1.0 of the
L-530 instrument printed a clean verdict over an empty table and exited 0, and
the cause was that not one of its nine fixtures was EMPTY. Three of the fixtures
below are empty reads, by name.

FIXTURE-VS-REAL IS A DECLARED, INSPECTABLE RULE
-----------------------------------------------
Never a hidden heuristic. The rule is printed in every run, in two layers:

  LAYER 1 (FIXTURE)  an artifact whose path carries any declared fixture marker
                     as a path component substring is a FIXTURE.
  LAYER 2 (REAL)     a non-fixture artifact is REAL only if a committed REGISTRY
                     names its case - here `frozen_inventory.json`, the very file
                     `grade_r5d.py`'s own G0 gate reads to choose its donor.
  OTHERWISE          UNCLASSIFIED. It is NAMED, it is counted, and it NEVER
                     silently becomes real.

An UNCLASSIFIED or FIXTURE artifact that SATISFIES the clause while every REAL
one fails does not turn the verdict green. It is printed as the L-529 SIGNATURE,
with every such artifact named, because that pattern - green only where the
producer was not the producer - IS the defect. Measured on this box, clause 5 has
exactly one such artifact, `closure-data/r4/ktest3`, an unregistered developer
smoke directory whose k diverges to 1e109 and which wrote fields at ITERATION 1 -
the single write iteration at which a once-per-run emit can coincide with a
per-iteration count. It is reported, by name, in the negative run below.

REFUSAL DISCIPLINE
------------------
Never an `assert` (L-332 / D476 31.3: asserts vanish under `python3 -O`). Every
refusal is an explicit exit with a printed reason, and `--selftest` is green
under BOTH `python3` and `python3 -O`.

USAGE
-----
    check_clause_demonstrated.py --clause R5D_RULE4_CLAUSE5
    check_clause_demonstrated.py --list
    check_clause_demonstrated.py --clause K --search-root DIR [--search-root DIR]
                                 [--registry FILE] [--min-real N] [--emit-json]
    check_clause_demonstrated.py --selftest

EXIT CODES - NO TWO STATES A CALLER MUST DISTINGUISH SHARE A CODE
-----------------------------------------------------------------
v1.0 shipped a COLLISION and it bit a reader twice in twenty minutes: argparse
exits 2 on a usage error, and v1.0 exited 2 for a genuine NOT-DEMONSTRATED
finding. A mistyped flag therefore returned the same code as "this clause is
unreachable by its real producer" - a false FINDING manufactured out of operator
error, which is the worst direction for the error to run in. It is the family
L-529 names, inverted: a RED that is an artifact of the harness, not a reading.

    code  meaning                                   is it a verdict?
    ----  ----------------------------------------  ----------------
     0    DEMONSTRATED - a NAMED non-fixture         YES, and 0 is
          artifact satisfies the clause              ONLY ever this
     1    INTERNAL ERROR - an uncaught exception,    no
          reported explicitly rather than as a
          bare traceback (a crash that swallows
          findings is not refusal discipline)
     2    NOT-DEMONSTRATED - a FINDING: enough       YES
          real artifacts were read, none satisfies
     3    HALF-DEMONSTRATED / COULD-NOT-RUN -        no (and never 0)
          clause not located, artifact root absent,
          empty / too-small / fixtures-only real
          population. A check that read nothing is
          not a pass.
     4    USAGE - a bad or missing flag, --help,     no
          --list. argparse's own exits are REMAPPED
          here, so no operator typo can ever be
          mistaken for a finding, and no
          informational limb can ever return 0.

The one documented exception: `--selftest` itself exits 0 when green and 2 when
not. A caller running `--selftest` is not asking for a verdict about a clause,
so the two states are never confusable in practice - but it is stated here
rather than left to be discovered.

Every one of the five is DRIVEN AND OBSERVED in `--selftest`, code 1 included
(via `--selftest-internal-error`, which exists solely so the code-1 handler is
shown to fire rather than assumed to).

EXCLUSION ON THE AUTHORITY OF A COMMITTED RECORD, NOT A NAME HEURISTIC
----------------------------------------------------------------------
A fourth bucket, EXCLUDED-BY-RECORD, holds artifacts a committed repository
record declares are not target extractions. The citation is checked at run time:
the record is read, the cited line range is read, and the declared quote must be
FOUND THERE and the case name must be named there. If the citation does not
verify, the exclusion is NOT applied and the artifact falls back to UNCLASSIFIED
- the conservative bucket - with the failure printed. An exclusion that cannot
show its record does not get to exclude anything.
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import tempfile

VERSION = "1.1"

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CLOSURE = os.path.join(_REPO, "cases", "RANS_LES_closure_models")

# ---------------------------------------------------------------------------
# THE DECLARED FIXTURE RULE. Printed on every run. A marker matches when it
# appears as a substring of any single path COMPONENT, case-folded.
# ---------------------------------------------------------------------------
FIXTURE_MARKERS = ("selftest", "grading_scratch", "scratch", "fixture",
                   "synthetic", "mock")

# A real population smaller than this cannot carry a NOT-DEMONSTRATED finding.
DEFAULT_MIN_REAL = 10


RC_DEMONSTRATED = 0
RC_INTERNAL = 1
RC_NOT_DEMONSTRATED = 2
RC_COULD_NOT_RUN = 3
RC_USAGE = 4


def _fail(code, msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(code)


def usage(msg):
    """A usage error is NOT a finding, and must never share 2 with one."""
    sys.stderr.write("USAGE ERROR (this is not a verdict): %s\n" % msg)
    sys.exit(RC_USAGE)


def refuse(msg):
    """A finding. The clause is not demonstrated by any real artifact."""
    _fail(RC_NOT_DEMONSTRATED, msg)


def unreadable(msg):
    """A check that could not be made is not a pass (L-529)."""
    sys.stderr.write("REFUSED (check could not be made): %s\n" % msg)
    sys.exit(RC_COULD_NOT_RUN)


# ===========================================================================
#  THE CLAUSE REGISTRY
#
#  Every pattern a predicate uses is EXTRACTED FROM THE GRADER'S SOURCE by
#  `ast`, never transcribed here: `pattern_from` names (file, function, call,
#  index) and the literal is read out of the tree. A number this repository
#  already holds is read, not copied (constraint 1).
# ===========================================================================
_R5D_GRADER = os.path.join(_CLOSURE, "R5D_identity_preserving_completion",
                           "grade_r5d.py")
_R4_LIB = os.path.join(_CLOSURE, "R4_sparta_build", "r4_lib.py")
_REGISTRY_JSON = os.path.join(_CLOSURE, "R4_sparta_build", "artefacts",
                              "frozen_inventory.json")

_FROZEN_POPULATION = {
    # The two registered frozen-extraction populations. L-529 measured this
    # clause "on 54 records across two independent populations (0 of 27 and
    # 0 of 27)" - these are those two roots.
    "search_roots": ["/home/ubuntu/closure-data",
                     os.path.join(_REPO, "verification", "runs")],
    "artifact_name": "log.frozen",
    "real_roots": ["/home/ubuntu/closure-data/r4/frozen",
                   "/home/ubuntu/closure-data/r5c/frozen"],
    "registry": {"path": _REGISTRY_JSON, "key": "inventory", "field": "case"},
    # LAYER 1b - exclusion on the authority of a COMMITTED RECORD, cited by
    # path and line, and VERIFIED at run time. Not a name heuristic: the quote
    # must be found in the cited range and the case must be named there.
    "excluded_by_record": [
        {"cases": ["ktest", "ktest2", "ktest3", "ktestA", "ktestB"],
         "under": "/home/ubuntu/closure-data/r4",
         "record": os.path.join(_CLOSURE, "R4_sparta_build", "RESULTS.md"),
         "lines": [70, 78],
         "quotes": ["this lane's own convergence diagnostics",
                    "Neither feeds any number in this file."],
         "corroboration": (
             "cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md:1336 - "
             "'NOT a grid family - k-transport tests on one mesh'; and "
             "R4_sparta_build/RESULTS.md:181-184 records each one's outcome as "
             "NOT CONVERGED, :1008 enumerates all five as 'the five "
             "convergence diagnostics of sec. 2.3'")},
    ],
}

CLAUSES = {
    "R5D_RULE4_CLAUSE5": {
        "what": "rule-4 completion clause 5: n_exec == write_iter",
        "grader": _R5D_GRADER,
        "function": "completion_rule4",
        "registered_line": 296,
        "locate": {"kind": "subscript_assign", "target": "info",
                   "key": "exec_count_ok"},
        "producer": ("sdk/openfoam/sparta/kCorrectiveFrozenFoam/"
                     "kCorrectiveFrozenFoam.C:192 (emit) vs :106-:166 "
                     "(while (runTime.loop()) open..close) - emit is OUTSIDE "
                     "the loop, so the channel is once-per-RUN, not "
                     "once-per-ITERATION"),
        "predicate": {
            "kind": "count_equals_capture",
            "count_pattern_from": {"file": _R5D_GRADER,
                                   "function": "completion_rule4",
                                   "call": "re.findall", "index": 0, "arg": 0},
            "capture_pattern_from": {"file": _R4_LIB,
                                     "function": "frozen_complete",
                                     "call": "re.search", "index": 3, "arg": 0},
        },
        "population": _FROZEN_POPULATION,
    },
    "R4LIB_FROZEN_END_LINE": {
        "what": "frozen_complete clause: the log carries an End line",
        "grader": _R4_LIB,
        "function": "frozen_complete",
        "registered_line": 295,
        "locate": {"kind": "call", "call": "re.search", "index": 0},
        "producer": ("sdk/openfoam/sparta/kCorrectiveFrozenFoam/"
                     "kCorrectiveFrozenFoam.C:196 - Info<< \"End\\n\" emitted "
                     "once per run on the normal exit path"),
        "predicate": {
            "kind": "pattern_present",
            "pattern_from": {"file": _R4_LIB, "function": "frozen_complete",
                             "call": "re.search", "index": 0, "arg": 0},
            "multiline": True,
        },
        "population": _FROZEN_POPULATION,
    },
}

# A registered clause whose locator names a key the grader does not carry. It
# exists so that "the clause could not be LOCATED" stays a DRIVEN rc=3 case
# after an unregistered KEY became rc=4: the two are different failures and the
# selftest must exercise both.
CLAUSES["SELFTEST_CLAUSE_NOT_IN_GRADER"] = {
    "what": "a locator that cannot be satisfied (selftest control)",
    "grader": _R5D_GRADER,
    "function": "completion_rule4",
    "registered_line": None,
    "locate": {"kind": "subscript_assign", "target": "info",
               "key": "no_such_clause_key"},
    "producer": "(none - this clause exists only to be NOT FOUND)",
    "predicate": CLAUSES["R5D_RULE4_CLAUSE5"]["predicate"],
    "population": _FROZEN_POPULATION,
}


# ===========================================================================
#  ast LAYER - locate the clause, and read its patterns out of the source
#
#  NEVER an import. The grader IS the instrument under test; importing it would
#  execute it, and an instrument that must run to be screened cannot be screened.
# ===========================================================================
def _parse(path):
    if not os.path.exists(path):
        unreadable("grader source %s is not on disk, so no clause can be "
                   "located in it" % path)
    try:
        return ast.parse(open(path, errors="replace").read())
    except SyntaxError as exc:
        unreadable("grader source %s does not parse: %s" % (path, exc))


def _function(path, name):
    tree = _parse(path)
    hits = [n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name == name]
    if not hits:
        unreadable("no function named %r in %s - the clause cannot be located, "
                   "and a clause that was not located was not screened"
                   % (name, path))
    if len(hits) > 1:
        unreadable("%d functions named %r in %s; the clause is ambiguous"
                   % (len(hits), name, path))
    return hits[0]


def _calls_in(fn, dotted):
    """Every call to `dotted` (e.g. 're.search') inside fn, in SOURCE order.

    ast.walk does not yield source order, so the list is sorted by (lineno,
    col_offset). The index in the spec is an index into THAT order.
    """
    mod, _, attr = dotted.partition(".")
    out = []
    for n in ast.walk(fn):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == attr
                and isinstance(n.func.value, ast.Name)
                and n.func.value.id == mod):
            out.append(n)
    out.sort(key=lambda n: (n.lineno, n.col_offset))
    return out


def locate_clause(spec):
    """Return (lineno, source_text). rc=3 if the clause is not in the grader."""
    fn = _function(spec["grader"], spec["function"])
    loc = spec["locate"]
    if loc["kind"] == "subscript_assign":
        for n in ast.walk(fn):
            if (isinstance(n, ast.Assign) and len(n.targets) == 1
                    and isinstance(n.targets[0], ast.Subscript)
                    and isinstance(n.targets[0].value, ast.Name)
                    and n.targets[0].value.id == loc["target"]):
                sl = n.targets[0].slice
                if isinstance(sl, ast.Constant) and sl.value == loc["key"]:
                    return n.lineno, ast.unparse(n)
        unreadable("clause %s[%r] not found in %s:%s - the clause could not be "
                   "LOCATED, so nothing was screened"
                   % (loc["target"], loc["key"], spec["grader"],
                      spec["function"]))
    elif loc["kind"] == "call":
        calls = _calls_in(fn, loc["call"])
        if len(calls) <= loc["index"]:
            unreadable("%s call #%d not found in %s:%s (%d present) - the "
                       "clause could not be LOCATED, so nothing was screened"
                       % (loc["call"], loc["index"], spec["grader"],
                          spec["function"], len(calls)))
        n = calls[loc["index"]]
        return n.lineno, ast.unparse(n)
    unreadable("unknown locator kind %r" % loc.get("kind"))


def literal_from_source(ref):
    """Read a string literal argument out of a named call, by ast.

    This is why the predicates below hold no transcribed regex: the pattern the
    grader actually uses is read out of the grader.
    """
    fn = _function(ref["file"], ref["function"])
    calls = _calls_in(fn, ref["call"])
    if len(calls) <= ref["index"]:
        unreadable("%s call #%d absent from %s:%s (%d present) - the clause's "
                   "own pattern could not be read from source"
                   % (ref["call"], ref["index"], ref["file"], ref["function"],
                      len(calls)))
    call = calls[ref["index"]]
    if len(call.args) <= ref["arg"]:
        unreadable("%s call #%d in %s:%s has no arg %d"
                   % (ref["call"], ref["index"], ref["file"], ref["function"],
                      ref["arg"]))
    node = call.args[ref["arg"]]
    if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
        unreadable("%s call #%d arg %d in %s:%s is not a string literal (%s) - "
                   "the pattern cannot be read statically"
                   % (ref["call"], ref["index"], ref["arg"], ref["file"],
                      ref["function"], type(node).__name__))
    return node.value, call.lineno


# ===========================================================================
#  POPULATION LAYER - the declared, inspectable fixture rule
# ===========================================================================
class Artifact(object):
    __slots__ = ("path", "case", "bucket", "why", "satisfied", "detail")

    def __init__(self, path, case, bucket, why):
        self.path, self.case, self.bucket, self.why = path, case, bucket, why
        self.satisfied, self.detail = None, ""


def fixture_marker_hit(path):
    for comp in os.path.abspath(path).split(os.sep):
        low = comp.lower()
        for mark in FIXTURE_MARKERS:
            if mark in low:
                return mark, comp
    return None, None


def load_registry(reg):
    """The committed registry of REAL cases. Absent/empty registry is rc=3."""
    if reg is None:
        return None
    path = reg["path"]
    if not os.path.exists(path):
        unreadable("the declared case registry %s is absent, so no artifact "
                   "can be classified REAL and nothing was screened" % path)
    try:
        blob = json.load(open(path))
    except Exception as exc:
        unreadable("the declared case registry %s does not parse: %s"
                   % (path, exc))
    rows = blob.get(reg["key"]) if isinstance(blob, dict) else blob
    if not rows:
        unreadable("the declared case registry %s carries no %r rows, so the "
                   "REAL population is empty by construction"
                   % (path, reg["key"]))
    names = set()
    for row in rows:
        if isinstance(row, dict) and reg["field"] in row:
            names.add(str(row[reg["field"]]))
        elif isinstance(row, str):
            names.add(row)
    if not names:
        unreadable("the declared case registry %s named no cases" % path)
    return names


def verify_exclusion_record(rule, record_override=None):
    """Read the cited record and CHECK the citation. Returns (ok, note).

    The exclusion is only as good as the record it names, so the record is read
    rather than trusted: the cited line range must exist, every declared quote
    must be found INSIDE it, and every case the rule excludes must be named
    there. A citation that does not verify excludes nothing (the artifact falls
    back to UNCLASSIFIED, the conservative bucket) and says so.
    """
    path = record_override or rule["record"]
    if not os.path.exists(path):
        return False, "cited record %s is not on disk" % path
    lines = open(path, errors="replace").read().splitlines()
    lo, hi = rule["lines"]
    if len(lines) < hi:
        return False, ("cited record %s has %d lines, fewer than the cited "
                       "range %d-%d" % (path, len(lines), lo, hi))
    window = "\n".join(lines[lo - 1:hi])
    for q in rule["quotes"]:
        if q not in window:
            return False, ("cited quote %r is NOT present at %s:%d-%d, so the "
                           "citation does not verify and excludes nothing"
                           % (q, path, lo, hi))
    missing = [c for c in rule["cases"] if c not in window]
    if missing:
        return False, ("%s:%d-%d does not name %s, so the record cannot be "
                       "said to cover %s"
                       % (path, lo, hi, ", ".join(missing), missing[0]))
    return True, ("verified at %s:%d-%d - %r"
                  % (os.path.relpath(path, _REPO), lo, hi, rule["quotes"][0]))


def discover(pop, search_roots=None, registry_path=None,
             exclusion_record=None):
    """Find every candidate artifact and CLASSIFY it by the declared rule.

    Returns (artifacts, roots_present, roots_absent, registry_names).
    """
    roots = [os.path.abspath(r) for r in (search_roots or pop["search_roots"])]
    present = [r for r in roots if os.path.isdir(r)]
    absent = [r for r in roots if not os.path.isdir(r)]
    if not present:
        unreadable("none of the declared search roots exist (%s) - no artifact "
                   "directory could be read, so nothing was screened"
                   % ", ".join(roots))

    reg = dict(pop["registry"]) if pop.get("registry") else None
    if reg is not None and registry_path:
        reg["path"] = os.path.abspath(registry_path)
    names = load_registry(reg)

    real_roots = [os.path.abspath(r) for r in pop.get("real_roots", [])]
    if search_roots:
        # An override repoints the population wholesale: any directory under an
        # overridden root that carries the artifact is eligible to be REAL, and
        # the registry still decides. Printed, never implicit.
        real_roots = present

    found = []
    for root in present:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames.sort()
            if pop["artifact_name"] in filenames:
                found.append(os.path.join(dirpath, pop["artifact_name"]))
    found.sort()

    # LAYER 1b - verify every record-based exclusion ONCE, before any artifact
    # is classified by it. A rule whose citation fails excludes nothing.
    excl = []
    excl_notes = []
    for rule in (pop.get("excluded_by_record") or []):
        ok, note = verify_exclusion_record(rule, exclusion_record)
        excl_notes.append((rule, ok, note))
        if ok:
            excl.append(rule)

    arts = []
    for path in found:
        case_dir = os.path.dirname(os.path.abspath(path))
        case = os.path.basename(case_dir)
        mark, comp = fixture_marker_hit(path)
        if mark is not None:
            arts.append(Artifact(path, case, "FIXTURE",
                                 "declared fixture marker %r matched path "
                                 "component %r" % (mark, comp)))
            continue
        hit = None
        for rule in excl:
            root = os.path.abspath(rule["under"])
            if case in rule["cases"] and (case_dir == os.path.join(root, case)):
                hit = rule
                break
        if hit is not None:
            arts.append(Artifact(
                path, case, "EXCLUDED-BY-RECORD",
                "committed record %s:%d-%d declares it a lane convergence "
                "diagnostic, not a target extraction (%r)"
                % (os.path.relpath(hit["record"], _REPO), hit["lines"][0],
                   hit["lines"][1], hit["quotes"][0])))
            continue
        under = [r for r in real_roots
                 if case_dir == r or case_dir.startswith(r + os.sep)]
        if not under:
            arts.append(Artifact(path, case, "UNCLASSIFIED",
                                 "no declared fixture marker, and not under "
                                 "any declared REAL root"))
            continue
        if names is not None and case not in names:
            arts.append(Artifact(path, case, "UNCLASSIFIED",
                                 "under a REAL root but the committed registry "
                                 "does not name case %r" % case))
            continue
        arts.append(Artifact(path, case, "REAL",
                             "under declared REAL root %s and named by the "
                             "committed registry" % under[0]))
    return arts, present, absent, names, excl_notes


# ===========================================================================
#  PREDICATE LAYER - evaluate the located clause against one artifact
# ===========================================================================
def build_predicate(spec):
    """Return (fn(text)->(bool, detail), a printable description)."""
    pred = spec["predicate"]
    if pred["kind"] == "count_equals_capture":
        cpat, cline = literal_from_source(pred["count_pattern_from"])
        kpat, kline = literal_from_source(pred["capture_pattern_from"])
        crx, krx = re.compile(cpat), re.compile(kpat)

        def run(text):
            n = len(crx.findall(text))
            m = krx.search(text)
            if m is None:
                return False, "count=%d capture=ABSENT" % n
            try:
                want = int(m.group(1))
            except (IndexError, ValueError):
                return False, "count=%d capture=UNPARSEABLE(%r)" % (n, m.group(0))
            return (n == want), "count=%d capture=%d" % (n, want)

        desc = ("count of /%s/ (read from %s:%d) == integer captured by /%s/ "
                "(read from %s:%d)"
                % (cpat, os.path.relpath(pred["count_pattern_from"]["file"], _REPO),
                   cline, kpat,
                   os.path.relpath(pred["capture_pattern_from"]["file"], _REPO),
                   kline))
        return run, desc

    if pred["kind"] == "pattern_present":
        pat, pline = literal_from_source(pred["pattern_from"])
        flags = re.M if pred.get("multiline") else 0
        rx = re.compile(pat, flags)

        def run(text):
            m = rx.search(text)
            return (m is not None), ("present" if m else "ABSENT")

        desc = ("/%s/ present (read from %s:%d, multiline=%s)"
                % (pat, os.path.relpath(pred["pattern_from"]["file"], _REPO),
                   pline, bool(pred.get("multiline"))))
        return run, desc

    unreadable("unknown predicate kind %r" % pred.get("kind"))


def evaluate(arts, predicate):
    read_errors = []
    for a in arts:
        try:
            text = open(a.path, errors="replace").read()
        except OSError as exc:
            a.satisfied, a.detail = None, "UNREADABLE: %s" % exc
            read_errors.append(a)
            continue
        a.satisfied, a.detail = predicate(text)
    return read_errors


# ===========================================================================
#  VERDICT LAYER
#
#  The clean sentence is built HERE and only here, and it cannot be produced
#  without the population counts and a named witness. This is the structural
#  repair carried by check_bar_above_floor.py v1.1 - copied as discipline.
# ===========================================================================
def demonstrated_sentence(n_screened, n_real, n_fixture, n_unclassified,
                          n_excluded, witness, detail):
    if n_screened <= 0:
        unreadable("a DEMONSTRATED verdict was requested over a population of "
                   "0 artifacts SCREENED. A check that read nothing is not a "
                   "pass.")
    if n_real <= 0:
        unreadable("a DEMONSTRATED verdict was requested with 0 REAL artifacts "
                   "in the population. Fixtures cannot demonstrate a clause.")
    if not witness:
        unreadable("a DEMONSTRATED verdict was requested with no named witness "
                   "artifact. A verdict without its artifact is not a reading.")
    return ("VERDICT: DEMONSTRATED - %d artifact(s) SCREENED (%d REAL, %d "
            "FIXTURE, %d EXCLUDED-BY-RECORD, %d UNCLASSIFIED), and the REAL "
            "artifact\n"
            "  %s\n"
            "satisfies the clause (%s). The clause is reachable by its real "
            "producer." % (n_screened, n_real, n_fixture, n_excluded,
                           n_unclassified, witness, detail))


def not_demonstrated_sentence(n_screened, n_real, n_fixture, n_unclassified,
                              n_excluded, min_real):
    if n_screened <= 0 or n_real <= 0:
        unreadable("a NOT-DEMONSTRATED verdict was requested over %d REAL of "
                   "%d screened. Not-demonstrated is a claim ABOUT a "
                   "population and cannot be made without one."
                   % (n_real, n_screened))
    return ("VERDICT: NOT-DEMONSTRATED - %d artifact(s) SCREENED (%d REAL, %d "
            "FIXTURE, %d EXCLUDED-BY-RECORD, %d UNCLASSIFIED), and NONE of the "
            "%d REAL artifacts satisfies the clause.\n"
            "  The REAL population exceeds the declared minimum of %d, so this "
            "is a FINDING about the clause and not a gap in the read: on this "
            "evidence the clause's green is unreachable by its real producer."
            % (n_screened, n_real, n_fixture, n_excluded, n_unclassified,
               n_real, min_real))


def report(spec, key, clause_line, clause_src, pred_desc, arts, present,
           absent, names, excl_notes, min_real, emit_json):
    real = [a for a in arts if a.bucket == "REAL"]
    fixt = [a for a in arts if a.bucket == "FIXTURE"]
    uncl = [a for a in arts if a.bucket == "UNCLASSIFIED"]
    excl = [a for a in arts if a.bucket == "EXCLUDED-BY-RECORD"]
    unreadable_arts = [a for a in arts if a.satisfied is None]
    real_sat = [a for a in real if a.satisfied]
    other_sat = [a for a in (fixt + uncl + excl) if a.satisfied]

    print("check_clause_demonstrated v%s" % VERSION)
    print("  clause key          : %s" % key)
    print("  clause              : %s" % spec["what"])
    print("  grader              : %s" % os.path.relpath(spec["grader"], _REPO))
    print("  located by ast at   : %s:%d  (registered line %s)"
          % (os.path.relpath(spec["grader"], _REPO), clause_line,
             spec.get("registered_line", "-")))
    print("  clause source       : %s" % clause_src)
    print("  predicate           : %s" % pred_desc)
    print("  producer channel    : %s" % spec["producer"])
    print("")
    print("  DECLARED FIXTURE RULE (layer 1): a path component containing any "
          "of %s" % ", ".join(repr(m) for m in FIXTURE_MARKERS))
    print("  DECLARED REAL RULE    (layer 2): under a declared REAL root AND "
          "named by the committed registry")
    for rule, ok, note in excl_notes:
        print("  DECLARED RECORD EXCLUSION (layer 1b): %s -> %s"
              % ("/".join([rule["under"]] + [""])[:-1] + "/{%s}"
                 % ",".join(rule["cases"]),
                 "APPLIED, citation %s" % note if ok
                 else "NOT APPLIED (citation did NOT verify: %s) - these "
                      "artifacts fall back to UNCLASSIFIED" % note))
        print("    corroboration   : %s" % rule["corroboration"])
    print("    REAL roots        : %s"
          % ", ".join(spec["population"].get("real_roots", [])) or "(none)")
    print("    registry          : %s (%d case(s) named)"
          % (spec["population"]["registry"]["path"] if
             spec["population"].get("registry") else "(none)",
             0 if names is None else len(names)))
    print("  OTHERWISE             : UNCLASSIFIED - named below, never "
          "silently REAL")
    print("  search roots present: %s" % ", ".join(present))
    if absent:
        print("  search roots ABSENT : %s" % ", ".join(absent))
    print("")
    print("  artifacts SCREENED  : %d" % len(arts))
    print("    REAL              : %d" % len(real))
    print("    FIXTURE excluded  : %d" % len(fixt))
    print("    EXCLUDED-BY-RECORD: %d" % len(excl))
    print("    UNCLASSIFIED      : %d" % len(uncl))
    print("    UNREADABLE        : %d" % len(unreadable_arts))
    print("    declared min REAL : %d" % min_real)
    print("")

    if fixt:
        print("  EXCLUDED AS FIXTURE, each with the rule that excluded it:")
        for a in fixt:
            print("    [%s] %s  (%s)"
                  % ("satisfies" if a.satisfied else "fails ", a.path, a.why))
        print("")
    if excl:
        print("  EXCLUDED BY A COMMITTED RECORD (never counted as real):")
        for a in excl:
            print("    [%s] %s\n          %s"
                  % ("satisfies" if a.satisfied else "fails ", a.path, a.why))
        print("")
    if uncl:
        print("  UNCLASSIFIED (third bucket - NOT counted as real):")
        for a in uncl:
            print("    [%s] %s  (%s)"
                  % ("satisfies" if a.satisfied else "fails ", a.path, a.why))
        print("")
    if unreadable_arts:
        print("  UNREADABLE ARTIFACTS - these are NOT MEASURED, not clean:")
        for a in unreadable_arts:
            print("    %s  (%s)" % (a.path, a.detail))
        print("")

    if real:
        sample = real_sat if real_sat else real[:5]
        print("  REAL artifacts, %s:"
              % ("every one that satisfies" if real_sat
                 else "first %d of %d, with the clause reading"
                      % (len(sample), len(real))))
        for a in sample:
            print("    [%s] %-58s %s"
                  % ("satisfies" if a.satisfied else "fails ",
                     os.path.relpath(a.path, "/home/ubuntu"), a.detail))
        if not real_sat:
            vals = sorted({a.detail for a in real})
            print("    distinct readings over all %d REAL artifacts: %d"
                  % (len(real), len(vals)))
            for v in vals[:8]:
                print("      %s" % v)
            if len(vals) > 8:
                print("      ... and %d more" % (len(vals) - 8))
        print("")

    rc = RC_DEMONSTRATED
    if len(arts) == 0:
        unreadable("the declared search produced 0 candidate artifacts named "
                   "%r under %s. A check that read nothing is not a pass."
                   % (spec["population"]["artifact_name"], ", ".join(present)))
    if len(real) == 0:
        if other_sat:
            print("VERDICT: HALF-DEMONSTRATED - %d artifact(s) SCREENED (0 "
                  "REAL, %d FIXTURE, %d EXCLUDED-BY-RECORD, %d UNCLASSIFIED). "
                  "The clause IS satisfied here, but only by artifacts the "
                  "declared rule refuses to call real. Fixtures alone cannot "
                  "demonstrate a clause."
                  % (len(arts), len(fixt), len(excl), len(uncl)))
        else:
            print("VERDICT: HALF-DEMONSTRATED / COULD-NOT-RUN - %d artifact(s) "
                  "SCREENED but 0 are REAL (%d FIXTURE, %d EXCLUDED-BY-RECORD, "
                  "%d UNCLASSIFIED). The clause was LOCATED and the population "
                  "was READ, but it contains nothing the declared rule calls a "
                  "real producer artifact."
                  % (len(arts), len(fixt), len(excl), len(uncl)))
        rc = RC_COULD_NOT_RUN
    elif real_sat:
        w = real_sat[0]
        print(demonstrated_sentence(len(arts), len(real), len(fixt), len(uncl),
                                    len(excl), w.path, w.detail))
        rc = RC_DEMONSTRATED
    elif len(real) < min_real:
        print("VERDICT: HALF-DEMONSTRATED / COULD-NOT-RUN - %d artifact(s) "
              "SCREENED, %d REAL, and none satisfies the clause - but %d is "
              "below the declared minimum REAL population of %d, so 'no real "
              "artifact satisfies it' cannot be separated from 'not enough "
              "real artifacts were read'."
              % (len(arts), len(real), len(real), min_real))
        rc = RC_COULD_NOT_RUN
    else:
        print(not_demonstrated_sentence(len(arts), len(real), len(fixt),
                                        len(uncl), len(excl), min_real))
        rc = RC_NOT_DEMONSTRATED

    if other_sat and real_sat == []:
        print("")
        print("  L-529 SIGNATURE - the clause IS satisfied, but ONLY outside "
              "the real population. Every such artifact, by name:")
        for a in other_sat:
            print("    [%s] %s  (%s)" % (a.bucket, a.path, a.detail))
        print("  A green seen only where the producer was not the real "
              "producer is the absence of a reading, not a reading.")

    if emit_json:
        print("")
        print("--- JSON ---")
        print(json.dumps({
            "version": VERSION, "clause": key, "rc": rc,
            "clause_line": clause_line, "registered_line":
                spec.get("registered_line"),
            "screened": len(arts), "real": len(real), "fixture": len(fixt),
            "unclassified": len(uncl), "excluded_by_record": len(excl),
            "unreadable": len(unreadable_arts),
            "real_satisfying": [a.path for a in real_sat],
            "other_satisfying": [[a.bucket, a.path] for a in other_sat],
        }, indent=1, sort_keys=True))
    return rc


def run_clause(key, search_roots, registry_path, min_real, emit_json,
               exclusion_record=None):
    if key not in CLAUSES:
        usage("no clause registered under %r. Registered: %s"
              % (key, ", ".join(sorted(CLAUSES))))
    spec = CLAUSES[key]
    clause_line, clause_src = locate_clause(spec)
    predicate, pred_desc = build_predicate(spec)
    arts, present, absent, names, excl_notes = discover(
        spec["population"], search_roots, registry_path, exclusion_record)
    evaluate(arts, predicate)
    return report(spec, key, clause_line, clause_src, pred_desc, arts, present,
                  absent, names, excl_notes, min_real, emit_json)


# ===========================================================================
#  PLANTED-FAILURE SELFTEST, DRIVEN ON REAL REGISTERED ARTIFACTS
#
#  Every fixture below is driven through the real entry point as a subprocess
#  and its rc and stdout are OBSERVED. No fixture invents a log: the two PLANT
#  cases COPY a real registered log.frozen and mutate exactly one quantity the
#  detector claims to read. THREE cases are EMPTY READS, by name - the L-530
#  instrument shipped L-529's own defect because not one of its nine fixtures
#  was empty.
# ===========================================================================
def _run(argv):
    cmd = [sys.executable]
    if sys.flags.optimize:
        cmd += ["-O"] * sys.flags.optimize
    cmd += [os.path.abspath(__file__)] + argv
    return subprocess.run(cmd, capture_output=True, text=True)


def _copy_case(src_log, dst_case, transform=None):
    os.makedirs(dst_case, exist_ok=True)
    text = open(src_log, errors="replace").read()
    if transform is not None:
        text = transform(text)
    open(os.path.join(dst_case, "log.frozen"), "w").write(text)


def _write_registry(path, cases):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({"inventory": [{"case": c} for c in cases]}, open(path, "w"))


def selftest():
    opt = "ON" if sys.flags.optimize else "off"
    print("check_clause_demonstrated v%s - PLANTED-FAILURE SELFTEST" % VERSION)
    print("python3 -O optimization: %s (sys.flags.optimize=%d)\n"
          % (opt, sys.flags.optimize))

    real_root = "/home/ubuntu/closure-data/r4/frozen"
    donor_case = "CBFS13700"
    donor = os.path.join(real_root, donor_case, "log.frozen")
    if not os.path.exists(donor):
        sys.stderr.write(
            "REFUSED: the real donor artifact %s is not on disk, so the "
            "two-direction control cannot be driven on real producer output. "
            "A selftest that falls back to an invented log is the fixture "
            "L-529 warns about, and is not offered.\n" % donor)
        sys.exit(2)

    cases = []
    with tempfile.TemporaryDirectory() as td:
        # ---- EMPTY READ 1: a search root that exists and holds no artifact
        empty_root = os.path.join(td, "empty_root")
        os.makedirs(os.path.join(empty_root, "nothing_here"))
        # ---- EMPTY READ 2: a search root that does not exist at all
        absent_root = os.path.join(td, "no_such_root")
        # ---- EMPTY READ 3: an empty committed registry
        empty_reg = os.path.join(td, "reg_empty", "frozen_inventory.json")
        _write_registry(empty_reg, [])

        # ---- PLANT A: the NEGATIVE clause must STOP refusing when a real
        #      artifact that satisfies it appears. Copy the real donor and move
        #      exactly one quantity the detector reads - the write iteration -
        #      down to the run's real once-per-run ExecutionTime count of 1.
        plant_a = os.path.join(td, "plantA")
        _copy_case(donor, os.path.join(plant_a, donor_case),
                   lambda t: re.sub(r"Writing fields at iteration \d+",
                                    "Writing fields at iteration 1", t))
        for i in range(12):          # pad to clear the declared min REAL
            c = "pad_%02d" % i
            _copy_case(donor, os.path.join(plant_a, c))
        reg_a = os.path.join(td, "regA", "frozen_inventory.json")
        _write_registry(reg_a, [donor_case] + ["pad_%02d" % i for i in range(12)])

        # ---- PLANT B: the POSITIVE clause must START refusing when the one
        #      string it reads is removed from every real artifact.
        plant_b = os.path.join(td, "plantB")
        for i in range(12):
            c = "noend_%02d" % i
            _copy_case(donor, os.path.join(plant_b, c),
                       lambda t: re.sub(r"(?m)^End\s*$", "Ended", t))
        reg_b = os.path.join(td, "regB", "frozen_inventory.json")
        _write_registry(reg_b, ["noend_%02d" % i for i in range(12)])

        # ---- FIXTURES-ONLY: a population where every artifact is a fixture
        fixt_only = os.path.join(td, "fixtures_only")
        for i in range(3):
            _copy_case(donor, os.path.join(fixt_only, "selftest", "case_%d" % i))
        reg_f = os.path.join(td, "regF", "frozen_inventory.json")
        _write_registry(reg_f, ["case_%d" % i for i in range(3)])

        # ---- CITATION PLANT: a record copy with the cited quote removed.
        #      The layer-1b exclusion must REFUSE to apply, and the five
        #      ktest* trees must fall back to UNCLASSIFIED, not to REAL.
        rec_src = os.path.join(_CLOSURE, "R4_sparta_build", "RESULTS.md")
        bad_rec = os.path.join(td, "RESULTS_quote_removed.md")
        if os.path.exists(rec_src):
            open(bad_rec, "w").write(
                open(rec_src, errors="replace").read().replace(
                    "this lane's own convergence diagnostics",
                    "this lane's own REDACTED"))

        # ---- TOO FEW REAL: below the declared minimum
        few = os.path.join(td, "few")
        _copy_case(donor, os.path.join(few, donor_case))
        reg_few = os.path.join(td, "regFew", "frozen_inventory.json")
        _write_registry(reg_few, [donor_case])

        NEG = "R5D_RULE4_CLAUSE5"
        POS = "R4LIB_FROZEN_END_LINE"
        cases = [
            # (name, argv, want_rc, must_contain, must_not_contain)
            ("REAL NEGATIVE  - clause 5 over the registered population",
             ["--clause", NEG], 2,
             ["VERDICT: NOT-DEMONSTRATED", "REAL", "ktest3"],
             ["VERDICT: DEMONSTRATED", "VERDICT: HALF-DEMONSTRATED"]),
            ("REAL POSITIVE  - the End-line clause over the same population",
             ["--clause", POS], 0,
             ["VERDICT: DEMONSTRATED", "SCREENED"],
             ["VERDICT: NOT-DEMONSTRATED", "VERDICT: HALF-DEMONSTRATED"]),
            ("PLANT A        - real log, write iteration moved to 1, must PASS",
             ["--clause", NEG, "--search-root", plant_a, "--registry", reg_a],
             0, ["VERDICT: DEMONSTRATED", "count=1 capture=1"],
             ["VERDICT: NOT-DEMONSTRATED", "VERDICT: HALF-DEMONSTRATED"]),
            ("PLANT B        - real logs with the End line removed, must FAIL",
             ["--clause", POS, "--search-root", plant_b, "--registry", reg_b],
             2, ["VERDICT: NOT-DEMONSTRATED", "ABSENT"], ["VERDICT: DEMONSTRATED"]),
            ("READ NOTHING 1 - search root exists, holds no artifact",
             ["--clause", NEG, "--search-root", empty_root, "--registry", reg_a],
             3, ["0 candidate artifacts"], ["VERDICT: DEMONSTRATED"]),
            ("READ NOTHING 2 - search root absent from disk",
             ["--clause", NEG, "--search-root", absent_root, "--registry", reg_a],
             3, ["none of the declared search roots exist"],
             ["VERDICT: DEMONSTRATED"]),
            ("READ NOTHING 3 - clause locator finds nothing in the grader",
             ["--clause", "SELFTEST_CLAUSE_NOT_IN_GRADER"], 3,
             ["could not be LOCATED"], ["VERDICT: DEMONSTRATED"]),
            ("READ NOTHING 4 - committed registry names no cases",
             ["--clause", NEG, "--search-root", plant_a, "--registry", empty_reg],
             3, ["carries no 'inventory' rows"], ["VERDICT: DEMONSTRATED"]),
            ("FIXTURES ONLY  - population is all fixtures, 0 REAL",
             ["--clause", POS, "--search-root", fixt_only, "--registry", reg_f],
             3, ["HALF-DEMONSTRATED", "0 REAL"], ["VERDICT: DEMONSTRATED"]),
            ("TOO FEW REAL   - 1 REAL, below the declared minimum",
             ["--clause", NEG, "--search-root", few, "--registry", reg_few],
             3, ["HALF-DEMONSTRATED", "below the declared minimum"],
             ["VERDICT: NOT-DEMONSTRATED"]),
            ("CITATION VERIFIES - layer-1b exclusion APPLIED on the real "
             "record",
             ["--clause", NEG], 2,
             ["DECLARED RECORD EXCLUSION (layer 1b)", "APPLIED, citation "
              "verified at", "EXCLUDED BY A COMMITTED RECORD", "ktest3"],
             ["NOT APPLIED (citation did NOT verify"]),
            ("CITATION PLANT   - cited quote removed, exclusion must NOT apply",
             ["--clause", NEG, "--exclusion-record", bad_rec], 2,
             ["NOT APPLIED (citation did NOT verify",
              "fall back to UNCLASSIFIED", "EXCLUDED-BY-RECORD: 0"],
             ["EXCLUDED BY A COMMITTED RECORD"]),
            ("EXIT CODE 4    - a mistyped flag is NOT a finding",
             ["--clause", NEG, "--roots", "/tmp"], 4,
             ["USAGE ERROR (this is not a verdict)"],
             ["VERDICT:"]),
            ("EXIT CODE 4    - --help is informational, never 0",
             ["--help"], 4, [], ["VERDICT:"]),
            ("EXIT CODE 4    - --list is informational, never 0",
             ["--list"], 4, ["registered clauses"], ["VERDICT:"]),
            ("EXIT CODE 4    - no --clause named at all",
             [], 4, ["NOT a finding"], ["VERDICT:"]),
            ("EXIT CODE 4    - an unregistered clause key is operator error",
             ["--clause", "NO_SUCH_CLAUSE"], 4, ["no clause registered"],
             ["VERDICT:"]),
            ("EXIT CODE 1    - an uncaught error is reported, not a verdict",
             ["--selftest-internal-error"], 1,
             ["INTERNAL ERROR (this is not a verdict)"], ["VERDICT:"]),
        ]

        npass = 0
        refusals = 0
        readnothing = 0
        usagecodes = 0
        internalcodes = 0
        for name, argv, want, must, mustnot in cases:
            proc = _run(argv)
            out = proc.stdout + proc.stderr
            ok = proc.returncode == want
            miss = [s for s in must if s not in out]
            bad = [s for s in mustnot if s in out]
            ok = ok and not miss and not bad
            if want == 2:
                refusals += 1
            if want == 3:
                readnothing += 1
            if want == 4:
                usagecodes += 1
            if want == 1:
                internalcodes += 1
            print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
            print("         rc=%d (want %d)" % (proc.returncode, want))
            if miss:
                print("         MISSING from output: %s" % miss)
            if bad:
                print("         FORBIDDEN in output: %s" % bad)
            if not ok:
                print("         ---- output ----")
                for line in out.splitlines()[-25:]:
                    print("         %s" % line)
            npass += 1 if ok else 0

    print("")
    print("  selftest: %d/%d PASS" % (npass, len(cases)))
    print("  refusals DRIVEN AND OBSERVED (rc=2): %d" % refusals)
    print("  read-nothing cases DRIVEN AND OBSERVED (rc=3): %d" % readnothing)
    print("  usage cases DRIVEN AND OBSERVED  (rc=4): %d" % usagecodes)
    print("  internal-error case DRIVEN AND OBSERVED (rc=1): %d"
          % internalcodes)
    print("  DEMONSTRATED cases DRIVEN AND OBSERVED  (rc=0): %d"
          % sum(1 for c in cases if c[2] == 0))
    print("  python3 -O: %s" % opt)
    if npass != len(cases):
        sys.stderr.write("REFUSED: selftest %d/%d - this instrument has NOT "
                         "been shown to fire in both directions and must not "
                         "be relied on.\n" % (npass, len(cases)))
        sys.exit(2)
    print("\n  L-529 (a): the refusals above FIRED on planted conditions.")
    print("  L-529 (b): PLANT A shows a REAL artifact CAN make the check say "
          "DEMONSTRATED, so its NOT-DEMONSTRATED is a reading and not an "
          "inability.")
    return 0


class _Parser(argparse.ArgumentParser):
    """argparse exits 2 on a usage error and 0 on --help. Both collide with a
    VERDICT code, so both are remapped to RC_USAGE. This is the v1.0 defect: a
    mistyped flag returned the same 2 as a genuine NOT-DEMONSTRATED finding,
    manufacturing an alarming result out of operator error.
    """

    def error(self, message):
        usage("%s\n(run --list to see the registered clause keys)" % message)

    def exit(self, status=0, message=None):
        if message:
            sys.stderr.write(message)
        sys.exit(RC_USAGE if status == 0 else status)


def main():
    ap = _Parser(add_help=True, description=__doc__.split("\n")[0])
    ap.add_argument("--clause")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--search-root", action="append", default=None)
    ap.add_argument("--registry", default=None)
    ap.add_argument("--exclusion-record", default=None,
                    help="override the record cited by the layer-1b exclusion "
                         "rule; used by --selftest to drive a citation that "
                         "does NOT verify")
    ap.add_argument("--min-real", type=int, default=DEFAULT_MIN_REAL)
    ap.add_argument("--emit-json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-internal-error", action="store_true",
                    help="raise deliberately, so the exit-code-1 handler is "
                         "SHOWN to fire rather than assumed to")
    args = ap.parse_args()

    if args.selftest_internal_error:
        raise RuntimeError("deliberate internal error, driven by --selftest to "
                           "prove the exit-code-1 handler fires")
    if args.selftest:
        return selftest()
    if args.list:
        print("check_clause_demonstrated v%s - registered clauses:" % VERSION)
        for k in sorted(CLAUSES):
            print("  %-24s %s" % (k, CLAUSES[k]["what"]))
            print("  %-24s %s:%s" % ("", os.path.relpath(CLAUSES[k]["grader"],
                                                         _REPO),
                                     CLAUSES[k].get("registered_line", "?")))
        # Informational, not a verdict: 0 is reserved for DEMONSTRATED.
        return RC_USAGE
    if not args.clause:
        usage("no --clause named, so nothing was even asked for. This is an "
              "operator error and NOT a finding. Try --list.")
    return run_clause(args.clause, args.search_root, args.registry,
                      args.min_real, args.emit_json, args.exclusion_record)


def _guarded_main():
    """A crash that swallows findings is not the refusal discipline this file
    keeps, so an uncaught exception is REPORTED and given its own code."""
    try:
        return main()
    except SystemExit:
        raise
    except BaseException as exc:          # noqa: BLE001 - deliberate
        import traceback
        sys.stderr.write("INTERNAL ERROR (this is not a verdict): %s: %s\n"
                         % (type(exc).__name__, exc))
        traceback.print_exc(file=sys.stderr)
        sys.exit(RC_INTERNAL)


if __name__ == "__main__":
    sys.exit(_guarded_main())
