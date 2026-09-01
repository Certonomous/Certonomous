#!/usr/bin/env bash
# T25RF -- launch ONE arm of the UNGATED numerics feasibility probe.
#
# Registered at docs/campaigns/T-family/T25RF_FEASIBILITY_NOTE.md.
# NO GATE.  NO THRESHOLD.  NO VERDICT.  Nothing here may be cited as a result.
#
# THREE THINGS THIS SCRIPT EXISTS TO GET RIGHT:
#
#  1. THE rc IS CAPTURED INSIDE THE DETACHED WRAPPER, NEVER AROUND `setsid`.
#     `setsid timeout cmd` EXITS 0 FOR EVERY OUTCOME, so an rc read from the
#     setsid line is the shape of a false clean.  The solver's own `$?` is
#     captured on the line after it runs, inside the same shell that ran it.
#
#  2. `0/module/T` IS TOUCHED LAST, immediately before the solver starts, and
#     nothing is written into the case after it.  (A multi-region case has no
#     top-level `0/T`; the referent is `0/module/T`.)
#
#  3. THE PROBE-WIDE COST CAP IS CHECKED BEFORE EVERY LAUNCH.  The note caps the
#     WHOLE probe -- all arms together -- at 30 core-min.  Reaching it STOPS the
#     probe; rule 12 gives no new budget.
#
# Usage: run_arm_t25RF.sh <ARM> <TIMEOUT_S>

set -u
ARM="${1:-}"
TIMEOUT_S="${2:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
D="$HERE/$ARM"
RANKS=1
PROBE_CAP_CORE_MIN=30
LEDGER="$HERE/COST_LEDGER.txt"

case "$ARM" in A0|A1|A2|A3|A2T) ;; *) echo "ABORT: arm must be A0|A1|A2|A3"; exit 1;; esac
[ -n "$TIMEOUT_S" ] || { echo "ABORT: timeout_s is never defaulted here"; exit 1; }
[ -d "$D" ] || { echo "ABORT: no $D -- run build_arm_t25RF.sh $ARM first"; exit 1; }

# --- GUARD 3: the PROBE-WIDE cap, checked BEFORE launching. -----------------
SPENT=0
if [ -f "$LEDGER" ]; then
  SPENT=$(awk -F= '/^core_min=/{s+=$2} END{printf "%.3f", s+0}' "$LEDGER")
fi
HEADROOM=$(awk -v c=$PROBE_CAP_CORE_MIN -v s="$SPENT" 'BEGIN{printf "%.3f", c-s}')
echo "PROBE COST: spent=$SPENT core_min  cap=$PROBE_CAP_CORE_MIN  headroom=$HEADROOM"
STOP=$(awk -v h="$HEADROOM" 'BEGIN{print (h<=0)?1:0}')
if [ "$STOP" = "1" ]; then
  echo "CAP STOP: the probe has reached its registered 30 core-min cap."
  echo "  CLAUDE.md rule 12: IT DOES NOT GET A NEW BUDGET.  $ARM is NOT launched."
  exit 3
fi
# the arm timeout may never exceed the remaining headroom
MAXT=$(awk -v h="$HEADROOM" -v r=$RANKS 'BEGIN{printf "%d", h*60/r}')
if [ "$TIMEOUT_S" -gt "$MAXT" ]; then
  echo "NOTE: timeout $TIMEOUT_S s exceeds remaining headroom; clamped to $MAXT s"
  TIMEOUT_S=$MAXT
fi

# --- GUARD: refuse a dirty case. -------------------------------------------
if [ -d "$D/0" ]; then
  echo "ABORT: $D/0 already exists.  The age referent is unevaluable and a"
  echo "       relaunch over an existing time tree is refused, not cleaned."
  exit 1
fi
STALE=$(find "$D" -maxdepth 1 -regextype posix-extended \
        -regex '.*/[0-9]+(\.[0-9]+)?' -not -name 0 2>/dev/null | head -3)
[ -n "$STALE" ] && { echo "ABORT: $D already holds time directories:"; echo "$STALE"; exit 1; }
[ -d "$D/0.orig" ] || { echo "ABORT: no $D/0.orig"; exit 1; }

cp -a "$D/0.orig" "$D/0" || { echo "ABORT: could not stage 0"; exit 1; }
[ -f "$D/0/module/T" ] || { echo "ABORT: no 0/module/T after staging"; exit 1; }

# --- GUARD 2: the age referent is touched LAST. -----------------------------
touch "$D/0/module/T" || { echo "ABORT: could not touch the age referent"; exit 1; }

START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
T0=$(date +%s)

# --- GUARD 1: rc captured INSIDE the wrapper. ------------------------------
setsid bash -c '
  cd "'"$D"'" || exit 97
  . /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
  timeout '"$TIMEOUT_S"' chtMultiRegionFoam > log.solve 2>&1
  echo $? > .rc.'"$ARM"'
' </dev/null >/dev/null 2>&1

while [ ! -f "$D/.rc.$ARM" ]; do sleep 3; done
RC=$(cat "$D/.rc.$ARM")
T1=$(date +%s)
WALL=$((T1 - T0))
CORE_MIN=$(awk -v w="$WALL" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')
CAPPED=no
[ "$RC" = "124" ] && CAPPED=yes

cat > "$D/STATUS.$ARM" <<EOF
arm=$ARM
rung=T25RF
gated=no
verdict=NONE_THIS_RUNG_IS_UNGATED
rc=$RC
wall_s=$WALL
ranks=$RANKS
core_min=$CORE_MIN
probe_cap_core_min=$PROBE_CAP_CORE_MIN
timeout_s=$TIMEOUT_S
capped=$CAPPED
solver=chtMultiRegionFoam
started_utc=$START
ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
note=rc-captured-INSIDE-the-detached-wrapper-NOT-around-setsid
EOF

printf 'arm=%s rc=%s wall_s=%s core_min=%s\ncore_min=%s\n' \
  "$ARM" "$RC" "$WALL" "$CORE_MIN" "$CORE_MIN" >> "$LEDGER"

echo "$ARM rc=$RC wall_s=$WALL core_min=$CORE_MIN capped=$CAPPED"
if [ "$CAPPED" = "yes" ]; then
  echo "CAP STOP: $ARM hit its timeout.  Rule 12: no new budget."
fi
exit 0
