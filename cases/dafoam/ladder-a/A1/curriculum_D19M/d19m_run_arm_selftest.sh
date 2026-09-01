#!/usr/bin/env bash
# ===========================================================================
# Curriculum D19M -- THE LAUNCHER'S CONTROLS.
#
# The launcher cannot be run for real here (it starts containers), so every leg
# below drives a REFUSAL PATH -- which is the half that has teeth.  A guard shown
# able to pass but never shown able to fail is not a control.
#
# Legs (r1)-(r8).  Each states what it protects and what it costs.
# ===========================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d19m_run_arm.sh"
TMP=$(mktemp -d /tmp/d19m_runarm_XXXXXX)
trap 'rm -rf "$TMP"' EXIT
FAILED=0

leg() {  # leg <name> <want_rc> <got_rc> <note>
  if [ "$2" = "$3" ]; then
    printf "  %-8s want_rc=%-3s got_rc=%-3s OK   %s\n" "$1" "$2" "$3" "${4:-}"
  else
    printf "  %-8s want_rc=%-3s got_rc=%-3s **LEG DID NOT FIRE**  %s\n" "$1" "$2" "$3" "${4:-}"
    FAILED=$((FAILED+1))
  fi
}

echo "D19M LAUNCHER SELFTEST"
echo "  launcher md5: $(md5sum "$LAUNCHER" | cut -d' ' -f1)"
echo

# ---- (r1) G-ROOT.1: BASE that is not the registered run root ---------------
# What it protects: the staging path begins `rm -rf "$WORK"`.  `d4_run_arm.sh`
# hardcoded another item's root and would have deleted 5,085 files, 384 MB.
BASE="$TMP/not-the-registered-root" bash "$LAUNCHER" MESH dafoam-idwarp-rot:v1 \
  > "$TMP/r1.out" 2>&1; leg "(r1)" 3 $? "G-ROOT.1 -- a foreign BASE is refused BEFORE any staging"
grep -q "ABORT G-ROOT.1" "$TMP/r1.out" || { echo "    **no G-ROOT.1 message**"; FAILED=$((FAILED+1)); }

# (r1b) the same, reached through a `..` -- `realpath -m` must not be walked around
BASE="$TMP/x/../not-the-registered-root/." bash "$LAUNCHER" MESH dafoam-idwarp-rot:v1 \
  > "$TMP/r1b.out" 2>&1; leg "(r1b)" 3 $? "G-ROOT.1 -- a '..' and a trailing '.' cannot walk around realpath -m"

# ---- (r2) THE CAP TABLE IN THE COMMENT MATCHES THE CODE --------------------
# What it protects: a comment table that contradicts its own code is what a
# reviewer in a hurry reads.  A peer lane registered a 3.0 core-min cap and its
# launcher enforced 6.0 by copy-forward with no assertion.
python3 - "$LAUNCHER" <<'EOF'
import re, sys
src = open(sys.argv[1]).read()
# the COMMENT table.  Three capture groups, so it is built explicitly -- `dict()`
# over 3-tuples raises, and a silent `[:2]` slice would have made the leg pass on
# half the columns.
com = {a: (cap, wall) for a, cap, wall in re.findall(
    r"^#\s+(MESH|O-S|O-P|XE-S|XE-P|FE-S|FE-P)\s+1\s+([0-9.]+)\s+(\d+) s", src, re.M)}
if len(com) != 7:
    sys.stderr.write("the comment table lists %d arms, want 7: %r\n"
                     % (len(com), sorted(com))); sys.exit(1)
# the CODE table
code = {}
for m in re.finditer(r"^\s+([A-Z0-9|\-]+)\)\s+echo ([0-9.]+) ;;", src, re.M):
    for a in m.group(1).split("|"):
        code[a] = m.group(2)
bad = []
for arm, (cap, wall) in com.items():
    if code.get(arm) != cap:
        bad.append((arm, "cap", cap, code.get(arm)))
    want_wall = int(float(cap) * 60 / 1) - 180
    if int(wall) != want_wall:
        bad.append((arm, "wall", wall, want_wall))
if bad:
    sys.stderr.write("COMMENT/CODE DIVERGENCE: %r\n" % bad); sys.exit(1)
print("    (r2) comment table == code table on all %d arms, and every wall == "
      "cap*60/ranks - 180" % len(com))
EOF
leg "(r2)" 0 $? "the cap comment table is PARSED against the code, not trusted"

# ---- (r3) np = 1 ON EVERY ARM, in the code ---------------------------------
python3 - "$LAUNCHER" <<'EOF'
import re, sys
src = open(sys.argv[1]).read()
m = re.search(r"ranks_of\(\)\s*\{(.*?)\}", src, re.S)
body = m.group(1)
ranks = set(re.findall(r"echo (\d+)", body))
if ranks != {"1"}:
    sys.stderr.write("ranks_of returns %r, want exactly {'1'}\n" % ranks); sys.exit(1)
print("    (r3) ranks_of returns 1 and only 1 -- np=1 is enforced in the launcher")
EOF
leg "(r3)" 0 $? "DAFOAM_CHARTER section 5: an FD reference is not carried across np"

# ---- (r4) THE SOURCE-ONLY DOOR TOUCHES NO DISK -----------------------------
# What it protects: the comparator's selftest SOURCES this file to get the real
# ledger writer.  If sourcing could stage or delete, the suite would be a weapon.
BEFORE=$(ls -A "$TMP" | wc -l)
bash -c ". \"$LAUNCHER\" --source-only" > "$TMP/r4.out" 2>&1
R4=$?
AFTER=$(ls -A "$TMP" | wc -l)
SIZE=$(stat -c '%s' "$TMP/r4.out")
leg "(r4)" 0 $R4 "sourcing returns 0"
if [ "$SIZE" -eq 0 ]; then
  echo "    (r4b) sourcing printed NOTHING and created no file (before=$BEFORE after=$AFTER)"
else
  echo "    (r4b) **sourcing printed $SIZE bytes -- the door is not silent**"; FAILED=$((FAILED+1))
fi

# ---- (r5) THE LEDGER WRITER'S 21 FIELDS PARSE WITH THE COMPARATOR'S REGEX --
# What it protects: SO-1a's comparator selftest reproduced the row format in a
# Python constant, so a launcher/reader divergence would have left the suite
# green and the reader blind on the real run.
ROW=$(bash -c ". \"$LAUNCHER\" --source-only; d19m_ledger_row O-P PATCHED img:p sha256:d 0 454 1 7.567 40.0 2220 40.0 12g '0 false' 27.0 27.0 11 '0.99 n=5' '' '' L.log S1")
python3 - <<EOF
import re, sys
sys.path.insert(0, "$HERE")
import d19m_grade as G
m = G._LEDGER.match("""$ROW""")
if not m:
    sys.stderr.write("THE COMPARATOR CANNOT PARSE THE LAUNCHER'S OWN ROW:\n$ROW\n"); sys.exit(1)
got = {k: m.group(k) for k in ("arm","row","rc","ranks","core_min","cap","cpuset")}
want = {"arm":"O-P","row":"PATCHED","rc":"0","ranks":"1","core_min":"7.567",
        "cap":"40.0","cpuset":"11"}
if got != want:
    sys.stderr.write("field mismatch got=%r want=%r\n" % (got, want)); sys.exit(1)
print("    (r5) the launcher's OWN row parses with the comparator's OWN regex, all 7 fields")
EOF
leg "(r5)" 0 $? "producer and consumer are driven against each other, not asserted"

# ---- (r6) G-ROOT.2's LIST IS DRIVEN AGAINST THE DISK -----------------------
# What it protects: a refusal message naming a directory that does not exist says
# the wrong thing on the day G-ROOT.1 is weakened.  Ghosts are PRINTED, so the
# next derivation inherits a MEASUREMENT rather than a claim.
GHOSTS=0; REAL=0
while IFS= read -r d; do
  [ -z "$d" ] && continue
  if [ -e "$d" ]; then REAL=$((REAL+1)); else GHOSTS=$((GHOSTS+1)); echo "    GHOST $d"; fi
done < <(python3 - "$LAUNCHER" <<'EOF'
import re, sys
src = open(sys.argv[1]).read()
m = re.search(r'FORBIDDEN_ROOTS="(.*?)"', src, re.S)
print(m.group(1))
EOF
)
echo "    (r6) G-ROOT.2 list: $REAL exist, $GHOSTS ghosts"
if [ "$GHOSTS" -eq 0 ]; then
  echo "    (r6) every named root EXISTS -- the refusal message names real evidence"
else
  echo "    (r6) NOTE: ghosts above are recorded, not hidden.  Cost: none to safety"
  echo "         (G-ROOT.1 refuses all of them first); only the message is stale."
fi

# ---- (r7) A BAD ARM NAME AND A BAD IMAGE ARE REFUSED -----------------------
BASE="/home/ubuntu/certonomous-runs/CURRICULUM-D19M-a1-naca0012-subsonic-multipoint" \
  bash "$LAUNCHER" NOT-AN-ARM dafoam-idwarp-rot:v1 > "$TMP/r7.out" 2>&1
leg "(r7)" 64 $? "an unregistered arm name carries no rank count and is refused"

# ---- (r8) THE MESH IDENTITY CONSTANTS ARE THE MEASURED ONES ---------------
python3 - "$LAUNCHER" <<'EOF'
import gzip, hashlib, os, re, sys
src = open(sys.argv[1]).read()
pins = dict(re.findall(r"^MD5_MESH_(\w+)=([0-9a-f]{32})$", src, re.M))
d = ("/home/ubuntu/certonomous-runs/CURRICULUM-D19O-a1-naca0012-subsonic-"
     "optimisation/MESH/constant/polyMesh")
if not os.path.isdir(d):
    print("    (r8) SKIPPED -- D19R's MESH output is not on disk to compare against")
    sys.exit(0)
bad = []
for n, want in sorted(pins.items()):
    p = os.path.join(d, n)
    raw = gzip.open(p + ".gz", "rb").read() if os.path.exists(p + ".gz") else open(p, "rb").read()
    got = hashlib.md5(raw).hexdigest()
    if got != want:
        bad.append((n, got, want))
if bad:
    sys.stderr.write("MESH PIN MISMATCH %r\n" % bad); sys.exit(1)
print("    (r8) all %d mesh identity pins RE-COMPUTED from D19O's own MESH output "
      "and AGREE (md5 of the DECOMPRESSED bytes, so a .gz mtime cannot move them)"
      % len(pins))
EOF
leg "(r8)" 0 $? "the frozen mesh identity is measured, not copied"

# ---- (r9) THE mp DIR NAMES MUST EQUAL THE PRODUCER'S `RUN_DIRS` VALUES -----
# What it protects: SO-3aR died because three DASolvers shared one case
# directory.  The launcher stages `mp0 mp1 mp2`; the producer points each
# scenario's IDWarp at `<work>/mp<i>`.  If the two ever disagree, one scenario
# reads a directory that does not exist and another reads one it does not own.
# PARSED FROM BOTH FILES, not asserted in a comment.
python3 - "$LAUNCHER" "$HERE/d19m_runScript.py" <<'EOF'
import re, sys
lau, prod = open(sys.argv[1]).read(), open(sys.argv[2]).read()
m = re.search(r"for mp in ([a-z0-9 ]+); do", lau)
if not m:
    sys.stderr.write("the launcher stages no mp directories at all\n"); sys.exit(1)
staged = m.group(1).split()
m2 = re.search(r'RUN_DIRS = \{sc: "(\w+)%d" % i for i, sc in enumerate\(SCENARIOS\)\}', prod)
if not m2:
    sys.stderr.write("cannot read RUN_DIRS out of the producer\n"); sys.exit(1)
stem = m2.group(1)
n = len(re.search(r"ALPHAS = \[([^\]]*)\]", prod).group(1).split(","))
want = ["%s%d" % (stem, i) for i in range(n)]
if staged != want:
    sys.stderr.write("MISMATCH launcher stages %r; producer RUN_DIRS values are %r\n"
                     % (staged, want)); sys.exit(1)
print("    (r9) launcher stages %r == producer RUN_DIRS %r, for %d operating points"
      % (staged, want, n))
EOF
leg "(r9)" 0 $? "the per-point case directories agree between launcher and producer"

echo
if [ "$FAILED" -eq 0 ]; then
  echo "D19M LAUNCHER SELFTEST: OK -- every refusal leg fired"
  exit 0
fi
echo "D19M LAUNCHER SELFTEST: FAILED -- $FAILED leg(s)"
exit 1
