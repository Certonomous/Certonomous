#!/usr/bin/env python3
"""
Turn T9a STATUS files into DONE markers, under the strict rule of mark_done_t1b.py.

A case is DONE only if ALL of:
  1. STATUS.<case> exists and reports rc=0
  2. log.solve ends with OpenFOAM's own "End" line
  3. the last written time directory equals the controlDict endTime
  4. that time directory carries every field the comparator reads (T, DT)
  5. the number of ExecutionTime lines equals endTime (no skipped or replayed steps)
  6. every field in that time directory is NEWER than the case's own 0/T
     (the wrapper re-copies 0/ at the start of the run allowed to answer, so
     anything older than 0/T was not written by that run)
Anything short of that gets no marker, and the frozen comparator refuses.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CASES = ["W_c", "W_m", "W_f", "W_C3", "F_c", "F_m", "F_f"]
NEEDED = ("T", "DT")

def end_time(case):
    txt = open(os.path.join(HERE, case, "system", "controlDict")).read()
    return float(re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", txt, re.M).group(1))

def check(case):
    d = os.path.join(HERE, case); fails = []
    st = os.path.join(HERE, f"STATUS.{case}")
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
    et = end_time(case)
    times = sorted((float(x) for x in os.listdir(d) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)))
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        fails.append("no time directory beyond 0")
    else:
        last = nonzero[-1]
        if abs(last - et) > 1e-9:
            fails.append(f"last written time {last:g} != endTime {et:g}")
        tdir = os.path.join(d, f"{last:g}")
        miss = [f for f in NEEDED if not os.path.isfile(os.path.join(tdir, f))]
        if miss:
            fails.append(f"time {last:g} is missing {','.join(miss)}")
        else:
            t0 = os.path.join(d, "0", "T")
            if not os.path.isfile(t0):
                fails.append("no 0/T, so the run's start cannot be dated")
            else:
                age0 = os.path.getmtime(t0)
                stale = [f for f in NEEDED if os.path.getmtime(os.path.join(tdir, f)) < age0]
                if stale:
                    fails.append(f"time {last:g} holds fields OLDER than 0/T ({','.join(stale)})")
    if n_exec != int(et):
        fails.append(f"{n_exec} ExecutionTime lines, expected {int(et)}")
    return fails

def main():
    ok, bad = [], {}
    for c in CASES:
        f = check(c); (ok.append(c) if not f else bad.setdefault(c, f))
    for c in ok:
        open(os.path.join(HERE, f"DONE.{c}"), "w").write("strict rule met\n")
    print(f"{len(ok)}/{len(CASES)} cases meet the strict completion rule: {' '.join(ok)}")
    for c in sorted(bad):
        print(f"  NOT DONE  {c}")
        for r in bad[c]: print(f"            - {r}")
    return 0 if not bad else 1

if __name__ == "__main__":
    sys.exit(main())
