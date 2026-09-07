#!/usr/bin/env python3
"""check_sidecar_before_run.py -- STATIC pre-freeze ordering check.

WHAT IT ENFORCES (L-504 clause-(c), producer side)
---------------------------------------------------
A rig / runScript that echoes its INPUT design vector to a sidecar file (an
`injected_dv.json` / `*_echo.json` / `*sidecar*` write) MUST perform that write
BEFORE it triggers the primal (`prob.run_model()` / `prob.run()` /
`prob.run_driver()`). If the echo is written AFTER the run call, then on a leg
where the primal raises DAFoam's EXPECTED post-End
`AnalysisError("Primal solution failed!")`, the write is never reached, the
sidecar is absent, and any downstream F4 echo-check hard-REFUSES (exit 2) on the
very legs the experiment is designed to count. This is exactly the SO3DR-F4
defect, and the fourth occurrence this session of the write-after-run class
(D6RF5, D6RF6, D9successor, SO3DR-F4). This check turns that repeatedly-paid
lesson into an enforced invariant: it REFUSES (nonzero exit) if a sidecar-echo
write's source line is after a run-trigger call's source line.

THE RULE (single comparison, honest and conservative)
-----------------------------------------------------
Let W = the set of source line numbers of sidecar-echo write calls, and
R = the set of source line numbers of run-trigger calls. The check REFUSES iff
`max(W) > min(R)` -- i.e. iff there EXISTS an echo write that lands after SOME
run call. An input echo must precede EVERY run trigger, so "write before the
earliest run" is the invariant; anything later cannot be guaranteed to survive
a raise. A file with no sidecar-echo write, or no run call, trivially PASSES
(there is nothing to order).

HOW IT RESOLVES LINES (AST, not regex)
--------------------------------------
The file is parsed with `ast`; line numbers come from real call nodes, so a
token appearing in a comment or an unrelated string cannot fire it and a call
split across several physical lines is attributed to the `ast.Call.lineno`
(the line the call name sits on). A run-trigger is an `ast.Call` whose function
is an attribute or name in {run_model, run, run_driver}. A sidecar-echo write is
an `ast.Call` to `open(...)` in a write mode ('w','wb','a','ab','x','w+', ...)
whose path argument (a) contains a string literal carrying an echo token, or
(b) references a local name previously bound to an expression that contains such
a string literal (one level of name resolution, documented below).

Echo tokens (case-insensitive substring, on string literals only):
    injected_dv, sidecar, _echo, echo_    -- extend ECHO_TOKENS to widen.

WHAT A STATIC CHECK CANNOT CATCH (stated honestly)
--------------------------------------------------
  * A path assembled with NO token-bearing string literal at all (e.g. a name
    built from `os.path.basename(__file__)`, an f-string with only a variable,
    or a path read from argv/JSON). Name resolution here is ONE level and
    literal-based; deeper dataflow is out of scope.
  * A write performed by a helper function called after the run, where the
    open() lives in the helper's body (a different lineno space). This check is
    intra-file and per-call-node; it does not follow the call graph. Prefer
    keeping the echo write inline in the rig's main(), which is where the
    ordering matters and where this check sees it.
  * A run triggered by a name this check does not know (a custom driver method).
    Extend RUN_TRIGGER_ATTRS if a rig uses one.
  * It does NOT verify the sidecar's FIELDS are pre-run knowable -- that is a
    human/field-by-field review (done for SO3DR-F4 in the successor prereg). It
    only enforces ORDERING.
This is a NECESSARY, not sufficient, guard: it makes the common write-after-run
mistake impossible to freeze silently; it does not prove the echo is correct.

PLANTED-CONTROL DISCIPLINE (CLAUDE.md rule 3 family)
----------------------------------------------------
`--selftest` runs the checker against TWO synthetic fixtures held in this file:
a write-AFTER-run fixture (the checker MUST fire / refuse) and a write-BEFORE-run
fixture (the checker MUST pass). A checker that cannot be shown to FIRE is not
evidence -- so the selftest fails unless the refusing fixture actually refuses
AND the passing fixture actually passes.

EXITS: 0 PASS (ordering ok, or nothing to order) | 3 REFUSE (write-after-run) |
       2 usage | 4 parse error. SUBMISSIONS PARKED; nothing leaves the box.
"""
import os
import sys
import ast
import argparse

RUN_TRIGGER_ATTRS = {"run_model", "run", "run_driver"}
ECHO_TOKENS = ("injected_dv", "sidecar", "_echo", "echo_")
WRITE_MODES = {"w", "wb", "a", "ab", "x", "xb", "w+", "wb+", "a+", "ab+", "r+"}


class OrderingRefusal(Exception):
    """Raised when a sidecar-echo write is ordered after a run-trigger call."""


def _has_echo_token(s):
    if not isinstance(s, str):
        return False
    low = s.lower()
    return any(tok in low for tok in ECHO_TOKENS)


def _string_literals(node):
    """Yield every str constant appearing anywhere under `node`."""
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            yield n.value


def _collect_token_names(tree):
    """One level of name resolution: names bound (via `name = <expr>`) to an
    expression that contains an echo-token string literal. Lets the check see
    `p = os.path.join(d, "injected_dv.json"); open(p, "w")`."""
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            if any(_has_echo_token(s) for s in _string_literals(n.value)):
                for tgt in n.targets:
                    if isinstance(tgt, ast.Name):
                        names.add(tgt.id)
        elif isinstance(n, (ast.AnnAssign, ast.NamedExpr)):
            val = n.value
            if val is not None and any(_has_echo_token(s) for s in _string_literals(val)):
                tgt = n.target
                if isinstance(tgt, ast.Name):
                    names.add(tgt.id)
    return names


def _is_open_call(call):
    f = call.func
    if isinstance(f, ast.Name):
        return f.id == "open"
    if isinstance(f, ast.Attribute):
        return f.attr == "open"     # io.open / os.open-style
    return False


def _open_is_write_mode(call):
    """True if this open() call carries a write/append mode (positional 2nd arg
    or a mode= kwarg). A default (read) open() is NOT a write."""
    if len(call.args) >= 2:
        m = call.args[1]
        if isinstance(m, ast.Constant) and isinstance(m.value, str) and m.value in WRITE_MODES:
            return True
    for kw in call.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant) \
                and isinstance(kw.value.value, str) and kw.value.value in WRITE_MODES:
            return True
    return False


def _open_path_is_echo(call, token_names):
    """True if the open() path argument carries an echo token, either as a string
    literal anywhere in the path expression or as a resolved token-bearing name."""
    if not call.args:
        return False
    path_arg = call.args[0]
    for s in _string_literals(path_arg):
        if _has_echo_token(s):
            return True
    for n in ast.walk(path_arg):
        if isinstance(n, ast.Name) and n.id in token_names:
            return True
    return False


def _is_run_trigger(call):
    f = call.func
    if isinstance(f, ast.Attribute):
        return f.attr in RUN_TRIGGER_ATTRS
    if isinstance(f, ast.Name):
        return f.id in RUN_TRIGGER_ATTRS
    return False


def scan_source(source, filename="<string>"):
    """Return (report_dict). Raises OrderingRefusal if write-after-run; raises
    SyntaxError (caller maps to exit 4) if the source does not parse."""
    tree = ast.parse(source, filename=filename)
    token_names = _collect_token_names(tree)

    run_lines = []
    write_lines = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _is_run_trigger(node):
            run_lines.append(node.lineno)
        elif _is_open_call(node) and _open_is_write_mode(node) and _open_path_is_echo(node, token_names):
            write_lines.append(node.lineno)

    report = {
        "file": filename,
        "run_trigger_lines": sorted(run_lines),
        "sidecar_echo_write_lines": sorted(write_lines),
        "resolved_token_names": sorted(token_names),
    }
    if not write_lines or not run_lines:
        report["verdict"] = "PASS"
        report["reason"] = "nothing to order (no echo write, or no run trigger)"
        return report

    latest_write = max(write_lines)
    earliest_run = min(run_lines)
    if latest_write > earliest_run:
        report["verdict"] = "REFUSE"
        raise OrderingRefusal(
            "%s: sidecar-echo write at line %d is AFTER a run-trigger at line %d. "
            "On a primal-raised leg the echo is never written and F4 hard-refuses. "
            "Move the echo write BEFORE the run call (L-504 clause-c)."
            % (filename, latest_write, earliest_run)
        )
    report["verdict"] = "PASS"
    report["reason"] = ("all %d echo write(s) precede the earliest run trigger "
                        "(max write line %d <= min run line %d)"
                        % (len(write_lines), latest_write, earliest_run))
    return report


def check_file(path):
    """Scan one file. Returns exit code: 0 PASS, 3 REFUSE, 4 parse error."""
    try:
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
    except OSError as e:
        sys.stderr.write("check_sidecar_before_run: cannot read %s: %s\n" % (path, e))
        return 4
    try:
        rep = scan_source(src, filename=path)
    except SyntaxError as e:
        sys.stderr.write("check_sidecar_before_run: parse error in %s: %s\n" % (path, e))
        return 4
    except OrderingRefusal as e:
        sys.stderr.write("REFUSE (exit 3): %s\n" % e)
        return 3
    sys.stdout.write("PASS: %s -- %s\n" % (path, rep["reason"]))
    return 0


# --------------------------------------------------------------------------
# PLANTED CONTROL (rule 3 family): the checker must be shown able to FIRE
# --------------------------------------------------------------------------
_FIXTURE_AFTER = '''
import os, json
def main():
    run_dir_abs = os.path.join(os.getcwd(), "mp04")
    prob = object()
    prob.run_model()
    with open(os.path.join(run_dir_abs, "injected_dv.json"), "w") as fh:
        json.dump({"a": 1}, fh)
'''

_FIXTURE_BEFORE = '''
import os, json
def main():
    run_dir_abs = os.path.join(os.getcwd(), "mp04")
    with open(os.path.join(run_dir_abs, "injected_dv.json"), "w") as fh:
        json.dump({"a": 1}, fh)
    prob = object()
    prob.run_model()
'''

# a second BEFORE fixture exercising the one-level name-resolution path
_FIXTURE_BEFORE_NAMERES = '''
import os, json
def main():
    p = os.path.join(os.getcwd(), "mp04", "injected_dv.json")
    with open(p, "w") as fh:
        json.dump({"a": 1}, fh)
    prob = object()
    prob.run_model()
'''

# an AFTER fixture via name resolution (must also fire)
_FIXTURE_AFTER_NAMERES = '''
import os, json
def main():
    p = os.path.join(os.getcwd(), "mp04", "injected_dv.json")
    prob = object()
    prob.run_driver()
    with open(p, "w") as fh:
        json.dump({"a": 1}, fh)
'''


def _fires(source):
    """True iff scan_source refuses this source."""
    try:
        scan_source(source, filename="<fixture>")
        return False
    except OrderingRefusal:
        return True


def selftest():
    checks = [
        ("write-AFTER-run (literal path) -> must REFUSE", _FIXTURE_AFTER, True),
        ("write-AFTER-run (name-resolved path) -> must REFUSE", _FIXTURE_AFTER_NAMERES, True),
        ("write-BEFORE-run (literal path) -> must PASS", _FIXTURE_BEFORE, False),
        ("write-BEFORE-run (name-resolved path) -> must PASS", _FIXTURE_BEFORE_NAMERES, False),
    ]
    all_ok = True
    for label, src, must_fire in checks:
        fired = _fires(src)
        ok = (fired == must_fire)
        all_ok = all_ok and ok
        print("  [%s] %s  (fired=%s, expected_fire=%s)"
              % ("OK" if ok else "FAIL", label, fired, must_fire))
    # negative control: a file with a run but NO echo write must PASS (nothing to order)
    no_echo = "def main():\n    prob=object()\n    prob.run_model()\n    open('log.txt','w')\n"
    fired = _fires(no_echo)
    ok = (fired is False)
    all_ok = all_ok and ok
    print("  [%s] no-echo-write (log only) -> must PASS  (fired=%s)"
          % ("OK" if ok else "FAIL", fired))
    if all_ok:
        print("SELFTEST OK -- the checker both FIRES on write-after-run and PASSES on write-before-run.")
        return 0
    print("SELFTEST FAILED -- the checker did not behave as a planted control requires.")
    return 1


def main(argv=None):
    p = argparse.ArgumentParser(description="Static pre-freeze sidecar-write-before-run ordering check.")
    p.add_argument("files", nargs="*", help="rig / runScript files to check")
    p.add_argument("--selftest", action="store_true", help="run the planted-control selftest and exit")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.files:
        sys.stderr.write("usage: check_sidecar_before_run.py <file> [<file> ...]  |  --selftest\n")
        return 2
    worst = 0
    for f in args.files:
        rc = check_file(f)
        worst = max(worst, rc)
    return worst


if __name__ == "__main__":
    sys.exit(main())
