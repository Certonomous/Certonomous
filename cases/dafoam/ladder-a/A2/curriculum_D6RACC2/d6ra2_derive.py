"""D6R-ACC2 derivation: byte-derive the launcher and driver from D6R's FROZEN files
by an ENUMERATED substitution set, EVERY substitution asserted present-then-absent.
Nothing is retyped; anything not listed here is D6R's bytes."""
import hashlib, os, subprocess, sys

SRC = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R"
DST = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6RACC2"
FAIL = []

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

def apply(text, subs, tag):
    for old, new, n_expect in subs:
        n = text.count(old)
        if n != n_expect:
            FAIL.append("%s: %r occurs %d times, expected %d" % (tag, old[:70], n, n_expect))
            continue
        text = text.replace(old, new)
        # An INTENTIONAL containment (the replacement keeps the original text) is not
        # a failed substitution; only a replacement that does NOT contain the original
        # is required to have consumed every occurrence.
        if old not in new and text.count(old) != 0:
            FAIL.append("%s: %r still present after substitution" % (tag, old[:70]))
        print("  %s subst x%d  %s" % (tag, n, old.splitlines()[0][:76]))
    return text

# ---- FROZEN SOURCE IDENTITY, asserted before a byte is read -----------------
SRC_MD5 = {"d6r_run_arm.sh": "243f0f631719edf7ae354410276b3cfd"}
got = md5(os.path.join(SRC, "d6r_run_arm.sh"))
if got != SRC_MD5["d6r_run_arm.sh"]:
    print("REFUSED: d6r_run_arm.sh md5 %s != the value D6R's own driver pins (%s)"
          % (got, SRC_MD5["d6r_run_arm.sh"]))
    sys.exit(2)
print("source launcher md5 %s == the md5 d6r_chain_driver.sh:32 pins -- the frozen bytes" % got)

OLD_ROOT = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint"
NEW_ROOT = "/home/ubuntu/certonomous-runs/CURRICULUM-D6RACC2-a2-wing-multipoint"

# ============================ THE LAUNCHER ==================================
t = open(os.path.join(SRC, "d6r_run_arm.sh")).read()
L_SUBS = [
 ("# Curriculum D6R arm launcher -- multipoint cruise (CL 0.4/0.5/0.6) on D4's case.\n",
  "# Curriculum D6R-ACC2 arm launcher -- THE ACC_mp ARM OF D6R RE-RUN AT A CORRECTLY\n"
  "# ANCHORED CAP.  DERIVED BY ASSERTED SUBSTITUTION from curriculum_D6R/d6r_run_arm.sh\n"
  "# md5 243f0f631719edf7ae354410276b3cfd; the substitution set is enumerated in\n"
  "# d6ra2_derive.py and the whole delta is d6ra2_run_arm_DELTAS_from_d6r.diff.\n"
  "# Everything not in that set is D6R's bytes.\n"
  "#\n"
  "# WHY: D6R-PREREG-DEF-1.  ACC_mp's 30.0 core-min cap traced to D6's `3.0 x 3`\n"
  "# anchor, and C-94 (docs/COST_CALIBRATION.md:170) is a 45-SECOND ACCEPTANCE PRIMAL\n"
  "# on an ALREADY-DECOMPOSED tree with no adjoint and no colouring.  The registered\n"
  "# program is `compute_totals` on a COLD staged copy at np=4, which must first\n"
  "# COLOUR the Jacobian three times.  Two independent measurements put that at\n"
  "# 112.4 and 107.4 core-min -- the arm needed ~4.7x its deadline and ~3.7x its cap\n"
  "# and COULD NOT HAVE FINISHED, not on a slow day and not on an empty box.\n",
  1),
 ("ITEM=D6R\n", "ITEM=D6RACC2\n", 1),
 ("REGISTERED_BASE=" + OLD_ROOT, "REGISTERED_BASE=" + NEW_ROOT, 1),
 # G-ROOT.2: name D6R's own root first, so a mis-pointed launcher says WHOSE evidence
 # it just protected -- and D6R's preserved root is exactly the evidence at risk here.
 ('FORBIDDEN_ROOTS="/home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv\n',
  'FORBIDDEN_ROOTS="' + OLD_ROOT + '\n/home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv\n', 1),
 ("#   ACC_mp      14.7        30.0       360              24.0   9.0 x 1.6308\n",
  "#   ACC_mp     112.4       240.0      3510            2400.0   RE-ANCHORED, below\n"
  "# D6R-ACC2's ACC_mp CAP IS NOT INHERITED AND NOT A COPY-FORWARD.  Two INDEPENDENT\n"
  "# measurements of the program this arm actually runs:\n"
  "#  (a) 1685.98 s, from the run's OWN logs: 75.10 s to the first colouring MEASURED\n"
  "#      in ACC_mp's own log (`Calculating dRdW Coloring... 75.1 s`, i.e. start-up +\n"
  "#      all three primals), plus three colourings MEASURED in O_mp's log at 419.08 /\n"
  "#      425.85 / 425.61 s, plus two adjoint intervals MEASURED at 111.64 / 115.25 s\n"
  "#      and a third INTERPOLATED at 113.45 s.  x4 ranks / 60 = 112.399 core-min.\n"
  "#  (b) 107.4 core-min, from CURRICULUM-D5's ledger: ARM=ACC48 rc=0 wall_s=537\n"
  "#      ranks=4 core_min=35.8 for ONE primal+adjoint pair on this same wing at np=4;\n"
  "#      three pairs = 1611 s.  Over-counts start-up twice, so it is an upper bound\n"
  "#      on the marginal scaling and a corroboration, not the primary.\n"
  "#  The two agree to 4.65 %.  REGISTERED POINT 112.4, CAP 240.0 = 2.135x, whose\n"
  "#  deadline inverts EXACTLY: (3510 + 90) * 4 / 60 = 240.000000, and 3510 s sits\n"
  "#  BELOW rule 12's 3600 s stall convention so an arm that runs to its deadline is\n"
  "#  never itself a stall row.\n", 1),
 ("    ACC_mp)  echo 30.0 ;;\n", "    ACC_mp)  echo 240.0 ;;\n", 1),
 ('d6r_${ARM}_', 'd6ra2_${ARM}_', 3),
 ('PIDFILE="$BASE/d6r_driver.pid"', 'PIDFILE="$BASE/d6ra2_driver.pid"', 1),
 # A STRENGTHENING that can only turn a launch into a refusal: this item registers
 # EXACTLY ONE arm, so the launcher refuses every other name before any guard runs.
 ('test -n "$IMG" || { echo "ABORT usage: d6r_run_arm.sh <O_mp|ACC_mp|F_mp|REF_off> <image>"; exit 64; }\n',
  'test -n "$IMG" || { echo "ABORT usage: d6ra2_run_arm.sh ACC_mp <image>"; exit 64; }\n'
  'test "$ARM" = "ACC_mp" || { echo "ABORT D6RACC2 registers EXACTLY ONE arm, ACC_mp; got \'$ARM\'.  A second arm is a separate item."; exit 64; }\n', 1),
 ('test -n "$ARM" || { echo "ABORT usage: d6r_run_arm.sh <O_mp|ACC_mp|F_mp|REF_off> <image>"; exit 64; }\n',
  'test -n "$ARM" || { echo "ABORT usage: d6ra2_run_arm.sh ACC_mp <image>"; exit 64; }\n', 1),
]
t = apply(t, L_SUBS, "LAUNCH")
if FAIL:
    print("REFUSED:\n  " + "\n  ".join(FAIL)); sys.exit(2)
lp = os.path.join(DST, "d6ra2_run_arm.sh")
open(lp, "w").write(t)
os.chmod(lp, 0o664)
LAUNCH_MD5 = md5(lp)
print("d6ra2_run_arm.sh md5 = %s" % LAUNCH_MD5)

# ============================ THE DRIVER ====================================
d = open(os.path.join(SRC, "d6r_chain_driver.sh")).read()
D_SUBS = [
 ("# D6R chain driver -- DERIVED from curriculum_D6/d6r_chain_driver.sh @ b4ddca65\n",
  "# D6R-ACC2 driver -- ONE ARM, ACC_mp, at a correctly anchored cap.  DERIVED BY\n"
  "# ASSERTED SUBSTITUTION from curriculum_D6R/d6r_chain_driver.sh; the substitution\n"
  "# set is enumerated in d6ra2_derive.py and the whole delta is\n"
  "# d6ra2_chain_driver_DELTAS_from_d6r.diff.  The INSTRUMENTS ARE D6R'S OWN, staged\n"
  "# from curriculum_D6R/ under their frozen md5s: the PROGRAM IS UNCHANGED and only\n"
  "# the cap moved.  Original D6R header follows.\n"
  "# D6R chain driver -- DERIVED from curriculum_D6/d6r_chain_driver.sh @ b4ddca65\n", 1),
 ('LAUNCHER="$HERE/d6r_run_arm.sh"', 'LAUNCHER="$HERE/d6ra2_run_arm.sh"', 1),
 ("BASE=" + OLD_ROOT + "\n", "BASE=" + NEW_ROOT + "\n", 1),
 ('D4_CASE_DIR="$HERE/../curriculum_D4"\n',
  'D4_CASE_DIR="$HERE/../curriculum_D4"\n'
  '# THE INSTRUMENTS ARE D6R\'S, READ FROM D6R\'S OWN CASE DIRECTORY UNDER THE SAME\n'
  '# FROZEN md5s ASSERTED BELOW.  Copying them into this item would create a second\n'
  '# copy of a frozen file, which is the drift this lab records.\n'
  'D6R_CASE_DIR="$HERE/../curriculum_D6R"\n', 1),
 ("MD5_LAUNCHER=243f0f631719edf7ae354410276b3cfd", "MD5_LAUNCHER=@@LAUNCH_MD5@@", 1),
 ('PIDFILE="$BASE/d6r_driver.pid"', 'PIDFILE="$BASE/d6ra2_driver.pid"', 1),
 ('echo "ITEM=D6R" > "$BASE/ledger.txt"', 'echo "ITEM=D6RACC2" > "$BASE/ledger.txt"', 1),
 ('cp -a "$HERE/d6r_opt_runScript.py" "$HERE/d6r_fd_endpoint.py" "$HERE/d6r_extract_endpoint.py" "$HERE/d6r_ref_off.py" "$D4_CASE_DIR/d4_extract_endpoint.py"',
  'cp -a "$D6R_CASE_DIR/d6r_opt_runScript.py" "$D6R_CASE_DIR/d6r_fd_endpoint.py" "$D6R_CASE_DIR/d6r_extract_endpoint.py" "$D6R_CASE_DIR/d6r_ref_off.py" "$D4_CASE_DIR/d4_extract_endpoint.py"', 1),
 ('python3 "$HERE/d6r_aggregate_memory.py"', 'python3 "$D6R_CASE_DIR/d6r_aggregate_memory.py"', 1),
 ('test $# -ge 1 || { echo "ABORT usage: d6r_chain_driver.sh <ARM...>"; exit 64; }\n',
  'test $# -ge 1 || { echo "ABORT usage: d6ra2_chain_driver.sh ACC_mp"; exit 64; }\n'
  '# A STRENGTHENING: this item registers EXACTLY ONE arm.  Any other argument list\n'
  '# REFUSES before the launcher md5 is even read, so no second arm can be bought.\n'
  'test "$*" = "ACC_mp" || { echo "ABORT D6RACC2 registers EXACTLY the arm list [ACC_mp]; got [$*]."; exit 64; }\n', 1),
]
d = apply(d, D_SUBS, "DRIVER")
if FAIL:
    print("REFUSED:\n  " + "\n  ".join(FAIL)); sys.exit(2)
if d.count("@@LAUNCH_MD5@@") != 1:
    print("REFUSED: launcher-md5 placeholder count %d" % d.count("@@LAUNCH_MD5@@")); sys.exit(2)
d = d.replace("@@LAUNCH_MD5@@", LAUNCH_MD5)
if "@@LAUNCH_MD5@@" in d:
    print("REFUSED: placeholder survived"); sys.exit(2)
dp = os.path.join(DST, "d6ra2_chain_driver.sh")
open(dp, "w").write(d)
os.chmod(dp, 0o664)
print("d6ra2_chain_driver.sh md5 = %s" % md5(dp))

# ---- the DELTAS diffs, so the whole change is readable as a diff ------------
for a, b, out in ((os.path.join(SRC, "d6r_run_arm.sh"), lp, "d6ra2_run_arm_DELTAS_from_d6r.diff"),
                  (os.path.join(SRC, "d6r_chain_driver.sh"), dp, "d6ra2_chain_driver_DELTAS_from_d6r.diff")):
    r = subprocess.run(["diff", "-u", a, b], stdout=subprocess.PIPE, text=True)
    open(os.path.join(DST, out), "w").write(r.stdout)
    ins = sum(1 for l in r.stdout.splitlines() if l.startswith("+") and not l.startswith("+++"))
    dels = sum(1 for l in r.stdout.splitlines() if l.startswith("-") and not l.startswith("---"))
    print("%s: +%d -%d lines" % (out, ins, dels))
print("bash -n syntax:")
for p in (lp, dp):
    r = subprocess.run(["bash", "-n", p])
    print("  %s rc=%d" % (os.path.basename(p), r.returncode))
    if r.returncode != 0:
        sys.exit(2)
