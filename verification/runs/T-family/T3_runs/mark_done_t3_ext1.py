#!/usr/bin/env python3
"""
Extension-aware amendment to mark_done_t3.py for the T3 run pool.
Pattern and rationale: T1_runs/mark_done_t1b_ext1.py, T1b_RESULTS.md sec.7.

WHY THIS FILE EXISTS.  mark_done_t3.py decides DONE.<case> from the ORIGINAL
run segment only.  Its test 2 demands an "End" line in log.solve, its test 3
demands the last written time == the controlDict endTime, and its test 5 counts
^ExecutionTime lines in log.solve and requires that count to equal endTime.
All eight T3 cases were found NOT iteratively converged at 20000 by the frozen
comparator and are being extended by run_one_t3_ext1.sh, which resumes from
latestTime to a raised endTime, writes a NEW log (log.solve.ext1; log.solve is
untouched) and writes STATUS_EXT1.<case>.

For such a case:
  * log.solve holds exactly 20000 ExecutionTime lines FOR EVER, while the
    controlDict endTime is now 28000..80000, so test 5 can never be satisfied
    however well the extension finishes; and
  * the last written time is now the raised endTime, so test 3 fails too.
Worse, mark_done_t3.py NEVER RETRACTS: main() only writes markers.  All eight
DONE.<case> files written when the cases met the rule at 20000 still sit on
disk certifying a state that the extension supersedes, and the frozen
comparator analyse_t3.py asks only whether DONE.<case> EXISTS.  A stale marker
would let it grade fields from a half-finished extension.

This file applies the SAME six tests, made aware of the extension segment:

  no log.solve.ext1 -> the case is judged exactly by mark_done_t3.check().
  log.solve.ext1    -> 1. STATUS.<case> rc=0 AND STATUS_EXT1.<case> rc=0
                       2. "End" in log.solve AND "End" in log.solve.ext1
                          (SEGMENT 1 End at 20000, SEGMENT 2 End at the new
                          endTime)
                       3. last written time dir == the NEW controlDict endTime
                       4. NEEDED (+ NEEDED_TURBULENT when RAS) present there
                       5. ExecutionTime(log.solve) + ExecutionTime(ext1)
                          == the new endTime, AND the first "Time = " of ext1
                          is exactly one past log.solve's ExecutionTime count
                          (20001): nothing replayed, nothing skipped
                       6. AGE GUARD: every field at the last time is NEWER
                          than the case's own 0/T (mark_done_t3 test 6, L-143)
                          AND NEWER than STATUS.<case>, the file that dated the
                          end of the original segment.  A field older than
                          STATUS.<case> was written by segment 1, not by the
                          extension.

A case WITH an ext1 log that FAILS has any pre-existing DONE.<case> REMOVED and
the removal printed with its reasons.  A marker is never removed for a case
WITHOUT an ext1 log -- that is the original tool's territory, and this tool
does not trespass on it.

This is an amendment to the MARKING tool only.  It does not touch, and must not
be read as touching, the frozen comparator analyse_t3.py.  It cannot move a
number; it decides only whether the comparator may read a case at all, and only
ever in the direction of refusing more.

mark_done_t3.py exposes CASES, NEEDED, NEEDED_TURBULENT, control_end_time,
is_ras and check; it has no is_laminar (that name is T1b's), so laminar is
taken here as `not is_ras(case_dir)`, which is the same test mark_done_t3.check
makes.  Nothing is redefined locally: every rule below is imported.

Usage: python3 mark_done_t3_ext1.py [--root DIR] [--dry-run] [--selftest] [case ...]
"""
import argparse
import os
import re
import shutil
import sys
import tempfile

from mark_done_t3 import (CASES, NEEDED, NEEDED_TURBULENT, check,
                          control_end_time, is_ras)

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = "ext1"
SEG1_END = 20000          # every T3 case's original controlDict endTime


def _rc(path):
    """(exists, rc_or_None, raw_text) for a STATUS-style file."""
    if not os.path.isfile(path):
        return False, None, ""
    s = open(path).read()
    m = re.search(r"rc=(\d+)", s)
    return True, (int(m.group(1)) if m else None), s.strip()


def has_ext(root, case):
    return os.path.isfile(os.path.join(root, case, f"log.solve.{EXT}"))


def check_ext(root, case):
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return ["no case directory"]
    fails = []

    # 1. both segments exited cleanly
    st1 = os.path.join(root, f"STATUS.{case}")
    st2 = os.path.join(root, f"STATUS_EXT1.{case}")
    ok1, rc1, raw1 = _rc(st1)
    if not ok1:
        fails.append("no STATUS file (original segment never finished)")
    elif rc1 != 0:
        fails.append(f"STATUS is {raw1!r}, not rc=0")
    ok2, rc2, raw2 = _rc(st2)
    if not ok2:
        fails.append(f"no STATUS_EXT1 file ({EXT} extension not finished)")
    elif rc2 != 0:
        fails.append(f"STATUS_EXT1 is {raw2!r}, not rc=0")

    # 2. both logs end with OpenFOAM's own End line
    log = os.path.join(d, "log.solve")
    logx = os.path.join(d, f"log.solve.{EXT}")
    if not os.path.isfile(log):
        return fails + ["no log.solve"]
    body = open(log, errors="replace").read()
    bodyx = open(logx, errors="replace").read()
    if not re.search(r"^End\s*$", body, re.M):
        fails.append("log.solve has no End line (segment 1 did not finish)")
    if not re.search(r"^End\s*$", bodyx, re.M):
        fails.append(f"log.solve.{EXT} has no End line (segment 2 did not finish)")
    n_orig = len(re.findall(r"^ExecutionTime", body, re.M))
    n_ext = len(re.findall(r"^ExecutionTime", bodyx, re.M))

    # segment 1 must still be the untouched 20000-iteration original
    if n_orig != SEG1_END:
        fails.append(f"log.solve holds {n_orig} ExecutionTime lines, expected "
                     f"{SEG1_END} -- segment 1 is not the original T3 segment")

    et = control_end_time(d)
    if et <= SEG1_END:
        fails.append(f"controlDict endTime {et:g} is not above {SEG1_END} -- "
                     f"an {EXT} log exists but no extension was requested")

    # 3./4./6. last time directory, its fields, their age
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
        if miss:
            fails.append(f"time {last:g} is missing {','.join(miss)}")
        else:
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
            if not ok1:
                fails.append("no STATUS, so the end of the original segment "
                             "cannot be dated")
            else:
                age1 = os.path.getmtime(st1)
                stale1 = [f for f in need
                          if os.path.getmtime(os.path.join(tdir, f)) < age1]
                if stale1:
                    fails.append("time %g holds fields OLDER than STATUS (%s) "
                                 "-- not written by the %s extension"
                                 % (last, ",".join(stale1), EXT))

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


def run(root, cases, dry_run=False, out=print):
    ok, bad, ext = [], {}, set()
    for c in cases:
        if has_ext(root, c):
            ext.add(c)
            f = check_ext(root, c)
        else:
            f = check(root, c)
        (ok.append(c) if not f else bad.setdefault(c, f))
    written, removed = [], []
    for c in ok:
        mk = os.path.join(root, f"DONE.{c}")
        text = ("strict rule met, extension %s included\n" % EXT
                if c in ext else "strict rule met\n")
        if not dry_run:
            open(mk, "w").write(text)
        written.append(c)
    for c in bad:
        mk = os.path.join(root, f"DONE.{c}")
        if c in ext and os.path.isfile(mk):
            if not dry_run:
                os.remove(mk)
            removed.append(c)
    tag = "DRY RUN -- nothing written or removed: " if dry_run else ""
    out(f"{tag}{len(ok)}/{len(cases)} cases meet the strict completion rule "
        f"({len(ext)} with an {EXT} extension)")
    for c in cases:
        if c in ok:
            out(f"  PASS      {c}" + (f"  [{EXT} included]" if c in ext else ""))
    for c in sorted(bad):
        out(f"  NOT DONE  {c}" + (f"  [{EXT} present]" if c in ext else ""))
        for r in bad[c]:
            out(f"            - {r}")
        if c in removed:
            verb = "would REMOVE" if dry_run else "REMOVED"
            out(f"            {verb} stale DONE.{c} -- it certified the "
                "superseded pre-extension state, for the reasons above")
    return ok, bad, removed


# ---------------------------------------------------------------- selftest --

def _forge(root, case, end=30000, n_ext=10000, first_ext=20001,
           n_orig=SEG1_END, ras=True, ext_end=True, status_ext_rc=0,
           last_time=None, stale_field=None, drop_status_ext=False):
    """Forge a complete two-segment case directory under root."""
    d = os.path.join(root, case)
    last_time = end if last_time is None else last_time
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    os.makedirs(os.path.join(d, "constant"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write(
        "startFrom       latestTime;\nstartTime       0;\nstopAt          endTime;\n"
        f"endTime         {end};\ndeltaT          1;\nwriteInterval   2000;\n")
    open(os.path.join(d, "constant", "turbulenceProperties"), "w").write(
        "simulationType  %s;\n" % ("RAS" if ras else "laminar"))
    fields = NEEDED + NEEDED_TURBULENT if ras else NEEDED
    # 0/ with T touched last, oldest of everything
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    open(os.path.join(d, "0", "T"), "w").write("0\n")
    t_zero = 1000.0
    os.utime(os.path.join(d, "0", "T"), (t_zero, t_zero))
    # segment 1 log: n_orig iterations + End
    with open(os.path.join(d, "log.solve"), "w") as fh:
        for i in range(1, n_orig + 1):
            fh.write(f"\nTime = {i}\n\nExecutionTime = {i * 0.1:.1f} s\n")
        fh.write("End\n")
    # STATUS.<case> dates the end of segment 1
    st1 = os.path.join(root, f"STATUS.{case}")
    open(st1, "w").write("rc=0 wall=100 checkMesh_rc=0\n")
    t_st1 = 2000.0
    os.utime(st1, (t_st1, t_st1))
    # segment 2 log
    with open(os.path.join(d, f"log.solve.{EXT}"), "w") as fh:
        for i in range(first_ext, first_ext + n_ext):
            fh.write(f"\nTime = {i}\n\nExecutionTime = {i * 0.1:.1f} s\n")
        if ext_end:
            fh.write("End\n")
    # the two surviving time dirs (purgeWrite 2), fields newer than STATUS
    for t in (last_time - 2000, last_time):
        td = os.path.join(d, str(t))
        os.makedirs(td, exist_ok=True)
        for f in fields:
            p = os.path.join(td, f)
            open(p, "w").write("x\n")
            age = t_zero - 500 if (stale_field == f and t == last_time) else 3000.0
            os.utime(p, (age, age))
    if not drop_status_ext:
        st2 = os.path.join(root, f"STATUS_EXT1.{case}")
        open(st2, "w").write(f"rc={status_ext_rc} wall=200 endTime={end}\n")
    return d


def selftest():
    root = tempfile.mkdtemp(prefix="t3ext1_selftest_")
    fails = []
    n = [0]

    def expect(name, cases, want_ok, want_reason=None, dry=True):
        got_ok, bad, removed = run(root, cases, dry_run=dry, out=lambda *a: None)
        n[0] += 1
        passed = (cases[0] in got_ok) == want_ok
        reasons = bad.get(cases[0], [])
        if want_reason is not None:
            passed = passed and any(want_reason in r for r in reasons)
        print(f"  [{'ok ' if passed else 'FAIL'}] {name}")
        if not passed:
            fails.append(name)
            print(f"         got ok={cases[0] in got_ok} reasons={reasons}")
        return removed, reasons

    print("SELFTEST mark_done_t3_ext1.py  (forged case dirs under %s)" % root)

    _forge(root, "A")                                        # clean 20000+10000=30000
    expect("clean two-segment case PASSES", ["A"], True)

    _forge(root, "B", first_ext=20501)                       # skipped iterations
    expect("first ext1 Time 20501 -> REJECT (replayed or skipped)",
           ["B"], False, "replayed or skipped")

    _forge(root, "C", n_ext=9000)                            # 20000+9000 != 30000
    expect("ExecutionTime count 29000 != 30000 -> REJECT",
           ["C"], False, "expected 30000")

    _forge(root, "D", ext_end=False)                         # segment 2 killed
    expect("no End in log.solve.ext1 -> REJECT",
           ["D"], False, "segment 2 did not finish")

    _forge(root, "E", status_ext_rc=1)
    expect("STATUS_EXT1 rc=1 -> REJECT", ["E"], False, "not rc=0")

    _forge(root, "F", drop_status_ext=True)
    expect("no STATUS_EXT1 -> REJECT", ["F"], False, "extension not finished")

    _forge(root, "G", last_time=28000)                       # stopped early
    expect("last time 28000 != endTime 30000 -> REJECT",
           ["G"], False, "!= endTime")

    _forge(root, "H", stale_field="T")                       # age guard vs 0/T
    expect("final T older than 0/T -> REJECT (age guard)",
           ["H"], False, "OLDER than 0/T")

    # stale-marker removal
    _forge(root, "I", n_ext=9000)
    open(os.path.join(root, "DONE.I"), "w").write("strict rule met\n")
    removed, _ = expect("failing ext1 case: stale DONE.I flagged for removal",
                        ["I"], False, dry=True)
    n[0] += 1
    if "I" not in removed:
        fails.append("stale marker not flagged"); print("  [FAIL] removal flagged")
    n[0] += 1
    if not os.path.isfile(os.path.join(root, "DONE.I")):
        fails.append("--dry-run REMOVED a marker"); print("  [FAIL] dry-run wrote")
    else:
        print("  [ok ] --dry-run left DONE.I on disk")
    run(root, ["I"], dry_run=False, out=lambda *a: None)
    n[0] += 1
    if os.path.isfile(os.path.join(root, "DONE.I")):
        fails.append("stale marker not removed"); print("  [FAIL] real run kept DONE.I")
    else:
        print("  [ok ] real run REMOVED stale DONE.I")

    # a laminar case (no nut/k/omega demanded)
    _forge(root, "J", ras=False)
    expect("laminar case (no nut/k/omega) PASSES", ["J"], True)

    # a case with NO ext1 log falls through to the original tool untouched
    _forge(root, "K")
    os.remove(os.path.join(root, "K", f"log.solve.{EXT}"))
    open(os.path.join(root, "K", "system", "controlDict"), "w").write(
        "startFrom latestTime;\nstopAt endTime;\nendTime         20000;\n")
    shutil.rmtree(os.path.join(root, "K", "30000"))
    shutil.rmtree(os.path.join(root, "K", "28000"))
    for t in (18000, 20000):
        td = os.path.join(root, "K", str(t)); os.makedirs(td)
        for f in NEEDED + NEEDED_TURBULENT:
            p = os.path.join(td, f); open(p, "w").write("x\n"); os.utime(p, (3000.0, 3000.0))
    open(os.path.join(root, "DONE.K"), "w").write("strict rule met\n")
    got_ok, bad, removed = run(root, ["K"], dry_run=False, out=lambda *a: None)
    n[0] += 1
    ok_k = ("K" in got_ok) and os.path.isfile(os.path.join(root, "DONE.K")) and "K" not in removed
    print(f"  [{'ok ' if ok_k else 'FAIL'}] no-ext1 case judged by the ORIGINAL tool, marker untouched")
    if not ok_k:
        fails.append("no-ext1 fallthrough")

    shutil.rmtree(root)
    print(f"SELFTEST {'PASSED' if not fails else 'FAILED: ' + ', '.join(fails)}"
          f"  ({n[0] - len(fails)}/{n[0]} checks)")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--dry-run", action="store_true",
                    help="report only; write no markers and remove none")
    ap.add_argument("--selftest", action="store_true",
                    help="forge case dirs in a temp root and check every rule")
    ap.add_argument("cases", nargs="*", default=CASES)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    ok, bad, _ = run(os.path.abspath(a.root), a.cases, dry_run=a.dry_run)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
