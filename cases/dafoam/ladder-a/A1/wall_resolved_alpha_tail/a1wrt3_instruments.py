#!/usr/bin/env python3
"""A1WRT3 -- THE SHARED INSTRUMENT LAYER.

`A1WRT3_SUCCESSOR_DRAFT.md` sections 3 and 4.  This module carries the two
readers that both the LAUNCHER (`a1wrt3_run_arm.sh`, before the container) and
the GRADER (`a1wrt3_grade.py`, after the arm) consume, so that the host side of
`G-ENVSEAM` and of `G-WALLTREAT` exists in ONE implementation rather than two
that can drift.

=============================================================================
WHY `G-ENVSEAM` CLAUSE 1 IS AN AST READER AND NOT A SHELL CHECK
=============================================================================
A1WRT2 carried 153 controls and NOT ONE OF THEM COULD SEE THE DEFECT, and the
reason is structural rather than a shortfall of diligence.  Its
`g_unbound_precondition` and `unbound_guard` read the LAUNCHER FOR UNBOUND
*SHELL* VARIABLES.  `AOA_ALPHA0` is not an unbound shell variable.  It is an
ABSENT PROCESS-ENVIRONMENT ENTRY, CONSUMED BY A PYTHON INTERPRETER, ON THE FAR
SIDE OF A `docker run`.  The launcher's shell was entirely well-formed.  A
154th control of the same kind repairs nothing.

Clause 1 therefore parses the STAGED PRODUCER with Python's `ast`, separates
`os.environ["X"]` (FATAL -- a `KeyError` at import) from `os.environ.get(...)`
and `os.getenv(...)` (DEFAULTED -- not fatal), and asserts every fatal name is
in the set the container will ACTUALLY receive.  CONFLATING THE TWO INFLATES
THE FINDING: the 2026-09-05 family sweep measured 31 of 37 resolvable entry
scripts in this family reading NOTHING fatal at all, and a gate that blocked
those would be useless.  Control `E5` drives that false-positive direction.

=============================================================================
SECTION 4.1 -- THE SINGLE-ARRAY REQUIREMENT, WHICH IS THIS MODULE'S CONTRACT
=============================================================================
THE SUPPLIED SET IS NOT RE-TYPED HERE AND MUST NEVER BE.  It is assembled from
exactly two sources, BOTH OF WHICH ARE THE BYTES THAT RUN:

  1. THE `-e` ARRAY ITSELF.  `a1wrt3_run_arm.sh` builds `DOCKER_ENV` ONCE and
     expands `"${DOCKER_ENV[@]}"` into BOTH this gate's argv AND the
     `docker run` command line.  Not a copy of the array -- the array.
  2. THE `AOA_*` NAMES THE C13 TRANSLATION SETS, extracted from
     `a1wrt3_cmd.sh` BY PARSING THAT FILE between its registered
     `A1WRT3 C13 TRANSLATION BEGIN/END` markers.  The gate reads the file that
     runs inside the container.

A clause-1 implementation that compared the producer's reads against a
HAND-MAINTAINED LIST OF NAMES would be a second list that drifts from the
first, and the gate would then certify a correspondence between two things
NEITHER OF WHICH IS WHAT RUNS -- the L-493 wrong-route shape in its most
literal form.  `translation_names()` and `supplied_from_docker_env()` below are
the two extractors; NO LITERAL ENVIRONMENT-NAME LIST APPEARS IN THIS FILE
OUTSIDE THE CONTROL FIXTURES' OWN EXPECTED VALUES.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ITEM = "A1WRT3"

# The registered producer pin.  MEASURED: `md5sum
# /home/ubuntu/certonomous-runs/A1WRT2/runScript.py`.  It is the EXPECTED side
# of G-WALLTREAT limb (c) and of G-FREEZE, and it is a registered constant --
# never read out of an artefact the run itself wrote.
PIN_RUNSCRIPT_MD5 = "d48f48c5e2e41e86981acbf6feccb3c4"

# The registered markers that delimit the C13 translation inside
# `a1wrt3_cmd.sh`.  Changing either one breaks extraction LOUDLY (refusal),
# never silently.
XLAT_BEGIN = ">>> A1WRT3 C13 TRANSLATION BEGIN"
XLAT_END = "<<< A1WRT3 C13 TRANSLATION END"

WALLTREAT_OK_MARKER = "A1WRT3_WALLTREAT_SCRIPT_OK"


class Refusal(Exception):
    """A refusal carries its own exit code.  REFUSE RATHER THAN DEGRADE."""

    def __init__(self, msg: str, code: int = 2):
        super().__init__(msg)
        self.code = code


def md5_of(path) -> str:
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def read_text(path) -> str:
    """An absent artefact REFUSES.  It never reads as an empty string, because
    an empty string is a zero from a reader that could not see (`CLAUDE.md`
    rule 3)."""
    p = Path(path)
    if not p.is_file():
        raise Refusal("REFUSE: subject absent at point of use: %s" % p)
    try:
        return p.read_text(errors="replace")
    except OSError as exc:
        raise Refusal("REFUSE: subject unreadable: %s (%s)" % (p, exc))


# =========================================================================
# THE AST EXTRACTOR
# =========================================================================

_FATAL = "FATAL"
_DEFAULTED = "DEFAULTED"


class _EnvVisitor(ast.NodeVisitor):
    """Collects every process-environment read, classified.

    ALIASES ARE TRACKED RATHER THAN ASSUMED ABSENT.  `import os as o` and
    `from os import environ as E` both hide `os.environ` from a naive matcher,
    and a gate blind to a form the codebase may legally use is a gate whose
    silence means nothing.  `_UNRESOLVABLE` below is the same principle applied
    to a non-constant subscript.
    """

    def __init__(self):
        self.reads = []            # {name, line, kind, scope}
        self.unresolvable = []     # {line, scope, expr}
        self.os_aliases = {"os"}
        self.environ_aliases = {"environ"}
        self.getenv_aliases = set()
        self._scope = ["module"]

    # ---- alias discovery ------------------------------------------------
    def visit_Import(self, node):
        for a in node.names:
            if a.name == "os":
                self.os_aliases.add(a.asname or "os")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module == "os":
            for a in node.names:
                if a.name == "environ":
                    self.environ_aliases.add(a.asname or "environ")
                elif a.name == "getenv":
                    self.getenv_aliases.add(a.asname or "getenv")
        self.generic_visit(node)

    # ---- scope tracking -------------------------------------------------
    def _push(self, label, node):
        self._scope.append(label)
        self.generic_visit(node)
        self._scope.pop()

    def visit_FunctionDef(self, node):
        self._push("function:%s" % node.name, node)

    def visit_AsyncFunctionDef(self, node):
        self._push("function:%s" % node.name, node)

    def visit_Lambda(self, node):
        self._push("lambda", node)

    def visit_ClassDef(self, node):
        self._push("class:%s" % node.name, node)

    @property
    def scope(self):
        # A read inside a module-level `if`/`for`/`try` block IS module scope:
        # it executes at import.  Only a def/class/lambda changes the answer.
        return self._scope[-1]

    # ---- the environ matchers ------------------------------------------
    def _is_environ(self, node) -> bool:
        if isinstance(node, ast.Attribute) and node.attr == "environ":
            return isinstance(node.value, ast.Name) and node.value.id in self.os_aliases
        if isinstance(node, ast.Name):
            return node.id in self.environ_aliases
        return False

    def visit_Subscript(self, node):
        if self._is_environ(node.value):
            # A WRITE OR A DELETE IS NOT A READ.  `os.environ["X"] = ...`
            # supplies the name, it does not consume it, and counting it as a
            # fatal read would block a launcher that is already correct.
            if isinstance(getattr(node, "ctx", None), ast.Load):
                key = node.slice
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    self.reads.append({"name": key.value, "line": node.lineno,
                                       "kind": _FATAL, "scope": self.scope})
                else:
                    self.unresolvable.append(
                        {"line": node.lineno, "scope": self.scope,
                         "expr": _unparse(node)})
        self.generic_visit(node)

    def visit_Call(self, node):
        f = node.func
        name = None
        if isinstance(f, ast.Attribute) and f.attr == "get" and self._is_environ(f.value):
            name = _const_arg0(node)
        elif isinstance(f, ast.Attribute) and f.attr == "getenv" \
                and isinstance(f.value, ast.Name) and f.value.id in self.os_aliases:
            name = _const_arg0(node)
        elif isinstance(f, ast.Name) and f.id in self.getenv_aliases:
            name = _const_arg0(node)
        if name is not None:
            self.reads.append({"name": name, "line": node.lineno,
                               "kind": _DEFAULTED, "scope": self.scope})
        self.generic_visit(node)


def _const_arg0(call):
    if call.args and isinstance(call.args[0], ast.Constant) \
            and isinstance(call.args[0].value, str):
        return call.args[0].value
    return "<NON-CONSTANT>"


def _unparse(node):
    try:
        return ast.unparse(node)
    except Exception:
        return "<unparseable>"


def extract_env_reads(producer_path):
    """Every process-environment read in the producer, classified and scoped.

    A SYNTAX ERROR REFUSES.  A producer this reader cannot parse is a producer
    about which it knows nothing, and reporting "no fatal reads" over it would
    be a planted zero of exactly the shape `CLAUDE.md` rule 3 forbids.
    """
    src = read_text(producer_path)
    try:
        tree = ast.parse(src, filename=str(producer_path))
    except SyntaxError as exc:
        raise Refusal("REFUSE G-ENVSEAM c1: producer %s does not parse (%s) -- "
                      "a reader that cannot parse its subject knows nothing "
                      "about it and must not report a clean set"
                      % (producer_path, exc))
    v = _EnvVisitor()
    v.visit(tree)
    return v.reads, v.unresolvable


# =========================================================================
# THE TWO EXTRACTORS THAT MAKE SECTION 4.1 TRUE
# =========================================================================

def supplied_from_docker_env(argv):
    """The names the `-e` ARRAY supplies, read OUT OF THE ARRAY ITSELF.

    `argv` is `"${DOCKER_ENV[@]}"` -- the same shell array, expanded, that
    `a1wrt3_run_arm.sh` expands into `docker run`.  Not a transcription of it.

    AN UNRECOGNISED TOKEN REFUSES.  Skipping one would silently shrink the
    supplied set and turn a launcher typo into a gate that passes.

    THE BARE PASS-THROUGH FORM `-e NAME` IS REFUSED.  It makes the supplied set
    depend on the HOST's ambient environment, which nothing in the manifest
    records and no reader downstream can reconstruct -- the same "declared the
    wrong side of the boundary" defect the manifest itself is being repaired
    for.  Every entry must be `NAME=VALUE`.
    """
    names = {}
    i = 0
    n = len(argv)
    while i < n:
        tok = argv[i]
        spec = None
        if tok in ("-e", "--env"):
            if i + 1 >= n:
                raise Refusal("REFUSE G-ENVSEAM c1: '%s' at end of the -e array "
                              "with no specification following" % tok)
            spec = argv[i + 1]
            i += 2
        elif tok.startswith("-e") and len(tok) > 2:
            spec = tok[2:]
            i += 1
        elif tok.startswith("--env="):
            spec = tok[len("--env="):]
            i += 1
        else:
            raise Refusal("REFUSE G-ENVSEAM c1: unrecognised token %r in the -e "
                          "array at index %d -- an unrecognised token is not "
                          "skipped, because skipping one silently shrinks the "
                          "supplied set" % (tok, i))
        if "=" not in spec:
            raise Refusal("REFUSE G-ENVSEAM c1: bare pass-through '-e %s' is "
                          "refused -- it makes the supplied set depend on the "
                          "host's ambient environment, which the manifest "
                          "cannot record" % spec)
        nm, val = spec.split("=", 1)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nm):
            raise Refusal("REFUSE G-ENVSEAM c1: %r is not a legal environment "
                          "variable name" % nm)
        names[nm] = val
    return names


def translation_names(cmd_sh_path):
    """The `AOA_*` names the C13 translation sets, READ OUT OF `a1wrt3_cmd.sh`.

    THE GATE READS THE FILE THAT RUNS INSIDE THE CONTAINER.  A hand-maintained
    copy of this list is exactly what section 4.1 rejects.

    Missing markers, an empty block, or a line inside the block that is not an
    assignment ALL REFUSE.  An empty translation block read as "no names" would
    make clause 1 report every producer name missing, or -- worse, if the
    producer were also trivial -- report clean over a translation that does not
    exist.
    """
    text = read_text(cmd_sh_path)
    lines = text.splitlines()
    try:
        b = next(i for i, ln in enumerate(lines) if XLAT_BEGIN in ln)
        e = next(i for i, ln in enumerate(lines) if XLAT_END in ln)
    except StopIteration:
        raise Refusal("REFUSE G-ENVSEAM c1: %s does not carry both registered "
                      "translation markers %r / %r -- the supplied set cannot "
                      "be extracted from the file that runs, and it will not "
                      "be re-typed" % (cmd_sh_path, XLAT_BEGIN, XLAT_END))
    if e <= b:
        raise Refusal("REFUSE G-ENVSEAM c1: translation markers out of order in %s"
                      % cmd_sh_path)
    names = []
    for ln in lines[b + 1:e]:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r'([A-Za-z_][A-Za-z0-9_]*)=', s)
        if not m:
            raise Refusal("REFUSE G-ENVSEAM c1: line inside the C13 translation "
                          "block of %s is not an assignment: %r -- the block is "
                          "the gate's source of truth and it may not contain "
                          "anything the gate cannot read" % (cmd_sh_path, s))
        names.append(m.group(1))
    if not names:
        raise Refusal("REFUSE G-ENVSEAM c1: the C13 translation block in %s is "
                      "EMPTY.  An empty translation is the A1WRT2 defect itself; "
                      "it is refused, not reported as a set of size zero."
                      % cmd_sh_path)
    return names


# =========================================================================
# G-ENVSEAM CLAUSE 1
# =========================================================================

def gate_envseam_clause1(producer_path, docker_env_argv, cmd_sh_path=None):
    """HOST-SIDE, STATIC, BEFORE THE CONTAINER STARTS.

    Returns `(verdict, missing, notes)`.  `verdict` is `PASS` or `BLOCKED`;
    `BLOCKED` means THE CONTAINER DOES NOT START, which is the whole purpose of
    putting this gate in front of it: the repair being incomplete costs zero
    compute instead of a four-second crash and a burned pre-registration.

    `missing` is the SORTED LIST OF EVERY unsupplied fatal name.  IT IS NEVER
    TRUNCATED AND NEVER SHORT-CIRCUITED AFTER THE FIRST.  A successor that
    "fixes" A1WRT2 by adding a single `-e` reproduces the defect, and control
    `E1` asserts ALL FOUR names come back.
    """
    notes = []
    supplied = dict(supplied_from_docker_env(docker_env_argv))
    notes.append("G-ENVSEAM c1: -e array supplies %d name(s): %s"
                 % (len(supplied), " ".join(sorted(supplied)) or "(none)"))

    xlat = []
    if cmd_sh_path is not None:
        xlat = translation_names(cmd_sh_path)
        notes.append("G-ENVSEAM c1: C13 translation in %s sets %d name(s), "
                     "EXTRACTED FROM THE FILE THAT RUNS: %s"
                     % (cmd_sh_path, len(xlat), " ".join(xlat)))
    else:
        notes.append("G-ENVSEAM c1: NO in-container translation layer supplied "
                     "-- this is the A1WRT2 configuration")

    will_receive = set(supplied) | set(xlat)

    reads, unresolvable = extract_env_reads(producer_path)
    fatal = sorted({r["name"] for r in reads if r["kind"] == _FATAL})
    defaulted = sorted({r["name"] for r in reads if r["kind"] == _DEFAULTED})
    notes.append("G-ENVSEAM c1: producer %s reads %d FATAL name(s) %s and %d "
                 "DEFAULTED name(s) %s"
                 % (producer_path, len(fatal), fatal, len(defaulted), defaulted))
    for r in reads:
        if r["kind"] == _FATAL:
            notes.append("    FATAL  %-20s line %-5d scope %s"
                         % (r["name"], r["line"], r["scope"]))

    if unresolvable:
        for u in unresolvable:
            notes.append("    UNRESOLVABLE subscript at line %d (%s): %s"
                         % (u["line"], u["scope"], u["expr"]))
        return ("BLOCKED", [],
                notes + ["G-ENVSEAM c1: BLOCKED -- %d os.environ subscript(s) "
                         "with a NON-CONSTANT key.  The gate cannot enumerate "
                         "what it cannot resolve and will not report clean over "
                         "it." % len(unresolvable)])

    missing = sorted(n for n in fatal if n not in will_receive)
    if missing:
        notes.append("G-ENVSEAM c1: BLOCKED -- %d fatal name(s) NOT SUPPLIED: %s"
                     % (len(missing), " ".join(missing)))
        notes.append("G-ENVSEAM c1: the container DOES NOT START.")
        return "BLOCKED", missing, notes

    # THE SET IT COMPARED AGAINST IS PRINTED ON THE PASS PATH TOO, so the
    # gate's silence is not its evidence (draft section 4.2 control `E2`).
    notes.append("G-ENVSEAM c1: PASS -- all %d fatal name(s) supplied; the set "
                 "compared against was %s"
                 % (len(fatal), " ".join(sorted(will_receive))))
    return "PASS", [], notes


# =========================================================================
# G-WALLTREAT -- THE HOST-SIDE CLAUSES
# =========================================================================

_BC_LINE = re.compile(r"BCType=nutLowReWallFunction")
_SPALDING = ("nutUSpaldingWallFunction", "nutkWallFunction", "nutUWallFunction")


def gate_walltreat_clause2(sweep_log):
    """WHAT THE SOLVER SAID IT DID.  Counted in that arm's OWN `sweep.log`.

    An UNREADABLE log REFUSES at exit 2; a readable log with COUNT 0 is
    `GATE FAIL`.  The two are different findings and are given different
    outcomes -- a refusal is "I could not see", a GATE FAIL is "I saw, and it
    was wrong".
    """
    text = read_text(sweep_log)          # refuses on absent/unreadable
    count = len(_BC_LINE.findall(text))
    if count == 0:
        return ("GATE FAIL", count,
                "G-WALLTREAT c2: GATE FAIL -- 0 occurrences of "
                "BCType=nutLowReWallFunction in %s" % sweep_log)
    return ("PASS", count,
            "G-WALLTREAT c2: PASS -- %d occurrence(s) of "
            "BCType=nutLowReWallFunction in %s" % (count, sweep_log))


def gate_walltreat_clause3(sweep_log):
    """THE NEGATIVE LIMB.  Any Spalding/high-Re wall-function line REFUSES.

    This is not a GATE FAIL.  A wall-resolved item whose solver installed a
    wall-function BC has produced numbers from a different physical model
    wearing this item's label, and the honest outcome is a refusal, not a
    graded failure that still leaves the numbers on the page.
    """
    text = read_text(sweep_log)
    hits = [(w, text.count(w)) for w in _SPALDING if w in text]
    if hits:
        raise Refusal("REFUSE G-WALLTREAT c3: wall-function line(s) in %s: %s"
                      % (sweep_log, ", ".join("%s x%d" % h for h in hits)))
    return ("PASS", 0,
            "G-WALLTREAT c3: PASS -- none of %s present in %s"
            % (", ".join(_SPALDING), sweep_log))


def gate_walltreat_presence(container_log, expect_md5=PIN_RUNSCRIPT_MD5):
    """THE COUNT-PINNED PRESENCE ASSERTION, AND LIMB (c)'s HOST SIDE.

    L-493: A PLANTED CONTROL THAT TESTS FOR PRESENCE CAN BE SATISFIED BY THE
    RIGHT ANSWER ARRIVING BY THE WRONG ROUTE -- PIN THE COUNT OR THE PATH, NOT
    THE APPEARANCE.  So this asserts the marker occurs EXACTLY ONCE in THAT
    ARM'S OWN `container.log`: not "at least once", not "somewhere in the run
    root".  Control `W4b` drives the duplicated direction and control `W4a` the
    absent one.

    Absent (count 0) is reported as *THE PRE-SOLVER WALL-TREATMENT GUARD DID
    NOT RUN*, which is a DIFFERENT FINDING from *it ran and failed*, and it is
    reported as a different one.  `A1WRT/cmd.sh:44` printed this line on the
    pass path and NOTHING ON THE HOST EVER ASSERTED IT WAS THERE -- so if
    `cmd.sh` had never been reached at all, the host would have seen exactly
    what it sees on a pass.
    """
    text = read_text(container_log)
    lines = [ln for ln in text.splitlines() if WALLTREAT_OK_MARKER in ln]
    n = len(lines)
    if n == 0:
        return ("GATE FAIL", None,
                "G-WALLTREAT presence: GATE FAIL -- %s absent from %s: THE "
                "PRE-SOLVER WALL-TREATMENT GUARD DID NOT RUN (this is not the "
                "same finding as: it ran and failed)"
                % (WALLTREAT_OK_MARKER, container_log))
    if n != 1:
        return ("GATE FAIL", None,
                "G-WALLTREAT presence: GATE FAIL -- %s occurs %d times in %s, "
                "the pinned count is exactly 1 (L-493: pin the count, not the "
                "appearance)" % (WALLTREAT_OK_MARKER, n, container_log))
    m = re.search(r"\bmd5=([0-9a-f]{32})\b", lines[0])
    if not m:
        return ("GATE FAIL", None,
                "G-WALLTREAT limb (c): GATE FAIL -- the OK line in %s carries "
                "no md5 field; a gate that reports on bytes it cannot identify "
                "is a gate on nothing" % container_log)
    got = m.group(1)
    if got != expect_md5:
        return ("GATE FAIL", got,
                "G-WALLTREAT limb (c): GATE FAIL -- the guard read bytes with "
                "md5 %s, the pinned producer is %s.  THIS FAMILY WAS MEASURED "
                "RESOLVING runScript.py BY BASENAME ACROSS 59 CANDIDATES AND "
                "SILENTLY PICKING THE WRONG ONE." % (got, expect_md5))
    pm = re.search(r"\bpath=(\S+)", lines[0])
    return ("PASS", got,
            "G-WALLTREAT presence+limb(c): PASS -- %s occurs exactly once in "
            "%s, naming path=%s with md5=%s == pin"
            % (WALLTREAT_OK_MARKER, container_log,
               pm.group(1) if pm else "UNSTATED", got))


# =========================================================================
# CLI -- the form `a1wrt3_run_arm.sh` calls, BEFORE the container starts
# =========================================================================

def main(argv=None):
    ap = argparse.ArgumentParser(prog="a1wrt3_instruments.py", add_help=True)
    ap.add_argument("--gate-envseam", action="store_true")
    ap.add_argument("--extract-reads", action="store_true")
    ap.add_argument("--producer")
    ap.add_argument("--cmd-sh", default=None)
    ap.add_argument("--json", action="store_true")
    # MUST BE LAST ON THE COMMAND LINE.  `a1wrt3_run_arm.sh` expands
    # `"${DOCKER_ENV[@]}"` here -- the SAME ARRAY it expands into `docker run`.
    ap.add_argument("--docker-env", nargs=argparse.REMAINDER, default=[])
    args = ap.parse_args(argv)

    try:
        if args.extract_reads:
            reads, unres = extract_env_reads(args.producer)
            print(json.dumps({"reads": reads, "unresolvable": unres}, indent=1))
            return 0
        if args.gate_envseam:
            if not args.producer:
                raise Refusal("REFUSE: --gate-envseam requires --producer")
            verdict, missing, notes = gate_envseam_clause1(
                args.producer, args.docker_env, args.cmd_sh)
            for n in notes:
                print(n)
            print("A1WRT3_GATE G-ENVSEAM %s missing=%d names=%s"
                  % (verdict, len(missing), ",".join(missing) or "-"))
            return 0 if verdict == "PASS" else 9
        ap.error("no action requested")
    except Refusal as r:
        print(str(r))
        return r.code
    return 0


if __name__ == "__main__":
    sys.exit(main())
