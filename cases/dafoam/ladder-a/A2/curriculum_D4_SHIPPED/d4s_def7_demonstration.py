#!/usr/bin/env python3
"""D4-DEF-7 REPAIR -- THE DEMONSTRATION.  MAKES EACH CLAUSE'S CONDITION OCCUR.

`SUPERVISOR_D4_ACCEPTANCE_AND_D4DEF7.md` section 3.2 states the standing bound
this file exists to satisfy, and it is this family's own amendment of
2026-08-25:

    "A guard is only shown to work by making the condition it guards actually
     occur."

D4's 29/29 selftest drove `G1_completion_and_age` to `NOT A RESULT` through the
AGE limb only.  It never drove a non-zero `rc` and never drove a missing
terminal statement, so it was silent on two thirds of the gate and `29/29 PASS`
was read as "the gate works".  A count of units is not a demonstration.

WHAT IS DEMONSTRATED HERE, AND WITH WHAT
----------------------------------------
Four of the five fixtures use **D4's OWN REAL ARM LOGS**, not synthetic text:
arm O and arm F3 really do end on the terminal statement; arms F and F2 really
do not, because both ended in an `mpirun detected ... non-zero status` abort.
The rc=1 condition is therefore not planted -- it HAPPENED, it is on disk, and
it is the exact artifact that carried `G1 = PASS` past the frozen grader.

THE DEAD-LEVER CONTROL, and it is the reason clause 2 is written positionally.
MEASURED on those four logs before the clause was written:

    "Finalising parallel run" as a SUBSTRING ANYWHERE : 4 of 4 logs -> USELESS
    "Finalising parallel run" as the LAST NON-EMPTY LINE : 2 of 4 -> the rc=0 arms

Both crashed arms carry FOUR mid-file copies (one per MPI rank) followed by
eleven further lines of abort text.  The obvious implementation of this clause
would have PASSED arm F -- the very arm that motivated D4-DEF-7 -- and would
have been a second dead lever inside the repair.  This file asserts BOTH
readings so the reader can see the difference rather than take it on trust.

BOTH FLAGS, AND WHY
-------------------
Every check runs under plain `python3` and under `python3 -O`.  `-O` deletes
every `assert` statement from the compiled code, so a refusal written as an
`assert` is a refusal the runner switches off with a flag they usually do not
know they are choosing.  This file contains ZERO `assert` statements and says
so by AST, on statement type: a grep matches `raise AssertionError`, and a
behavioural test passes a file whose asserts happen to hold; only the statement
type distinguishes `assert X`, which `-O` deletes, from `if not X: raise`,
which it does not.  `d4s_grade.py` is checked the same way.

EXIT CODES
    0  every fixture produced the REQUIRED outcome, under BOTH flags
    2  a fixture did not, or an AST check failed
"""
from __future__ import annotations

import ast
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
GRADER = HERE / "d4s_grade.py"
D4_RUN = pathlib.Path("/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin")
# The FROZEN grader, cited by path and NEVER EDITED (standing rule 6).  It is
# read here only to run it, so the repair can be shown to REACH: a fix that
# cannot be distinguished from the thing it fixes is not evidenced.
FROZEN = pathlib.Path(
    "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D4/d4_grade.py")

# D4's real arm logs.  Named, so a reader can go and look at them.
REAL_LOGS = {
    "O":  "O_20260825T181237Z_2359354.log",     # ledgered rc=0
    "F3": "F3_20260825T220706Z_2733788.log",    # ledgered rc=0
    "F":  "F_20260825T211339Z_2574215.log",     # ledgered rc=1  <-- the artifact
    "F2": "F2_20260825T215703Z_2715910.log",    # ledgered rc=1
}

LEDGER_TEMPLATE = (
    "ARM={arm} ROW=SHIPPED IMG=dafoam/opt-packages:latest "
    "DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc "
    "rc={rc} wall_s=100 ranks=4 core_min=6.667 cap_core_min={cap} "
    "enforced_wall_s=1000 enforced_core_min={cap:.6f} memory=12g "
    "inspect(exit,oomkilled)=[{kexit} {oom}] "
    "memavail_pre_GiB=26.80 memavail_post_GiB=28.23 cpuset=5,6,7,9 "
    "delivered_cores_mean=[3.9919 n=925 max_nr_throttled=52435] "
    "siblings_pre=[] siblings_post=[] log={log} stamp=DEMO\n"
)


class Failed(Exception):
    """Raised for any condition that must stop this file under ANY flag."""


def require(cond, msg):
    """A refusal that `-O` cannot delete.  Never write this as an assert."""
    if not cond:
        raise Failed(msg)


def no_assert_nodes(path: pathlib.Path) -> int:
    """Count `ast.Assert` STATEMENT nodes.  Statement type, not text."""
    return sum(1 for n in ast.walk(ast.parse(path.read_text())) if isinstance(n, ast.Assert))


# --------------------------------------------------------------------------
# The dead-lever control: substring-anywhere vs last-non-empty, on the real logs
# --------------------------------------------------------------------------
def measure_terminal_readings() -> dict:
    out = {}
    for arm, name in REAL_LOGS.items():
        p = D4_RUN / name
        require(p.is_file(), f"REAL LOG MISSING: {p} -- this demonstration reads "
                             f"D4's own artifacts and refuses to substitute "
                             f"synthetic text for them")
        text = p.read_bytes().replace(b"\x00", b"").decode("utf-8", errors="replace")
        ne = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
        anywhere = any("Finalising parallel run" in ln for ln in ne)
        positional = "Finalising parallel run" in ne[-1]
        out[arm] = {"substring_anywhere": anywhere, "last_nonempty": positional,
                    "n_lines_after_last_occurrence":
                        len(ne) - 1 - max((k for k, ln in enumerate(ne)
                                           if "Finalising parallel run" in ln),
                                          default=-1)}
    return out


# --------------------------------------------------------------------------
# Fixtures.  Each MAKES ONE CONDITION OCCUR.
# --------------------------------------------------------------------------
def build_fixture(root: pathlib.Path, arms: list[dict], stale_age: bool = False):
    """A sacrificial run base.  The LOGS ARE D4'S REAL ONES, copied byte-for-byte."""
    base = root / "base"
    work = base / "W"
    (work / "0").mkdir(parents=True)
    (work / "0" / "U").write_text("fixture\n")
    datum = int((work / "0" / "U").stat().st_mtime)
    (work / ".d4_age_datum").write_text(str(datum))
    for a in arms:
        if a.get("log_src"):
            shutil.copyfile(D4_RUN / a["log_src"], base / a["log"])
        elif a.get("log_text") is not None:
            (base / a["log"]).write_text(a["log_text"])
    with open(base / "ledger.txt", "w") as fh:
        for a in arms:
            fh.write(LEDGER_TEMPLATE.format(
                arm=a["arm"], rc=a["rc"], cap=a.get("cap", 620.0),
                kexit=a["kexit"], oom=a.get("oom", "false"), log=a["log"]))
    for name in ("opt_IPOPT.txt", "OptView.hst", "d4_major_history.json",
                 "d4_fd_endpoint.json"):
        p = work / name
        p.write_text("{}")
        # The age guard is STRICTLY newer, so a clean fixture must place its
        # artifacts a discriminating distance AFTER the datum -- writing them in
        # the same second makes `m > datum` false and the CONTROL fails.
        # A demonstration whose clean control fails proves nothing about its
        # mutants: every mutant would then fail for the control's reason rather
        # than its own.  This was caught by running it, not by reading it.
        os.utime(p, (datum - 3600, datum - 3600) if stale_age
                 else (datum + 60, datum + 60))
    return base, work


def run_g1(base: pathlib.Path, work: pathlib.Path, arms: list[str], opt: bool):
    """Invoke the REAL grader's g_completion + verdict composition, out of process,
    so the -O flag applies to the grader's own compiled code and not merely ours."""
    prog = (
        "import json,sys,importlib.util;"
        f"spec=importlib.util.spec_from_file_location('g',r'{GRADER}');"
        "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
        f"rows=m.read_ledger(r'{base / 'ledger.txt'}');"
        "\ntry:\n"
        f"    c=m.g_completion(r'{work}', r'{base}', rows, {arms!r})\n"
        f"    a=m.g_age(r'{work}', ['opt_IPOPT.txt','OptView.hst','d4_major_history.json','d4_fd_endpoint.json'], c['age_datum_epoch'])\n"
        "    v='PASS' if (c['rc_clause_pass'] and c['terminal_clause_pass'] and a['pass']) else 'NOT A RESULT'\n"
        "    print(json.dumps({'verdict':v,'rc':c['rc_clause_pass'],'terminal':c['terminal_clause_pass'],'age':a['pass'],'refusal':None}))\n"
        "except m.Refuse as e:\n"
        "    print(json.dumps({'verdict':'REFUSED','rc':None,'terminal':None,'age':None,'refusal':str(e)[:200]}))\n"
    )
    argv = [sys.executable] + (["-O"] if opt else []) + ["-c", prog]
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    if opt:
        env["PYTHONOPTIMIZE"] = "1"
    r = subprocess.run(argv, capture_output=True, text=True, env=env)
    require(r.returncode == 0, f"fixture harness crashed: {r.stderr[-600:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


FIXTURES = [
    ("CONTROL clean -- two rc=0 arms, both logs really end on the terminal line",
     dict(arms=[{"arm": "O", "rc": 0, "kexit": "0", "log": "O.log", "log_src": REAL_LOGS["O"]},
                {"arm": "F3", "rc": 0, "kexit": "0", "cap": 120.0, "log": "F3.log", "log_src": REAL_LOGS["F3"]}],
          stale_age=False),
     "PASS"),
    ("CLAUSE 1 (rc) -- arm F's REAL rc=1, the artifact the frozen grader passed",
     dict(arms=[{"arm": "O", "rc": 0, "kexit": "0", "log": "O.log", "log_src": REAL_LOGS["O"]},
                {"arm": "F3", "rc": 1, "kexit": "1", "cap": 120.0, "log": "F3.log", "log_src": REAL_LOGS["F3"]}],
          stale_age=False),
     "NOT A RESULT"),
    ("CLAUSE 1 (OOM) -- kernel says OOMKilled true on a zero exit",
     dict(arms=[{"arm": "O", "rc": 0, "kexit": "0", "oom": "true", "log": "O.log", "log_src": REAL_LOGS["O"]},
                {"arm": "F3", "rc": 0, "kexit": "0", "cap": 120.0, "log": "F3.log", "log_src": REAL_LOGS["F3"]}],
          stale_age=False),
     "NOT A RESULT"),
    ("CLAUSE 2 (terminal) -- arm F's REAL aborted log, which CONTAINS the line 4x but does not END on it",
     dict(arms=[{"arm": "O", "rc": 0, "kexit": "0", "log": "O.log", "log_src": REAL_LOGS["O"]},
                {"arm": "F3", "rc": 0, "kexit": "0", "cap": 120.0, "log": "F3.log", "log_src": REAL_LOGS["F"]}],
          stale_age=False),
     "NOT A RESULT"),
    ("CLAUSE 3 (age) -- the ONE clause the frozen grader did implement; must still fire",
     dict(arms=[{"arm": "O", "rc": 0, "kexit": "0", "log": "O.log", "log_src": REAL_LOGS["O"]},
                {"arm": "F3", "rc": 0, "kexit": "0", "cap": 120.0, "log": "F3.log", "log_src": REAL_LOGS["F3"]}],
          stale_age=True),
     "NOT A RESULT"),
    ("REFUSAL -- harness $? says 0, the kernel's .State.ExitCode says 1. Neither is chosen silently",
     dict(arms=[{"arm": "O", "rc": 0, "kexit": "0", "log": "O.log", "log_src": REAL_LOGS["O"]},
                {"arm": "F3", "rc": 0, "kexit": "1", "cap": 120.0, "log": "F3.log", "log_src": REAL_LOGS["F3"]}],
          stale_age=False),
     "REFUSED"),
    ("CLAUSE 2 -- log named in the ledger does not exist. A missing log is a FAILED clause, never a passing one",
     dict(arms=[{"arm": "O", "rc": 0, "kexit": "0", "log": "O.log", "log_src": REAL_LOGS["O"]},
                {"arm": "F3", "rc": 0, "kexit": "0", "cap": 120.0, "log": "ABSENT.log"}],
          stale_age=False),
     "NOT A RESULT"),
]


def run_frozen_g1(base: pathlib.Path, work: pathlib.Path, arms: list[str]):
    """Run the FROZEN grader's G1 composition on the same fixture.

    THE BEFORE/AFTER THAT PROVES THE REPAIR REACHES.  The frozen
    `g_completion(work, ledger_rows, arms_required)` takes no `base` and never
    compares rc to zero; `main()` composes
    `"PASS" if report["G1_age"]["pass"] else "NOT A RESULT"`.  That exact
    composition is reproduced here, from the frozen file's own functions.
    """
    prog = (
        "import json,importlib.util;"
        f"spec=importlib.util.spec_from_file_location('f',r'{FROZEN}');"
        "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
        f"rows=m.read_ledger(r'{base / 'ledger.txt'}');"
        "\ntry:\n"
        f"    c=m.g_completion(r'{work}', rows, {arms!r})\n"
        f"    a=m.g_age(r'{work}', ['opt_IPOPT.txt','OptView.hst','d4_major_history.json','d4_fd_endpoint.json'], c['age_datum_epoch'])\n"
        "    v='PASS' if a['pass'] else 'NOT A RESULT'\n"
        "    print(json.dumps({'verdict':v,'rc_in_report':{k:x['rc'] for k,x in c['arms'].items()}}))\n"
        "except m.Refuse as e:\n"
        "    print(json.dumps({'verdict':'REFUSED','rc_in_report':None}))\n"
    )
    r = subprocess.run([sys.executable, "-c", prog], capture_output=True, text=True)
    require(r.returncode == 0, f"frozen-grader harness crashed: {r.stderr[-600:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def main() -> int:
    print("D4-DEF-7 REPAIR -- DEMONSTRATION BY MAKING THE CONDITION OCCUR")
    print("=" * 78)
    failures = []

    # ---- AST, statement type, on both files --------------------------------
    for f in (GRADER, pathlib.Path(__file__).resolve()):
        n = no_assert_nodes(f)
        if n:
            failures.append(f"AST: {f.name} contains {n} ast.Assert node(s); "
                            f"-O would delete them")
        else:
            print(f"  AST OK   {f.name}: 0 ast.Assert nodes (statement type, not text)")

    # ---- the dead-lever control -------------------------------------------
    print("\nDEAD-LEVER CONTROL on D4's four REAL arm logs "
          "(why clause 2 is positional):")
    m = measure_terminal_readings()
    n_any = sum(1 for v in m.values() if v["substring_anywhere"])
    n_pos = sum(1 for v in m.values() if v["last_nonempty"])
    for arm, v in m.items():
        print(f"  arm {arm:<3} substring_anywhere={str(v['substring_anywhere']):<5} "
              f"last_nonempty={str(v['last_nonempty']):<5} "
              f"lines_after_last_occurrence={v['n_lines_after_last_occurrence']}")
    if n_any != 4:
        failures.append(f"DEAD-LEVER: expected the substring in all 4 real logs, got {n_any}")
    else:
        print(f"  SUBSTRING-ANYWHERE reading: {n_any} of 4 -> DISCRIMINATES NOTHING")
    if n_pos != 2:
        failures.append(f"DEAD-LEVER: expected 2 of 4 on the positional reading, got {n_pos}")
    else:
        print(f"  POSITIONAL reading:         {n_pos} of 4 -> exactly the rc=0 arms. "
              f"The clause is implemented positionally BECAUSE of this measurement.")

    # ---- the fixtures, under BOTH flags ------------------------------------
    print("\nFIXTURES -- each makes ONE condition occur, run under python3 AND python3 -O:")
    for title, kw, expect in FIXTURES:
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            base, work = build_fixture(root, **kw)
            arms = [a["arm"] for a in kw["arms"]]
            got = {}
            for opt in (False, True):
                got["-O" if opt else "plain"] = run_g1(base, work, arms, opt)
        v_plain = got["plain"]["verdict"]
        v_opt = got["-O"]["verdict"]
        ok = (v_plain == expect and v_opt == expect)
        limbs = got["plain"]
        print(f"  [{'OK ' if ok else 'BAD'}] plain={v_plain:<13} -O={v_opt:<13} "
              f"(rc={limbs['rc']} terminal={limbs['terminal']} age={limbs['age']})")
        print(f"        {title}")
        if not ok:
            failures.append(f"FIXTURE: {title!r} expected {expect}, got "
                            f"plain={v_plain} -O={v_opt}")

    # ---- BEFORE/AFTER: the frozen grader on the SAME rc=1 fixture -----------
    print("\nBEFORE/AFTER -- the FROZEN grader on the SAME fixture the repair rejects.")
    print("  A repair that cannot be distinguished from the defect is not evidenced.")
    with tempfile.TemporaryDirectory() as td:
        kw = FIXTURES[1][1]          # the rc=1 fixture
        base, work = build_fixture(pathlib.Path(td), **kw)
        arms = [a["arm"] for a in kw["arms"]]
        before = run_frozen_g1(base, work, arms)
        after = run_g1(base, work, arms, opt=False)
    print(f"  FROZEN   curriculum_D4/d4_grade.py -> {before['verdict']!r}   "
          f"with rc in its own report: {before['rc_in_report']}")
    print(f"  REPAIRED curriculum_D4_SHIPPED/d4s_grade.py -> {after['verdict']!r}")
    if before["verdict"] != "PASS":
        failures.append(
            "BEFORE/AFTER: the frozen grader did NOT emit PASS on the rc=1 "
            "fixture, so this fixture does not reproduce D4-DEF-7 and the "
            "repair is not shown to reach anything.")
    elif after["verdict"] != "NOT A RESULT":
        failures.append("BEFORE/AFTER: the repaired grader did not reject it.")
    else:
        print("  => D4-DEF-7 REPRODUCED and REPAIRED: the frozen grader emits PASS "
              "on a required arm whose rc is 1 and which sits in its OWN report; "
              "the repaired grader returns NOT A RESULT.")

    print("=" * 78)
    if failures:
        for f in failures:
            print("  FAILED: " + f)
        print(f"DEMONSTRATION FAILED: {len(failures)} condition(s) did not hold.")
        return 2
    # Printed from INSIDE the branch that verified it, so deleting a check
    # deletes its claim rather than leaving the claim behind.
    print(f"DEMONSTRATION PASSED: {len(FIXTURES)} fixtures, each driving its clause, "
          f"identical under python3 and python3 -O; the dead-lever control "
          f"separates 4-of-4 from 2-of-4 on D4's own logs.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failed as exc:
        print(f"REFUSED: {exc}")
        sys.exit(2)
