#!/usr/bin/env python3
"""audit_unread_arguments.py -- find DECLARED-AND-NEVER-READ command-line arguments.

WHY THIS EXISTS.  On 2026-09-12 the cfd team found `--time` in
`render_openfoam_3d_paraview.py` declared, documented, passed by every caller, and NEVER
CONSULTED -- so a field image captioned "latest" was iteration 1750 of a run whose graded
endTime was 2000.  `--min-ink` in the same file had been the same defect earlier.

IN THIS LAB PARAMETERS ARE REGISTERED, so this is not a usability wart.  A caller that
passed a flag and got the default BELIEVED IT GOT WHAT IT ASKED FOR, and our callers are
queue entries, launch scripts and comparators whose flags are frozen into
pre-registrations.  A run whose registration says "graded at time T" while the grader
silently read the default is a WRONG NUMBER WITH A CORRECT-LOOKING PROVENANCE CHAIN.

WHY ast AND NOT grep.  A regex sweep of this question was written first and WAS WRONG
THREE TIMES, each time in a way that looked like an answer:
  1. it counted the flag's own quoted name (`"--selftest"` IS a string token on its own
     line) as an enclosing string literal, and so declared EVERY declaration a false
     positive -- a uniform answer to a heterogeneous question, and it would have retired
     the question with "nothing found";
  2. it could not match `main(ap.parse_args().mode)` because `.mode` follows a `)`, and
     so falsely accused three of another team's instruments;
  3. it hardcoded the dest instead of resolving `dest=`, and so falsely accused
     `--frame` (dest `frame_mode`) in this lab's other renderer.
So: dests are resolved from the CALL, and a "read" is any attribute load, dict-key access
or `getattr` of that dest anywhere in the module.

THE BIAS IS DELIBERATE AND IS TOWARD ACQUITTAL.  This tool names other teams' instruments,
so it is built to UNDER-report: anything that looks like a read counts as a read.  ITS
OUTPUT IS A FLOOR, NOT A CENSUS.

--selftest drives a KNOWN-TRUTH control in BOTH directions against a file whose answer is
established, and REFUSES (exit 2) if it cannot reproduce it.  A sweep that has not been
shown able to accuse AND to acquit is not evidence.
"""
import argparse, ast, os, sys

EXIT_REFUSE = 2


def resolve(path):
    """-> (list of (flag, dest, lineno) never read, error-or-None)."""
    try:
        src = open(path, errors="replace").read()
        tree = ast.parse(src)
    except Exception as e:
        return None, repr(e)[:80]
    decls = []
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "add_argument"):
            longs = [a.value for a in n.args
                     if isinstance(a, ast.Constant) and isinstance(a.value, str)
                     and a.value.startswith("--")]
            if not longs:
                continue
            dest = None
            for kw in n.keywords:
                if kw.arg == "dest" and isinstance(kw.value, ast.Constant):
                    dest = kw.value.value
            decls.append((longs[0], dest or longs[0].lstrip("-").replace("-", "_"),
                          n.lineno))
    # A FLAG INTERCEPTED BEFORE parse_args IS READ, AND THAT PATTERN IS DELIBERATE.
    # MEASURED on verification/runs/F5_runs/cylinder_ladder.py, whose own comment says
    # why: `--name`, `--reynolds`, `--turbulence` and `--out` are required=True, so
    # argparse exits 2 on their absence BEFORE any selftest flag is reached -- checking
    # `args.selftest_rank_cap` after parsing left the control UNREACHABLE.  So it tests
    # `"--selftest-rank-cap" in sys.argv[1:]` instead.  Four flags there, all reachable,
    # and this tool accused all four before this branch existed.
    argv_literals = set()
    add_arg_consts = set()
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "add_argument"):
            for a in ast.walk(n):
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    add_arg_consts.add(id(a))
    for n in ast.walk(tree):
        if (isinstance(n, ast.Constant) and isinstance(n.value, str)
                and n.value.startswith("--") and id(n) not in add_arg_consts):
            argv_literals.add(n.value)

    attrs, keys = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Load):
            attrs.add(n.attr)                       # a.foo
        if (isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
                and isinstance(n.slice.value, str)):
            keys.add(n.slice.value)                 # ctx["foo"]
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "getattr" and len(n.args) > 1
                and isinstance(n.args[1], ast.Constant)):
            attrs.add(n.args[1].value)              # getattr(a, "foo", default)
    return [(f, d, l) for f, d, l in decls
            if d not in attrs and d not in keys and f not in argv_literals], None


def selftest(repo):
    """KNOWN TRUTH, BOTH DIRECTIONS. The repaired renderer must come back CLEAN, and a
    copy of it with the repair backed out must come back ACCUSED. A sweep shown able to
    do only one of those is not a sweep."""
    import tempfile, re, shutil
    live = os.path.join(repo, "scripts", "render_openfoam_3d_paraview.py")
    if not os.path.exists(live):
        sys.stderr.write("REFUSE: the control file %s is absent; the sweep cannot be "
                         "shown correct and its output is not evidence.\n" % live)
        sys.exit(EXIT_REFUSE)
    hits, err = resolve(live)
    if err:
        sys.stderr.write("REFUSE: control file did not parse: %s\n" % err)
        sys.exit(EXIT_REFUSE)
    if hits:
        sys.stderr.write("REFUSE: the ACQUIT direction failed -- the repaired renderer "
                         "should have no unread arguments, got %s\n" % hits)
        sys.exit(EXIT_REFUSE)
    print("  [PASS] acquit direction: the repaired renderer reports no unread arguments")

    # back the --time repair out of a COPY and require the sweep to catch it
    src = open(live, errors="replace").read()
    broken = re.sub(r"\bchosen_time, all_times = resolve_time\(reader, a\.time\)",
                    "chosen_time, all_times = resolve_time(reader, 'latest')", src)
    if broken == src:
        sys.stderr.write("REFUSE: could not construct the negative control -- the line "
                         "the repair hinges on was not found, so the ACCUSE direction "
                         "cannot be driven and this selftest proves only half.\n")
        sys.exit(EXIT_REFUSE)
    d = tempfile.mkdtemp(prefix="unread_arg_ctrl_")
    try:
        p = os.path.join(d, "broken.py")
        open(p, "w").write(broken)
        hits2, err2 = resolve(p)
        if err2 or not any(f == "--time" for f, _, _ in hits2):
            sys.stderr.write("REFUSE: the ACCUSE direction failed -- with the only read "
                             "of a.time removed, --time was NOT flagged. got %s\n" % hits2)
            sys.exit(EXIT_REFUSE)
        print("  [PASS] accuse direction: with the sole read of `a.time` removed, "
              "--time IS flagged")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("SELFTEST OK: the sweep was shown able to ACQUIT a clean file and to ACCUSE a "
          "planted one. Its output is a FLOOR -- it is biased toward acquittal.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default="/home/ubuntu/Certonomous")
    ap.add_argument("--roots", default="scripts,cases,verification")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest(a.repo))
    hits, scanned, errors = [], 0, 0
    for root in a.roots.split(","):
        for dp, _, fns in os.walk(os.path.join(a.repo, root.strip())):
            if "__pycache__" in dp or "/processor" in dp:
                continue
            for fn in fns:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(dp, fn)
                try:
                    if "add_argument" not in open(p, errors="replace").read():
                        continue
                except Exception:
                    continue
                scanned += 1
                res, err = resolve(p)
                if err:
                    errors += 1          # COUNTED AND REPORTED, never silently skipped
                    continue
                for f, d, l in res:
                    hits.append((os.path.relpath(p, a.repo), f, d, l))
    print("files scanned: %d   files that would not parse (NOT audited): %d" %
          (scanned, errors))
    print("DECLARED AND NEVER READ: %d  -- a FLOOR, this tool is biased toward acquittal\n"
          % len(hits))
    for p, f, d, l in sorted(hits):
        print("  %-62s %-18s (dest=%s, line %d)" % (p, f, d, l))
    return 0


if __name__ == "__main__":
    sys.exit(main())
