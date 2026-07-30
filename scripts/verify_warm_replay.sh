#!/usr/bin/env bash
# verify_warm_replay.sh -- prove a warm replay reproduces its measured numbers.
#
# For each act: snapshot the current transcript, re-run the act through the
# control room exactly as the camera will, then diff. The physics must be
# identical.
#
# Two classes of line legitimately move between runs and are handled, not
# frozen:
#
#   * HOST READINGS -- the compute audit's free-core and free-memory numbers.
#     These describe the machine at this instant, not the physics. They are
#     excluded from the comparison outright.
#   * MEASURED WALL CLOCKS -- stage times, core-minutes, the race's lane
#     clocks. These are real measurements taken in THIS run, so they are
#     expected to move. They are NOT excluded: the strict diff runs first, and
#     only if the sole remaining differences are timings does the act report
#     "IDENTICAL apart from measured wall clocks" -- and it prints those lines
#     so nothing is hidden behind the softer verdict.
#
#   scripts/verify_warm_replay.sh [act ...]
#   REPEATS=2 scripts/verify_warm_replay.sh nasa-hump    # timing variance
#
# Act names are the mission-output directory names, which is also where each
# act writes its transcript.
#
# ONE CAVEAT. That transcript is a single file per act, overwritten by whoever
# runs the act last. If anything else is driving the control room while this
# runs -- another operator, another agent -- its run becomes this script's
# baseline and the next act reports DIFFERS on a prompt it never sent. Seen
# repeatedly. Run this with the box to yourself, and re-run any act that
# differs only in its SYSTEM line before believing it.
set -u

HOST=http://127.0.0.1:8765
OUTDIR=/home/ubuntu/Certonomous/mission-output
REPEATS=${REPEATS:-1}

declare -A PROMPT=(
  # -- the eight-act validation sequence -------------------------------------
  [supersonic-wedge]="Solve the supersonic wedge at Mach 2 with a 15 degree half-angle and check the oblique shock angle."
  [supersonic-cone]="Solve the supersonic cone at Mach 2.35 with a 10 degree half-angle and check the conical shock angle."
  [diamond-airfoil]="Solve the diamond airfoil at Mach 2 and check the wave drag against shock-expansion theory."
  [hypersonic-cylinder]="Solve hypersonic flow over a blunt cylinder at Mach 8 and check the shock standoff distance."
  [cylinder-vortex-shedding]="Solve vortex shedding behind a circular cylinder at Reynolds 100 and check the Strouhal number."
  [ahmed-body]="Solve the Ahmed body with the 25 degree slant and check the drag against the wind tunnel."
  [nasa-hump]="Solve the NASA wall-mounted hump and check separation and reattachment."
  [crm-wingbody]="Solve the CRM wing-body and check the drag."
  # -- the headline acts -----------------------------------------------------
  [adjoint-optimization]="Cut the drag on the wing with the discrete adjoint and verify the gradient against finite differences."
  [aircraft-optimization]="Optimize the L/D of an airliner for 300 passengers, 6000 km range."
  [valve-study]="Find the valve opening angle that minimizes pressure loss over the cardiac cycle."
  [race-study]="Race a Monte Carlo uncertainty study against a reduced-order model."
  [geometry-study]="Solve the external aerodynamics of the supplied B-52 geometry."
)

# Acts filmed with a surface uploaded from the laptop. The prompt still names
# nothing: the surface is threaded in exactly as /api/geometry/upload threads
# it, so this verifies the upload path the camera will use, not a shortcut.
declare -A SURFACE=(
  [geometry-study]="b52.stl"
)

ACTS=("$@")
[ ${#ACTS[@]} -eq 0 ] && ACTS=(supersonic-wedge supersonic-cone diamond-airfoil
                               hypersonic-cylinder cylinder-vortex-shedding
                               ahmed-body nasa-hump crm-wingbody
                               adjoint-optimization aircraft-optimization
                               valve-study geometry-study race-study)

# Lines carrying live host state rather than measurement.
NOISE='Compute audit|cores free|GB available|other job'

# An act that fails the same way twice diffs clean. That is how a broken
# cylinder vortex-shedding act -- the control room had been restarted without
# the OpenFOAM launcher on its environment, so every utility call raised
# FileNotFoundError -- reported IDENTICAL while putting "the wake solve did not
# complete" on screen. Reproducibility is necessary, not sufficient: the act
# must also have produced a result. These are the phrases the acts use when
# they stop honestly rather than report a number.
BROKEN='did not complete|did not finish cleanly|no result is reported|could not be read as a surface|will not solve a different body'

# Measured wall clocks, normalised only for the SECOND-PASS diff. Each pattern
# targets a timing phrasing specifically, never a bare number, so no physical
# quantity is masked by accident.
normalise() {
    sed -E \
        -e 's/Time [0-9]+(\.[0-9]+)? s/Time <clock> s/g' \
        -e 's/in [0-9]+(\.[0-9]+)? minutes/in <clock> minutes/g' \
        -e 's/solve stage [0-9]+(\.[0-9]+)? seconds/solve stage <clock> seconds/g' \
        -e 's/: [0-9]+(\.[0-9]+)? s,/: <clock> s,/g' \
        -e 's/[0-9]+(\.[0-9]+)? core-min/<clock> core-min/g' \
        -e 's/Core-minutes [0-9]+(\.[0-9]+)?/Core-minutes <clock>/g' \
        -e 's/[0-9]+(\.[0-9]+)?(x|×) (in core-minutes|measured)/<clock>x \3/g' \
        -e 's/speedup [0-9]+(\.[0-9]+)?/speedup <clock>/g'
}

pass=0; soft=0; fail=0
declare -A TIMES

for act in "${ACTS[@]}"; do
    p=${PROMPT[$act]:-}
    if [ -z "$p" ]; then echo "  $act: no prompt registered, skipped"; continue; fi
    surf=${SURFACE[$act]:-}

    before=$(ls "$OUTDIR/$act"/transcript.* 2>/dev/null | head -1)
    if [ -z "$before" ]; then
        echo "  $act: NO PRIOR TRANSCRIPT -- run it once before verifying"
        fail=$((fail+1)); continue
    fi
    snap=$(mktemp); cp "$before" "$snap"

    runs=""
    verdict=""
    for rep in $(seq 1 "$REPEATS"); do
        t0=$(date +%s)
        body=$(python3 -c 'import json,sys
print(json.dumps({"request": sys.argv[1], "surface": sys.argv[2]}))' "$p" "$surf")
        mid=$(curl -s -m 30 -X POST "$HOST/api/missions" \
                -H 'Content-Type: application/json' -d "$body" \
              | python3 -c 'import json,sys; print(json.load(sys.stdin).get("mission_id",""))')

        state=""
        for _ in $(seq 1 240); do
            state=$(curl -s -m 15 "$HOST/api/missions" | python3 -c "
import json,sys
ms=json.load(sys.stdin); ms=ms.get('missions',ms) if isinstance(ms,dict) else ms
for m in ms:
    if m.get('mission_id')=='$mid': print(m.get('state','')); break
")
            case "$state" in complete|failed|incomplete) break;; esac
            sleep 2
        done
        secs=$(( $(date +%s) - t0 ))
        runs="$runs ${secs}s"

        if [ "$state" != "complete" ]; then
            verdict="STATE=$state"
            break
        fi

        after=$(ls "$OUTDIR/$act"/transcript.* 2>/dev/null | head -1)
        if grep -Eq "$BROKEN" "$after"; then
            verdict="NO-RESULT"
            DIFFLINES=$(grep -E "$BROKEN" "$after" | head -3)
            break
        fi
        if diff <(grep -Ev "$NOISE" "$snap") <(grep -Ev "$NOISE" "$after") >/dev/null; then
            [ -z "$verdict" ] && verdict="IDENTICAL"
        elif diff <(grep -Ev "$NOISE" "$snap" | normalise) \
                  <(grep -Ev "$NOISE" "$after" | normalise) >/dev/null; then
            verdict="CLOCKS-ONLY"
            CLOCKLINES=$(diff <(grep -Ev "$NOISE" "$snap") \
                              <(grep -Ev "$NOISE" "$after") | head -8)
        else
            verdict="DIFFERS"
            DIFFLINES=$(diff <(grep -Ev "$NOISE" "$snap") \
                             <(grep -Ev "$NOISE" "$after") | head -14)
            break
        fi
        cp "$after" "$snap"   # repeat 2 compares against repeat 1
    done
    rm -f "$snap"

    TIMES[$act]="$runs"
    case "$verdict" in
        IDENTICAL)
            echo "  $act: IDENTICAL, replay$runs"; pass=$((pass+1));;
        CLOCKS-ONLY)
            echo "  $act: IDENTICAL apart from measured wall clocks, replay$runs"
            printf '%s\n' "$CLOCKLINES" | sed 's/^/      /'
            soft=$((soft+1));;
        DIFFERS)
            echo "  $act: DIFFERS, replay$runs"
            printf '%s\n' "$DIFFLINES" | sed 's/^/      /'
            fail=$((fail+1));;
        NO-RESULT)
            echo "  $act: RAN BUT REPORTED NO RESULT, replay$runs"
            printf '%s\n' "$DIFFLINES" | sed 's/^/      /'
            fail=$((fail+1));;
        *)
            echo "  $act: replay did not complete ($verdict) after$runs"
            fail=$((fail+1));;
    esac
done

echo
echo "  measured durations"
for act in "${ACTS[@]}"; do
    [ -n "${TIMES[$act]:-}" ] && printf '    %-26s%s\n' "$act" "${TIMES[$act]}"
done
echo
echo "  identical: $pass    clocks-only: $soft    differing or failed: $fail"
[ "$fail" -eq 0 ]
