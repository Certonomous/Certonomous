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
#     The race's own lane clocks were named in that paragraph before they were
#     handled. The reduced-order and Monte Carlo tables print a "Solve seconds"
#     column (race_study._ROM_HEADERS, _MC_HEADERS) and no rule below matched
#     it, so those rows differed on the clock alone while their L/D matched to
#     the digit: 18.14, 15.73, 12.47, 10.15 and the confirmation at 18.14, with
#     3.93 against 3.88 seconds between them. The rule added below is anchored
#     to the literal column name and the lines still print.
#
#     THAT RULE DOES NOT MAKE race-study REPORT IDENTICAL, and saying so here
#     is the point: the anchor rows also arrive in a DIFFERENT ORDER between
#     runs, which is a real difference and not a clock, so it is left to fail.
#     Masking it would be masking a quantity. Whoever settles the ordering
#     should settle it in the act, not in this file.
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
#
# THIS GATE FAILS CLOSED. Given an act name it did not recognise it printed
# `no prompt registered, skipped`, counted nothing, and finished with
#
#     identical: 0    clocks-only: 0    differing or failed: 0
#
# and exit 0. Three zeros are not a pass. They are the shape of an instrument
# that was handed nothing and said so quietly enough to be read as agreement --
# a typo in an act name on filming morning cleared the reproducibility gate
# without replaying a single act. So every requested act is now RESOLVED
# BEFORE ANY OF THEM IS RUN, the summary carries `N of M act(s) resolved` so
# the denominator is on the same line as the zeros, an act that cannot be
# resolved is named with the reason and makes the exit code non-zero, and a
# run in which NOTHING resolved prints RED and exits 2 with no summary line at
# all -- a replay that never happened has no verdict to offer.
#
# Exit codes:  0 = every requested act resolved and replayed clean
#              1 = something to look at: a DIFFERS, a NO-RESULT, or an act
#                  that could not be resolved
#              2 = nothing resolved                    (RED -- verdict withheld)
#
# CONTROL HARNESS. The three settings below are overridable by environment so
# this gate can be pointed at a scratch corpus and a stub control room and
# shown to fire, the way `audit_transcripts.sh` takes a corpus argument. The
# names are long and script-specific on purpose: a gate a stray exported
# `HOST` could silently repoint would be a fresh instance of what it polices.
#
#   WARM_REPLAY_OUTDIR=/scratch/copy   -- where prior transcripts are read
#   WARM_REPLAY_HOST=http://127.0.0.1:PORT
#   WARM_REPLAY_RESOLVE_ONLY=1         -- resolve and stop. Runs no act, so it
#                                         touches no transcript, and it prints
#                                         NO reproducibility verdict: it is not
#                                         a cheap way to pass this gate.
set -u

HOST=${WARM_REPLAY_HOST:-http://127.0.0.1:8765}
OUTDIR=${WARM_REPLAY_OUTDIR:-/home/ubuntu/Certonomous/mission-output}
RESOLVE_ONLY=${WARM_REPLAY_RESOLVE_ONLY:-0}
REPEATS=${REPEATS:-1}

declare -A PROMPT=(
  # -- the eight-act validation sequence -------------------------------------
  [supersonic-wedge]="Solve the supersonic wedge at Mach 2 with a 15 degree half-angle and check the oblique shock angle."
  [supersonic-cone]="Solve the supersonic cone at Mach 2.35 with a 10 degree half-angle and check the conical shock angle."
  [diamond-airfoil]="Solve the diamond airfoil at Mach 2 and check the wave drag against shock-expansion theory."
  [hypersonic-cylinder]="Solve hypersonic flow over a blunt cylinder at Mach 8 and check the shock standoff distance."
  [cylinder-vortex-shedding]="Solve vortex shedding behind a circular cylinder at Reynolds 100 and check the Strouhal number."
  [ahmed-body]="Solve the Ahmed body with the 25 degree slant and check the drag against the wind tunnel."
  [nasa-hump]="Solve the NASA wall-mounted hump and check separation"
  [crm-wingbody]="Solve the CRM wing-body and check the drag."
  # -- the headline acts -----------------------------------------------------
  [adjoint-optimization]="Cut the drag on the wing with the discrete adjoint and verify the gradient against finite differences."
  # The airliner prompt is the one Katie types on camera, verbatim, and it
  # arrives with a surface: "the attached twin airliner" is an upload, and the
  # worker clause is what makes the act state its headroom in numbers. Verified
  # here with the surface threaded in, because a run without it searches a
  # different span ladder and lands on a different wing.
  [aircraft-optimization]="Optimize lift drag coefficient of the attached twin airliner. Constraints: 300 passengers, Range: 6000 km, take off speed: 80 m/s landing speed: 70 m/s. Don't use all of my workers"
  [valve-study]="Find the valve opening angle that minimizes pressure loss over the cardiac cycle."
  [race-study]="Race a Monte Carlo uncertainty study against a reduced-order model."
  [geometry-study]="Solve the external aerodynamics of the supplied B-52 geometry."
  # Registered but deliberately NOT in the default sweep below. The act is
  # new, and a control room started before it existed holds the old router in
  # memory: this prompt would route somewhere else and the act would report
  # DIFFERS on a routing fault rather than on its physics. Add it to the
  # default list once the control room has been restarted on the router that
  # knows the route. Until then run it by name.
  [sobol-sensitivity]="Apportion the output variance across the input spreads with a Sobol pick-and-freeze design and say which spread is worth buying down first."
)

# Acts filmed with a surface uploaded from the laptop. The prompt still names
# nothing: the surface is threaded in exactly as /api/geometry/upload threads
# it, so this verifies the upload path the camera will use, not a shortcut.
declare -A SURFACE=(
  [geometry-study]="b52.stl"
  [aircraft-optimization]="airliner_wing_span52.stl"
)

ACTS=("$@")
[ ${#ACTS[@]} -eq 0 ] && ACTS=(supersonic-wedge supersonic-cone diamond-airfoil
                               hypersonic-cylinder cylinder-vortex-shedding
                               ahmed-body nasa-hump crm-wingbody
                               adjoint-optimization aircraft-optimization
                               valve-study geometry-study race-study)

# ---------------------------------------------------------------------------
# Resolve every requested act BEFORE running any of them. Both resolution tests
# are answerable without touching the control room, so a typo costs nothing and
# is reported first rather than after twelve acts have already replayed.
#
#   registered  -- the name appears in PROMPT above. A misspelling does not.
#   baselined   -- the act has a prior transcript to diff against.
#
# The requested count is kept because it is the denominator: `0 of 1 resolved`
# is a typo, `13 of 13 resolved` is a sweep, and both used to print as silence.
# ---------------------------------------------------------------------------
REQUESTED=${#ACTS[@]}
RESOLVED=(); UNRESOLVED=(); WHY=()

for act in "${ACTS[@]}"; do
    if [ -z "${PROMPT[$act]:-}" ]; then
        UNRESOLVED+=("$act"); WHY+=("$act: no prompt registered -- check the spelling against the PROMPT table")
        continue
    fi
    if [ -z "$(ls "$OUTDIR/$act"/transcript.* 2>/dev/null | head -1)" ]; then
        UNRESOLVED+=("$act"); WHY+=("$act: no prior transcript in $OUTDIR/$act -- run the act once before verifying")
        continue
    fi
    RESOLVED+=("$act")
done

# --- fail closed -----------------------------------------------------------
# No summary line is printed on either arm. The old script's three zeros were
# a summary of nothing, and a summary of nothing is what got read as a pass.
if [ ! -d "$OUTDIR" ]; then
    echo "  RED: transcript directory does not exist -- $OUTDIR"
    echo "       Every baseline this gate diffs against lives under it."
    echo "  No verdict. 0 of $REQUESTED act(s) resolved; nothing was replayed."
    exit 2
fi
if [ "${#RESOLVED[@]}" -eq 0 ]; then
    echo "  RED: no requested act could be resolved."
    for w in "${WHY[@]}"; do echo "       $w"; done
    echo "  No verdict. 0 of $REQUESTED act(s) resolved; nothing was replayed,"
    echo "  so this gate has said nothing about whether anything reproduces."
    exit 2
fi

# Named up front, next to the count, so the reach is known before the first
# replay rather than inferred from a short list of results at the end.
echo "  resolved ${#RESOLVED[@]} of $REQUESTED act(s)"
for w in "${WHY[@]}"; do echo "  UNRESOLVED  $w"; done
[ "${#WHY[@]}" -gt 0 ] && echo

if [ "$RESOLVE_ONLY" != 0 ]; then
    echo "  WARM_REPLAY_RESOLVE_ONLY is set: no act was run, no transcript was"
    echo "  touched, and NOTHING is claimed about reproducibility. This is the"
    echo "  control harness, not a pass."
    [ "${#UNRESOLVED[@]}" -eq 0 ] || exit 1
    exit 0
fi

ACTS=("${RESOLVED[@]}")

# Lines carrying live host state rather than measurement. "granted slots" is
# the same class as the compute audit's free-core count: how many slots the
# box handed out this instant, not a property of the answer. The airliner act
# reported DIFFERS on it while every solved coefficient matched.
#
# The worker-headroom rows join them for exactly that reason. Available, Taken
# and Held back are read off the free-core count at the moment the act runs, so
# a busy box moves them while the physics does not. Left out, a filming-day
# check reports DIFFERS on an act that did not change.
#
# So does the SENTENCE that introduces those rows, and it is anchored on its
# opening clause rather than on any one of its wordings. The act says one thing
# on a box with slots to spare and another on a box already at capacity one,
# where there is no headroom to leave and it says so rather than claiming some.
# Which branch runs is the free-core count at that instant, so the two are the
# same host reading in prose. Matching only the first wording is what made this
# act report DIFFERS while every solved coefficient matched to the digit.
NOISE='Compute audit|cores free|GB available|other job|granted slots|Worker headroom|Available|Taken|Held back|asked me to leave headroom|no headroom to leave'

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
        -e 's/converged force in [0-9]+(\.[0-9]+)? (s|min)/converged force in <clock>/g' \
        -e 's/Wall clock \| Measured [0-9]+(\.[0-9]+)? (s|min)/Wall clock | Measured <clock>/g' \
        -e 's/solve stage [0-9]+(\.[0-9]+)? seconds/solve stage <clock> seconds/g' \
        -e 's/Solve seconds [0-9]+(\.[0-9]+)?/Solve seconds <clock>/g' \
        -e 's/: [0-9]+(\.[0-9]+)? s,/: <clock> s,/g' \
        -e 's/[0-9]+(\.[0-9]+)? core-min/<clock> core-min/g' \
        -e 's/Core-minutes [0-9]+(\.[0-9]+)?/Core-minutes <clock>/g' \
        -e 's/[0-9]+(\.[0-9]+)?(x|×) (in core-minutes|measured)/<clock>x \3/g' \
        -e 's/speedup [0-9]+(\.[0-9]+)?/speedup <clock>/g'
}

pass=0; soft=0; fail=0
declare -A TIMES

for act in "${ACTS[@]}"; do
    # Both conditions were settled in the resolution pass above, so neither
    # can be true here. They stay as a guard, and they now count as failures
    # rather than `continue`-ing past: a `skipped` that leaves every counter
    # untouched is exactly how the all-zeros pass was manufactured.
    p=${PROMPT[$act]:-}
    if [ -z "$p" ]; then
        echo "  $act: no prompt registered, NOT VERIFIED"
        fail=$((fail+1)); continue
    fi
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
# The denominator rides on the same line as the counts. Read alone, three zeros
# describe a clean sweep and an empty one identically; `0 of 1 resolved` cannot
# be mistaken for either, and `13 of 13` says how much the zeros are worth.
echo "  identical: $pass    clocks-only: $soft    differing or failed: $fail" \
     "   --  ${#RESOLVED[@]} of $REQUESTED act(s) resolved," \
     "$((pass + soft + fail)) replayed"
if [ "${#UNRESOLVED[@]}" -gt 0 ]; then
    echo "  not verified at all: ${UNRESOLVED[*]}"
fi

# An act this gate could not resolve is an act it did not verify, and a gate
# that did less than it was asked to do does not get to exit 0.
[ "$fail" -eq 0 ] && [ "${#UNRESOLVED[@]}" -eq 0 ]
