#!/usr/bin/env python3
"""Curriculum D6RF -- the LAUNCHER AND DRIVER guard self-test.  DRIVEN.

`d6rf_run_arm.sh` contains `sudo -n rm -rf "$WORK"`.  A launcher with a
destructive step is trusted only after its guards are **driven and shown to
abort on the case they must abort on** -- the D6RACC2 section 4 standard.  This
file drives them.

**ZERO CONTAINERS ARE CREATED.**  The census is taken before and after and both
must agree, and no invocation below can reach `docker run`: every one of them
aborts at a guard that precedes it.  The two "happy path" drives (G5, G6) are
pointed at this item's registered run root, WHICH DOES NOT EXIST, so they run
the real cap arithmetic in the real code path and then stop at the L-251 mode
check with rc 4 -- exercising the arithmetic without staging a byte.

**L-316 IS STATED RATHER THAN HOPED:** a `--selftest` proves the instrument it
drives, never the case.  What this file proves is that the launcher's guards
fire, that its cap identity is the registered one when the real code computes
it, that its one recursive remove cannot escape the arm directory, that every
guard precedes it, and that the units gate is present at BOTH of its call
sites.  It proves nothing about whether `F_mp` converges.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAUNCHER = os.path.join(HERE, "d6rf_run_arm.sh")
DRIVER = os.path.join(HERE, "d6rf_chain_driver.sh")
D6R_ROOT = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint"
D4_ROOT = "/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin"
REG_ROOT = "/home/ubuntu/certonomous-runs/CURRICULUM-D6RF-a2-wing-multipoint-fd"
IMG = "dafoam-idwarp-rot:v1"

REG_CAPS = {"F_mp": 480.0, "REF_off": 190.0}
REG_TMO = {"F_mp": 7110, "REF_off": 2760}
FRAME_ALLOWANCE_S = 90
RANKS = 4
ITEM_CEILING = 670.0

OK, FAIL = [], []


def rec(label, good, detail=""):
    print("  %-62s %s" % (label, "PASS" if good else "FAIL"))
    if detail:
        print("        %s" % detail[:200])
    (OK if good else FAIL).append(label)
    return good


def census():
    r = subprocess.run(["sudo", "-n", "docker", "ps", "--format", "{{.Names}}"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return sorted(x for x in r.stdout.decode().split() if x)


def run_launcher(arm, base=None):
    env = dict(os.environ)
    if base is not None:
        env["BASE"] = base
    r = subprocess.run(["bash", LAUNCHER] + ([arm, IMG] if arm else []),
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                       cwd=HERE)
    return r.returncode, r.stdout.decode(errors="replace")


def run_driver(args):
    r = subprocess.run(["bash", DRIVER] + args, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, cwd=HERE)
    return r.returncode, r.stdout.decode(errors="replace")


def exec_lines(path):
    """(1-based line no, text) for lines that are not blank and not comments."""
    out = []
    with open(path) as fh:
        for i, line in enumerate(fh, 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            out.append((i, line.rstrip("\n")))
    return out


def md5_of(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def main():
    print("D6RF LAUNCHER/DRIVER GUARD SELFTEST -- driven, zero containers\n")
    before = census()
    print("  container census BEFORE: %d [%s]\n" % (len(before), ",".join(before)))

    # =====================================================================
    print("A. G-ROOT -- the launcher pointed somewhere it must never write")
    rc, out = run_launcher("F_mp", D6R_ROOT)
    rec("U1  BASE = D6R PRESERVED run root -> ABORT rc 3", rc == 3,
        (out.strip().splitlines() or [""])[0])
    rec("U2  ...and the abort NAMES D6R's root and what it protects",
        D6R_ROOT in out and "2,257.933" in out and "READ-ONLY SOURCE" in out)
    rc, out = run_launcher("F_mp", D4_ROOT)
    rec("U3  BASE = D4's run root -> ABORT rc 3", rc == 3, out.strip().splitlines()[0])
    rec("U4  ...and the abort NAMES the root it just protected", D4_ROOT in out and "THE ROOT JUST PROTECTED" in out)
    rc, out = run_launcher("F_mp", os.path.join(D6R_ROOT, "O_mp", os.pardir))
    rec("U5  a `..` traversal back to D6R's root -> ABORT rc 3 (realpath -m)",
        rc == 3, out.strip().splitlines()[0])
    rc, out = run_launcher("F_mp", "/home/ubuntu/certonomous-runs")
    rec("U6  BASE = the runs directory itself -> ABORT rc 3", rc == 3,
        out.strip().splitlines()[0])

    # =====================================================================
    print("\nB. THE ARM GUARD IS AN EQUALITY, NOT A PREFIX MATCH")
    for bad in ("F_m", "F_mpX", "REF_of", "REF_offX", "O_mp", "ACC_mp"):
        rc, out = run_launcher(bad, REG_ROOT)
        rec("U7  arm '%s' -> ABORT rc 64" % bad,
            rc == 64 and "not one of this item's two REGISTERED arms" in out)
    rc, out = run_launcher(None, REG_ROOT)
    rec("U8  no arguments -> ABORT rc 64", rc == 64)

    # =====================================================================
    print("\nC. THE CAP IDENTITY -- computed by the REAL code, not read off")
    print("     (pointed at the registered run root, WHICH DOES NOT EXIST, so")
    print("      each drive stops at the L-251 mode check with rc 4)")
    rec("U9  the registered run root really is absent", not os.path.exists(REG_ROOT),
        REG_ROOT)
    for arm in ("F_mp", "REF_off"):
        rc, out = run_launcher(arm, REG_ROOT)
        m = re.search(r"D6RF_CAP_FRAME arm=%s registered_core_min=(\S+) ranks=(\d+) "
                      r"deadline_in_container_s=(\d+) frame_allowance_s=(\d+) "
                      r"kill_grace_s=(\d+) worst_case_host_core_min=(\S+)" % arm, out)
        if not rec("U10 %-7s the launcher printed its own cap frame" % arm, bool(m)):
            continue
        cap, ranks, tmo, fa, kg, back = (float(m.group(1)), int(m.group(2)),
                                         int(m.group(3)), int(m.group(4)),
                                         int(m.group(5)), float(m.group(6)))
        rec("U11 %-7s cap == the registered %.1f" % (arm, REG_CAPS[arm]),
            cap == REG_CAPS[arm], "got %.1f" % cap)
        rec("U12 %-7s TMO == the registered %d s" % (arm, REG_TMO[arm]),
            tmo == REG_TMO[arm], "got %d" % tmo)
        rec("U13 %-7s TMO > 0 (the D19T identity)" % arm, tmo > 0, "TMO=%d" % tmo)
        rec("U14 %-7s frame allowance is 90, kill grace 60, ranks 4" % arm,
            fa == FRAME_ALLOWANCE_S and kg == 60 and ranks == RANKS)
        rec("U15 %-7s the inversion returns the cap exactly" % arm,
            abs(back - cap) < 1e-9 and abs((tmo + fa) * ranks / 60.0 - cap) < 1e-9,
            "(%d+%d)*%d/60 = %.6f" % (tmo, fa, ranks, (tmo + fa) * ranks / 60.0))
        alt = int(cap * 60.0 / ranks) - 60          # the A1/D19 convention
        rec("U16 %-7s TMO also > 0 under CAP_MARGIN_S = 60 (%d s)" % (arm, alt),
            alt > 0)
        rec("U17 %-7s the drive stopped at the L-251 mode check, rc 4" % arm,
            rc == 4 and "L-251 run root mode" in out, "rc=%d" % rc)
        anchor_wall = {"F_mp": 2335.5, "REF_off": 901.0}[arm]
        rec("U18 %-7s TMO >= 1.5 x the measured-anchor wall (%.1f s)"
            % (arm, anchor_wall), tmo >= 1.5 * anchor_wall,
            "ratio %.3f" % (tmo / anchor_wall))

    # =====================================================================
    print("\nD. THE DESTRUCTIVE STEP -- one, guarded, and it cannot escape")
    lines = exec_lines(LAUNCHER)
    rm_r = [(n, t) for n, t in lines if re.search(r"\brm\s+(-[A-Za-z]*r[A-Za-z]*)\s", t)]
    rm_rf_work = [(n, t) for n, t in rm_r if 'sudo -n rm -rf "$WORK"' in t]
    rec("U19 exactly ONE `sudo -n rm -rf \"$WORK\"` in executable code",
        len(rm_rf_work) == 1,
        "at line %s" % (rm_rf_work[0][0] if rm_rf_work else "NONE"))
    escapes = [(n, t) for n, t in rm_r
               if not re.search(r'rm\s+-[A-Za-z]*r[A-Za-z]*\s+.*"\$WORK', t)
               and not re.search(r'rm\s+-[A-Za-z]*r[A-Za-z]*\s+"\$d"', t)]
    rec("U20 EVERY executable recursive remove targets \"$WORK...\" or the "
        "$d inside the swept loop", not escapes,
        "; ".join("line %d: %s" % (n, t.strip()[:60]) for n, t in escapes))
    # a commented occurrence is COUNTED AND NAMED, never hidden -- the D6RACC2
    # U15/U16 false positive was a detector that could not tell a statement from
    # prose about a statement.
    commented = []
    with open(LAUNCHER) as fh:
        for i, line in enumerate(fh, 1):
            if line.strip().startswith("#") and re.search(r"\brm\s+-rf\b", line):
                commented.append(i)
    print("        commented `rm -rf` occurrences (counted, not hidden): %s"
          % (commented or "none"))
    first_destructive = min(n for n, _ in rm_r) if rm_r else None
    guard_names = ["G-ROOT.2a", "G-ROOT.1", "G-ROOT.2", "G-ROOT.3", "G-ROOT.5",
                   "D6RF_CAP_FRAME", "L-251 run root mode", "G-ROW"]
    guard_lines = {}
    for n, t in lines:
        for g in guard_names:
            if g in t and g not in guard_lines:
                guard_lines[g] = n
    missing = [g for g in guard_names if g not in guard_lines]
    rec("U21 every named guard is present in executable code", not missing,
        "missing: %s" % missing)
    last_guard = max(guard_lines.values()) if guard_lines else None
    rec("U22 EVERY guard precedes the first destructive step "
        "(guards end line %s, first remove line %s) -- both RECOMPUTED here"
        % (last_guard, first_destructive),
        first_destructive is not None and last_guard is not None
        and last_guard < first_destructive)
    docker_run = [n for n, t in lines if "docker run -d" in t]
    rec("U23 the first `docker run` (line %s) follows every guard and the "
        "destructive step" % (docker_run[0] if docker_run else None),
        bool(docker_run) and docker_run[0] > first_destructive)

    # =====================================================================
    print("\nE. THE UNITS GATE AT BOTH CALL SITES (CLAUDE.md rule 14)")
    src = open(LAUNCHER).read()
    rec("U24 call site 1: the launcher runs the gate HOST-side at staging",
        'python3 "$WORK/d6rf_units_assert.py" "$WORK/$DVFILE"' in src)
    rec("U25 call site 1 refuses with the DISTINCT rc 7",
        re.search(r"ABORT UNITS \(call site 1, host\)[\s\S]{0,400}?exit 7", src)
        is not None)
    cmds = re.findall(r'CMD="([^"]+)"', src)
    armcmds = [c for c in cmds if "mpirun" in c]
    rec("U26 both arm commands exist", len(armcmds) == 2, "found %d" % len(armcmds))
    rec("U27 call site 2: the gate sits BETWEEN the wrapper and the mpirun in "
        "BOTH arm commands",
        all(re.search(r"endpoint_physical\.py[^&]*&&[^&]*d6rf_units_assert\.py"
                      r"[^&]*&&[^&]*mpirun", c) for c in armcmds))
    rec("U28 the launcher REFUSES an arm command that lacks the gate",
        "call site 2 is missing (rule 14)" in src)
    rec("U29 the in-container refusal rc 77 is NAMED on the ledger, not left bare",
        "D6RF_UNITS_REFUSAL_IN_CONTAINER" in src and "rc=77" in src)

    # =====================================================================
    print("\nF. THE TIME-DIRECTORY SWEEP -- the REAL function, on REAL names")
    fn = re.search(r"(  is_time_dir\(\) \{[\s\S]*?\n  \})", src)
    if rec("U30 the `is_time_dir` function was extracted from the launcher",
           fn is not None):
        body = fn.group(1)
        probe = os.path.join(D6R_ROOT, "O_mp", "mp04", "processor0")
        names = sorted(os.listdir(probe)) if os.path.isdir(probe) else []
        script = (body + "\nfor n in \"$@\"; do if is_time_dir \"$n\"; then "
                  "echo \"SEL $n\"; else echo \"KEEP $n\"; fi; done\n")
        r = subprocess.run(["bash", "-c", script, "x"] + names + ["0.orig", "1000"],
                           stdout=subprocess.PIPE)
        res = dict((l.split(" ", 1)[1], l.split(" ", 1)[0])
                   for l in r.stdout.decode().strip().splitlines())
        rec("U31 `0` is KEPT (the initial fields)", res.get("0") == "KEEP")
        rec("U32 `0.orig` is KEPT -- a bare `0.*` glob would have DELETED it",
            res.get("0.orig") == "KEEP")
        rec("U33 `constant` is KEPT", res.get("constant") == "KEEP")
        rec("U34 `1000` is SELECTED for the sweep", res.get("1000") == "SEL")
        sel = [n for n, v in res.items() if v == "SEL" and n in names]
        rec("U35 exactly 76 of D6R's own %d entries under mp04/processor0 are "
            "swept (75 pseudo-times + the endTime)" % len(names), len(sel) == 76,
            "selected %d" % len(sel))
        rec("U36 the launcher asserts 0/, 0.orig/ and processor*/0/ SURVIVED",
            "0.orig was dropped" in src and "processor0/0/U was dropped" in src)

    # =====================================================================
    print("\nG. THE FROZEN PINS")
    rec("U37 the driver's pinned launcher md5 == the launcher on disk",
        ("MD5_LAUNCHER=%s" % md5_of(LAUNCHER)) in open(DRIVER).read(),
        md5_of(LAUNCHER))
    pins = dict(re.findall(r"^(MD5_[A-Z0-9_]+)=([0-9a-f]{32})", src, re.M))
    files = {"MD5_RUNSCRIPT6": "../curriculum_D6R/d6r_opt_runScript.py",
             "MD5_FD": "../curriculum_D6R/d6r_fd_endpoint.py",
             "MD5_EXTRACT6": "../curriculum_D6R/d6r_extract_endpoint.py",
             "MD5_REFOFF": "../curriculum_D6R/d6r_ref_off.py",
             "MD5_EXTRACT4": "../curriculum_D4/d4_extract_endpoint.py",
             "MD5_RUNSCRIPT4": "../curriculum_D4/d4_opt_runScript.py",
             "MD5_LOCUS4": "../curriculum_D4/d4_endpoint_locus.py",
             "MD5_PHYS4": "../curriculum_D4/d4_endpoint_physical.py",
             "MD5_LOCUS6": "d6rf_endpoint_locus.py",
             "MD5_PHYS6": "d6rf_endpoint_physical.py",
             "MD5_UNITS": "d6rf_units_assert.py"}
    bad = []
    for k, rel in files.items():
        p = os.path.abspath(os.path.join(HERE, rel))
        if not os.path.isfile(p) or pins.get(k) != md5_of(p):
            bad.append(k)
    rec("U38 every staged-instrument md5 pinned in the launcher matches the "
        "file it names (%d pins)" % len(files), not bad, "mismatched: %s" % bad)
    rec("U39 the D4 history md5 pin matches the artefact on disk",
        pins.get("MD5_D4_HST") == md5_of(os.path.join(D4_ROOT, "O", "OptView.hst")))
    rec("U40 the reference-mesh md5 pin matches base AND all three mp trees",
        all(pins.get("MD5_REF_MESH")
            == md5_of(os.path.join(D6R_ROOT, "O_mp", mp, "constant", "polyMesh",
                                   "points.gz"))
            for mp in ("mp04", "mp05", "mp06")))
    rec("U41 no stale predecessor cap survives in the launcher",
        not re.search(r"echo (2900\.0|30\.0|300\.0|40\.0|2000\.0)\b", src))
    rec("U42 the caps in the file are exactly 480.0 and 190.0",
        "F_mp)    echo 480.0 ;;" in src and "REF_off) echo 190.0 ;;" in src)

    # =====================================================================
    print("\nH. THE DRIVER")
    dsrc = open(DRIVER).read()
    rec("U43 the item ceiling is 670.0 == 480.0 + 190.0",
        ("ITEM_CEILING_CORE_MIN=%s" % ITEM_CEILING) in dsrc
        and abs(sum(REG_CAPS.values()) - ITEM_CEILING) < 1e-9)
    rec("U44 cumulative spend is asserted BEFORE every arm",
        "D6RF_SPEND_CENSUS" in dsrc and "ABORT ITEM CEILING" in dsrc)
    fn = re.search(r"(spent_core_min\(\) \{[\s\S]*?\n\})", dsrc)
    if rec("U45 the `spent_core_min` reader was extracted from the driver",
           fn is not None):
        # DRIVEN ON A REAL LEDGER LINE: the regex must NOT also match
        # `cap_core_min=`, or every arm would look like it had spent its cap.
        import tempfile
        td = tempfile.mkdtemp(prefix="d6rf_guard_")
        with open(os.path.join(td, "ledger.txt"), "w") as fh:
            fh.write("ITEM=D6RF\n")
            fh.write(open(os.path.join(D6R_ROOT, "ledger.txt")).read()
                     .splitlines()[2] + "\n")
        body = fn.group(1).replace("$BASE", td)
        r = subprocess.run(["bash", "-c", body + "\nspent_core_min\n"],
                           stdout=subprocess.PIPE)
        got = r.stdout.decode().strip()
        rec("U46 it reads D6R's real O_mp row as 2257.933, NOT its 2900.0 cap",
            got == "2257.933", "got %s" % got)
    for bad_arm in ("O_mp", "ACC_mp", "F_m"):
        rc, out = run_driver([bad_arm])
        rec("U47 the driver refuses arm '%s' -> rc 64" % bad_arm,
            rc == 64 and "not one of this item's two REGISTERED arms" in out)
    rec("U48 the driver's H5 and aggregate gates HOLD, never refuse",
        "H5_HOLD" in dsrc and "AGGREGATE_HOLD" in dsrc
        and "holding_not_refusing" in dsrc and "RE-FIREABLE" in dsrc)
    rec("U49 rc is captured INSIDE the wrapper, from the launcher's own exit",
        "rc=$?" in dsrc and "docker_inspect_ExitCode" in dsrc
        and "setsid" not in dsrc.split("# ---- ROOT STAGING")[1])
    rec("U50 the ledger row carries every field the supervisor named",
        all(f in src for f in ("ARM=$ARM", "rc=$rc", "wall_s=$WALL",
                               "ranks=$RANKS", "core_min=$CORE_MIN",
                               "memavail_GiB=$MEMAVAIL_GIB",
                               "inspect(exit,oomkilled)=[$INSPECT]",
                               "log=$(basename \"$LOG\")")))
    rec("U51 `docker inspect` is read BEFORE `docker rm`",
        src.index("State.ExitCode") < src.index("docker rm")
        and src.index("State.FinishedAt") < src.index("docker rm"))

    # =====================================================================
    after = census()
    print("\n  container census AFTER: %d [%s]" % (len(after), ",".join(after)))
    rec("U52 CONTAINER CENSUS BEFORE == AFTER (zero containers created)",
        before == after, "before=%s after=%s" % (before, after))
    rec("U53 no container carrying this item's prefix exists",
        not [c for c in after if c.startswith("d6rf_")])
    rec("U54 the registered run root is STILL absent after every drive",
        not os.path.exists(REG_ROOT), REG_ROOT)

    print("\nD6RF_GUARD_SELFTEST %d/%d PASS" % (len(OK), len(OK) + len(FAIL)))
    if FAIL:
        print("FAILED: %s" % ", ".join(FAIL))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
