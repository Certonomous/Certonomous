#!/usr/bin/env python3
"""
Extension-aware amendment to mark_done_t1b.py for the T1b run pool.

WHY THIS FILE EXISTS.  mark_done_t1b.py decides DONE.<case> from the ORIGINAL
run segment only: test 1 reads STATUS2.<case>, test 2 demands an End line in
log.solve, and test 5 counts ^ExecutionTime lines in log.solve and requires the
count to equal the controlDict endTime.  Six fine-level cases (R_30k_f,
R_100k_f, R_300k_f, P_30k, P_100k, P_300k) were found NOT iteratively converged
at 20000 iterations by the comparator and are being extended by
run_one_ext1.sh, which resumes from latestTime to a raised endTime, appends to
log.solve.ext1 (log.solve is untouched) and writes STATUS3.<case>.  For such a
case log.solve will for ever hold exactly 20000 ExecutionTime lines while the
endTime is 30000..68000, so the original rule can never be satisfied, however
well the extension finishes.  Worse, the original rule never REMOVES a marker:
the DONE.<case> files written when those cases passed at 20000 still exist and
certify a state that has been superseded.  The frozen comparator analyse_t1b.py
only asks whether DONE.<case> exists, so a stale marker would let it grade
fields from an extension that may not have met the rule at all.

This file applies the SAME six tests, made aware of the extension segment:

  no log.solve.ext1  -> the case is judged exactly by mark_done_t1b.check().
  log.solve.ext1     -> 1. STATUS2 rc=0 AND STATUS3 exists with rc=0
                        2. End line in log.solve AND End line in log.solve.ext1
                        3. last written time == controlDict endTime
                        4. NEEDED (+ NEEDED_TURBULENT unless laminar) present
                        5. ExecutionTime(log.solve) + ExecutionTime(ext1)
                           == endTime, AND the first "Time = " of ext1 is
                           exactly one past the ExecutionTime count of
                           log.solve (20001): nothing replayed, nothing skipped
                        6. every field at endTime NEWER than 0/T AND NEWER
                           than STATUS2.<case>, the file that dated the end of
                           the original segment; older fields were not
                           written by the extension.

A case with an ext1 log that FAILS has any pre-existing DONE.<case> REMOVED,
and the removal is printed with the reasons.  A marker is never removed for a
case without an ext1 log -- that is the original tool's territory.

This is an amendment to the MARKING tool only.  It does not touch, and must not
be read as touching, the frozen comparator analyse_t1b.py.

It was written on 2026-08-20 while all six extensions were still running,
before any of them had finished (no STATUS3 file existed, every ext1 log was
still growing), so it could not have been tuned to an outcome.
"""
import os
import re
import sys

from mark_done_t1b import (CASES, NEEDED, NEEDED_TURBULENT, check,
                           control_end_time, is_laminar)

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = "ext1"


def _rc(path):
    """Return (exists, rc_or_None, raw_text) for a STATUS-style file."""
    if not os.path.isfile(path):
        return False, None, ""
    s = open(path).read()
    m = re.search(r"rc=(\d+)", s)
    return True, (int(m.group(1)) if m else None), s.strip()


def has_ext(case):
    return os.path.isfile(os.path.join(HERE, case, f"log.solve.{EXT}"))


def check_ext(case):
    d = os.path.join(HERE, case)
    fails = []

    # 1. both segments exited cleanly
    st2 = os.path.join(HERE, f"STATUS2.{case}")
    st3 = os.path.join(HERE, f"STATUS3.{case}")
    ok2, rc2, raw2 = _rc(st2)
    if not ok2:
        fails.append("no STATUS2 file (original segment never finished)")
    elif rc2 != 0:
        fails.append(f"STATUS2 is {raw2!r}, not rc=0")
    ok3, rc3, raw3 = _rc(st3)
    if not ok3:
        fails.append(f"no STATUS3 file ({EXT} extension not finished)")
    elif rc3 != 0:
        fails.append(f"STATUS3 is {raw3!r}, not rc=0")

    # 2. both logs end with OpenFOAM's own End line
    log = os.path.join(d, "log.solve")
    logx = os.path.join(d, f"log.solve.{EXT}")
    if not os.path.isfile(log):
        return fails + ["no log.solve"]
    body = open(log, errors="replace").read()
    bodyx = open(logx, errors="replace").read()
    if not re.search(r"^End\s*$", body, re.M):
        fails.append("log.solve has no End line")
    if not re.search(r"^End\s*$", bodyx, re.M):
        fails.append(f"log.solve.{EXT} has no End line")
    n_orig = len(re.findall(r"^ExecutionTime", body, re.M))
    n_ext = len(re.findall(r"^ExecutionTime", bodyx, re.M))

    # 3./4./6. last time directory, its fields, their age
    et = control_end_time(case)
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
        need = NEEDED if is_laminar(case) else NEEDED + NEEDED_TURBULENT
        miss = [f for f in need if not os.path.isfile(os.path.join(tdir, f))]
        if not miss:
            t0 = os.path.join(d, "0", "T")
            if not os.path.isfile(t0):
                fails.append("no 0/T, so the run's start cannot be dated")
            else:
                age0 = os.path.getmtime(t0)
                stale0 = [f for f in need
                          if os.path.getmtime(os.path.join(tdir, f)) < age0]
                if stale0:
                    fails.append("time %g holds fields OLDER than 0/T (%s) -- "
                                 "not written by this run"
                                 % (last, ",".join(stale0)))
            if not ok2:
                fails.append("no STATUS2, so the end of the original segment "
                             "cannot be dated")
            else:
                age2 = os.path.getmtime(st2)
                stale2 = [f for f in need
                          if os.path.getmtime(os.path.join(tdir, f)) < age2]
                if stale2:
                    fails.append("time %g holds fields OLDER than STATUS2 (%s)"
                                 " -- not written by the %s extension"
                                 % (last, ",".join(stale2), EXT))
        if miss:
            fails.append(f"time {last:g} is missing {','.join(miss)}")

    # 5. iteration accounting across the two segments
    if n_orig + n_ext != int(et):
        fails.append(f"{n_orig}+{n_ext}={n_orig + n_ext} ExecutionTime lines "
                     f"(log.solve+{EXT}), expected {int(et)}")
    m = re.search(r"^Time = ([0-9.eE+-]+)\s*$", bodyx, re.M)
    if not m:
        fails.append(f"log.solve.{EXT} has no 'Time = ' line")
    else:
        first = float(m.group(1))
        if abs(first - (n_orig + 1)) > 1e-9:
            fails.append(f"first Time in log.solve.{EXT} is {first:g}, expected "
                         f"{n_orig + 1} (one past log.solve's {n_orig} "
                         "ExecutionTime lines) -- replayed or skipped")
    return fails


def main():
    ok, bad, ext = [], {}, set()
    for c in CASES:
        if has_ext(c):
            ext.add(c)
            f = check_ext(c)
        else:
            f = check(c)
        (ok.append(c) if not f else bad.setdefault(c, f))
    for c in ok:
        text = ("strict rule met, extension %s included\n" % EXT
                if c in ext else "strict rule met\n")
        open(os.path.join(HERE, f"DONE.{c}"), "w").write(text)
    removed = []
    for c in bad:
        mk = os.path.join(HERE, f"DONE.{c}")
        if c in ext and os.path.isfile(mk):
            os.remove(mk)
            removed.append(c)
    print(f"{len(ok)}/{len(CASES)} cases meet the strict completion rule "
          f"({len(ext)} with an {EXT} extension)")
    for c in CASES:
        if c in ok:
            print(f"  PASS      {c}" + (f"  [{EXT} included]" if c in ext else ""))
    for c in sorted(bad):
        print(f"  NOT DONE  {c}" + (f"  [{EXT} present]" if c in ext else ""))
        for r in bad[c]:
            print(f"            - {r}")
        if c in removed:
            print(f"            REMOVED stale DONE.{c} -- it certified the "
                  "superseded pre-extension state, for the reasons above")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
