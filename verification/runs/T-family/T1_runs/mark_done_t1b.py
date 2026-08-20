#!/usr/bin/env python3
"""
Turn T1b run-pool STATUS files into DONE markers, under a rule the pool runner
does not itself apply.

The runner writes STATUS2.<case> containing the solver's exit code.  An exit code
of zero is NOT sufficient evidence that a case produced a gradeable solution:
a run that is killed after writing its last checkpoint, or one whose endTime was
reached without the fields being written, can still exit cleanly enough to leave
a plausible-looking STATUS behind.

A case is DONE here only if ALL of:
  1. STATUS.<case> exists and reports rc=0
  2. log.solve ends with OpenFOAM's own "End" line
  3. the last written time directory equals the controlDict endTime
  4. that time directory carries every field the comparator will read
  5. the number of ExecutionTime lines equals endTime  (no silently skipped
     iterations, and no restart that replayed part of the run)
  6. every field in that time directory is NEWER than the case's own 0/T

Test 6 exists because of a contamination that nothing else here could see.  When
T1b attempt 1 was archived mid-run, OpenFOAM kept writing to the ABSOLUTE case
path it resolved at startup, not to the directory its process had followed, so a
finished attempt-1 solver dropped a complete 20000/ into the freshly rebuilt
attempt-2 case of the same name.  Both meshes have 81920 cells -- they differ
only in the radial GRADING -- so a cell-count check is blind to it, and the
stray directory carried the right time, the right field list and the right
length.  Only its age gives it away: run_one writes 0/ at the start of the run
that is allowed to produce the answer, so anything older than 0/T is not from
that run.

Anything short of that is left without a marker, and the frozen comparator
refuses on the missing marker rather than grading a partial case.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = ([f"R_{t}_{l}" for t in ("10k", "30k", "100k", "300k")
          for l in ("c", "m", "f")]
         + [f"P_{t}" for t in ("10k", "30k", "100k", "300k")]
         + ["W_100k", "W_300k", "C_lam"])
# Every case must write these.  alphat is written even by the laminar control,
# because buoyantBoussinesqSimpleFoam owns it regardless of the turbulence model.
NEEDED = ("T", "U", "p_rgh", "alphat")
# These exist ONLY where a turbulence model is solved.  Demanding them of the
# laminar control would fail the Charter 2c trivial baseline for doing exactly
# what it was built to do, so the requirement is read from the case, not fixed.
NEEDED_TURBULENT = ("nut", "k", "omega")


def is_laminar(case):
    txt = open(os.path.join(HERE, case, "constant", "turbulenceProperties")).read()
    return re.search(r"^\s*simulationType\s+laminar\s*;", txt, re.M) is not None


def control_end_time(case):
    txt = open(os.path.join(HERE, case, "system", "controlDict")).read()
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", txt, re.M)
    return float(m.group(1))


def check(case):
    d = os.path.join(HERE, case)
    fails = []
    st = os.path.join(HERE, f"STATUS2.{case}")
    if not os.path.isfile(st):
        return ["no STATUS2 file (case never finished)"]
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
    ok, bad = [], {}
    for c in CASES:
        f = check(c)
        (ok.append(c) if not f else bad.setdefault(c, f))
    for c in ok:
        open(os.path.join(HERE, f"DONE.{c}"), "w").write("strict rule met\n")
    print(f"{len(ok)}/{len(CASES)} cases meet the strict completion rule")
    for c in sorted(bad):
        print(f"  NOT DONE  {c}")
        for r in bad[c]:
            print(f"            - {r}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
