#!/usr/bin/env bash
# =============================================================================
# MAAOA -- the in-container UNIT program: ONE fixed-lift trim point, np = 1,
# one cpuset core, OMP_NUM_THREADS=1 exported by the launcher.
# Governed by MAAOA_PREREGISTRATION.md. Never retries, relaxes or re-tunes;
# a trim that raises is RECORDED (rc 97) and reported as-is.
# =============================================================================
set -uo pipefail

cd /mnt/case || { echo "MAAOA_FATAL cannot cd /mnt/case"; exit 90; }
test -f /mnt/runScript.py           || { echo "MAAOA_FATAL runScript absent"; exit 91; }
test -d 0.orig                      || { echo "MAAOA_FATAL 0.orig absent"; exit 92; }
test -f constant/polyMesh/points.gz || { echo "MAAOA_FATAL mesh absent"; exit 93; }
test -n "${MAAOA_MACH:-}"           || { echo "MAAOA_FATAL MAAOA_MACH unset"; exit 94; }
test -n "${MAAOA_TMO:-}"            || { echo "MAAOA_FATAL MAAOA_TMO unset"; exit 94; }
mkdir -p /mnt/out || { echo "MAAOA_FATAL cannot mkdir /mnt/out"; exit 95; }

grep -q '"useWallFunction": False,' /mnt/runScript.py \
  || { echo "MAAOA_FATAL G-WALLTREAT: staged runScript does not carry useWallFunction False"; exit 98; }
echo "MAAOA_UNIT mach=$MAAOA_MACH U0=${MAAOA_U0:-10-incomp} tmo=$MAAOA_TMO omp=${OMP_NUM_THREADS:-UNSET} utc=$(date -u +%Y-%m-%dT%H%M%SZ)"

rm -rf 0 && cp -r 0.orig 0 || { echo "MAAOA_FATAL cannot reset 0/ from 0.orig"; exit 96; }
echo "MAAOA_COLD_START 0/ reset from 0.orig"

AOA_ALPHA0="${MAAOA_ALPHA0:-4.0}" \
MAAOA_TRIM_JSON=/mnt/out/trim.json \
timeout -k 60 "$MAAOA_TMO" \
  python /mnt/runScript.py -task trim > /mnt/out/trim.log 2>&1
RC=$?
echo "MAAOA_TRIM_RC rc=$RC log=/mnt/out/trim.log"

BCOK="$(grep -c 'BCType=nutLowReWallFunction' /mnt/out/trim.log 2>/dev/null || true)"; BCOK="${BCOK:-0}"
VAL="$(grep -c '^MAAOA_TRIM_VALUES ' /mnt/out/trim.log 2>/dev/null || true)"; VAL="${VAL:-0}"
echo "MAAOA_COUNTS trim_values_lines=$VAL walltreat_lines=$BCOK"
grep '^MAAOA_TRIM_VALUES ' /mnt/out/trim.log || true

if [ "$VAL" -ge 1 ] && [ "$RC" -eq 0 ]; then
  echo "MAAOA_POINT_COMPLETE mach=$MAAOA_MACH"
  exit 0
fi
echo "MAAOA_POINT_RECORDED_WITH_ERROR mach=$MAAOA_MACH rc=$RC values_lines=$VAL -- reported, not retried"
exit 97
