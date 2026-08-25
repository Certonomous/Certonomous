#!/usr/bin/env python3
"""Two static probes for graders that cannot read their own output.

Both defects this file hunts were found on 2026-08-25, in ONE day, in TWO different
comparators, and in BOTH cases THE REGISTRATION WAS WORKING CORRECTLY AND THE GRADER
COULD NOT READ ITS OWN OUTPUT.

PROBE A -- the FIFTH shape (L-322).  A grader that cannot REPRESENT an outcome its own
registered rules MANDATE.  ``grade_f3.py`` built ``report["runs"][key]`` at two sites
with different key sets: the ``PENDING`` branch (run directory absent -- the state
section 7's pre-wave budget check GUARANTEES whenever the budget binds) omitted
``core_s``, and the summary then read ``v["core_s"]`` across every entry.  The cap fired
exactly as registered and the grader crashed on it having fired.

    Probe A flags: two or more ``dict(...)`` assignments to the SAME subscript target
    whose keyword-key sets DIFFER, where any consumer reads a key that some branch
    does not write.

PROBE B -- the FOURTH shape (L-321).  A fixture that constructs its artifact by the SAME
route the reader resolves it shares one wrong assumption with the checker, so the two
agree and their agreement carries no information.  ``analyse_f5b_physics.py`` resolved
the endTime directory by string-matching ``END_TIME_STR`` and its ``_synthetic_run``
fixture CREATED that directory from the same constant -- so every selftest passed while
``case/21.9440/`` never existed on a real run (OpenFOAM writes ``case/21.944/``).

    Probe B flags: a module-level string/number constant used BOTH to BUILD a path in a
    fixture/synthetic constructor AND to RESOLVE or match a path in the checked code.

NEITHER PROBE IS A PROOF OF CORRECTNESS.  They are cheap static smells for two shapes
that have each cost this lab a graded run.  A clean report is not a guarantee; a flag is
a thing to go and look at.

Usage
-----
    python3 scripts/check_grader_self_blindness.py --selftest
    python3 scripts/check_grader_self_blindness.py <file.py> [<file.py> ...]

``--selftest`` plants BOTH defects and BOTH clean counterparts and requires the probes
to fire on the defective ones and stay silent on the clean ones.  A probe never shown
able to fire is not evidence (standing rule 3), and a probe never shown able to stay
QUIET is a probe that flags everything.
"""
import argparse
import ast
import os
import sys
import tempfile

FIXTURE_HINTS = ("synthetic", "fixture", "_make_", "make_", "plant", "_write_")
RESOLVE_HINTS = ("resolve", "check_", "grade", "completion", "verify", "read", "parse")


# --------------------------------------------------------------------------
# PROBE A -- divergent dict schemas on one container
# --------------------------------------------------------------------------
def _subscript_target(node):
    """Render ``report["runs"][key] = ...`` as the stable prefix ``report["runs"]``."""
    parts = []
    cur = node
    while isinstance(cur, ast.Subscript):
        sl = cur.slice
        if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
            parts.append(repr(sl.value))
        else:
            parts.append("<var>")
        cur = cur.value
    if not isinstance(cur, ast.Name):
        return None
    parts.append(cur.id)
    parts.reverse()
    # drop the trailing <var> index: report["runs"][key] -> report['runs']
    while parts and parts[-1] == "<var>":
        parts.pop()
    if len(parts) < 2:
        return None
    return parts[0] + "".join("[%s]" % p for p in parts[1:])


def probe_a(tree):
    """Return a list of finding strings."""
    writes = {}          # target -> list of (lineno, frozenset(keys))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        tgt = node.targets[0]
        if not isinstance(tgt, ast.Subscript):
            continue
        name = _subscript_target(tgt)
        if name is None:
            continue
        val = node.value
        keys = None
        if isinstance(val, ast.Call) and isinstance(val.func, ast.Name) \
                and val.func.id == "dict":
            keys = frozenset(kw.arg for kw in val.keywords if kw.arg)
        elif isinstance(val, ast.Dict):
            keys = frozenset(k.value for k in val.keys
                             if isinstance(k, ast.Constant) and isinstance(k.value, str))
        if keys is None:
            continue
        writes.setdefault(name, []).append((node.lineno, keys))

    # which keys does anything READ off this container's members?
    reads = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        sl = node.slice
        if not (isinstance(sl, ast.Constant) and isinstance(sl.value, str)):
            continue
        reads.setdefault(sl.value, []).append(node.lineno)

    out = []
    for name, sites in writes.items():
        if len(sites) < 2:
            continue
        keysets = [k for _, k in sites]
        union, inter = set().union(*keysets), set(keysets[0]).intersection(*keysets)
        missing = union - inter
        if not missing:
            continue
        risky = sorted(k for k in missing if k in reads)
        detail = ("%s written at %s with DIFFERING key sets; keys absent from at least "
                  "one branch: %s" % (name, ", ".join("L%d" % l for l, _ in sites),
                                      sorted(missing)))
        if risky:
            detail += ("  ** AND READ ELSEWHERE: %s (read at %s) -- a branch that omits "
                       "one of these raises on the read" %
                       (risky, ", ".join("L%d" % l for k in risky for l in reads[k][:3])))
        out.append(("ERROR" if risky else "WARN", detail))
    return out


# --------------------------------------------------------------------------
# PROBE B -- fixture and checker sharing one constant to build/resolve a path
# --------------------------------------------------------------------------
def _enclosing_functions(tree):
    """map lineno -> function name, for every line inside a FunctionDef."""
    owner = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lo = node.lineno
            hi = max((getattr(n, "lineno", lo) for n in ast.walk(node)), default=lo)
            for ln in range(lo, hi + 1):
                owner.setdefault(ln, node.name)
    return owner


def probe_b(tree):
    consts = {n.targets[0].id for n in ast.walk(tree)
              if isinstance(n, ast.Assign) and len(n.targets) == 1
              and isinstance(n.targets[0], ast.Name)
              and n.targets[0].id.isupper()}
    if not consts:
        return []
    owner = _enclosing_functions(tree)

    # a constant "builds a path" if it appears inside an os.path.join(...) call
    builds, resolves = {}, {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        is_join = (isinstance(fn, ast.Attribute) and fn.attr == "join"
                   and isinstance(fn.value, ast.Attribute) and fn.value.attr == "path")
        if not is_join:
            continue
        for a in ast.walk(node):
            if isinstance(a, ast.Name) and a.id in consts:
                who = owner.get(node.lineno, "<module>")
                low = who.lower()
                if any(h in low for h in FIXTURE_HINTS):
                    builds.setdefault(a.id, []).append((node.lineno, who))
                elif any(h in low for h in RESOLVE_HINTS):
                    resolves.setdefault(a.id, []).append((node.lineno, who))
    out = []
    for c in sorted(set(builds) & set(resolves)):
        b = builds[c][0]
        r = resolves[c][0]
        out.append(("ERROR",
                    "constant %s BUILDS a path in fixture %s (L%d) and RESOLVES a path "
                    "in checker %s (L%d) -- fixture and checker share one assumption, so "
                    "their agreement carries NO information (L-321). The fixture must "
                    "construct by a DIFFERENT route than the reader resolves."
                    % (c, b[1], b[0], r[1], r[0])))
    return out


def scan(path):
    src = open(path, "r", errors="replace").read()
    tree = ast.parse(src, filename=path)
    return probe_a(tree) + probe_b(tree)


# --------------------------------------------------------------------------
# SELFTEST -- plant BOTH defects and BOTH clean counterparts
# --------------------------------------------------------------------------
BAD_A = '''
def main():
    report = {"runs": {}}
    for key in ("a", "b"):
        if missing(key):
            report["runs"][key] = dict(status="PENDING", note="not launched")
            continue
        report["runs"][key] = dict(status="COMPLETE", core_s=1.0)
    total = sum(v["core_s"] or 0.0 for v in report["runs"].values())
    return total
'''

GOOD_A = '''
def run_entry(status, core_s=None, note=None):
    return dict(status=status, core_s=core_s, note=note)

def main():
    report = {"runs": {}}
    for key in ("a", "b"):
        if missing(key):
            report["runs"][key] = run_entry("PENDING", note="not launched")
            continue
        report["runs"][key] = run_entry("COMPLETE", core_s=1.0)
    total = sum((v["core_s"] or 0.0) for v in report["runs"].values())
    return total
'''

BAD_B = '''
import os
END_TIME_STR = "21.9440"

def _synthetic_run(root):
    case = os.path.join(root, "case")
    tdir = os.path.join(case, END_TIME_STR)
    return tdir

def check_completion(case):
    tdir = os.path.join(case, END_TIME_STR)
    return os.path.isdir(tdir)
'''

GOOD_B = '''
import os
END_TIME_STR = "21.9440"

def _synthetic_run(root):
    case = os.path.join(root, "case")
    tdir = os.path.join(case, "%g" % float(END_TIME_STR))
    return tdir

def resolve_time_dir(case, want):
    for nm in os.listdir(case):
        try:
            if abs(float(nm) - want) < 1e-9:
                return os.path.join(case, nm)
        except ValueError:
            continue
    return None

def check_completion(case):
    return resolve_time_dir(case, float(END_TIME_STR)) is not None
'''


def _scan_src(src):
    return probe_a(ast.parse(src)) + probe_b(ast.parse(src))


def selftest():
    print("=" * 74)
    print("check_grader_self_blindness.py -- SELFTEST (planted controls)")
    print("=" * 74)
    ok = True
    cases = [
        ("A defective -- PENDING branch omits core_s, summary reads it", BAD_A, True, "A"),
        ("A clean     -- one constructor, single schema", GOOD_A, False, "A"),
        ("B defective -- fixture and checker share END_TIME_STR", BAD_B, True, "B"),
        ("B clean     -- fixture formats, reader resolves numerically", GOOD_B, False, "B"),
    ]
    for label, src, must_fire, which in cases:
        f = _scan_src(src)
        rel = [x for x in f if (which == "B") == ("L-321" in x[1])]
        fired = bool(rel)
        good = fired == must_fire
        ok = ok and good
        print("  %-58s fired=%-5s expect=%-5s %s"
              % (label, fired, must_fire, "OK" if good else "*** WRONG ***"))
        for sev, d in rel:
            print("      [%s] %s" % (sev, d[:150]))
    print()
    if ok:
        print("SELFTEST PASSED: each probe was shown able to FIRE on a planted defect")
        print("and able to STAY QUIET on its clean counterpart.  A probe never shown able")
        print("to fire is not evidence; one never shown able to stay quiet flags everything.")
    else:
        print("SELFTEST FAILED")
    return 0 if ok else 2


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("files", nargs="*")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.files:
        ap.error("give at least one .py file, or --selftest")
    worst = 0
    for p in a.files:
        try:
            findings = scan(p)
        except SyntaxError as exc:
            print("%s: SKIPPED -- does not parse (%s)" % (p, exc))
            continue
        if not findings:
            print("%s: clean on both probes (NOT a proof of correctness)" % p)
            continue
        for sev, d in findings:
            print("%s: [%s] %s" % (p, sev, d))
            worst = max(worst, 2 if sev == "ERROR" else 1)
    return worst


if __name__ == "__main__":
    sys.exit(main())
