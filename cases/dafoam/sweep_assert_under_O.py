#!/usr/bin/env python3
"""D-ASSERT-O family sweep: locate every `assert` STATEMENT in every dafoam
instrument at HEAD, name the function that holds it, and classify it.

MECHANISM, NOT TOKEN.  `python3 -O` / PYTHONOPTIMIZE=1 elides the bytecode for
the `ast.Assert` node.  This sweep therefore parses each blob with `ast` and
counts `ast.Assert` nodes.  It does NOT grep for the string "assert": a grep
matches the word in comments, docstrings and identifiers (`assert_close(...)`)
and MISSES nothing only by accident.  The AST node IS the thing the flag
removes.

POPULATION: tracked blobs at HEAD (`git ls-tree -r HEAD`), never the worktree.
The shared index is decayed and other teams' files sit modified in the tree.

L-325: every pattern is planted BOTH WAYS before any zero is believed --
a name known to EXIST must come back, and a name known NOT to exist must be
REFUSED.  A control that only proves the reader is alive does not prove it can
say no.  No `head`, `tail` or pager appears anywhere in the enumeration path.

Exit 2 on any control failure.  Nothing here is sent, filed or posted
(CLAUDE.md rule 7).
"""
import ast
import json
import subprocess
import sys

REPO = "/home/ubuntu/Certonomous"


def sh(args):
    r = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("command failed: %r rc=%d stderr=%s"
                           % (args, r.returncode, r.stderr[:400]))
    return r.stdout


def head_paths():
    out = sh(["git", "ls-tree", "-r", "HEAD", "--name-only"])
    return [p for p in out.split("\n") if p]


def blob(path):
    """Read a blob at HEAD.  Returns None if the path is not at HEAD -- an
    ABSENT file and a file with ZERO asserts must never look the same."""
    r = subprocess.run(["git", "show", "HEAD:%s" % path],
                       cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return r.stdout


class Walker(ast.NodeVisitor):
    """Records every ast.Assert with its full enclosing def/class chain."""

    def __init__(self):
        self.stack = []
        self.hits = []

    def _scoped(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_FunctionDef = _scoped
    visit_AsyncFunctionDef = _scoped
    visit_ClassDef = _scoped

    def visit_Assert(self, node):
        self.hits.append({
            "lineno": node.lineno,
            "scope": ".".join(self.stack) if self.stack else "<module>",
            "func": self.stack[-1] if self.stack else "<module>",
            "outer": self.stack[0] if self.stack else "<module>",
            "src": ast.unparse(node) if hasattr(ast, "unparse") else "",
        })
        self.generic_visit(node)


def asserts_in(path):
    """(status, hits).  status is one of ABSENT / UNPARSEABLE / OK."""
    text = blob(path)
    if text is None:
        return "ABSENT", []
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return "UNPARSEABLE:%s" % exc.msg, []
    w = Walker()
    w.visit(tree)
    return "OK", w.hits


# NOTE ON `outer` vs `func`: d12r_grade.py holds its 59 asserts in 32 unit
# functions that are NESTED INSIDE the module-level `selftest`.  Keying on the
# INNERMOST holder would report 32 unrelated functions and would have hidden
# the ruling's actual finding.  Classification keys on the OUTERMOST scope --
# the module-level entry point that owns the assert -- and both are recorded.

# ----------------------------------------------------------------- CONTROLS
# L-325 BOTH DIRECTIONS.  Positive plants are facts already MEASURED by
# dafoam-supervisor and recorded in docs/dafoam/SUPERVISOR_ASSERT_UNDER_O_RULING.md
# section 3 -- if this instrument disagrees with them it is the instrument that
# is wrong, and it must refuse rather than publish a number.
POSITIVE_PLANTS = [
    # (path, expected assert count, expected sole holding function or None)
    ("cases/dafoam/curriculum_D12/d12r_grade.py", 59, "selftest"),
]
ZERO_PLANTS = [
    # files MEASURED to hold zero asserts -- present, parseable, empty of them
    "cases/dafoam/ladder-a/A3/curriculum_D7/d7_grade.py",
    "cases/dafoam/ladder-a/A3/curriculum_D7/d7_g8_token.py",
]
NEGATIVE_PLANTS = [
    # names that DO NOT EXIST.  The reader must REFUSE, not return zero.
    "cases/dafoam/curriculum_D12/d99_grade_does_not_exist.py",
    "cases/dafoam/NO_SUCH_DIRECTORY_AT_ALL/x.py",
]


def run_controls(verbose=True):
    ok = True
    for path, n_expected, func_expected in POSITIVE_PLANTS:
        status, hits = asserts_in(path)
        got = len(hits)
        funcs = sorted({h["outer"] for h in hits})
        good = (status == "OK" and got == n_expected
                and (func_expected is None or funcs == [func_expected]))
        if verbose:
            print("CONTROL+ %-70s status=%s n=%d (expect %d) funcs=%s -> %s"
                  % (path, status, got, n_expected, funcs,
                     "OK" if good else "FAILED"))
        ok = ok and good
    for path in ZERO_PLANTS:
        status, hits = asserts_in(path)
        good = (status == "OK" and len(hits) == 0)
        if verbose:
            print("CONTROL0 %-70s status=%s n=%d (expect present+0) -> %s"
                  % (path, status, len(hits), "OK" if good else "FAILED"))
        ok = ok and good
    for path in NEGATIVE_PLANTS:
        status, hits = asserts_in(path)
        good = (status == "ABSENT")
        if verbose:
            print("CONTROL- %-70s status=%s (expect ABSENT, NOT a zero) -> %s"
                  % (path, status, "OK" if good else "FAILED"))
        ok = ok and good
    return ok


def main():
    print("=== CONTROLS (L-325, both directions) ===")
    if not run_controls():
        print("REFUSED: a planted control did not come back as expected. "
              "No count from this instrument is evidence. exit 2")
        sys.exit(2)

    print()
    print("=== POPULATION ===")
    paths = head_paths()
    in_scope = [p for p in paths
                if (p.startswith("cases/dafoam/") or p.startswith("docs/dafoam/"))
                and (p.endswith(".py") or p.endswith(".sh"))]
    py = [p for p in in_scope if p.endswith(".py")]
    shf = [p for p in in_scope if p.endswith(".sh")]
    print("tracked paths at HEAD                : %d" % len(paths))
    print("in dafoam folder scope, .py or .sh   : %d" % len(in_scope))
    print("  .py (ast-parseable population)     : %d" % len(py))
    print("  .sh (no assert mechanism; see note): %d" % len(shf))

    records = []
    unparseable = []
    for p in sorted(py):
        status, hits = asserts_in(p)
        if status == "ABSENT":
            raise RuntimeError("path from ls-tree absent on show: %s" % p)
        if status.startswith("UNPARSEABLE"):
            unparseable.append((p, status))
            continue
        if hits:
            records.append({"path": p, "n": len(hits), "hits": hits})

    print()
    print("=== FILES WITH >=1 ast.Assert ===")
    total = 0
    for rec in sorted(records, key=lambda r: -r["n"]):
        total += rec["n"]
        funcs = {}
        for h in rec["hits"]:
            funcs[h["outer"]] = funcs.get(h["outer"], 0) + 1
        print("%-78s %3d  %s" % (rec["path"], rec["n"],
              ", ".join("%s:%d" % (k, v) for k, v in sorted(funcs.items()))))
    print()
    print("files with >=1 assert : %d of %d .py" % (len(records), len(py)))
    print("total ast.Assert nodes: %d" % total)
    print("unparseable blobs     : %d %s" % (len(unparseable), unparseable))

    with open("/tmp/claude-1000/-home-ubuntu-Certonomous/"
              "64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/assert_census.json",
              "w") as fh:
        json.dump({"records": records, "n_py": len(py), "n_sh": len(shf),
                   "unparseable": unparseable}, fh, indent=1)
    print("census written for classification pass")


if __name__ == "__main__" and "--classify" not in sys.argv:
    main()


# =========================================================================
# CLASSIFICATION PASS -- GATE / SELFTEST / NEITHER
# =========================================================================
# Definitions, stated because the three counts are worthless without them.
# They are the RULING's own words (SUPERVISOR_ASSERT_UNDER_O_RULING.md sec.4):
# "no `assert` in an instrument may carry a refusal, guard, control or gate."
#
#   GATE     -- the assert carries a refusal, guard or control on a path that
#               runs during a REAL (non-selftest) execution.  Removing it lets
#               the instrument PROCEED with unvalidated data, an unmade
#               substitution, a wrong execution mode or a skipped refusal.
#               A parser length-guard is a GATE under this definition: failing
#               open there yields a number nothing checked.
#   SELFTEST -- the assert lives on the selftest/battery path ONLY.  Removing
#               it makes the battery vacuous but changes no live verdict.
#               (The ruling sec.4 extension: a SELFTEST IS A CONTROL.)
#   NEITHER  -- removing it cannot change any output of the program as
#               written, because the condition is guaranteed by the
#               immediately preceding statements.  A guard against a FUTURE
#               edit, not a live control.
#
# NOTHING BELOW IS AN ASSERT.  Coverage is a COUNTED result and the pass
# REFUSES (exit 2) by counting if the classification does not cover the
# census exactly -- the failure mode this whole sweep exists to eliminate.

NEITHER_HITS = {
    # (path, lineno): rationale
    ("cases/dafoam/ladder-a/A2/curriculum_D4/d4_accept_compare.py", 181):
        "line 180 assigns verdict from the two-element literal choice "
        "{'PASS','GATE FAIL'}, both members of VOCAB (defined line 53). The "
        "assert cannot fire as the file is written. It is a maintenance guard "
        "against a future edit -- and it would stop guarding SILENTLY under -O.",
}

SERIAL = "comm.size"


def subclass(path, hit):
    src, outer = hit["src"], hit["outer"]
    base = path.rsplit("/", 1)[-1]
    if SERIAL in src:
        return "SERIAL_GUARD"
    if base in ("d13_opt_runScript.py", "d1_opt_runScript.py"):
        return "LIVE_PRODUCER"
    if base in ("d8_gen_arm.py", "f6a_recheck.py"):
        return "LIVE_PRODUCER"
    if base in ("build_ensemble.py", "rmt_sampler.py"):
        return "LIVE_PRODUCER"
    if ("CONTROL" in src) or ("sanity check" in src) or ("does not actually "
                                                         "exercise" in src):
        return "NAMED_CONTROL"
    if outer.startswith("read_") or "expected" in src or "mismatch" in src \
            or "shape[0]" in src or ".size ==" in src or "len(" in src:
        return "READER_GUARD"
    return "OTHER_GUARD"


def classify():
    with open("/tmp/claude-1000/-home-ubuntu-Certonomous/"
              "64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/"
              "assert_census.json") as fh:
        census = json.load(fh)

    buckets = {"GATE": [], "SELFTEST": [], "NEITHER": []}
    subs = {}
    for rec in census["records"]:
        for h in rec["hits"]:
            key = (rec["path"], h["lineno"])
            if h["outer"] == "selftest":
                buckets["SELFTEST"].append(key)
            elif key in NEITHER_HITS:
                buckets["NEITHER"].append(key)
            else:
                buckets["GATE"].append(key)
                s = subclass(rec["path"], h)
                subs[s] = subs.get(s, 0) + 1

    total_census = sum(r["n"] for r in census["records"])
    total_class = sum(len(v) for v in buckets.values())

    print("=== CLASSIFICATION ===")
    for b in ("GATE", "SELFTEST", "NEITHER"):
        print("  %-9s %3d" % (b, len(buckets[b])))
    print("  %-9s %3d  (census total: %d)" % ("TOTAL", total_class,
                                              total_census))
    print()
    print("  GATE subclasses:")
    for s, n in sorted(subs.items(), key=lambda kv: -kv[1]):
        print("    %-16s %3d" % (s, n))

    # COUNTED coverage control -- no assert, and it must be able to REFUSE.
    failures = 0
    if total_class != total_census:
        print("COVERAGE FAILURE: classified %d of %d census hits"
              % (total_class, total_census))
        failures += 1
    unknown = [k for k in buckets["NEITHER"] if k not in NEITHER_HITS]
    if unknown:
        print("NEITHER bucket holds unrationalised hits: %s" % unknown)
        failures += 1
    stale = [k for k in NEITHER_HITS if k not in buckets["NEITHER"]]
    if stale:
        print("NEITHER rationale names a hit not in the census "
              "(the file moved or the line shifted): %s" % stale)
        failures += 1
    # L-332 (ruling Amendment 1): the success claim is printed INSIDE the
    # passing branch, so removing the check removes the CLAIM. It is NOT
    # printed unconditionally after the check -- that shape survives the
    # check's removal and certifies a pass that never ran.
    if failures:
        print("REFUSED: %d coverage control(s) failed. exit 2" % failures)
        sys.exit(2)
    else:
        print()
        print("coverage controls passed: %d hits, all classified, all NEITHER "
              "hits carry a written rationale" % total_class)
    return buckets


if __name__ == "__main__" and "--classify" in sys.argv:
    classify()
