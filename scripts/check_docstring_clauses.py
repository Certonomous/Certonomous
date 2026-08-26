#!/usr/bin/env python3
"""A COMMENT THAT NAMES A CLAUSE IS THE IMPLEMENTATION'S ALIBI, NOT ITS EVIDENCE.

Measured three times in three independent instruments on 2026-08-25/26:

  D4-DEF-7        `d4_grade.py`'s `g_completion` docstring names `rc == 0`, a
                  terminal statement from the producer's own log FILE, and the
                  age guard -- and implements THE AGE GUARD ALONE.  D4 emitted
                  `G1_completion_and_age = PASS` on a run whose REQUIRED arm F
                  ledger row reads `rc=1`.
  D4-DEF-7 (2)    `d4_grade_SUPPLEMENT.py` carries the SAME docstring and the
                  SAME omission.
  D7R-GRADER-DEF-7  `d7_grade.py`'s `g1_completion` names three clauses and
                  implements two.  THE SHARPEST FORM: in that whole 74,338-byte
                  file the string `End` occurs EXACTLY ONCE -- inside the
                  docstring that claims the check.

The docstring was the only place the missing clause existed, and every reader
downstream -- including two supervisors -- took the NAME for the CHECK.

WHAT THIS FILE DOES.  For each target function it AST-parses the file, reads the
function's docstring, works out which registered CLAUSES the docstring NAMES,
and then asks whether each named clause appears in an EXECUTABLE node of that
function's own body.  A clause named in prose and absent from the code is
reported as `ALIBI`.

WHAT IT DOES NOT DO, stated so nobody over-reads it.  It does not verify that an
implementation is CORRECT -- only that one is PRESENT.  A wrong `rc` test passes
this check.  It is a floor, not a gate, and it is not a substitute for reading
the diff.

REFUSES (exit 2) rather than degrading, this family's discipline:
  * a target file or function that does not exist;
  * a target whose docstring names ZERO registered clauses -- a check with
    nothing to check is not a check (L-302);
  * zero targets resolved.

EXIT 0  every clause named by every target is implemented
EXIT 1  at least one ALIBI found
EXIT 2  refusal
EXIT 3  selftest failure

`--selftest` DEMONSTRATES each detector by building a fixture that violates
exactly one thing and REQUIRING the detector to fire, and a clean fixture and
REQUIRING it not to.  A check not shown to fire is ceremony (CLAUDE.md rule 3's
principle, applied to a guard rather than a zero).
"""
import argparse
import ast
import json
import os
import re
import sys


class Refuse(Exception):
    pass


def refuse(where, detail):
    raise Refuse("%s: %s" % (where, json.dumps(detail, sort_keys=True, default=str)[:900]))


# ---------------------------------------------------------------- helpers
def _executable_nodes(fn):
    """Every node of the function body EXCEPT bare string-expression statements.

    A bare string expression has no effect: it is a docstring or a prose note,
    and it is exactly the thing this file exists to refuse to count as code.
    """
    out = []
    for stmt in fn.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) \
                and isinstance(stmt.value.value, str):
            continue                      # the docstring, or a prose note
        for n in ast.walk(stmt):
            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) \
                    and isinstance(n.value.value, str):
                continue
            out.append(n)
    return out


def _str_constants(nodes):
    return [n.value for n in nodes
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _identifiers(nodes):
    ids = set()
    for n in nodes:
        if isinstance(n, ast.Name):
            ids.add(n.id)
        elif isinstance(n, ast.Attribute):
            ids.add(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            ids.add(n.value)
    return ids


# ------------------------------------------------------- the clause registry
def _det_rc_zero(nodes):
    """An executable comparison between something called `rc` and 0."""
    for n in nodes:
        if not isinstance(n, ast.Compare):
            continue
        operands = [n.left] + list(n.comparators)
        names = set()
        has_zero = False
        for o in operands:
            for sub in ast.walk(o):
                if isinstance(sub, ast.Name):
                    names.add(sub.id)
                elif isinstance(sub, ast.Attribute):
                    names.add(sub.attr)
                elif isinstance(sub, ast.Constant):
                    if isinstance(sub.value, str):
                        names.add(sub.value)
                    elif sub.value == 0 and not isinstance(sub.value, bool):
                        has_zero = True
        if has_zero and any(x == "rc" or x.endswith("_rc") or x.startswith("rc")
                            for x in names):
            return {"node": type(n).__name__, "lineno": getattr(n, "lineno", None)}
    return None


TERMINAL_TOKENS = re.compile(r"(^|[^A-Za-z])End([^A-Za-z]|$)|Finalising|\.log\.ok|"
                             r"Simulation completed|ExecutionTime")


def _det_log_terminal(nodes):
    """A terminal statement READ OUT OF THE PRODUCER'S OWN LOG FILE.

    Satisfied by an executable string constant carrying a terminal token, or by
    a call that opens/reads something whose name mentions a log.
    """
    for s in _str_constants(nodes):
        if TERMINAL_TOKENS.search(s):
            return {"evidence": "string constant %r" % s[:60]}
    ids = _identifiers(nodes)
    opens_a_log = any(("log" in str(i).lower()) for i in ids)
    calls_open = any(isinstance(n, ast.Call) and (
        (isinstance(n.func, ast.Name) and n.func.id == "open")
        or (isinstance(n.func, ast.Attribute) and n.func.attr in ("read", "readlines")))
        for n in nodes)
    if opens_a_log and calls_open:
        return {"evidence": "reads a name mentioning 'log'"}
    return None


def _det_age_guard(nodes):
    ids = _identifiers(nodes)
    if any("mtime" in str(i) for i in ids):
        return {"evidence": "mtime access"}
    if any("datum" in str(i).lower() for i in ids):
        return {"evidence": "age datum"}
    return None


CLAUSES = [
    {"id": "RC_ZERO",
     "doc": re.compile(r"\brc\s*(==|!=|=)\s*0\b"),
     "what": "the producer's return code compared to 0",
     "det": _det_rc_zero},
    {"id": "LOG_TERMINAL",
     "doc": re.compile(r"terminal statement|terminal line|"
                       r"own (output|log) FILE terminal|"
                       r"producer'?s own (output|log) FILE|"
                       r"an?\s+`?End`?\s+line", re.I),
     "what": "a terminal statement read from the producer's own log FILE",
     "det": _det_log_terminal},
    {"id": "AGE_GUARD",
     "doc": re.compile(r"age[ -]guard|age datum|strictly NEWER|newer than", re.I),
     "what": "the age guard",
     "det": _det_age_guard},
]


# --------------------------------------------------------------- the check
def check_function(path, funcname, src=None):
    if src is None:
        if not os.path.isfile(path):
            refuse("target", {"file_absent": path})
        src = open(path, errors="replace").read()
    tree = ast.parse(src, filename=path)
    fn = None
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == funcname:
            fn = n
            break
    if fn is None:
        refuse("target", {"file": path, "function_not_found": funcname})
    doc = ast.get_docstring(fn) or ""
    nodes = _executable_nodes(fn)
    named, findings = [], []
    for spec in CLAUSES:
        if not spec["doc"].search(doc):
            continue
        named.append(spec["id"])
        hit = spec["det"](nodes)
        findings.append({"clause": spec["id"], "what": spec["what"],
                         "implemented": bool(hit), "evidence": hit,
                         "verdict": "OK" if hit else "ALIBI"})
    if not named:
        refuse("check_function",
               {"file": path, "function": funcname,
                "clauses_named_by_docstring": 0,
                "note": "this docstring names none of the registered clauses, so "
                        "this check checked nothing; a check with nothing to "
                        "check is not a check (L-302)"})
    return {"file": path, "function": funcname, "lineno": fn.lineno,
            "n_executable_nodes": len(nodes),
            "clauses_named": named, "n_clauses_named": len(named),
            "findings": findings,
            "n_alibi": sum(1 for f in findings if not f["implemented"])}


# --------------------------------------------------------------- selftest
_CLEAN = '''
import os
def g1(work, ledger, arms):
    """rc == 0, the producer's own output FILE terminal, and THE AGE GUARD --
    every graded artifact strictly NEWER than the case's own datum."""
    ok = True
    for a in arms:
        rc = ledger[a]["rc"]
        if rc != 0:
            ok = False
    txt = open(os.path.join(work, ledger["log"])).read()
    if "End" not in txt:
        ok = False
    datum = int(open(os.path.join(work, ".datum")).read())
    if int(os.stat(work).st_mtime) <= datum:
        ok = False
    return ok
'''


def _mutate(src, drop):
    """Remove exactly one clause's implementation, leaving the docstring."""
    if drop == "RC_ZERO":
        return src.replace('        rc = ledger[a]["rc"]\n'
                           '        if rc != 0:\n'
                           '            ok = False\n',
                           '        rec = {"rc": ledger[a]["rc"]}\n')
    if drop == "LOG_TERMINAL":
        return src.replace('    txt = open(os.path.join(work, ledger["log"])).read()\n'
                           '    if "End" not in txt:\n'
                           '        ok = False\n', '')
    if drop == "AGE_GUARD":
        return src.replace('    datum = int(open(os.path.join(work, ".datum")).read())\n'
                           '    if int(os.stat(work).st_mtime) <= datum:\n'
                           '        ok = False\n', '')
    raise AssertionError(drop)


def selftest():
    units = []

    def unit(name, want, got, detail=""):
        units.append({"unit": name, "ok": want == got, "want": want,
                      "got": got, "detail": detail})

    r = check_function("<clean>", "g1", src=_CLEAN)
    unit("CLEAN names all three clauses", 3, r["n_clauses_named"])
    unit("CLEAN has zero ALIBI", 0, r["n_alibi"],
         "named=%s" % ",".join(r["clauses_named"]))

    for cid in ("RC_ZERO", "LOG_TERMINAL", "AGE_GUARD"):
        m = _mutate(_CLEAN, cid)
        if m == _CLEAN:
            unit("MUTANT %s actually changed the source" % cid, True, False,
                 "THE MUTATION DID NOT APPLY -- the unit below would be vacuous")
            continue
        unit("MUTANT %s actually changed the source" % cid, True, True)
        rr = check_function("<mutant-%s>" % cid, "g1", src=m)
        got = [f["clause"] for f in rr["findings"] if not f["implemented"]]
        unit("MUTANT %s FIRES, and on that clause alone" % cid, [cid], got)
        unit("MUTANT %s still names all three in prose" % cid, 3,
             rr["n_clauses_named"],
             "the docstring is the alibi and it is untouched")

    # a docstring that names nothing registered must REFUSE, not pass
    nada = 'def g1(a):\n    """Grades things."""\n    return True\n'
    try:
        check_function("<no-clauses>", "g1", src=nada)
        unit("docstring naming zero clauses REFUSES", "REFUSED", "no-refusal")
    except Refuse:
        unit("docstring naming zero clauses REFUSES", "REFUSED", "REFUSED")
    try:
        check_function("<missing-fn>", "not_there", src=_CLEAN)
        unit("absent function REFUSES", "REFUSED", "no-refusal")
    except Refuse:
        unit("absent function REFUSES", "REFUSED", "REFUSED")

    n_ok = sum(1 for u in units if u["ok"])
    for u in units:
        sys.stdout.write("  %-52s %s  %s\n"
                         % (u["unit"], "ok" if u["ok"] else "FAILED",
                            u["detail"] or ("want=%r got=%r" % (u["want"], u["got"]))))
    sys.stdout.write("DOCSTRING_CLAUSE_SELFTEST units=%d passed=%d failed=%d\n"
                     % (len(units), n_ok, len(units) - n_ok))
    if not units:
        sys.stdout.write("REFUSE zero units ran\n")
        return 3
    return 0 if n_ok == len(units) else 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", action="append", default=[],
                    metavar="FILE:FUNCTION")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.target:
        sys.stderr.write("DOCSTRING_CLAUSE REFUSED no --target given; zero "
                         "targets resolved is a refusal, never a pass\n")
        sys.exit(2)
    out, n_alibi = [], 0
    try:
        for t in a.target:
            if ":" not in t:
                refuse("argv", {"target_not_FILE:FUNCTION": t})
            path, fn = t.rsplit(":", 1)
            r = check_function(path, fn)
            out.append(r)
            n_alibi += r["n_alibi"]
    except Refuse as exc:
        sys.stderr.write("DOCSTRING_CLAUSE REFUSED %s\n" % exc)
        sys.exit(2)
    if a.json:
        sys.stdout.write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    else:
        for r in out:
            sys.stdout.write("%s:%s (line %d, %d executable nodes)\n"
                             % (r["file"], r["function"], r["lineno"],
                                r["n_executable_nodes"]))
            for f in r["findings"]:
                sys.stdout.write("    %-14s %-6s %s\n"
                                 % (f["clause"], f["verdict"], f["what"]))
    sys.stdout.write("DOCSTRING_CLAUSE targets=%d alibis=%d\n" % (len(out), n_alibi))
    sys.exit(1 if n_alibi else 0)


if __name__ == "__main__":
    main()
