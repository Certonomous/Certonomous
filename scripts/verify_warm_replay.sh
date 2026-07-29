#!/usr/bin/env bash
# verify_warm_replay.sh -- prove a warm replay reproduces its measured numbers.
#
# For each act: snapshot the current transcript, re-run the act through the
# control room exactly as the camera will, then diff. The measured quantities
# must be identical. Lines that report live machine state (the compute audit's
# free-core and free-memory reading) legitimately differ between runs and are
# excluded from the comparison -- they are host readings, not physics.
#
#   scripts/verify_warm_replay.sh [act ...]
set -u

HOST=http://127.0.0.1:8765
OUTDIR=/home/ubuntu/Certonomous/mission-output

declare -A PROMPT=(
  [supersonic-wedge]="Solve the supersonic wedge at Mach 2 with a 15 degree half-angle and check the oblique shock angle."
  [supersonic-cone]="Solve the supersonic cone at Mach 2.35 with a 10 degree half-angle and check the conical shock angle."
  [diamond-airfoil]="Solve the diamond airfoil at Mach 2 and check the wave drag against shock-expansion theory."
  [hypersonic-cylinder]="Solve hypersonic flow over a blunt cylinder at Mach 8 and check the shock standoff distance."
  [cylinder-vortex-shedding]="Solve vortex shedding behind a circular cylinder at Reynolds 100 and check the Strouhal number."
)

ACTS=("$@")
[ ${#ACTS[@]} -eq 0 ] && ACTS=(supersonic-wedge supersonic-cone diamond-airfoil
                               hypersonic-cylinder cylinder-vortex-shedding)

# Lines carrying live host state rather than measurement.
NOISE='Compute audit|cores free|GB available|other job'

pass=0; fail=0

for act in "${ACTS[@]}"; do
    p=${PROMPT[$act]:-}
    if [ -z "$p" ]; then echo "  $act: no prompt registered, skipped"; continue; fi

    before=$(ls "$OUTDIR/$act"/transcript.* 2>/dev/null | head -1)
    if [ -z "$before" ]; then
        echo "  $act: NO PRIOR TRANSCRIPT -- run it once before verifying"
        fail=$((fail+1)); continue
    fi
    snap=$(mktemp); cp "$before" "$snap"

    t0=$(date +%s)
    body=$(python3 -c 'import json,sys; print(json.dumps({"request": sys.argv[1]}))' "$p")
    mid=$(curl -s -m 30 -X POST "$HOST/api/missions" \
            -H 'Content-Type: application/json' -d "$body" \
          | python3 -c 'import json,sys; print(json.load(sys.stdin).get("mission_id",""))')

    state=""
    for _ in $(seq 1 120); do
        state=$(curl -s -m 15 "$HOST/api/missions" | python3 -c "
import json,sys
ms=json.load(sys.stdin); ms=ms.get('missions',ms) if isinstance(ms,dict) else ms
for m in ms:
    if m.get('mission_id')=='$mid': print(m.get('state','')); break
")
        case "$state" in complete|failed) break;; esac
        sleep 5
    done
    secs=$(( $(date +%s) - t0 ))

    after=$(ls "$OUTDIR/$act"/transcript.* 2>/dev/null | head -1)
    if [ "$state" != "complete" ]; then
        echo "  $act: replay $state after ${secs}s"
        fail=$((fail+1)); rm -f "$snap"; continue
    fi

    if diff <(grep -Ev "$NOISE" "$snap") <(grep -Ev "$NOISE" "$after") >/dev/null; then
        echo "  $act: IDENTICAL, replay ${secs}s"
        pass=$((pass+1))
    else
        echo "  $act: DIFFERS, replay ${secs}s"
        diff <(grep -Ev "$NOISE" "$snap") <(grep -Ev "$NOISE" "$after") | head -12 | sed 's/^/      /'
        fail=$((fail+1))
    fi
    rm -f "$snap"
done

echo
echo "  identical: $pass    differing or failed: $fail"
[ "$fail" -eq 0 ]
