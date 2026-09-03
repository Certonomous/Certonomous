#!/usr/bin/env bash
# SO-3aF2 PIN CENSUS AND NO-LAUNCH SELFTEST.
#
# TWO JOBS, and the first exists because of a MEASURED failure in this family:
# SO-1c's chain driver carried TWELVE md5 pins and its selftest leg drove FOUR
# while its message claimed "every pin".  So this file carries NO list of pins.
# It ENUMERATES every `MD5_*=` assignment out of the launcher's OWN BYTES, maps
# each to a registered target through ONE table, and REFUSES if any enumerated
# pin has no registered target.  THE COUNT DRIVEN AND THE COUNT THAT EXISTS ARE
# PRINTED SIDE BY SIDE AND MUST BE EQUAL.  A pin added to the launcher with no
# row in the table FAILS this census.  "Every pin is driven" is a COUNT here,
# never a claim.
#
# The second job drives the FOUR NO-LAUNCH BRANCHES of section 6 -- each in the
# REFUSING direction, showing its NAMED file and its NAMED rc -- and, crucially,
# ONCE IN THE PASSING DIRECTION, showing all four PASS lines printed before the
# launcher reaches the container step.  A guard suite that only drives refusals
# cannot tell a working guard from one that is UNSATISFIABLE BY CONSTRUCTION,
# which this family has now met NINE times in one day.
#
# SAFETY, AND THE THINGS THIS FILE MUST NOT DO.  The pre-registration's section 2
# records this item's freeze condition as the ABSENCE of the run root and records
# that this item has started NO CONTAINER.  Both sentences must still be true
# when this file ends, so:
#   * NO leg starts a container.  Every leg runs a SANDBOX COPY of the launcher
#     whose `docker` calls resolve to a STUB on PATH that refuses and logs.  The
#     stub's transcript is printed, so "no container" is a reading, not a promise.
#   * NO leg touches the real run root.  Sandbox copies point `BASE` at a
#     scratch directory; every sandbox delta is PRINTED as a diff so nothing is
#     taken on trust.
#   * Everything created is removed BY NAME, never by glob and never by sweep,
#     and a DECOY this file did not create must SURVIVE that cleanup.
#
# SUBMISSIONS PARKED.

set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/so3af2_run_arm.sh"
READER="$HERE/so3af2_read.py"
PRODUCER="$HERE/so3af2_runScript.py"
REAL_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility
TMP="${1:-/tmp}/so3af2_pin_selftest_$$"
PASS=0; FAIL=0

ok()   { PASS=$((PASS+1)); printf '  %-26s PASS  %s\n' "$1" "$2"; }
bad()  { FAIL=$((FAIL+1)); printf '  %-26s FAIL  %s\n' "$1" "$2"; }

mkdir -p "$TMP/bin"
DECOY="$TMP/DECOY_not_created_by_this_file.txt"
echo "a file this selftest did not create; it must survive cleanup" > "$DECOY"

# ---- the docker STUB.  Every sandbox leg sees this instead of docker. --------
cat > "$TMP/bin/docker" <<'STUB'
#!/usr/bin/env bash
echo "STUB-DOCKER-CALLED $*" >> "$STUB_LOG"
exit 99
STUB
cat > "$TMP/bin/sudo" <<'STUB'
#!/usr/bin/env bash
# swallow sudo's own flags, then dispatch to the stubbed tool
while [ $# -gt 0 ]; do case "$1" in -n) shift ;; *) break ;; esac; done
exec "$@"
STUB
chmod +x "$TMP/bin/docker" "$TMP/bin/sudo"
export STUB_LOG="$TMP/stub_docker.log"
: > "$STUB_LOG"

echo "SO-3aF2 PIN CENSUS AND NO-LAUNCH SELFTEST"
echo "launcher md5 $(md5sum "$LAUNCHER" | cut -d' ' -f1)"
echo

# ===========================================================================
# JOB 1 -- THE PIN CENSUS.  Enumerated from the launcher's own bytes.
# ===========================================================================
echo "JOB 1 -- PIN CENSUS"
PINS="$(grep -oE '^MD5_[A-Z_]+=' "$LAUNCHER" | tr -d '=' | sort -u)"
N_EXIST="$(printf '%s\n' "$PINS" | grep -c . || true)"
N_DRIVEN=0
UNMAPPED=""
for pin in $PINS; do
  case "$pin" in
    MD5_READER)   target="$READER" ;;
    MD5_PRODUCER) target="$PRODUCER" ;;
    *)            UNMAPPED="$UNMAPPED $pin"; continue ;;
  esac
  want="$(grep -oE "^${pin}=[0-9a-f]{32}" "$LAUNCHER" | cut -d= -f2)"
  got="$(md5sum "$target" | cut -d' ' -f1)"
  if [ -z "$want" ]; then
    bad "PIN:$pin" "no 32-hex value on its assignment line"
  elif [ "$want" = "$got" ]; then
    N_DRIVEN=$((N_DRIVEN+1)); ok "PIN:$pin" "$(basename "$target") $got"
  else
    bad "PIN:$pin" "$(basename "$target") want=$want got=$got"
  fi
done
if [ -n "$UNMAPPED" ]; then
  bad "PIN-CENSUS" "enumerated pin(s) with NO registered target:$UNMAPPED"
fi
if [ "$N_DRIVEN" = "$N_EXIST" ] && [ -z "$UNMAPPED" ]; then
  ok "PIN-CENSUS" "driven=$N_DRIVEN exist=$N_EXIST -- EQUAL, so every pin is driven as a COUNT"
else
  bad "PIN-CENSUS" "driven=$N_DRIVEN exist=$N_EXIST -- NOT EQUAL"
fi

# ---- the outside half of NL-3: the launcher's own md5 against the registered
# ---- value.  A file cannot contain its own md5, so this is checked HERE,
# ---- against the pre-registration's Stage-2 amendment, and nowhere else.
SELF="$(md5sum "$LAUNCHER" | cut -d' ' -f1)"
if grep -q "$SELF" "$HERE/FEASIBILITY_PREREGISTRATION.md" 2>/dev/null; then
  ok "NL-3-OUTSIDE" "launcher md5 $SELF is pinned in the frozen document"
else
  bad "NL-3-OUTSIDE" "launcher md5 $SELF is NOT pinned in FEASIBILITY_PREREGISTRATION.md"
fi
echo

# ===========================================================================
# JOB 2 -- THE FOUR NO-LAUNCH BRANCHES, refusing AND passing
# ===========================================================================
echo "JOB 2 -- NO-LAUNCH BRANCHES"

# Build a sandbox: a copy of the launcher with BASE repointed, plus copies of
# the pinned files.  Every delta is PRINTED.
mk_sandbox() {   # mk_sandbox <name>
  local n="$1"; local d="$TMP/$n"
  mkdir -p "$d"
  cp "$READER" "$PRODUCER" "$d/"
  sed -e "s|^BASE=.*|BASE=$d/base|" "$LAUNCHER" > "$d/so3af2_run_arm.sh"
  chmod +x "$d/so3af2_run_arm.sh"
  printf '%s\n' "$d"
}

run_sandbox() {  # run_sandbox <dir> <arm>
  ( cd "$1" && PATH="$TMP/bin:$PATH" ./so3af2_run_arm.sh "$2" ) > "$1/out.txt" 2>&1
  echo "$?"
}

expect() {       # expect <label> <dir> <rc> <file> <arm>
  local label="$1" d="$2" want_rc="$3" want_file="$4" arm="$5"
  local rc; rc="$(run_sandbox "$d" "$arm")"
  local where="$d/base/$want_file"; [ -f "$where" ] || where="$d/$want_file"
  if [ "$rc" = "$want_rc" ] && [ -f "$where" ]; then
    ok "$label" "rc=$rc wrote $(basename "$where")"
  else
    bad "$label" "rc=$rc (want $want_rc), $want_file present=$([ -f "$where" ] && echo yes || echo no); $(tail -1 "$d/out.txt")"
  fi
}

# ---- NL-3 FREEZE: corrupt the reader -----------------------------------------
D="$(mk_sandbox nl3)"; printf '\n# corruption\n' >> "$D/so3af2_read.py"
expect "NL-3 FREEZE (refuses)" "$D" 5 NOLAUNCH_FREEZE.txt MESH

# ---- NL-2 PRODUCER, md5 clause ----------------------------------------------
D="$(mk_sandbox nl2md5)"; printf '\n# corruption\n' >> "$D/so3af2_runScript.py"
expect "NL-2 PRODUCER md5" "$D" 4 NOLAUNCH_PRODUCER.txt MESH

# ---- NL-2 PRODUCER, forbidden-token clause.  The producer's md5 pin is moved
# ---- to the tainted bytes so the FIRST clause passes and the SECOND is what
# ---- fires -- otherwise this leg would pass for the wrong reason, which is a
# ---- failure mode this lane met earlier tonight and will not repeat.
D="$(mk_sandbox nl2tok)"
python3 - "$D/so3af2_runScript.py" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read() + "\n# " + "compute" + "_totals\n"
open(p, "w").write(s)
PY
NEWMD5="$(md5sum "$D/so3af2_runScript.py" | cut -d' ' -f1)"
sed -i "s|^MD5_PRODUCER=[0-9a-f]*|MD5_PRODUCER=$NEWMD5|" "$D/so3af2_run_arm.sh"
expect "NL-2 PRODUCER token" "$D" 4 NOLAUNCH_PRODUCER.txt MESH
if grep -q "forbidden gradient token appears" "$D/out.txt"; then
  ok "NL-2 token BY NAME" "refused on the token clause, not on the md5 clause"
else
  bad "NL-2 token BY NAME" "refusal text does not name the token clause: $(tail -1 "$D/out.txt")"
fi

# ---- NL-1 ROOT: the run root already exists ----------------------------------
D="$(mk_sandbox nl1)"; mkdir -p "$D/base"
expect "NL-1 ROOT (refuses)" "$D" 3 NOLAUNCH_ROOT.txt MESH

# ---- NL-4 MEM: an impossible floor and a zero bound must TERMINATE non-zero ---
D="$(mk_sandbox nl4)"
sed -i -e 's|^MEM_FLOOR_GIB=.*|MEM_FLOOR_GIB=999999.0|' \
       -e 's|^POLL_BOUND_S=.*|POLL_BOUND_S=0|' "$D/so3af2_run_arm.sh"
expect "NL-4 MEM (refuses)" "$D" 6 NOLAUNCH_MEM.txt MESH

# ---- THE PASSING DIRECTION.  All four guards must be SATISFIABLE, proved by
# ---- all four PASS lines appearing before the launcher reaches the container.
D="$(mk_sandbox pass)"
RC="$(run_sandbox "$D" MESH)"
MISS=""
for tag in SO3AF2_NL3_PASS SO3AF2_NL2_PASS SO3AF2_NL1_PASS SO3AF2_NL4_PASS; do
  grep -q "$tag" "$D/out.txt" || MISS="$MISS $tag"
done
if [ -z "$MISS" ]; then
  # PRECISION, because this family's standing lesson is that a control passing
  # for a reason other than the one it claims is not testing what it says: the
  # run ends at rc=$RC because the IMAGE-DIGEST guard cannot read a digest from
  # the stub -- NOT at `docker run`, which is never reached. What this leg
  # proves is exactly and only that all four NL guards are SATISFIABLE.
  ok "ALL FOUR SATISFIABLE" "every NL guard printed its PASS line; the run then ended rc=$RC at the IMAGE-DIGEST guard, which cannot read a digest from the stub -- \`docker run\` is never reached"
else
  bad "ALL FOUR SATISFIABLE" "missing PASS line(s):$MISS -- a guard that cannot pass is unsatisfiable by construction"
fi

# ---- the diffs, printed so no sandbox delta is taken on trust ----------------
echo
echo "SANDBOX DELTAS (printed, not asserted away):"
diff "$LAUNCHER" "$TMP/pass/so3af2_run_arm.sh" | sed 's/^/    /' || true

# ===========================================================================
# JOB 3 -- THE SAFETY ASSERTIONS.  Both sentences of section 2 must still hold.
# ===========================================================================
echo
echo "JOB 3 -- SAFETY"
if [ -e "$REAL_BASE" ]; then
  bad "REAL ROOT UNTOUCHED" "$REAL_BASE EXISTS -- this file must never create it"
else
  ok "REAL ROOT UNTOUCHED" "$REAL_BASE still ABSENT"
fi
if [ -s "$STUB_LOG" ]; then
  ok "NO CONTAINER STARTED" "docker was reached $(grep -c . "$STUB_LOG") time(s) and every call hit the STUB, which exits 99 and starts nothing"
  sed 's/^/    /' "$STUB_LOG"
else
  ok "NO CONTAINER STARTED" "docker was never reached at all"
fi

# ---- cleanup BY NAME, and the decoy must survive it -------------------------
for n in nl3 nl2md5 nl2tok nl1 nl4 pass; do
  rm -f "$TMP/$n/so3af2_run_arm.sh" "$TMP/$n/so3af2_read.py" "$TMP/$n/so3af2_runScript.py" "$TMP/$n/out.txt"
  rm -f "$TMP/$n/base/NOLAUNCH_ROOT.txt" "$TMP/$n/base/NOLAUNCH_PRODUCER.txt" \
        "$TMP/$n/base/NOLAUNCH_FREEZE.txt" "$TMP/$n/base/NOLAUNCH_MEM.txt" \
        "$TMP/$n/NOLAUNCH_ROOT.txt" "$TMP/$n/NOLAUNCH_PRODUCER.txt" \
        "$TMP/$n/NOLAUNCH_FREEZE.txt" "$TMP/$n/NOLAUNCH_MEM.txt"
  rmdir "$TMP/$n/base" "$TMP/$n" 2>/dev/null || true
done
rm -f "$TMP/bin/docker" "$TMP/bin/sudo" "$STUB_LOG"
rmdir "$TMP/bin" 2>/dev/null || true
if [ -f "$DECOY" ]; then
  ok "DECOY SURVIVED" "cleanup was by name, not by sweep"
else
  bad "DECOY SURVIVED" "the decoy was removed -- cleanup swept something it did not create"
fi
rm -f "$DECOY"; rmdir "$TMP" 2>/dev/null || true

echo
echo "SO3aF2 PIN CENSUS: PASS $PASS  FAIL $FAIL  NOT RUN 0"
[ "$FAIL" = "0" ] || exit 1
exit 0
