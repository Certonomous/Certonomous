#!/usr/bin/env python3
"""DONE marker for T3 R_ff: the strict completion rule (CLAUDE.md rule 4) with the
age guard, plus reconstructPar's rc, read from the key=value STATUS.R_ff that
launch_t3_rff.sh writes IN-WRAPPER.  Registered by T3_R_FF_PREREGISTRATION.md
AMENDMENT 1; frozen before R_ff iterated.

Field classes (the supervisor's 2026-08-26 ruling, cited there as L-342):
  PHYSICS-CRITICAL -- any failure is NOT DONE; an absent STATUS is a REFUSAL (exit 2):
    solver rc = 0 from STATUS.R_ff; End line in log.solve; last time == endTime;
    fields T U p_rgh alphat phi nut k omega present at that time; ExecutionTime
    count == endTime; every field NEWER than the case's own 0/T (age guard);
    reconstructpar_rc = 0 (the fields are reconstructed -- a failed
    reconstruction is not a result).  If log.solve.ext1 exists, the two-segment
    rule of the frozen mark_done_t3_ext1.check_ext applies verbatim.
  INFRASTRUCTURE -- reported; absent or odd values are stated as NOT MEASURED and
    disclosed in the marker, NEVER a refusal: wall_s, ranks, core_min, timeout_s,
    capped, checkmesh_rc, decomposepar_rc, log.launch / log.decomposePar /
    log.reconstructPar presence, marker mtime.
Clauses 1-6 are the frozen mark_done_t3.check(root, case) (HEAD blob 5da28c73),
imported and called on "R_ff"; nothing is restated.  Never retracts.
Usage: python3 mark_done_t3_rff.py [--root DIR] [--dry-run] | --selftest
Exit 0 DONE (or dry-run), 1 NOT DONE, 2 refusal.  Zero `assert` statements.
"""
import os, shutil, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mark_done_t3 as MD          # frozen, blob 5da28c73
import mark_done_t3_ext1 as MDX    # frozen, blob e4cbb992

CASE = "R_ff"
INFRA = ("wall_s", "ranks", "core_min", "timeout_s", "capped", "checkmesh_rc", "decomposepar_rc")
INFRA_LOGS = ("log.launch", "log.decomposePar", "log.reconstructPar", "log.checkMesh.run")


def read_status(root):
    p = os.path.join(root, "STATUS.%s" % CASE)
    if not os.path.isfile(p):
        return None
    d = {}
    for line in open(p):
        if "=" in line:
            k, v = line.strip().split("=", 1)
            d[k] = v
    return d


def judge(root):
    """Returns (physics_fails, infra_report) or raises SystemExit(2) on an absent STATUS."""
    st = read_status(root)
    if st is None:
        print("REFUSE: no STATUS.%s -- the run never finished (or never ran); an absent rc is not a zero" % CASE)
        sys.exit(2)
    fails = list(MD.check(root, CASE))          # clauses 1-6 (rc, End, last time, fields, count, age guard)
    if MDX.has_ext(root, CASE):
        fails = list(MDX.check_ext(root, CASE))  # two-segment rule supersedes, verbatim
    rrc = st.get("reconstructpar_rc")
    if rrc is None:
        fails.append("STATUS carries no reconstructpar_rc (physics-critical: the fields are reconstructed)")
    elif rrc != "0":
        fails.append("reconstructpar_rc=%s, not 0" % rrc)
    infra = {}
    for k in INFRA:
        infra[k] = st.get(k, "NOT MEASURED")
    for lg in INFRA_LOGS:
        infra[lg] = "present" if os.path.isfile(os.path.join(root, CASE, lg)) else "NOT MEASURED (absent)"
    return fails, infra


def run(root, dry_run=False):
    fails, infra = judge(root)
    disclosed = ["%s=%s" % (k, v) for k, v in infra.items()]
    if fails:
        print("NOT DONE  %s" % CASE)
        for f in fails:
            print("  - " + f)
        print("infrastructure (disclosed, not gating): " + "; ".join(disclosed))
        return 1
    marker = os.path.join(root, "DONE.%s" % CASE)
    text = ("strict rule met (mark_done_t3.check clauses 1-6 + reconstructpar_rc=0"
            + (" + two-segment rule" if MDX.has_ext(root, CASE) else "") + ")\n"
            "infrastructure (disclosed, not gating): " + "; ".join(disclosed) + "\n")
    if dry_run:
        print("DRY RUN -- %s meets the strict completion rule; nothing written" % CASE)
    elif not os.path.exists(marker):
        open(marker, "w").write(text)
        print("DONE.%s written" % CASE)
    else:
        print("DONE.%s already present; left alone" % CASE)
    print(text.strip())
    return 0


def _forge(root, rc="0", recon="0", end=4000, n_exec=None, with_end=True, stale=False, status=True, infra=True):
    d = os.path.join(root, CASE)
    for sub in ("0", "constant", "system"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write("endTime %d;\n" % end)
    open(os.path.join(d, "constant", "turbulenceProperties"), "w").write("simulationType RAS;\n")
    open(os.path.join(d, "0", "T"), "w").write("x\n")
    t0 = time.time() - 100
    os.utime(os.path.join(d, "0", "T"), (t0, t0))
    td = os.path.join(d, str(end)); os.makedirs(td, exist_ok=True)
    for f in MD.NEEDED + MD.NEEDED_TURBULENT:
        p = os.path.join(td, f); open(p, "w").write("y\n")
        if stale:
            os.utime(p, (t0 - 100, t0 - 100))
    n = end if n_exec is None else n_exec
    open(os.path.join(d, "log.solve"), "w").write("ExecutionTime = 1 s\n" * n + ("End\n" if with_end else ""))
    if status:
        lines = ["case=%s" % CASE, "rc=%s" % rc, "reconstructpar_rc=%s" % recon]
        if infra:
            lines += ["wall_s=10", "ranks=8", "core_min=1.333", "timeout_s=205500", "capped=no",
                      "checkmesh_rc=0", "decomposepar_rc=0"]
        open(os.path.join(root, "STATUS.%s" % CASE), "w").write("\n".join(lines) + "\n")


def selftest():
    fails = []
    def expect(name, want_code, **kw):
        tmp = tempfile.mkdtemp(prefix="t3rffmd_")
        try:
            _forge(tmp, **kw)
            code = None
            try:
                code = run(tmp, dry_run=False)
            except SystemExit as e:
                code = e.code
            ok = code == want_code
            marker = os.path.exists(os.path.join(tmp, "DONE.%s" % CASE))
            ok = ok and (marker == (want_code == 0))
            print("  [%s] %s -> exit %s marker %s" % ("ok" if ok else "FAIL", name, code, marker))
            if not ok:
                fails.append(name)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print("planted controls (each drives the rule; a rule that cannot reject is not a rule):")
    expect("clean forged case -> DONE", 0)
    expect("rc=1 -> NOT DONE", 1, rc="1")
    expect("reconstructpar_rc=3 -> NOT DONE", 1, recon="3")
    expect("no End line -> NOT DONE", 1, with_end=False)
    expect("ExecutionTime count short -> NOT DONE", 1, n_exec=3999)
    expect("fields OLDER than 0/T (age guard) -> NOT DONE", 1, stale=True)
    expect("absent STATUS -> REFUSE exit 2", 2, status=False)
    expect("infrastructure fields absent -> still DONE, NOT MEASURED disclosed", 0, infra=False)
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = os.path.abspath(argv[argv.index("--root") + 1]) if "--root" in argv else HERE
    return run(root, dry_run="--dry-run" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
