#!/usr/bin/env python3
"""mark_done_t5.py -- writes DONE.<case> under the STRICT completion rule (standing
rule 4; prereg S15) and NOTHING ELSE.  It never infers: an absent STATUS.<case> is a
REFUSAL (exit 2), not a NOT DONE -- nothing ran or the launcher died, and either is a
question for a person.  The rule, all-or-nothing, mirroring analyse_t5.py's
check_completion so the two instruments cannot disagree:
  1. STATUS.<case> exists (else REFUSE), rc=0, capped=0
  2. log.solve carries OpenFOAM's `End` line
  3. last `Time = N` equals controlDict endTime and ExecutionTime count == endTime
  4. <endTime>/ holds every required field (per region for chtMultiRegion cases;
     nut/k/omega only when turbulenceProperties says RAS)
  5. AGE GUARD: every required field at endTime is NEWER than the case's own
     0/**/T, which run_one_t5.sh touches LAST before the solver starts (L-143)
An existing DONE marker is never retracted here.  No `assert` (L-332); refusals are
driven under `python3 -O` in --selftest.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS_CUBE = ("T", "U", "p_rgh", "alphat")
FIELDS_X2D = ("U", "p")
FIELDS_RAS = ("nut", "k", "omega")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def read_kv(path):
    d = {}
    with open(path, errors="replace") as fh:
        for line in fh:
            if "=" in line:
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip()
    return d


def is_ras(case):
    for p in ("constant/air/turbulenceProperties", "constant/turbulenceProperties"):
        f = os.path.join(case, p)
        if os.path.isfile(f):
            return re.search(r"^\s*simulationType\s+RAS\s*;", open(f).read(), re.M) is not None
    return False


def end_time(case):
    txt = open(os.path.join(case, "system/controlDict")).read()
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", txt, re.M)
    if not m:
        refuse("%s: no endTime in controlDict" % case)
    return int(float(m.group(1)))


def check(root, case):
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        refuse("no case directory %s" % d)
    st_path = os.path.join(root, "STATUS." + case)
    if not os.path.isfile(st_path):
        refuse("%s: NO STATUS FILE -- nothing ran, or the launcher died before writing one. "
               "Not inferred." % case)
    st = read_kv(st_path)
    why = []
    if st.get("rc") != "0":
        why.append("rc=%s (note=%s)" % (st.get("rc"), st.get("note")))
    if st.get("capped") == "1":
        why.append("capped=1: stopped by its own budget (right-censored, PENDING)")
    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        why.append("no log.solve")
        return why
    txt = open(log, errors="replace").read()
    et = end_time(d)
    if not re.search(r"^End\s*$", txt, re.M):
        why.append("no End line")
    times = [int(float(m.group(1))) for m in re.finditer(r"^Time = ([0-9.eE+-]+)\s*$", txt, re.M)]
    if not times:
        why.append("no Time lines")
    elif times[-1] != et:
        why.append("last time %d != endTime %d" % (times[-1], et))
    nexec = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    if nexec != et:
        why.append("ExecutionTime count %d != endTime %d" % (nexec, et))
    tdir = os.path.join(d, str(et))
    if not os.path.isdir(tdir):
        why.append("no %d/ directory" % et)
        return why
    multi = os.path.isdir(os.path.join(d, "constant", "air"))
    need = list(FIELDS_CUBE if multi else FIELDS_X2D) + (list(FIELDS_RAS) if is_ras(d) else [])
    files = []
    if multi:
        for f in need:
            files.append(os.path.join(tdir, "air", f))
        files.append(os.path.join(tdir, "epoxy", "T")) if os.path.isdir(os.path.join(d, "constant", "epoxy")) else None
    else:
        files = [os.path.join(tdir, f) for f in need]
    missing = [os.path.relpath(f, tdir) for f in files if not os.path.isfile(f)]
    if missing:
        why.append("fields missing at endTime: " + ",".join(missing))
    zt = None
    for dp, _dn, fn in os.walk(os.path.join(d, "0")):
        if "T" in fn or (not multi and "U" in fn):
            zt = os.path.getmtime(os.path.join(dp, "T" if "T" in fn else "U"))
            break
    if zt is None:
        why.append("no 0/**/T (or 0/U for X_2d): the age guard has no datum")
    else:
        stale = [os.path.relpath(f, tdir) for f in files if os.path.isfile(f) and os.path.getmtime(f) <= zt]
        if stale:
            why.append("AGE GUARD: field(s) at endTime not newer than 0/T: " + ",".join(stale))
    return why


def _fake_case(root, case, complete=True, stale=False):
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"))
    open(os.path.join(d, "system/controlDict"), "w").write("endTime 3;\n")
    os.makedirs(os.path.join(d, "constant"))
    open(os.path.join(d, "constant/turbulenceProperties"), "w").write("simulationType RAS;\n")
    os.makedirs(os.path.join(d, "3"))
    for f in ("U", "p", "nut", "k", "omega"):
        open(os.path.join(d, "3", f), "w").write("x")
    os.makedirs(os.path.join(d, "0"))
    open(os.path.join(d, "0", "U"), "w").write("x")
    now = time.time()
    os.utime(os.path.join(d, "0", "U"), (now - 10, now - 10) if not stale else (now + 10, now + 10))
    open(os.path.join(d, "log.solve"), "w").write(
        "".join("Time = %d\nExecutionTime = 1 s\n" % t for t in (1, 2, 3)) + ("End\n" if complete else ""))
    return d


def selftest():
    fails = []
    tmp = tempfile.mkdtemp(prefix="t5_markdone_")
    me = os.path.abspath(__file__)
    def run(argv_prefix, case):
        return subprocess.run(argv_prefix + [me, "--root", tmp, case], capture_output=True, text=True)
    # arm 1: NO STATUS -> REFUSE (rc 2), under both interpreters
    _fake_case(tmp, "A")
    rcs = {t: run(a, "A").returncode for t, a in (("py", [sys.executable]), ("py -O", [sys.executable, "-O"]))}
    if not all(v == 2 for v in rcs.values()):
        fails.append("absent STATUS did not REFUSE under both interpreters: %r" % rcs)
    if os.path.exists(os.path.join(tmp, "DONE.A")):
        fails.append("a DONE marker was written with no STATUS")
    # arm 2: STATUS rc=0 but AGE GUARD violated -> NOT DONE (rc 1), no marker
    _fake_case(tmp, "B", stale=True)
    open(os.path.join(tmp, "STATUS.B"), "w").write("case=B\nrc=0\ncapped=0\n")
    p = run([sys.executable, "-O"], "B")
    if p.returncode != 1 or "AGE GUARD" not in p.stdout or os.path.exists(os.path.join(tmp, "DONE.B")):
        fails.append("stale fields were not caught by the age guard: rc=%d %s" % (p.returncode, p.stdout[-200:]))
    # arm 3: no End line -> NOT DONE
    _fake_case(tmp, "C", complete=False)
    open(os.path.join(tmp, "STATUS.C"), "w").write("case=C\nrc=0\ncapped=0\n")
    p = run([sys.executable, "-O"], "C")
    if p.returncode != 1 or "End" not in p.stdout:
        fails.append("missing End line not caught")
    # arm 4: every clause holds -> DONE marker written
    _fake_case(tmp, "D")
    open(os.path.join(tmp, "STATUS.D"), "w").write("case=D\nrc=0\ncapped=0\n")
    p = run([sys.executable, "-O"], "D")
    if p.returncode != 0 or not os.path.isfile(os.path.join(tmp, "DONE.D")):
        fails.append("compliant case not marked DONE: rc=%d %s" % (p.returncode, p.stdout[-200:]))
    # arm 5: capped=1 -> NOT DONE
    _fake_case(tmp, "E")
    open(os.path.join(tmp, "STATUS.E"), "w").write("case=E\nrc=0\ncapped=1\n")
    p = run([sys.executable], "E")
    if p.returncode != 1 or "capped" not in p.stdout:
        fails.append("capped run marked done")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    for f in fails:
        print("FAILED: " + f)
    print("SELFTEST %s: 5 arms, %d FAILED (%s)" % ("PASS" if not fails else "FAIL", len(fails),
                                                    "-O" if not __debug__ else "plain"))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("cases", nargs="*")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.cases:
        ap.print_help()
        return 0
    rc = 0
    for c in a.cases:
        why = check(a.root, c)
        marker = os.path.join(a.root, "DONE." + c)
        if why:
            rc = 1
            print("NOT DONE  %s: %s" % (c, "; ".join(why)))
        else:
            if not a.dry_run and not os.path.exists(marker):
                with open(marker, "w") as fh:
                    fh.write("DONE %s under the strict rule (rc=0, End, endTime, fields, age guard) at %s\n"
                             % (c, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            print("DONE      %s%s" % (c, " (dry run, marker not written)" if a.dry_run else ""))
    return rc


if __name__ == "__main__":
    sys.exit(main())
