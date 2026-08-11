#!/usr/bin/env python3
"""Find gates that answer "what did I find?" without answering "did I run?".

DOCKET B2. The defect this exists to find was found in this lab's own guard:
a per-surface `except Exception` kept one bad document from ending the audit --
correct -- and then left the STATUS green while reporting the skip only in the
frame line. Inject a raise on exactly the surface carrying a fault and the
verdict read "all 0 placement expression(s) agree with the published board".

A SURFACE THAT COULD NOT BE READ IS NOT A SURFACE THAT AGREES. A two-valued
gate cannot say "I looked at nothing", so it says it as a pass.

------------------------------------------------------------------------------
THE METHOD, stated mechanically so it can be run against a known positive.

For each fail-open SHAPE site -- an `except` handler whose body swallows (only
pass/continue/break, or ending in one within three lines):

  1. Find the enclosing function F.
  2. Does F EMIT A VERDICT? Any of: a `return <Call>` carrying a bare name in
     {PASS, FAIL, WARN, OK, ERROR} or a status-token string constant; a
     `sys.exit`/`SystemExit`; a `print` carrying a status token; an assignment
     to a name matching status|verdict|ok|passed|clean|result|gate.
  3. Compute GUARD NAMES -- the names the CHOICE of verdict can depend on:
     every Name in every if/ternary/while/assert test in F, plus every Name in
     the STATUS POSITION of a verdict emission. Names appearing only in TEXT
     (a summary, a detail line, an f-string) DO NOT COUNT. That distinction is
     the whole method: the known positive DID record its skip -- in the frame
     line -- and still shipped a green STATUS.
  4. Compute SWALLOW WRITES -- names assigned or augmented inside the handler.
  5. FLAG the site when F emits a verdict AND (SWALLOW WRITES n GUARD NAMES) is
     empty: nothing the swallow records can move the verdict.

A FLAG IS A CANDIDATE, NOT A DEFECT. Whether the verdict is PUBLISHED, and
whether the swallowed surface counts toward it as agreement/absence/zero, is
decided by reading and then settled by INJECTION. Reporting every flag as a
defect is the count-inflation error recorded as L-67.

THE CONTROL, and it is not optional. `--control` runs the method against
`038b36da:scripts/self_audit.py`, where `check_board_placement_words` is a
known-positive instance of the exact shape, and against the repaired version,
where the same site records its skip into a name the verdict consults. A sweep
that returns "few or no fail-open gates" is not believable unless it was shown
capable of finding one, so this exits non-zero if the positive is missed OR if
the repair is not cleared.

FRAME. Tracked files only (`git ls-files '*.py'`), which is honest about being
tracked-only. `grep -r` in this environment execs `ugrep --ignore-files` and
would have silently excluded gitignored paths (L-75), so no count here comes
from it. Files that will not parse are reported as UNPARSED and counted -- this
instrument refuses to do to itself what it exists to catch.

WHAT IT CANNOT SEE, stated rather than discovered later. Dataflow is
intraprocedural and name-based: a swallow that reaches a verdict through an
attribute, a mutable container, a global, or a second function is invisible to
step 5, so a cleared site is not a proven-safe site. `emits_verdict` keys on
vocabulary, so a verdict published under names this file does not know is
missed entirely, and a non-verdict named `result` is flagged. Shape detection
requires the handler to swallow syntactically; a handler that logs and then
returns a default value is a fail-open this scan does not model. And it reads
Python only -- shell, JS and notebook gates are outside it.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

STATUS_NAMES = {"PASS", "FAIL", "WARN", "OK", "ERROR", "UNKNOWN", "INCOMPLETE"}
STATUS_TOKEN = re.compile(r"\b(PASS(ED)?|FAIL(ED|URE)?|WARN|CLEAN|OK|AGREE\w*|"
                          r"VERDICT|GATE|STATUS|COMPLIANT)\b", re.I)
STATUS_VAR = re.compile(r"^(status|verdict|ok|passed|clean|result|gate)\w*$",
                        re.I)

# The known positive: the shape as it stood before the repair, and the
# function it lived in.
CONTROL_COMMIT = "038b36da"
CONTROL_PATH = "scripts/self_audit.py"
CONTROL_FUNC = "check_board_placement_words"


def _names(node: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _verdict_emission(node: ast.AST):
    """(emits, status_position_nodes) for one statement."""
    if isinstance(node, ast.Return) and node.value is not None:
        value = node.value
        if isinstance(value, ast.Call):
            positions = []
            for arg in value.args:
                if isinstance(arg, ast.Name) and arg.id in STATUS_NAMES:
                    positions.append(arg)
                elif (isinstance(arg, ast.Constant)
                        and isinstance(arg.value, str)
                        and STATUS_TOKEN.search(arg.value)):
                    positions.append(arg)
            if positions:
                return True, positions
        if (isinstance(value, ast.Constant) and isinstance(value.value, str)
                and STATUS_TOKEN.fullmatch(value.value.strip())):
            return True, [value]
        if isinstance(value, ast.Name) and value.id in STATUS_NAMES:
            return True, [value]
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        called = ast.unparse(node.value.func)
        if called in ("sys.exit", "exit", "os._exit"):
            return True, list(node.value.args)
        if called == "print" and STATUS_TOKEN.search(ast.unparse(node.value)):
            return True, list(node.value.args)
    if (isinstance(node, ast.Raise) and node.exc is not None
            and ast.unparse(node.exc).startswith("SystemExit")):
        return True, [node.exc]
    if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        targets = (node.targets if isinstance(node, ast.Assign)
                   else [node.target])
        for target in targets:
            if isinstance(target, ast.Name) and STATUS_VAR.match(target.id):
                return True, [node.value] if node.value is not None else []
    return False, []


def _handler_writes(handler: ast.ExceptHandler) -> set[str]:
    """Names the handler records into.

    MUTATION COUNTS, not only assignment. The repair this scan is calibrated
    against records its skip with `skipped.append(...)` and a later
    `if skipped:` reads it -- so a scan that only saw `=` and `+=` would flag
    the FIXED code and its positive control would prove nothing.
    """
    writes: set[str] = set()
    for statement in ast.walk(handler):
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                writes |= _names(target)
        elif isinstance(statement, (ast.AugAssign, ast.AnnAssign)):
            writes |= _names(statement.target)
        elif isinstance(statement, ast.Call) and isinstance(statement.func,
                                                            ast.Attribute):
            receiver = statement.func.value
            if isinstance(receiver, ast.Name):
                writes.add(receiver.id)
    return writes


def _is_swallow(handler: ast.ExceptHandler) -> bool:
    body = handler.body
    if {type(b).__name__ for b in body} <= {"Pass", "Continue", "Break"}:
        return True
    return (isinstance(body[-1], (ast.Pass, ast.Continue))
            and body[-1].lineno - handler.lineno <= 3)


def scan_source(label: str, source: str) -> list[dict]:
    """Every fail-open SHAPE site in one module, classified by the method."""
    tree = ast.parse(source)
    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    def enclosing(node):
        current = parents.get(node)
        while current is not None:
            if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return current
            current = parents.get(current)
        return None

    sites = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler) or not _is_swallow(node):
            continue
        function = enclosing(node)
        scope = function if function is not None else tree
        emits, status_positions = False, []
        for statement in ast.walk(scope):
            emitted, positions = _verdict_emission(statement)
            if emitted:
                emits = True
                status_positions.extend(positions)
        guard: set[str] = set()
        for statement in ast.walk(scope):
            if isinstance(statement, (ast.If, ast.IfExp, ast.While)):
                guard |= _names(statement.test)
            elif isinstance(statement, ast.Assert):
                guard |= _names(statement.test)
        for position in status_positions:
            guard |= _names(position)
        writes = _handler_writes(node)
        moves = sorted(writes & guard)
        sites.append({
            "file": label,
            "line": node.lineno,
            "func": function.name if function is not None else "<module>",
            "excepts": ast.unparse(node.type) if node.type else "BARE",
            "emits_verdict": emits,
            "swallow_writes": sorted(writes),
            "moves_verdict": moves,
            "flag": emits and not moves,
        })
    return sites


def _tracked_python() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z", "*.py"], cwd=REPO,
                         capture_output=True, text=True, check=True).stdout
    return [name for name in out.split("\0") if name]


def _head() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                          capture_output=True, text=True,
                          check=True).stdout.strip()


def scan_repo(exclude: tuple[str, ...] = ()) -> dict:
    sites, unparsed = [], []
    files = _tracked_python()
    for relative in files:
        if relative in exclude:
            continue
        path = REPO / relative
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            sites.extend(scan_source(relative, source))
        except (OSError, SyntaxError, ValueError) as exc:
            # An unparsed file is NOT a file with no fail-open gates. It is the
            # instrument's own third verdict, and it is counted, not dropped.
            unparsed.append({"file": relative,
                             "reason": f"{type(exc).__name__}: {exc}"})
    return {
        "frame": "tracked .py files (git ls-files '*.py'), no grep filter",
        "commit": _head(),
        "excluded": list(exclude),
        "files_scanned": len(files) - len(exclude) - len(unparsed),
        "shape_sites": len(sites),
        "verdict_reaching": sum(1 for s in sites if s["emits_verdict"]),
        "flagged": sum(1 for s in sites if s["flag"]),
        "UNPARSED": unparsed,
        "sites": sites,
    }


def run_control() -> int:
    """The positive control, and its mirror on the repaired code.

    Both directions matter. Flagging the known positive shows the method can
    find one; clearing the repair shows it is not merely flagging everything,
    which would make the first result worthless.
    """
    broken = subprocess.run(
        ["git", "show", f"{CONTROL_COMMIT}:{CONTROL_PATH}"], cwd=REPO,
        capture_output=True, text=True, check=True).stdout
    sites = [s for s in scan_source(f"{CONTROL_PATH}@{CONTROL_COMMIT}", broken)
             if s["func"] == CONTROL_FUNC]
    found = [s for s in sites if s["flag"]]
    print(f"POSITIVE CONTROL  {CONTROL_PATH}@{CONTROL_COMMIT}::{CONTROL_FUNC}")
    for site in sites:
        print(f"  line {site['line']:>5}  except {site['excepts']:<28} "
              f"writes={site['swallow_writes'] or '-'} "
              f"moves_verdict={site['moves_verdict'] or '-'}  "
              f"{'FLAGGED' if site['flag'] else 'cleared'}")
    print(f"  -> {'FLAGGED' if found else 'MISSED'} "
          f"({len(found)} of {len(sites)} shape site(s) in that function)")

    current = (REPO / CONTROL_PATH).read_text(encoding="utf-8")
    tree = ast.parse(current)
    repaired = [n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == CONTROL_FUNC]
    consulted = False
    if repaired:
        scope = repaired[0]
        guard: set[str] = set()
        for statement in ast.walk(scope):
            if isinstance(statement, (ast.If, ast.IfExp, ast.While)):
                guard |= _names(statement.test)
            emitted, positions = _verdict_emission(statement)
            if emitted:
                for position in positions:
                    guard |= _names(position)
        for handler in [n for n in ast.walk(scope)
                        if isinstance(n, ast.ExceptHandler)]:
            if _handler_writes(handler) & guard:
                consulted = True
    print(f"\nNEGATIVE CONTROL  {CONTROL_PATH} (working tree)::{CONTROL_FUNC}")
    print(f"  -> the repaired handler records into a name the verdict "
          f"consults: {consulted}")

    if not found:
        print("\nCONTROL FAILED: the method missed the known positive. Any "
              "negative result from it means nothing.")
        return 1
    if not consulted:
        print("\nCONTROL FAILED: the repaired site was not cleared, so the "
              "method may simply be flagging everything.")
        return 1
    print("\nCONTROL PASSED in both directions.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--control", action="store_true",
                        help="run the known-positive control and exit")
    parser.add_argument("--exclude", action="append", default=[],
                        help="tracked path to leave out (repeatable)")
    parser.add_argument("--json", type=Path, default=None)
    parser.add_argument("--flagged-only", action="store_true")
    args = parser.parse_args(argv)

    if args.control:
        return run_control()

    report = scan_repo(tuple(args.exclude))
    print(f"frame: {report['frame']}")
    print(f"commit: {report['commit']}")
    if report["excluded"]:
        print(f"excluded by request: {', '.join(report['excluded'])}")
    print(f"files scanned: {report['files_scanned']}   "
          f"UNPARSED: {len(report['UNPARSED'])}")
    for entry in report["UNPARSED"]:
        print(f"  UNPARSED {entry['file']}: {entry['reason']}")
    print(f"fail-open SHAPE sites: {report['shape_sites']}")
    print(f"  in a function that emits a verdict: {report['verdict_reaching']}")
    print(f"  FLAGGED (verdict emitted, swallow cannot move it): "
          f"{report['flagged']}")
    print("A FLAG IS A CANDIDATE. Only injection settles a defect.")
    for site in report["sites"]:
        if args.flagged_only and not site["flag"]:
            continue
        print(f"{'FLAG' if site['flag'] else '    '} "
              f"{site['file']}:{site['line']} {site['func']} "
              f"except {site['excepts']}")
    if args.json:
        args.json.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
