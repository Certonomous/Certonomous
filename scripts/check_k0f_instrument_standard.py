#!/usr/bin/env python3
"""K0f INSTRUMENT STANDARD -- no `assert` may carry a refusal, guard, control
or gate, and every registered refusal is DRIVEN under `python3 -O`.

REGISTERED AT: docs/campaigns/F14-cooling-ladder/K0f_PREREGISTRATION.md
section 3C.  BINDING IN THIS RUNG ONLY.  Adopting it lab-wide is a charter
matter and is not a lane's, nor a supervisor's, to land.

WHY.  `assert` statements are REMOVED by `python3 -O` / `PYTHONOPTIMIZE=1`, so
a refusal written as an assert is NOT A REFUSAL under every interpreter the
script can be launched with.  Measured elsewhere in this lab, not theoretical:
a repository guard refused under `python3` and PROCEEDED TO `git add -A` on the
shared tree under `python3 -O`; and a measurement script whose planted controls
were all asserts lost every control under `-O` and exited 0 -- standing rule 3
defeated by an interpreter flag.

THREE ARMS, because two of them are not enough:

  1. STATEMENT TYPE.  Every K0f instrument's own AST must carry ZERO `Assert`
     nodes.  This catches a revert without running anything, and it is the arm
     that survives a refusal being moved, renamed or reworded.

  2. DRIVEN UNDER `-O`.  Every registered refusal is EXECUTED under `python3 -O`
     and must fire IDENTICALLY -- *not* merely "the selftest passes under -O",
     because A PASSING SELFTEST PROVES ONLY THE CLEAN PATH, AND THE CLEAN PATH
     IS EXACTLY THE ONE AN EVAPORATED GUARD STILL WALKS.

  3. MUTATION.  Arm 1 is itself shown able to FIRE: a copy of an instrument
     with one refusal reverted to an `assert` must be CAUGHT.  An arm never
     shown able to say no is not evidence.

Exit codes: 0 clean, 1 a violation, 2 the check could not be performed.
"""
import ast
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
INSTRUMENTS = ("analyse_k0f.py", "build_k0f.py", "check_k0f_mesh.py",
               "mark_done_k0f.py", "check_k0f_extraction_equivalence.py",
               "check_k0f_instrument_standard.py")
EXIT_OK, EXIT_VIOLATION, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def assert_nodes(path):
    """Count `Assert` statements in a file's OWN AST."""
    try:
        tree = ast.parse(open(path).read(), filename=path)
    except SyntaxError as e:
        refuse(f"{path}: does not parse ({e})")
    return [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]


# --- the registered refusals, each with the argv that DRIVES it -----------
# Every row must exit with the stated code under BOTH `python3` and
# `python3 -O`.  A row whose two interpreters disagree is the whole defect.
def refusal_drives(tmp):
    empty = os.path.join(tmp, "empty_root")
    os.makedirs(empty, exist_ok=True)
    return (
        ("build_k0f.py: --preflight on a non-case",
         ["build_k0f.py", "--preflight", os.path.join(tmp, "nope")], 2),
        ("build_k0f.py: --root missing",
         ["build_k0f.py"], 2),
        ("mark_done_k0f.py: --root missing",
         ["mark_done_k0f.py"], 2),
        ("mark_done_k0f.py: unregistered case",
         ["mark_done_k0f.py", "--root", empty, "NOT_A_REGISTERED_CASE"], 2),
        ("analyse_k0f.py: --root is not a directory",
         ["analyse_k0f.py", "--root", os.path.join(tmp, "nope")], 2),
        ("analyse_k0f.py: freeze check on a wrong sha",
         ["analyse_k0f.py", "--root", empty, "--expect-sha", "0" * 40], 2),
        ("check_k0f_mesh.py: --root missing",
         ["check_k0f_mesh.py"], 2),
        ("check_k0f_extraction_equivalence.py: --case on a non-directory",
         ["check_k0f_extraction_equivalence.py", "--case",
          os.path.join(tmp, "nope")], 2),
    )


def run(argv, optimised):
    cmd = [sys.executable] + (["-O"] if optimised else []) + \
          [os.path.join(HERE, argv[0])] + argv[1:]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return r.returncode


def main():
    print("=" * 74)
    print("K0f INSTRUMENT STANDARD (section 3C)")
    print("=" * 74)
    bad = []

    print("\nARM 1 -- STATEMENT TYPE: zero `Assert` nodes in each instrument")
    for f in INSTRUMENTS:
        p = os.path.join(HERE, f)
        if not os.path.isfile(p):
            refuse(f"{p}: absent, and an instrument that cannot be read cannot "
                   f"be cleared")
        lines = assert_nodes(p)
        print(f"  {'OK  ' if not lines else 'FAIL'}  {f:<42} "
              f"{len(lines)} Assert node(s)"
              + (f" at lines {lines}" if lines else ""))
        if lines:
            bad.append(f"{f}: {len(lines)} assert(s) at {lines}")

    print("\nARM 3 -- MUTATION: arm 1 must be shown able to FIRE")
    with tempfile.TemporaryDirectory() as tmp:
        mut = os.path.join(tmp, "mutant.py")
        open(mut, "w").write(
            "import sys\n"
            "def guard(ranks):\n"
            "    assert ranks == 1, 'K0f is registered SERIAL'\n"
            "    return True\n")
        got = assert_nodes(mut)
        print(f"  {'OK  ' if got else 'FAIL'}  a refusal reverted to an "
              f"`assert` is CAUGHT on statement type alone   "
              f"[{len(got)} node(s)]")
        if not got:
            bad.append("MUTATION NOT CAUGHT: arm 1 is blind")
        # and the negative half: the same guard as an exit is NOT flagged
        clean = os.path.join(tmp, "clean.py")
        open(clean, "w").write(
            "import sys\n"
            "def guard(ranks):\n"
            "    if ranks != 1:\n"
            "        print('REFUSE'); sys.exit(2)\n"
            "    return True\n")
        got2 = assert_nodes(clean)
        print(f"  {'OK  ' if not got2 else 'FAIL'}  the SAME guard written as "
              f"`sys.exit(2)` is NOT flagged   [{len(got2)} node(s)]")
        if got2:
            bad.append("arm 1 flags a compliant guard")

        print("\nARM 2 -- DRIVEN under `python3` AND `python3 -O`, identical rc")
        for label, argv, want in refusal_drives(tmp):
            a = run(argv, False)
            b = run(argv, True)
            ok = (a == want and b == want)
            print(f"  {'OK  ' if ok else 'FAIL'}  {label:<58} "
                  f"python3={a} -O={b} (want {want})")
            if not ok:
                bad.append(f"{label}: python3={a} -O={b}, want {want}")

    print()
    if bad:
        print(f"VIOLATION: {len(bad)} finding(s)")
        for b in bad:
            print("   - " + b)
        return EXIT_VIOLATION
    print("CLEAN: no instrument refusal is carried by an `assert`, every")
    print("registered refusal fires IDENTICALLY under `python3 -O`, and the")
    print("statement-type arm was shown able to catch a revert.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
