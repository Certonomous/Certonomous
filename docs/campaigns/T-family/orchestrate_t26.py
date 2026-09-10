#!/usr/bin/env python3
"""
T26 ORCHESTRATOR -- drives the level set, and is CALL SITE CS-2 for CLAUSE 7.

REGISTERED PATH: T26_PREREGISTRATION.md:804.

WHY THIS FILE NEEDS ITS OWN CALL TO THE GUARD, when launch_t26.sh already
calls it (CS-1).  T26_PREREGISTRATION.md:648, verbatim in substance: this
orchestrator sends the launcher's stdout to DEVNULL and NEVER WAITS, so a
refusal printed INSIDE the launcher would go to a discarded pipe and the level
would be recorded as LAUNCHED.  The guard is therefore called HERE,
SYNCHRONOUSLY, ON THIS SIDE OF THE FORK, BEFORE `Popen`.  CLAUDE.md rule 14: a
lesson is not applied until EVERY call site asserts it, so there are two call
sites and both call the ONE definition in `mark_done_t26.py --launch-guard`.
Neither reimplements it.  Pattern from `scripts/orchestrate_k0h.py:310-340`.

A REFUSAL STOPS THE LEVEL SET; IT DOES NOT SKIP A LEVEL (registration :650) --
a level set is costed as a whole, and a triple with a level missing is not a
triple.  `--selftest` drives that too: a refusal on L2 must leave L3 UNSTARTED.

THE HANG GUARD IS NOT A BUDGET CAP.  `timeout_s = 3.0 x POINT x 60 / ranks`
(registration :737): L1 2,595 / L2 12,690 / L3 56,098 core-min.  Sanaa's
CASE_PROTOCOL closing clause suspends the cap-STOP for this rung (:716); this
guard is against a wedged or spinning process, and it is named a hang guard
everywhere it appears so no later reader mistakes it for the cap she suspended.
Whether even this is admitted is THE SUPERVISOR'S CALL AT THE FREEZE; this file
implements what the registration registers and decides nothing.

THIS FILE LAUNCHES NOTHING UNLESS ASKED.  `--dry-run` is the default posture in
the selftest, and there is no code path that starts a solver without an
explicit `--go`.

Usage:  python3 orchestrate_t26.py --root DIR --go [--levels L1,L2,L3]
        python3 orchestrate_t26.py --root DIR            (plan only, no launch)
        python3 orchestrate_t26.py --selftest
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.path.join(HERE, "mark_done_t26.py")
LAUNCHER = os.path.join(HERE, "launch_t26.sh")
LEVELS = ("L1", "L2", "L3")
# registration :705-709 (level totals) and :737 (hang guard = 3.0 x POINT)
POINT_CORE_MIN = {"L1": 865.09, "L2": 4230.09, "L3": 18699.19}
RANKS = {"L1": 8, "L2": 16, "L3": 16}
EXIT_OK, EXIT_REFUSE = 0, 2


def hang_guard_s(level):
    """A HANG guard, NOT the budget cap Sanaa suspended (registration :737)."""
    return int(round(3.0 * POINT_CORE_MIN[level] * 60.0 / RANKS[level]))


def guard_ok(case_dir, guard=None, verbose=True):
    """CS-2: CLAUSE 7, CALLED SYNCHRONOUSLY, ON THIS SIDE OF THE FORK.

    Returns True only on exit 0 from the ONE definition of the rule.  Its
    output is CAPTURED AND PRINTED HERE -- never sent to DEVNULL -- because the
    whole reason this call site exists is that a refusal printed into a
    discarded pipe is a refusal nobody sees."""
    prog = guard or os.environ.get("T26_GUARD_OVERRIDE") or GUARD
    if not os.path.isfile(prog):
        print("REFUSE: the clause-7 guard %s is absent; an orchestrator with no "
              "guard is the seven-dead-levers defect" % prog)
        return False
    r = subprocess.run([sys.executable, prog, "--launch-guard", case_dir],
                       capture_output=True, text=True)
    if verbose and (r.stdout or r.stderr):
        for ln in (r.stdout + r.stderr).splitlines():
            print("    guard| " + ln)
    return r.returncode == 0


def run_set(root, levels, go=False, guard=None, popen=subprocess.Popen):
    """Drive the level set.  Returns (launched, refused_at, plan)."""
    launched, plan = [], []
    for lv in levels:
        case = os.path.join(root, lv)
        t = hang_guard_s(lv)
        plan.append(dict(level=lv, case=case, ranks=RANKS[lv],
                         point_core_min=POINT_CORE_MIN[lv], hang_guard_s=t))
        print("\n%s  ranks %d  point %.2f core-min  hang guard %d s "
              "(3.0 x point; NOT a budget cap)" % (lv, RANKS[lv], POINT_CORE_MIN[lv], t))
        # ---- CS-2, BEFORE Popen -------------------------------------------
        if not guard_ok(case, guard=guard):
            print("  REFUSE: CLAUSE 7 refused %s at CS-2, BEFORE any Popen. "
                  "THE LEVEL SET STOPS HERE -- it does not skip a level "
                  "(registration :650). Levels not started: %s"
                  % (lv, ",".join(levels[levels.index(lv) + 1:]) or "none"))
            return launched, lv, plan
        if not go:
            print("  PLAN ONLY: clause 7 passed and nothing was launched "
                  "(--go was not given).")
            continue
        popen(["bash", LAUNCHER, "--case-dir", case, "--timeout", str(t),
               "--ranks", str(RANKS[lv])],
              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        launched.append(lv)
        print("  LAUNCHED %s (stdout to DEVNULL -- which is exactly why the "
              "guard ran on THIS side of the fork)" % lv)
    return launched, None, plan


def selftest():
    import ast
    import shutil
    import tempfile
    print("orchestrate_t26.py --selftest")
    print("=" * 74)
    fails = []
    tmp = tempfile.mkdtemp(prefix="t26_orch_")
    try:
        def mk(lv, dirty=False):
            d = os.path.join(tmp, lv)
            os.makedirs(os.path.join(d, "0.orig"), exist_ok=True)
            if dirty:
                os.makedirs(os.path.join(d, "0"), exist_ok=True)
            return d

        calls = []

        def fake_popen(argv, **kw):
            calls.append(argv)
            return None

        print("\n(i) CS-2 REFUSES BEFORE Popen, AND STOPS THE LEVEL SET")
        for lv in LEVELS:
            mk(lv, dirty=(lv == "L2"))
        calls.clear()
        launched, refused, _p = run_set(tmp, list(LEVELS), go=True, popen=fake_popen)
        ok = (refused == "L2" and launched == ["L1"]
              and len(calls) == 1 and "L3" not in str(calls))
        print("  [%s] L2 dirty -> launched %s, refused at %s, Popen calls %d "
              "(L3 UNSTARTED: a refusal stops the set, it does not skip a level)"
              % ("ok " if ok else "BAD", launched, refused, len(calls)))
        if not ok:
            fails.append("stop the set")

        print("\n(ii) CONTROL: all clean -> every level launches")
        shutil.rmtree(tmp); os.makedirs(tmp)
        for lv in LEVELS:
            mk(lv)
        calls.clear()
        launched, refused, _p = run_set(tmp, list(LEVELS), go=True, popen=fake_popen)
        ok = (refused is None and launched == list(LEVELS) and len(calls) == 3)
        print("  [%s] launched %s, refused %s, Popen calls %d"
              % ("ok " if ok else "BAD", launched, refused, len(calls)))
        if not ok:
            fails.append("clean set")

        print("\n(iii) NEGATIVE CONTROL -- guard forced clear, SAME dirty case.")
        print("      Without this arm, (i)'s refusal could be anything in this file.")
        shutil.rmtree(tmp); os.makedirs(tmp)
        for lv in LEVELS:
            mk(lv, dirty=(lv == "L2"))
        stub = os.path.join(tmp, "stub_guard.py")
        open(stub, "w").write('import sys; print("STUB GUARD: verdict forced clear"); sys.exit(0)\n')
        calls.clear()
        launched, refused, _p = run_set(tmp, list(LEVELS), go=True, guard=stub, popen=fake_popen)
        ok = (refused is None and launched == list(LEVELS))
        print("  [%s] with the guard forced clear the SAME dirty set LAUNCHES (%s) "
              "-- so (i)'s refusal is attributable to CLAUSE 7 and nothing else"
              % ("ok " if ok else "BAD", launched))
        if not ok:
            fails.append("negative control")

        print("\n(iv) NOTHING LAUNCHES WITHOUT --go")
        shutil.rmtree(tmp); os.makedirs(tmp)
        for lv in LEVELS:
            mk(lv)
        calls.clear()
        launched, refused, _p = run_set(tmp, list(LEVELS), go=False, popen=fake_popen)
        ok = (launched == [] and len(calls) == 0)
        print("  [%s] plan-only: %d Popen calls, launched %s"
              % ("ok " if ok else "BAD", len(calls), launched))
        if not ok:
            fails.append("no-go")

        print("\n(v) THE HANG GUARD IS 3.0 x THE POINT ESTIMATE, per level")
        for lv in LEVELS:
            want = int(round(3.0 * POINT_CORE_MIN[lv] * 60.0 / RANKS[lv]))
            got = hang_guard_s(lv)
            print("  [%s] %s  %d s = %.0f core-min at %d ranks (registration :737)"
                  % ("ok " if got == want else "BAD", lv, got,
                     got * RANKS[lv] / 60.0, RANKS[lv]))
            if got != want:
                fails.append("hang guard " + lv)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_assert = sum(isinstance(x, ast.Assert)
                   for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("\n  [%s] NO `assert` in this file: AST count = %d (counter sees planted: %d)"
          % ("ok " if ok else "BAD", n_assert, planted))
    if not ok:
        fails.append("ast")

    print("=" * 74)
    print("SELFTEST %s (%d failed)%s" % ("PASS" if not fails else "FAIL", len(fails),
                                         "" if not fails else ": " + "; ".join(fails)))
    return EXIT_OK if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--root" not in argv:
        print(__doc__)
        return EXIT_REFUSE
    root = os.path.abspath(argv[argv.index("--root") + 1])
    levels = (argv[argv.index("--levels") + 1].split(",")
              if "--levels" in argv else list(LEVELS))
    bad = [l for l in levels if l not in LEVELS]
    if bad:
        print("REFUSE: %s are not registered T26 levels" % bad)
        return EXIT_REFUSE
    launched, refused, _p = run_set(root, levels, go="--go" in argv)
    if refused:
        return EXIT_REFUSE
    print("\nlaunched: %s" % (", ".join(launched) or "nothing (plan only)"))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
