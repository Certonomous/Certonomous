#!/usr/bin/env python3
"""
DONE markers for the four T1b fourth-level cases R_*_x, under the strict rule
of mark_done_t1b.py and the extension rule of mark_done_t1b_ext1.py.

The two frozen marking tools are not edited.  Their CASES lists name the 19
attempt-2 cases and their test 1 reads STATUS2.<case>; the x cases are run by
run_one_t1b_L4.sh, which writes STATUS.<case> (the pool format used by the
D_Ts and T3 runners), so this file re-expresses the same six tests against
that file name, importing NEEDED, NEEDED_TURBULENT, control_end_time and
is_laminar from mark_done_t1b so the field list and the endTime parser are
the originals.

A case is DONE only if ALL of (mark_done_t1b.py tests 1-6):
  1. STATUS.<case> exists and reports rc=0
  2. log.solve ends with OpenFOAM's own End line
  3. the last written time directory equals the controlDict endTime
  4. that time directory carries every field the comparator will read
  5. the number of ExecutionTime lines equals endTime
  6. every field in that time directory is NEWER than the case's own 0/T,
     which run_one_t1b_L4.sh touches LAST when it creates 0 from 0.orig
     (the D438 / L-143 stray-write guard)

If the case has been EXTENDED (log.solve.ext1 exists, written by an extension
runner that resumes from latestTime to a raised endTime under the T1b section
6 disclosure rule and writes STATUS_ext1.<case>), the tests are applied across
both segments exactly as mark_done_t1b_ext1.py applies them:
  1. STATUS rc=0 AND STATUS_ext1 rc=0
  2. End line in log.solve AND in log.solve.ext1
  3./4. as above
  5. ExecutionTime(log.solve) + ExecutionTime(ext1) == endTime AND the first
     "Time = " of ext1 is exactly one past log.solve's count
  6. every field at endTime NEWER than 0/T AND NEWER than STATUS.<case>
A case with an ext1 log that fails has any pre-existing marker REMOVED and
the reasons printed; a marker is never removed for a case without an ext1
log (it was written under the strict rule and still certifies that state,
unless the case has since been extended, in which case this branch applies).

This is a marking tool.  It cannot move a number; it decides only whether
analyse_t1b_L4.py may read a case at all, and only in the direction of
refusing more.  Written 2026-08-21 before any x case had a mesh, so it could
not have been tuned to an outcome.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mark_done_t1b import (NEEDED, NEEDED_TURBULENT, control_end_time,   # noqa: E402
                           is_laminar)

CASES = [f"R_{t}_x" for t in ("10k", "30k", "100k", "300k")]
EXT = "ext1"
STATUS = "STATUS"                 # run_one_t1b_L4.sh writes STATUS.<case>
STATUS_EXT = f"STATUS_{EXT}"      # an extension runner writes STATUS_ext1.<case>


def _rc(path):
    if not os.path.isfile(path):
        return False, None, ""
    s = open(path).read()
    m = re.search(r"rc=(\d+)", s)
    return True, (int(m.group(1)) if m else None), s.strip()


def has_ext(case):
    return os.path.isfile(os.path.join(HERE, case, f"log.solve.{EXT}"))


def _fields_and_age(case, d, fails, need, et, date_files):
    times = sorted((float(x) for x in os.listdir(d)
                    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        fails.append("no time directory beyond 0")
        return
    last = nonzero[-1]
    if abs(last - et) > 1e-9:
        fails.append(f"last written time {last:g} != endTime {et:g}")
    tdir = os.path.join(d, f"{last:g}")
    miss = [f for f in need if not os.path.isfile(os.path.join(tdir, f))]
    if miss:
        fails.append(f"time {last:g} is missing {','.join(miss)}")
        return
    for label, ref in date_files:
        if not os.path.isfile(ref):
            fails.append(f"no {label}, so the run cannot be dated")
            continue
        age = os.path.getmtime(ref)
        stale = [f for f in need
                 if os.path.getmtime(os.path.join(tdir, f)) < age]
        if stale:
            fails.append("time %g holds fields OLDER than %s (%s) -- not "
                         "written by this run" % (last, label, ",".join(stale)))


def check(case):
    """mark_done_t1b.check(), against STATUS.<case> instead of STATUS2."""
    d = os.path.join(HERE, case)
    fails = []
    if not os.path.isdir(d):
        return ["no case directory"]
    ok, rc, raw = _rc(os.path.join(HERE, f"{STATUS}.{case}"))
    if not ok:
        return ["no STATUS file (case never finished)"]
    if rc != 0:
        fails.append(f"STATUS is {raw!r}, not rc=0")
    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"]
    body = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", body, re.M):
        fails.append("log.solve has no End line")
    n_exec = len(re.findall(r"^ExecutionTime", body, re.M))
    et = control_end_time(case)
    need = NEEDED if is_laminar(case) else NEEDED + NEEDED_TURBULENT
    _fields_and_age(case, d, fails, need, et,
                    [("0/T", os.path.join(d, "0", "T"))])
    if n_exec != int(et):
        fails.append(f"{n_exec} ExecutionTime lines, expected {int(et)}")
    return fails


def check_ext(case):
    """mark_done_t1b_ext1.check_ext(), against STATUS / STATUS_ext1."""
    d = os.path.join(HERE, case)
    fails = []
    st = os.path.join(HERE, f"{STATUS}.{case}")
    stx = os.path.join(HERE, f"{STATUS_EXT}.{case}")
    ok1, rc1, raw1 = _rc(st)
    if not ok1:
        fails.append("no STATUS file (original segment never finished)")
    elif rc1 != 0:
        fails.append(f"STATUS is {raw1!r}, not rc=0")
    okx, rcx, rawx = _rc(stx)
    if not okx:
        fails.append(f"no {STATUS_EXT} file ({EXT} extension not finished)")
    elif rcx != 0:
        fails.append(f"{STATUS_EXT} is {rawx!r}, not rc=0")

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

    et = control_end_time(case)
    need = NEEDED if is_laminar(case) else NEEDED + NEEDED_TURBULENT
    dates = [("0/T", os.path.join(d, "0", "T"))]
    if ok1:
        dates.append((f"{STATUS}.{case}", st))
    else:
        fails.append("no STATUS, so the end of the original segment cannot "
                     "be dated")
    _fields_and_age(case, d, fails, need, et, dates)

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


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    dry = "--dry-run" in argv
    ok, bad, ext = [], {}, set()
    for c in CASES:
        if has_ext(c):
            ext.add(c)
            f = check_ext(c)
        else:
            f = check(c)
        (ok.append(c) if not f else bad.setdefault(c, f))
    removed = []
    if not dry:
        for c in ok:
            text = ("strict rule met, extension %s included\n" % EXT
                    if c in ext else "strict rule met\n")
            open(os.path.join(HERE, f"DONE.{c}"), "w").write(text)
        for c in bad:
            mk = os.path.join(HERE, f"DONE.{c}")
            if c in ext and os.path.isfile(mk):
                os.remove(mk)
                removed.append(c)
    print(f"{len(ok)}/{len(CASES)} x-level cases meet the strict completion "
          f"rule ({len(ext)} with an {EXT} extension)"
          + ("  [dry run: no marker written or removed]" if dry else ""))
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
