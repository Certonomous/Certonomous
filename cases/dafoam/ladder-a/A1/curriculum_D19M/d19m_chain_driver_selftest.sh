#!/usr/bin/env bash
# ===========================================================================
# Curriculum D19M -- THE CHAIN DRIVER'S CONTROLS.
#
# The driver cannot be run for real here (it stages a run root and starts
# containers).  Every leg drives a REFUSAL PATH or a PURE-TEXT invariant, which
# is the half with teeth.
#
# THE SCHEMA CONTRACT IS DRIVEN, NOT ASSERTED.  Leg (c6) runs the REAL stop
# marker on a REAL grade artefact the REAL comparator wrote, then RENAMES the key
# and requires the marker to report it absent.  A schema contract that cannot
# fail is not a contract -- SO-1c refused on 2026-08-31 because its consumer read
# `gates` at the top level while its producer wrote them at `grade.gates`, and a
# 51-leg suite could not see it.
# ===========================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DRIVER="$HERE/d19m_chain_driver.sh"
MARKER="$HERE/d19m_stop_marker.sh"
TMP=$(mktemp -d /tmp/d19m_chain_XXXXXX)
trap 'rm -rf "$TMP"' EXIT
FAILED=0

leg() {
  if [ "$2" = "$3" ]; then
    printf "  %-8s want=%-22s got=%-22s OK   %s\n" "$1" "$2" "$3" "${4:-}"
  else
    printf "  %-8s want=%-22s got=%-22s **LEG DID NOT FIRE**  %s\n" "$1" "$2" "$3" "${4:-}"
    FAILED=$((FAILED+1))
  fi
}

echo "D19M CHAIN DRIVER SELFTEST"
echo "  driver md5: $(md5sum "$DRIVER" | cut -d' ' -f1)"
echo

# ---- (c1) AN UNREGISTERED ARM IS REFUSED, BEFORE ANYTHING ELSE -------------
bash "$DRIVER" MESH NOT-AN-ARM > "$TMP/c1.out" 2>&1
leg "(c1)" 64 $? "an arm outside the registered seven is refused"
grep -q "is not a registered D19M arm" "$TMP/c1.out" \
  || { echo "    **no arm-name message**"; FAILED=$((FAILED+1)); }

# ---- (c2) NO ARGUMENTS IS REFUSED -----------------------------------------
bash "$DRIVER" > "$TMP/c2.out" 2>&1
leg "(c2)" 64 $? "the driver takes its arms from argv and will not invent them"

# ---- (c3) EXISTENCE IS ASSERTED BEFORE ANY md5, IN THAT ORDER, IN THE BYTES -
# `SO2a-DRIVER-DEF-1`: an md5-agreement control over a subset reads agreement on
# every pin it holds while a dependency the frozen code executes is ABSENT.
python3 - "$DRIVER" <<'EOF'
import sys
src = open(sys.argv[1]).read()
i_exist = src.index("D19M_18_3_EXISTENCE_OK")
i_md5 = src.index("| md5sum -c -")
if not i_exist < i_md5:
    sys.stderr.write("the existence assertion does not precede the first md5 check\n")
    sys.exit(1)
print("    (c3) existence assertion at offset %d PRECEDES the first md5 at %d"
      % (i_exist, i_md5))
EOF
leg "(c3)" 0 $? "DAFOAM_CHARTER section 18.3, in the byte order of the file"

# ---- (c4) EVERY FILE THE DRIVER EXECUTES IS IN ITS OWN EXISTENCE LIST -------
# The section 18.3 CALL SITE: extract every `$HERE/`-style reference from the
# frozen driver and resolve each against the item directory.  The charter
# declares this NOT BUILT; it is built here.
python3 - "$DRIVER" "$HERE" <<'EOF'
import os, re, sys
src, here = open(sys.argv[1]).read(), sys.argv[2]
refs = set(re.findall(r'\$HERE/([A-Za-z0-9_.\-]+)', src))
listed = set(re.findall(r'^(?:LAUNCHER|GRADER|XF|AGE|STALL|AGGMEM|MARKER|RUNSCRIPT|DECOMP)'
                        r'="\$HERE/([^"]+)"', src, re.M))
missing_on_disk = sorted(r for r in refs if not os.path.exists(os.path.join(here, r)))
not_in_guard = sorted(refs - listed)
print("    (c4) %d local dependency names in the frozen driver; %d pinned+guarded"
      % (len(refs), len(listed)))
if missing_on_disk:
    sys.stderr.write("REFERENCED BUT ABSENT ON DISK: %r\n" % missing_on_disk); sys.exit(1)
if not_in_guard:
    print("    (c4) referenced but NOT in the existence guard (each must be "
          "accounted for): %r" % not_in_guard)
    # The selftests are referenced by the driver and are NOT instruments of the
    # graded path: they are DRIVEN before staging and their absence would fail
    # the selftest loop loudly.  Named rather than silently tolerated.
    allowed = {"d19m_xf_selftest.py", "d19m_grade_selftest.py"}
    stray = set(not_in_guard) - allowed
    if stray:
        sys.stderr.write("UNACCOUNTED reference(s): %r\n" % sorted(stray)); sys.exit(1)
    print("    (c4) all accounted for: the two selftests, driven before staging")
EOF
leg "(c4)" 0 $? "the section 18.3 extraction, BUILT here (the charter declares it NOT BUILT)"

# ---- (c5) NO PIN IS STILL THE FAIL-CLOSED SENTINEL -------------------------
python3 - "$DRIVER" <<'EOF'
import re, sys
src = open(sys.argv[1]).read()
unset = re.findall(r"^(MD5_\w+)=(\w*_UNSET)$", src, re.M)
if unset:
    sys.stderr.write("PIN STILL UNSET: %r -- run d19m_repin.sh\n" % unset); sys.exit(1)
pins = re.findall(r"^(MD5_\w+)=([0-9a-f]{32})$", src, re.M)
zeros = [k for k, v in pins if v == "0" * 32]
if zeros:
    sys.stderr.write("A ZEROS PIN IS A WELL-FORMED md5 AND WOULD BE COUNTED AS "
                     "REAL: %r\n" % zeros); sys.exit(1)
print("    (c5) %d pins, all well-formed, none the sentinel, none 32 zeros" % len(pins))
EOF
leg "(c5)" 0 $? "a dead sentinel of 32 zeros would be a fail-open waiting to be re-used"

# ---- (c6) THE SCHEMA CONTRACT, DRIVEN IN BOTH DIRECTIONS -------------------
# Build a REAL grade artefact with the REAL comparator, run the REAL marker on
# it, then RENAME the key and require the marker to SEE it go.
python3 - "$HERE" "$TMP" <<'EOF'
import json, os, subprocess, sys
here, tmp = sys.argv[1], sys.argv[2]
sys.path.insert(0, here)
import d19m_grade_selftest as ST
root = ST.build_root(os.path.join(tmp, "schema"))
out = os.path.join(tmp, "grade.json")
import d19m_grade as G
rc = G.main(["--root", root, "--out", out])
if rc != 0:
    sys.stderr.write("the comparator did not write an artefact (rc=%d)\n" % rc); sys.exit(1)
print("    (c6) the comparator wrote a REAL artefact: verdict=%s"
      % json.load(open(out))["verdict"])

def marker(grade):
    subprocess.run(["bash", os.path.join(here, "d19m_stop_marker.sh"), root,
                    "selftest", grade], capture_output=True, text=True)
    return json.load(open(os.path.join(root, "D19M_STOP_MARKER.json")))

m = marker(out)
if m["verdict"] is None or m["keys_absent"]:
    sys.stderr.write("GREEN LEG: the marker could not read a well-formed "
                     "artefact: %r\n" % m); sys.exit(1)
print("    (c6) GREEN -- marker read verdict=%r ceiling=%r capped_anywhere=%r"
      % (m["verdict"], m["verdict_ceiling"], m["capped_by_ceiling_anywhere"]))

# THE RED HALF: rename the key the marker reads by its literal name.
g = json.load(open(out))
g["VERDICT_RENAMED"] = g.pop("verdict")
bad = os.path.join(tmp, "grade_renamed.json")
json.dump(g, open(bad, "w"))
m2 = marker(bad)
if "verdict" not in m2["keys_absent"]:
    sys.stderr.write("RED LEG DID NOT FIRE: the marker did not notice `verdict` "
                     "was renamed: %r\n" % m2); sys.exit(1)
print("    (c6) RED   -- key renamed, marker reports keys_absent=%r" % m2["keys_absent"])
print("    (c6) a schema contract that cannot fail is not a contract")
EOF
leg "(c6)" 0 $? "the stop marker's schema contract is DRIVEN, both directions"

# ---- (c7) THE COST BLOCK PRICES THE O ARMS AT AN EXPECTED MAJOR COUNT ------
# SO-3 registered 228.59 core-min and spent 28.900 (0.126x) because its IPOPT
# arms were priced at max_iter.  This leg reads the driver's own cost block.
python3 - "$DRIVER" "$HERE" <<'EOF'
import re, sys
src = open(sys.argv[1]).read()
sys.path.insert(0, sys.argv[2])
import d19m_xf as XF
if "PRICED AT AN EXPECTED MAJOR COUNT, NOT AT max_iter" not in src:
    sys.stderr.write("the cost block does not state its pricing basis\n"); sys.exit(1)
m = re.search(r"EXPECTED_MAJOR_ROWS = (\d+)", src)
if not m or int(m.group(1)) != XF.EXPECTED_MAJOR_ROWS:
    sys.stderr.write("the cost block's expected-major figure does not match "
                     "d19m_xf.EXPECTED_MAJOR_ROWS=%d\n" % XF.EXPECTED_MAJOR_ROWS)
    sys.exit(1)
# the per-arm predictions in the driver must equal the comparator's
import d19m_grade as G
tbl = dict((a, float(c)) for a, c in
           re.findall(r"^  (MESH|O-S|XE-S|FE-S|O-P|XE-P|FE-P)\s+1\s+([0-9.]+)\s+[0-9.]+$",
                      src, re.M))
if tbl != G.PREDICTED_CORE_MIN:
    sys.stderr.write("driver cost table %r != comparator PREDICTED_CORE_MIN %r\n"
                     % (tbl, G.PREDICTED_CORE_MIN)); sys.exit(1)
print("    (c7) the driver's cost table == the comparator's PREDICTED_CORE_MIN on "
      "all 7 arms, total %.2f core-min, and max_iter=%d is the CAP"
      % (sum(tbl.values()), XF.MAX_MAJORS))
EOF
leg "(c7)" 0 $? "the estimate cannot drift between the driver and the comparator"

# ---- (c8) THE DRIVER LAUNCHES NOTHING WHEN A SELFTEST REFUSES --------------
python3 - "$DRIVER" <<'EOF'
import sys
src = open(sys.argv[1]).read()
i_self = src.index("D19M_SELFTESTS_OK")
i_stage = src.index("ROOT STAGING on the first fire only")
i_launch = src.index('bash "$LAUNCHER" "$ARM"')
if not (i_self < i_stage < i_launch):
    sys.stderr.write("the selftest gate does not precede staging and launching\n")
    sys.exit(1)
print("    (c8) selftests(%d) < staging(%d) < launch(%d): a comparator whose "
      "controls do not fire stops the chain BEFORE any compute is bought"
      % (i_self, i_stage, i_launch))
EOF
leg "(c8)" 0 $? "finding out after the arms are bought is finding out too late"

echo
if [ "$FAILED" -eq 0 ]; then
  echo "D19M CHAIN DRIVER SELFTEST: OK -- every leg fired"
  exit 0
fi
echo "D19M CHAIN DRIVER SELFTEST: FAILED -- $FAILED leg(s)"
exit 1
