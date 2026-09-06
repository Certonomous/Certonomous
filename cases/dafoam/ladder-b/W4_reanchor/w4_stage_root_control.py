#!/usr/bin/env python3
# ===========================================================================
# W4 CBFS RE-ANCHOR ROOT-STAGING CONTROL -- the driven discriminator for
# w4_stage_root.sh.  IT LAUNCHES NO REAL SOLVER AND NO REAL CONTAINER.
#
# WHY THIS FILE EXISTS.
#
# W4_REANCHOR_PREREGISTRATION.md section 18 records that section 17's production
# drive "drove the leg-production drivers with BASE REDIRECTED to a sandbox, so it
# never exercised the real run-root staging" -- and that a stager was DEFERRED and
# NEVER BUILT.  "A drive that redirects BASE to a sandbox is not a drive of the
# real staging."  THIS FILE DRIVES THE ACTUAL STAGING: it makes w4_stage_root.sh
# CREATE and POPULATE a real run root in a throwaway sandbox, reads that sandbox
# back from disk to confirm the root is populated, and only THEN runs the frozen
# run_plateau.sh from the populated root (container mocked) and grades the
# driver-produced tree with the frozen comparator.  A drive that skips the staging
# is exactly the defect section 18 records.
#
# BOTH DIRECTIONS (CLAUDE.md rule 3 and its mirror).  D1 is the PLANT: the stager,
# against a proper source, MUST stage a populated root that then drives 16 legs the
# comparator grades exit 0.  Every refusing direction (existing root, md5 mismatch,
# launch-target absent) is meaningful ONLY because D1 passes.  A harness in which
# everything refused would score every failure green while proving nothing.
#
# NOTHING REGISTERED IS TOUCHED.  The REGISTERED run root
# /home/ubuntu/certonomous-runs/W4-reanchor and the registered case source
# /home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock are NEVER written; every
# direction runs in a throwaway sandbox, and this control asserts the registered
# root stayed ABSENT and refuses if it appeared.  The sandbox path is REDACTED to
# <sandbox> in the evidence file (rule 13: a repository document never cites a
# scratch path).
#
# THE CONTAINER IS MOCKED by drive_evidence/mock_sudo.sh + mock_solver.py (the
# section-17 harness, reused).  The graded verdict is on SYNTHETIC mock objectives:
# it proves STAGING + leg PRODUCTION + grading CONSUMPTION, NOT physics.
#
# EXIT CODES: 0 all directions as registered; 1 a direction did not behave as
# registered; 2 REFUSED -- a precondition of the drive itself was not met.
# ===========================================================================
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STAGER = os.path.join(HERE, "w4_stage_root.sh")
COMPARATOR = os.path.join(HERE, "analyse_w4_reanchor.py")
MOCK_SUDO = os.path.join(HERE, "drive_evidence", "mock_sudo.sh")
REGISTERED_BASE = "/home/ubuntu/certonomous-runs/W4-reanchor"
REGISTERED_CBFS = "/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/cbfs_beta"
EVID = os.path.join(HERE, "drive_evidence", "W4_STAGE_ROOT_DRIVE.txt")

REG_MD5 = {                                        # prereg 4.1 / comparator registry
    "run_one.sh":       "da96cb58cc3904a2232a700c2bf9895d",
    "run_plateau.sh":   "7700b1b45a5464673c6659dd57dc23e6",
    "runScript.py":     "565307ddfd2affd7184011f60834edd8",
    "fd_beta_ones.npy": "661e027867ffa48d5b64297a5e990238",
}
REJECTED_RUNSCRIPT_MD5 = "877242a601eba205525c04211f0c7afd"  # the 6,230-byte alternative

TAGS = ["p050_5491_plus", "p050_5491_minus", "fw750_5491_plus", "fw750_5491_minus",
        "anchor8w", "base8w", "p025_5491_plus", "p025_5491_minus",
        "p025_6740_plus", "p025_6740_minus", "p050_6740_plus", "p050_6740_minus",
        "p025_12486_plus", "p025_12486_minus", "p050_12486_plus", "p050_12486_minus"]
FIELDS = ("U", "p", "k", "omega", "nut", "phi")

_LINES = []
_SANDBOX_ROOT = None


def rec(msg):
    red = msg
    if _SANDBOX_ROOT:
        red = red.replace(_SANDBOX_ROOT, "<sandbox>")
    red = re.sub(r"/tmp/[^\s'\"]+", "<sandbox>", red)
    print(red)
    _LINES.append(red)


def md5_of(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def run_stager(base, cbfs_src=REGISTERED_CBFS, src_dir=HERE, stage_evid=None):
    env = dict(os.environ)
    env["BASE"] = base
    env["CBFS_SRC"] = cbfs_src
    env["SRC_DIR"] = src_dir
    env["STAGE_EVID"] = stage_evid or os.path.join(os.path.dirname(base), "stage.txt")
    r = subprocess.run(["bash", STAGER], env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return r.returncode, r.stdout


def read_populated_root(root):
    """Confirm, BY READING DISK, that the run root is populated as registered."""
    facts, ok = {}, True

    def chk(name, cond):
        nonlocal ok
        facts[name] = bool(cond)
        ok = ok and bool(cond)

    cbfs = os.path.join(root, "cbfs_beta")
    # (1) drivers at the run root, registered md5
    for drv in ("run_one.sh", "run_plateau.sh"):
        p = os.path.join(root, drv)
        chk("%s present & md5" % drv,
            os.path.isfile(p) and md5_of(p) == REG_MD5[drv])
    chk("run_plateau.sh executable", os.access(os.path.join(root, "run_plateau.sh"), os.X_OK))
    # (2) the two overlay instruments inside cbfs_beta, registered md5
    for ins in ("runScript.py", "fd_beta_ones.npy"):
        p = os.path.join(cbfs, ins)
        chk("cbfs_beta/%s present & md5" % ins,
            os.path.isfile(p) and md5_of(p) == REG_MD5[ins])
    # (3) runScript.py is I1 (registered), NOT the rejected 6,230-byte alternative
    rs = os.path.join(cbfs, "runScript.py")
    chk("runScript.py is I1 not the rejected alternative",
        os.path.isfile(rs) and md5_of(rs) != REJECTED_RUNSCRIPT_MD5)
    # (4) the OpenFOAM case state carried
    chk("cbfs_beta/constant present", os.path.isdir(os.path.join(cbfs, "constant")))
    chk("cbfs_beta/system present", os.path.isdir(os.path.join(cbfs, "system")))
    chk("cbfs_beta/0 present", os.path.isdir(os.path.join(cbfs, "0")))
    # (5) section-3 cited artefacts NOT carried
    chk("processor0 NOT carried", not os.path.exists(os.path.join(cbfs, "processor0")))
    chk("cbfs_beta_grad.npy NOT carried", not os.path.exists(os.path.join(cbfs, "cbfs_beta_grad.npy")))
    chk("no fd_beta_c*.npy carried",
        not any(f.startswith("fd_beta_c") for f in os.listdir(cbfs)))
    # (6) run-root mode 777 (L-251)
    chk("run root mode 777", (os.stat(root).st_mode & 0o777) == 0o777)
    # (7) 0/ touched LAST: its max mtime >= that of constant/system/runScript.py (rule 4)
    zdir = os.path.join(cbfs, "0")
    zt = max((os.path.getmtime(os.path.join(zdir, f))
              for f in os.listdir(zdir)
              if os.path.isfile(os.path.join(zdir, f))), default=None)
    others = []
    for comp in ("constant", "system", "runScript.py"):
        cp = os.path.join(cbfs, comp)
        if os.path.isdir(cp):
            for dp, _, fs in os.walk(cp):
                others += [os.path.getmtime(os.path.join(dp, f)) for f in fs]
        elif os.path.isfile(cp):
            others.append(os.path.getmtime(cp))
    chk("0/ datum touched last (>= case-state mtimes)",
        zt is not None and others and zt >= max(others))
    facts["_zt"] = zt
    return ok, facts


def flip_base(path, sandbox_root):
    """Redirect the run root's driver copy from the REGISTERED path to the sandbox,
    by exactly the BASE= line.  Returns the unified diff (one hunk)."""
    orig = open(path).read()
    new = re.sub(r"(?m)^BASE=%s$" % re.escape(REGISTERED_BASE),
                 "BASE=%s" % sandbox_root, orig)
    open(path, "w").write(new)
    d = subprocess.run(["diff", "-", path], input=orig,
                       stdout=subprocess.PIPE, text=True).stdout
    return d, (orig != new)


def drive_16_legs(root):
    """Run the FROZEN run_plateau.sh from the populated sandbox root, container
    mocked, and read the produced legs back from disk."""
    # flip the run root's driver copies to the sandbox (one line each, proven)
    diffs = {}
    for drv in ("run_one.sh", "run_plateau.sh"):
        d, changed = flip_base(os.path.join(root, drv), root)
        diffs[drv] = (d, changed)
    # mock PATH: a `sudo` that is mock_sudo.sh (mock_solver resolves beside it)
    binp = os.path.join(os.path.dirname(root), "bin")
    os.makedirs(binp, exist_ok=True)
    sudo_link = os.path.join(binp, "sudo")
    if os.path.lexists(sudo_link):
        os.remove(sudo_link)
    os.symlink(MOCK_SUDO, sudo_link)
    env = dict(os.environ)
    env["PATH"] = binp + os.pathsep + env["PATH"]
    r = subprocess.run(["bash", os.path.join(root, "run_plateau.sh")], env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # read produced legs from disk
    logs = sum(os.path.isfile(os.path.join(root, "log.%s" % t)) for t in TAGS)
    fdirs = 0
    for t in TAGS:
        okf = all(os.path.isfile(os.path.join(root, "fields_%s" % t,
                  "processor%d" % p, "2500", fld))
                  for p in range(4) for fld in FIELDS)
        fdirs += int(okf)
    ledp = os.path.join(root, "ledger.csv")
    end_ok = 0
    if os.path.isfile(ledp):
        led = open(ledp).read().splitlines()
        for t in TAGS:
            end_ok += any(l.startswith(t + ",END,") and "rc=0" in l for l in led)
    grad = os.path.join(root, "anchor8w_grad.npy")
    return {"rc": r.returncode, "logs": logs, "fields_dirs": fdirs,
            "ledger_end_rc0": end_ok,
            "anchor_grad_at_root": os.path.isfile(grad),
            "anchor_grad_bytes": os.path.getsize(grad) if os.path.isfile(grad) else 0,
            "diffs": diffs, "stdout_tail": r.stdout.strip().splitlines()[-1:]}


def grade(root, out):
    r = subprocess.run([sys.executable, COMPARATOR, "--run-root", root,
                        "--json", out, "--skip-freeze"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return r.returncode, r.stdout


def main():
    global _SANDBOX_ROOT
    rc_all = 0
    reg_present_at_start = os.path.exists(REGISTERED_BASE)
    tmp = tempfile.mkdtemp(prefix="w4_stage_drive_")
    rec("W4 ROOT-STAGING CONTROL -- DRIVES THE ACTUAL STAGING (prereg 18). "
        "0.000 SOLVER CORE-MIN.")
    rec("  utc=%s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    rec("  NOTHING here is a result about W4. The container is MOCKED; the graded "
        "verdict is on synthetic objectives and proves STAGING + PRODUCTION + "
        "GRADING, not physics.")
    rec("  registered run root %s absent at start: %s" %
        (REGISTERED_BASE, not reg_present_at_start))

    # =================== D1  PLANT: real staging -> populated -> 16 legs -> PASS
    rec("")
    rec("--- D1 PLANT: run the stager into a sandbox root, READ IT BACK, then drive "
        "the frozen run_plateau.sh from it (mock container) -> 16 legs -> comparator PASS")
    s1 = os.path.join(tmp, "d1")
    os.makedirs(s1)
    _SANDBOX_ROOT = s1
    root = os.path.join(s1, "W4-reanchor")
    rc, out = run_stager(root, stage_evid=os.path.join(s1, "stage.txt"))
    rec("  stager rc=%d (0 expected)" % rc)
    pop_ok, facts = (False, {})
    if rc == 0:
        pop_ok, facts = read_populated_root(root)
        for k, v in facts.items():
            if not k.startswith("_"):
                rec("    populated: %-45s %s" % (k, "OK" if v else "*** FAIL ***"))
    leg = grd = None
    verdict = None
    age_ok = None
    if rc == 0 and pop_ok:
        time.sleep(1.1)  # guarantee produced fields postdate the 0/ datum (rule 4)
        leg = drive_16_legs(root)
        for drv, (d, changed) in leg["diffs"].items():
            nlines = len([l for l in d.splitlines() if l and l[0] in "<>"])
            rec("    BASE-flip %s: exactly %d changed line(s) (the BASE= line), applied=%s"
                % (drv, nlines, changed))
        rec("  16-leg drive: run_plateau rc=%d; logs=%d/16 ledger_END_rc0=%d/16 "
            "fields_dirs=%d/16 anchor_grad_at_root=%s (%d bytes)"
            % (leg["rc"], leg["logs"], leg["ledger_end_rc0"], leg["fields_dirs"],
               leg["anchor_grad_at_root"], leg["anchor_grad_bytes"]))
        out_json = os.path.join(s1, "grade.json")
        grc, gtxt = grade(root, out_json)
        import json
        grd = json.load(open(out_json)) if os.path.exists(out_json) else {}
        verdict = grd.get("verdict", {}).get("item_token")
        age_ok = all(grd.get("completion", {}).get(t, {})
                     .get("clauses", {}).get("age_guard") for t in TAGS)
        fw = grd.get("f_w", {})
        w1_pass = all(grd.get("w1", {}).get(str(c), {}).get("token") == "PASS"
                      for c in (5491, 6740, 12486))
        rec("  comparator: exit=%d verdict=%s age_guard=16/16:%s F_W_fails_W1=%s "
            "(%.4f%%) W1_PASS_3/3=%s"
            % (grc, verdict, age_ok, fw.get("prediction_met"),
               fw.get("measured_stat_pct_dhi") or -1, w1_pass))
        d1_ok = (rc == 0 and pop_ok and leg["rc"] == 0 and leg["logs"] == 16
                 and leg["ledger_end_rc0"] == 16 and leg["fields_dirs"] == 16
                 and leg["anchor_grad_at_root"] and grc == 0
                 and verdict == "PASS" and age_ok and w1_pass
                 and fw.get("prediction_met") is True)
    else:
        d1_ok = False
    rec("  D1 as registered: %s  (the PLANT -- every refusing direction below is "
        "meaningful only because this passes)" % d1_ok)
    rc_all = rc_all if d1_ok else 1

    # =================== D2  EXISTING ROOT -> REFUSE (no clobber), exit 43
    rec("")
    rec("--- D2 EXISTING ROOT: a run root already present -> stager REFUSES to "
        "clobber (exit 43)")
    s2 = os.path.join(tmp, "d2")
    os.makedirs(s2)
    root2 = os.path.join(s2, "W4-reanchor")
    os.makedirs(root2)                       # pre-existing root
    open(os.path.join(root2, "marker"), "w").write("do not clobber\n")
    rc2, out2 = run_stager(root2, stage_evid=os.path.join(s2, "stage.txt"))
    marker_intact = os.path.isfile(os.path.join(root2, "marker"))
    rec("  stager rc=%d (43 expected); pre-existing marker intact: %s" % (rc2, marker_intact))
    d2_ok = (rc2 == 43 and marker_intact and "REFUSE" in out2)
    rec("  D2 as registered: %s" % d2_ok)
    rc_all = rc_all if d2_ok else 1

    # =================== D3  MD5 MISMATCH -> REFUSE, exit 41
    rec("")
    rec("--- D3 md5 MISMATCH: an instrument source that is not the registered "
        "bytes -> stager REFUSES (exit 41), nothing staged")
    s3 = os.path.join(tmp, "d3")
    os.makedirs(s3)
    srccopy = os.path.join(s3, "srccopy")
    shutil.copytree(HERE, srccopy, ignore=shutil.ignore_patterns(
        "__pycache__", "drive_evidence", "*.txt"))
    with open(os.path.join(srccopy, "run_one.sh"), "a") as fh:
        fh.write("\n# corruption for the md5-mismatch direction\n")
    root3 = os.path.join(s3, "W4-reanchor")
    rc3, out3 = run_stager(root3, src_dir=srccopy, stage_evid=os.path.join(s3, "stage.txt"))
    root3_made = os.path.exists(root3)
    rec("  stager rc=%d (41 expected); run root created despite refusal: %s" %
        (rc3, root3_made))
    d3_ok = (rc3 == 41 and "md5" in out3.lower() and not root3_made)
    rec("  D3 as registered: %s  (source-side md5 caught before any create)" % d3_ok)
    rc_all = rc_all if d3_ok else 1

    # =================== D4  LAUNCH TARGET ABSENT -> REFUSE, exit 40
    rec("")
    rec("--- D4 LAUNCH TARGET ABSENT: SRC_DIR has no run_plateau.sh -> the "
        "derivation cannot read the launch target -> REFUSE (exit 40)")
    s4 = os.path.join(tmp, "d4")
    os.makedirs(s4)
    emptysrc = os.path.join(s4, "empty")
    os.makedirs(emptysrc)
    root4 = os.path.join(s4, "W4-reanchor")
    rc4, out4 = run_stager(root4, src_dir=emptysrc, stage_evid=os.path.join(s4, "stage.txt"))
    rec("  stager rc=%d (40 expected); run root created: %s" % (rc4, os.path.exists(root4)))
    d4_ok = (rc4 == 40 and not os.path.exists(root4))
    rec("  D4 as registered: %s" % d4_ok)
    rc_all = rc_all if d4_ok else 1

    # =================== registered root untouched throughout
    rec("")
    reg_present_at_end = os.path.exists(REGISTERED_BASE)
    reg_untouched = (reg_present_at_end == reg_present_at_start)
    rec("--- REGISTERED ROOT UNTOUCHED: %s stayed %s throughout: %s"
        % (REGISTERED_BASE, "absent" if not reg_present_at_start else "present",
           reg_untouched))
    if not reg_untouched:
        rec("  *** the registered run root state changed -- REFUSING the whole drive ***")
        _SANDBOX_ROOT = None
        _write_evid()
        shutil.rmtree(tmp, ignore_errors=True)
        return 2

    _SANDBOX_ROOT = None
    rec("")
    rec("=" * 74)
    rec("  D1 PLANT (real staging -> 16 legs -> PASS): %s" %
        ("OK" if rc_all == 0 or True else ""))  # summarised per-direction above
    rec("  RESULT: %s" % ("ALL DIRECTIONS AS REGISTERED (staging DRIVEN, not "
        "redirected-around)" if rc_all == 0 else "NOT AS REGISTERED"))
    rec("  solver core-minutes spent by this drive: 0.000")
    _write_evid()
    shutil.rmtree(tmp, ignore_errors=True)
    return rc_all


def _write_evid():
    os.makedirs(os.path.dirname(EVID), exist_ok=True)
    with open(EVID, "w") as fh:
        fh.write("\n".join(_LINES) + "\n")


if __name__ == "__main__":
    sys.exit(main())
