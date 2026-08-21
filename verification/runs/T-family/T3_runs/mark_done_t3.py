#!/usr/bin/env python3
"""
Turn T3 STATUS files into DONE markers, under a rule the runner does not
itself apply (copied from mark_done_t1b.py; rationale there and in L-143).

A case is DONE here only if ALL of:
  1. STATUS.<case> exists and reports rc=0
  2. log.solve ends with OpenFOAM's own "End" line
  3. the last written time directory equals the controlDict endTime
  4. that time directory carries every field the comparator will read:
     T U p_rgh alphat phi, plus nut k omega when turbulenceProperties says RAS
  5. the number of ExecutionTime lines equals endTime (no silently skipped
     iterations, and no restart that replayed part of the run)
  6. every field in that time directory is NEWER than the case's own 0/T,
     which run_one_t3.sh touches LAST when it creates 0 from 0.orig

Test 6 exists because of the contamination in L-143: a moved case's solver kept
writing to the absolute path it resolved at startup and dropped a complete
final time directory into a freshly rebuilt case of the same name.  Only file
age distinguishes it.

This script never retracts: an existing DONE.<case> is left alone.  It exits
1 if any case in the list is not done.

Usage:  python3 mark_done_t3.py [--root DIR] [case ...]
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = ["R_c", "R_m", "R_f", "P_m", "C_lam_m", "W_m", "D_m", "O_m"]
NEEDED = ("T", "U", "p_rgh", "alphat", "phi")
NEEDED_TURBULENT = ("nut", "k", "omega")


def is_ras(d):
    txt = open(os.path.join(d, "constant", "turbulenceProperties")).read()
    return re.search(r"^\s*simulationType\s+RAS\s*;", txt, re.M) is not None


def control_end_time(d):
    txt = open(os.path.join(d, "system", "controlDict")).read()
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", txt, re.M)
    return float(m.group(1))


def check(root, case):
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return ["no case directory"]
    fails = []
    st = os.path.join(root, f"STATUS.{case}")
    if not os.path.isfile(st):
        return ["no STATUS file (case never finished)"]
    s = open(st).read()
    m = re.search(r"rc=(\d+)", s)
    if not m or int(m.group(1)) != 0:
        fails.append(f"STATUS is {s.strip()!r}, not rc=0")

    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"]
    body = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", body, re.M):
        fails.append("log.solve has no End line")
    n_exec = len(re.findall(r"^ExecutionTime", body, re.M))

    et = control_end_time(d)
    times = sorted((float(x) for x in os.listdir(d)
                    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        fails.append("no time directory beyond 0")
    else:
        last = nonzero[-1]
        if abs(last - et) > 1e-9:
            fails.append(f"last written time {last:g} != endTime {et:g}")
        tdir = os.path.join(d, f"{last:g}")
        need = NEEDED + NEEDED_TURBULENT if is_ras(d) else NEEDED
        miss = [f for f in need if not os.path.isfile(os.path.join(tdir, f))]
        if not miss:
            t0 = os.path.join(d, "0", "T")
            if not os.path.isfile(t0):
                fails.append("no 0/T, so the run's start cannot be dated")
            else:
                age0 = os.path.getmtime(t0)
                stale = [f for f in need
                         if os.path.getmtime(os.path.join(tdir, f)) < age0]
                if stale:
                    fails.append("time %g holds fields OLDER than 0/T (%s) -- "
                                 "not written by this run"
                                 % (last, ",".join(stale)))
        if miss:
            fails.append(f"time {last:g} is missing {','.join(miss)}")
    if n_exec != int(et):
        fails.append(f"{n_exec} ExecutionTime lines, expected {int(et)}")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("cases", nargs="*", default=CASES)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    ok, bad = [], {}
    for c in a.cases:
        f = check(root, c)
        (ok.append(c) if not f else bad.setdefault(c, f))
    for c in ok:
        marker = os.path.join(root, f"DONE.{c}")
        if not os.path.exists(marker):
            open(marker, "w").write("strict rule met\n")
    print(f"{len(ok)}/{len(a.cases)} cases meet the strict completion rule")
    for c in sorted(bad):
        print(f"  NOT DONE  {c}")
        for r in bad[c]:
            print(f"            - {r}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
