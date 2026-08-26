#!/usr/bin/env bash
# d8r_driver_names_selftest.sh -- D8R ADDENDUM 1 (D8R-DRIVER-DEF-1, found by the supervisor's
# check 1 on the frozen driver: `d8r_chain_driver.sh` copied and md5-asserted `d8r_xf.py`
# while the instrument is `d8r_of.py`, so the FIRST fire would have aborted at staging with
# `ABORT copy instruments`, exit 4, zero compute).  The G-ROOT.5 selftest never reaches the
# driver's staging copy, so it could not see it.  This leg does, statically, with no root:
#   (1) `bash -n` the driver;
#   (2) every "$HERE/<file>" the driver COPIES must exist in the case directory;
#   (3) every "$BASE/d8r_<file>" the driver md5-ASSERTS must be among the files it copies;
#   (4) every "$BASE/d8r_*.py" the LAUNCHER md5-asserts must be among the files the driver copies;
#   (5) PLANTED CONTROL (rule 3): a scratch copy of the driver naming `d8r_bogus.py` must FAIL
#       this leg -- a zero from a reader not shown able to see a non-zero is not evidence.
# usage: bash d8r_driver_names_selftest.sh [<driver path>]   (default: the frozen driver beside it)
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DRV="${1:-$HERE/d8r_chain_driver.sh}"; LNC="$HERE/d8r_run_arm.sh"
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "D8R DRIVER-NAMES SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) driver=$DRV md5=$(md5sum "$DRV" | cut -d' ' -f1)"
if bash -n "$DRV" 2>/dev/null; then ok "(1) bash -n $(basename "$DRV")"; else bad "(1) bash -n $(basename "$DRV") FAILED"; fi
COPIED=$(grep -o '"\$HERE/[A-Za-z0-9_.-]*"' "$DRV" | tr -d '"' | sed 's#^\$HERE/##' | sort -u)
test -n "$COPIED" || bad "(2) the driver copies NOTHING from \$HERE -- the extraction saw no name"
for n in $COPIED; do
  if [ -f "$HERE/$n" ]; then ok "(2) driver copies $n -> exists in the case directory"; else bad "(2) driver copies $n -> ABSENT from the case directory"; fi
done
ASSERTED=$(grep -o '\$BASE/d8r_[A-Za-z0-9_.-]*' "$DRV" | sed 's#^\$BASE/##' | sort -u)
for n in $ASSERTED; do
  case "$n" in d8r_driver.pid) continue ;; esac
  if echo "$COPIED" | grep -qx "$n"; then ok "(3) driver md5-asserts $n, which it also copies"; else bad "(3) driver md5-asserts $n but NEVER copies it (ABSENT at staging)"; fi
done
LNAMES=$(grep -o '\$BASE/d8r_[A-Za-z0-9_.-]*\.py' "$LNC" | sed 's#^\$BASE/##' | sort -u)
for n in $LNAMES; do
  if echo "$COPIED" | grep -qx "$n"; then ok "(4) launcher stages $n, which the driver copies"; else bad "(4) launcher stages $n but the driver NEVER copies it"; fi
done
if [ -z "${D8R_NAMES_PLANTED:-}" ]; then
  T=$(mktemp -d)
  sed 's/d8r_of\.py/d8r_bogus.py/g' "$DRV" > "$T/driver_planted.sh"
  out=$(D8R_NAMES_PLANTED=1 bash "$0" "$T/driver_planted.sh" 2>&1); prc=$?
  if [ "$prc" -ne 0 ] && echo "$out" | grep -q "ABSENT"; then ok "(5) PLANTED CONTROL: a driver naming d8r_bogus.py FAILS this leg (rc=$prc): $(echo "$out" | grep ABSENT | head -1 | cut -c1-110)"; else bad "(5) PLANTED CONTROL did not fire (rc=$prc)"; fi
  rm -rf "$T"
fi
echo "D8R DRIVER-NAMES SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
