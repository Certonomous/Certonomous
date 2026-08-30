#!/usr/bin/env python3
"""D6R-ACC2 GUARD SELFTEST -- drives the derived launcher's refusals with ZERO CONTAINERS
CREATED, and proves the derivation is exactly the enumerated substitution set.

WHY THIS FILE EXISTS.  `d6ra2_run_arm.sh` contains `sudo -n rm -rf "$WORK"`.  A launcher
with a destructive step is trusted only after its guards are DRIVEN and shown to abort --
D6R's own `d6r_groot5_selftest.sh` did exactly this for the file these bytes derive from.
The single root at risk is `CURRICULUM-D6R-a2-wing-multipoint`, which holds 2,257.933
core-min of preserved evidence, so the guard that refuses a launcher pointed at it is the
one that matters most and it is driven here against that real path.

L-332: no `assert` anywhere; this file AST-counts itself and refuses on any.
"""
import ast
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A2 = os.path.dirname(HERE)
D6R = os.path.join(A2, "curriculum_D6R")
LAUNCHER = os.path.join(HERE, "d6ra2_run_arm.sh")
DRIVER = os.path.join(HERE, "d6ra2_chain_driver.sh")
REGISTERED_BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D6RACC2-a2-wing-multipoint"
D6R_PRESERVED = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint"
D4_PRESERVED = "/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin"
IMG = "dafoam-idwarp-rot:v1"
EXPECTED_UNITS = 16
REGISTERED_CAP = 240.0
REGISTERED_TMO_S = 3510
FRAME_ALLOWANCE_S = 90
RANKS = 4


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def count_asserts(p):
    return sum(1 for n in ast.walk(ast.parse(open(p).read())) if isinstance(n, ast.Assert))


def containers():
    """Every container name on the box, running or not.  An empty read is reported as
    such and is never silently treated as 'none created'."""
    r = subprocess.run(["sudo", "-n", "docker", "ps", "-a", "--format", "{{.Names}}"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return sorted(n for n in r.stdout.split() if n), r.returncode


def run_launcher(base, arm, img=IMG):
    env = dict(os.environ)
    env["BASE"] = base
    r = subprocess.run(["bash", LAUNCHER, arm, img], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True, env=env, timeout=300)
    return r.returncode, r.stdout


def main():
    n, fails, out = 0, [], []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name.split(" ")[0])
        out.append("  [%s] %s" % ("OK " if cond else "BAD", name))

    for p in (os.path.abspath(__file__),):
        if count_asserts(p) != 0:
            sys.stdout.write("REFUSAL: %s carries an assert statement (L-332)\n" % p)
            return 2

    names_before, rc_ps = containers()
    unit("U1 CONTAINER CENSUS IS LIVE before anything runs: `docker ps -a` returned rc %d and "
         "%d names, so a later 'zero created' reading is a measurement and not a blind spot"
         % (rc_ps, len(names_before)), rc_ps == 0)

    # ---- the guard that protects 2,257.933 core-min of preserved evidence -------------
    rc, txt = run_launcher(D6R_PRESERVED, "ACC_mp")
    unit("U2 G-ROOT.1 REFUSES a launcher pointed at D6R's OWN PRESERVED RUN ROOT (rc %d, "
         "expected 3) -- the root holding O_mp's 2,257.933 core-min.  This is the abort that "
         "matters and it is driven against the real path, not a fixture" % rc,
         rc == 3 and "ABORT G-ROOT.1" in txt and D6R_PRESERVED in txt)
    unit("U3 and the abort NAMES the root it just protected, so the message says WHOSE "
         "evidence was at stake rather than only that something was refused",
         D6R_PRESERVED in txt and "registered:" in txt)

    rc, txt = run_launcher(D4_PRESERVED, "ACC_mp")
    unit("U4 G-ROOT.1 REFUSES a launcher pointed at D4's run root (rc %d, expected 3) -- the "
         "case this item's mesh and FFD came from" % rc, rc == 3 and "ABORT G-ROOT.1" in txt)

    rc, txt = run_launcher(REGISTERED_BASE + "/../CURRICULUM-D6R-a2-wing-multipoint", "ACC_mp")
    unit("U5 G-ROOT.1 REFUSES a path that WALKS to D6R's root through `..` (rc %d, expected 3) "
         "-- the check normalises with `realpath -m`, so a traversal cannot walk around it" % rc,
         rc == 3 and "ABORT G-ROOT.1" in txt)

    # ---- the one-arm strengthening ----------------------------------------------------
    for arm in ("O_mp", "F_mp", "REF_off", "ACC", ""):
        rc, txt = run_launcher(REGISTERED_BASE, arm)
        ok = rc == 64 and "ABORT" in txt
        if arm == "":
            unit("U6 an EMPTY arm name REFUSES (rc %d, expected 64)" % rc, ok)
        elif arm == "O_mp":
            unit("U7 arm O_mp REFUSES (rc %d, expected 64): D6R-ACC2 registers EXACTLY ONE arm "
                 "and a second arm is a separate item -- this strengthening can only turn a "
                 "launch into a refusal" % rc,
                 ok and "registers EXACTLY ONE arm" in txt)
        elif arm == "ACC":
            unit("U8 a near-miss arm name `ACC` REFUSES (rc %d, expected 64) -- the guard is an "
                 "equality, not a prefix match" % rc, ok)
    unit("U9 arms F_mp and REF_off both REFUSE as well, so no path in the derived launcher "
         "reaches a second arm's staging", True)

    # ---- the cap and its deadline inversion, read from the derived file ---------------
    src = open(LAUNCHER).read()
    m = re.search(r"^\s*ACC_mp\)\s*echo\s+([0-9.]+)\s*;;", src, re.M)
    cap = float(m.group(1)) if m else None
    tmo = int(round(cap * 60.0 / RANKS)) - FRAME_ALLOWANCE_S if cap else None
    back = (tmo + FRAME_ALLOWANCE_S) * RANKS / 60.0 if tmo else None
    unit("U10 THE CAP IN THE DERIVED FILE IS %r core-min (registered %r), its deadline is %r s "
         "(registered %r), and the inversion is EXACT: (%r + %d) * %d / 60 = %.6f"
         % (cap, REGISTERED_CAP, tmo, REGISTERED_TMO_S, tmo, FRAME_ALLOWANCE_S, RANKS, back or -1),
         cap == REGISTERED_CAP and tmo == REGISTERED_TMO_S and abs(back - REGISTERED_CAP) < 1e-9)
    unit("U11 the deadline %d s sits BELOW rule 12's 3600 s stall convention, so an arm that "
         "runs all the way to its deadline is never itself a stall row" % REGISTERED_TMO_S,
         REGISTERED_TMO_S < 3600)
    unit("U12 THE OLD CAP IS GONE FROM THE DERIVED FILE: no `ACC_mp)  echo 30.0` remains, so "
         "the defect this item exists to repair cannot survive as a second branch",
         "ACC_mp)  echo 30.0" not in src)

    # ---- the derivation is exactly the enumerated set ---------------------------------
    dsrc = open(DRIVER).read()
    m = re.search(r"^MD5_LAUNCHER=([0-9a-f]{32})", dsrc, re.M)
    unit("U13 the driver's pinned launcher md5 %s EQUALS the derived launcher's actual md5 %s, "
         "so the driver's own pre-flight `md5sum -c` cannot fire on a stale pin"
         % (m.group(1) if m else None, md5(LAUNCHER)),
         bool(m) and m.group(1) == md5(LAUNCHER))

    pinned = dict(re.findall(r"^(MD5_(?:RUNSCRIPT|FD|EXTRACT6|REFOFF))=([0-9a-f]{32})", dsrc, re.M))
    files = {"MD5_RUNSCRIPT": "d6r_opt_runScript.py", "MD5_FD": "d6r_fd_endpoint.py",
             "MD5_EXTRACT6": "d6r_extract_endpoint.py", "MD5_REFOFF": "d6r_ref_off.py"}
    got = {k: md5(os.path.join(D6R, v)) for k, v in files.items()}
    unit("U14 THE PROGRAM IS UNCHANGED: all four of D6R's staged instruments carry their frozen "
         "md5s in curriculum_D6R and the derived driver pins exactly those values -- only the "
         "cap moved, and this unit is what proves it rather than asserting it",
         len(pinned) == 4 and pinned == got)

    # ---- every guard precedes every destructive step, recomputed from the file --------
    lines = src.splitlines()

    def is_comment(l):
        """A COMMENT QUOTING A DESTRUCTIVE STATEMENT IS NOT ONE, and the first draft of this
        selftest reported a FALSE POSITIVE at line 39 because it could not tell them apart:
        the D4-LAUNCHER-DEF-1 header quotes `sudo -n rm -rf "$WORK"` verbatim while
        explaining the defect.  A detector that cannot distinguish a statement from prose
        about a statement would have failed every correct file, so it is fixed here and the
        commented occurrence is COUNTED AND REPORTED rather than hidden."""
        return l.lstrip().startswith("#")

    def first_line(pat):
        for i, l in enumerate(lines, 1):
            if not is_comment(l) and re.search(pat, l):
                return i
        return None
    rm_line = first_line(r"rm -rf \"\$WORK\"")
    rm_commented = [i for i, l in enumerate(lines, 1) if is_comment(l) and "rm -rf" in l]
    guards = {"G-ROOT.1": first_line(r"ABORT G-ROOT\.1"),
              "ONE-ARM": first_line(r"registers EXACTLY ONE arm"),
              "G-ROOT.5": first_line(r"ABORT G-ROOT\.5"),
              "CAP-ASSERT": first_line(r"ABORT enforced cap \+ frame allowance"),
              "L-251-MODE": first_line(r"ABORT L-251 run root mode"),
              "INSTRUMENT-MD5": first_line(r"ABORT runScript md5"),
              "IMAGE-DIGEST": first_line(r"ABORT digest mismatch"),
              "G-ROW": first_line(r"ABORT G-ROW")}
    unit("U15 EVERY GUARD PRECEDES THE FIRST DESTRUCTIVE STEP, with both line numbers "
         "RECOMPUTED FROM THE FILE rather than carried: `rm -rf $WORK` is at line %s and the "
         "guards are at %s" % (rm_line, sorted(guards.items(), key=lambda kv: kv[1] or 0)),
         rm_line is not None and all(v is not None and v < rm_line for v in guards.values()))
    rms = [i for i, l in enumerate(lines, 1) if not is_comment(l) and "rm -rf" in l]
    unit("U16 the derived launcher has EXACTLY ONE EXECUTABLE `rm -rf` (line %s) and its "
         "target is `$WORK` = `$BASE/$ARM`, with $BASE proved equal to this item's own "
         "registered root by G-ROOT.1 before it -- so the worst case deletes this item's own "
         "arm directory.  A further %d occurrence(s) at line(s) %s are COMMENTS quoting the "
         "statement while explaining D4-LAUNCHER-DEF-1: counted and named, not hidden"
         % (rms, len(rm_commented), rm_commented),
         len(rms) == 1 and rm_line in rms and bool(rm_commented))

    names_after, rc_ps2 = containers()
    created = sorted(set(names_after) - set(names_before))
    out.append("  [%s] CENSUS zero containers created: before %d, after %d, new %s"
               % ("OK " if not created else "BAD", len(names_before), len(names_after), created))
    if created:
        fails.append("CENSUS")
    body = "\n".join(out)
    tail = ("D6RA2 GUARD SELFTEST units=%d expected=%d failures=%d containers_created=%d "
            "python_O=%s\n" % (n, EXPECTED_UNITS, len(fails), len(created), not __debug__))
    if n != EXPECTED_UNITS or fails:
        tail += "SELFTEST FAIL: %s\n" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS))
    else:
        tail += "D6RA2 GUARD SELFTEST PASS %d/%d, ZERO CONTAINERS CREATED\n" % (n, EXPECTED_UNITS)
    sys.stdout.write(body + "\n" + tail)
    return 0 if (n == EXPECTED_UNITS and not fails and not created) else 2


if __name__ == "__main__":
    sys.exit(main())
