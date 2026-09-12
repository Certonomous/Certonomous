#!/usr/bin/env python3
"""d6r2_grade.py self-test.  Builds synthetic run roots and asserts that the
comparator returns each of its three registered labels, and that a clean
control does NOT pass when a single registered condition is broken.

Run:  python3 d6r2_grade_selftest.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, "d6r2_grade.py")

LOG_TMPL = """Time = 1000
CD: 0.0275 final: 0.0275
Objectives
{{'obj.J': array([{j0:.17g}])}}
Nonlinear constraints
{{'cl04.aero_post.functionals.CL': array([0.4]),
 'cl05.aero_post.functionals.CL': array([0.5]),
 'cl06.aero_post.functionals.CL': array([0.6])}}
Objectives
{{'obj.J': array([{jf:.17g}])}}
Nonlinear constraints
{{'cl04.aero_post.functionals.CL': array([{c4:.8f}]),
 'cl05.aero_post.functionals.CL': array([{c5:.8f}]),
 'cl06.aero_post.functionals.CL': array([{c6:.8f}])}}
Finalising parallel run
"""

IPOPT_TMPL = """Number of Iterations....: {iters}

EXIT: {exit_line}
"""


def build(root, j0=0.03064163, jf=0.02223880, iters=25,
          exit_line="Maximum Number of Iterations Exceeded.",
          c4=0.4, c5=0.5, c6=0.6, rc=0, drop=None):
    W = os.path.join(root, "O_mp")
    os.makedirs(W, exist_ok=True)
    datum = int(time.time()) - 600
    open(os.path.join(W, ".d4_age_datum"), "w").write(str(datum))
    open(os.path.join(root, "D6R2_ARM_RC.txt"), "w").write(str(rc))
    open(os.path.join(root, "O_mp_20260912T000000Z_1.log"), "w").write(
        LOG_TMPL.format(j0=j0, jf=jf, c4=c4, c5=c5, c6=c6))
    if drop != "opt_IPOPT.txt":
        open(os.path.join(W, "opt_IPOPT.txt"), "w").write(
            IPOPT_TMPL.format(iters=iters, exit_line=exit_line))
    if drop != "OptView.hst":
        open(os.path.join(W, "OptView.hst"), "w").write("x" * 128)
    for mp in ("mp04", "mp05", "mp06"):
        if drop == mp:
            continue
        for pr in ("processor0", "processor1"):
            os.makedirs(os.path.join(W, mp, pr, "1000"), exist_ok=True)
    open(os.path.join(root, "ledger.txt"), "w").write(
        "ITEM=D6R2\nARM=O_mp ROW=PATCHED rc=0 wall_s=12000 ranks=4 core_min=800.0\n")
    return root


def grade(root):
    p = subprocess.run([sys.executable, GRADER, "--base", root],
                       capture_output=True, text=True)
    if p.returncode == 2:
        return "REFUSE", p.stdout.strip()
    j = json.load(open(os.path.join(root, "D6R2_grade.json")))
    return j["verdict"], p.stdout.strip()


CASES = [
    ("clean control",                     dict(),                                             "PASS"),
    ("G2 misses the 10% band",            dict(jf=0.02900000),                                "GATE FAIL"),
    ("G2 exactly at the band",            dict(jf=0.03064163 * 0.90),                         "PASS"),
    ("G2 a hair inside the band",         dict(jf=0.03064163 * 0.9000001),                    "GATE FAIL"),
    ("G3 one CL outside 1e-3",            dict(c5=0.5021),                                    "GATE FAIL"),
    ("G3 one CL just inside 1e-3",        dict(c5=0.5009),                                    "PASS"),
    ("G1 the IPOPT crash D6R suffered",   dict(exit_line="Invalid number in NLP function or derivative detected."), "NOT A RESULT"),
    ("G1 stopped short of the budget",    dict(iters=18),                                     "NOT A RESULT"),
    ("G1 rc=124, the clock kill",         dict(rc=124),                                       "NOT A RESULT"),
    ("G4 no optimiser history",           dict(drop="OptView.hst"),                           "NOT A RESULT"),
    ("G4 one point wrote no fields",      dict(drop="mp06"),                                  "NOT A RESULT"),
]


def main():
    fails = 0
    for name, kw, want in CASES:
        d = tempfile.mkdtemp(prefix="d6r2_selftest_")
        try:
            build(d, **kw)
            got, out = grade(d)
            ok = got == want
            fails += 0 if ok else 1
            print("%-4s %-34s want=%-12s got=%s" % ("ok" if ok else "FAIL", name, want, got))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    # the planted reader control must be EXERCISED-PASS on a real read
    d = tempfile.mkdtemp(prefix="d6r2_selftest_plant_")
    try:
        build(d)
        grade(d)
        j = json.load(open(os.path.join(d, "D6R2_grade.json")))
        st = j["controls"]["planted_reader"]["state"]
        ok = st == "EXERCISED-PASS"
        fails += 0 if ok else 1
        print("%-4s %-34s want=%-12s got=%s" % ("ok" if ok else "FAIL",
              "planted reader control", "EXERCISED-PASS", st))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("SELFTEST %s  failures=%d" % ("PASS" if fails == 0 else "FAIL", fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
