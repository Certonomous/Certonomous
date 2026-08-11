#!/usr/bin/env bash
# audit_transcripts.sh -- check what the acts say on camera.
#
# The reuse is silent: nothing an act prints may reveal that a mesh or a solve
# came back from cache, and nothing may expose the machinery behind the lab --
# file names, internal paths, study IDs, module names. This greps every act
# transcript for the banned vocabulary and prints the offending line so it can
# be judged in context rather than just counted.
#
# Companion to scripts/audit_camera_discretion.sh, which polices the wider
# METHOD half under docs/DEMO_DISCRETION_CHARTER.md. Run both before filming.
#
#   scripts/audit_transcripts.sh              # the real corpus
#   scripts/audit_transcripts.sh <corpus-dir> # a scratch copy, for controls
#
# THIS GATE FAILS CLOSED. It used to say `clean` after scanning nothing: an
# absent or empty corpus root expands the glob to no matches, `hits` stays 0,
# and 0 hits printed the same green line as a corpus that was read in full. A
# gate that cannot find its inputs must go RED, because the reader in front of
# a camera cannot tell "read all 17 and found nothing" from "read none" unless
# the verdict says which. So the corpus is counted BEFORE it is judged, an
# unusable corpus exits 2 with no verdict at all, and the verdict line always
# carries its own reach -- transcripts scanned and terms checked -- rather than
# a bare adjective. A caveat that lives only in this comment does not reach the
# person reading the last line of output, which is the whole point.
#
# Exit codes:  0 = scanned >=1 transcript, no hits   (green)
#              1 = hits to review                     (amber -- read them)
#              2 = corpus missing or empty            (RED -- verdict withheld)
set -u

OUT=${1:-/home/ubuntu/Certonomous/mission-output}

# Words that would give away the cache. The single most important rule.
REUSE='\b(cached|caching|cache|precomputed|pre-computed|reused|reuse|replayed|stored|saved|memoi[sz]ed|warm start|from disk)\b'

# Machinery that should never reach the screen.
LEAK='(\.py\b|\.md\b|\.json\b|\.stl\b|\.sh\b|/home/|sdk/|workflows\.|chief_engineer|mission-output|snappyHexMesh|blockMesh|simpleFoam|pimpleFoam|rhoCentralFoam|DASimpleFoam|OpenFOAM|Docker|dafoam|python)'

# The one exception, and it is required rather than tolerated. A toolchain name
# doing the job of a REFERENCE IDENTITY is not a leak: it says what the lab was
# graded against, which docs/DEMO_DISCRETION_CHARTER.md keeps on camera in every
# case. "per OpenFOAM mesh-quality guidance" names the published threshold the
# gate cites; "the DAFoam project's own published CRM wing tutorial
# documentation" names the publisher of the number we are compared to. Both
# stay. Deleting them to quiet this audit would strip the comparison out of the
# claim, which is the exact failure the charter exists to prevent. Anything
# else naming the same stack is still a leak and still fires.
KEEP='(per OpenFOAM mesh-quality guidance|the DAFoam project.s own published)'

# Bare URLs -- links must render as the word "source".
URL='https?://'

RULES=(REUSE LEAK URL)

# ---------------------------------------------------------------------------
# Establish the reach BEFORE judging anything. The denominator is the fix: a
# verdict is only meaningful against the size of the set it was computed over.
# ---------------------------------------------------------------------------
shopt -s nullglob
files=("$OUT"/*/transcript.*)
actdirs=("$OUT"/*/)
shopt -u nullglob

# Count the banned terms, so the verdict can state how much vocabulary it knows
# rather than asserting that it knows enough.
terms=0
for label in "${RULES[@]}"; do
    pat=${!label}
    n=$(printf '%s' "$pat" | tr -cd '|' | wc -c)
    terms=$((terms + n + 1))
done

# --- fail closed -------------------------------------------------------------
# Both arms print RED and exit 2. Neither prints a verdict: an instrument that
# read nothing has no opinion to offer, and offering one anyway is the defect
# this gate was built to stop being an instance of.
if [ ! -d "$OUT" ]; then
    echo "  RED: corpus root does not exist -- $OUT"
    echo "  No verdict. 0 transcripts scanned; this gate cannot clear filming."
    exit 2
fi
if [ "${#files[@]}" -eq 0 ]; then
    echo "  RED: corpus root exists but holds no transcripts -- $OUT"
    echo "  Looked for: $OUT/*/transcript.*  (${#actdirs[@]} act directory/ies present)"
    echo "  No verdict. 0 transcripts scanned; this gate cannot clear filming."
    exit 2
fi

hits=0
hitlines=0
for f in "${files[@]}"; do
    [ -f "$f" ] || continue
    act=$(basename "$(dirname "$f")")
    for label in "${RULES[@]}"; do
        pat=${!label}
        found=$(grep -nEi "$pat" "$f" 2>/dev/null)
        # Strip the reference-identity exception, then re-test what is left of
        # the line: a line that leaks twice still reports.
        if [ "$label" = LEAK ] && [ -n "$found" ]; then
            found=$(printf '%s\n' "$found" | while IFS= read -r line; do
                if printf '%s\n' "$line" | sed -E "s/$KEEP//gi" \
                   | grep -qEi "$pat"; then printf '%s\n' "$line"; fi
            done)
        fi
        if [ -n "$found" ]; then
            # Print every match. The old `head -4` silently dropped the 5th
            # onward, so a combination could under-report exactly when it had
            # the most to say -- the same withheld-reach defect one layer down.
            nlines=$(printf '%s\n' "$found" | wc -l)
            echo "  [$label] $act -- $nlines line(s)"
            printf '%s\n' "$found" | sed 's/^/        /'
            hits=$((hits + 1))
            hitlines=$((hitlines + nlines))
        fi
    done
done

echo
# The reach travels with the verdict, on the same line a reader stops at. An
# adjective on its own ("clean") is the failure mode: it reads identically at
# 17 transcripts and at 0.
reach="${#files[@]} transcript(s) x ${#RULES[@]} rules (${terms} terms) scanned"

# An act directory with no transcript is an act this gate did not read. Say so
# next to the verdict rather than leaving it to be inferred from the count.
# Counted per directory, not as (dirs - files): one act may hold both a
# transcript.txt and a transcript.md, and subtracting would under-report.
silent=0
for d in "${actdirs[@]}"; do
    shopt -s nullglob
    t=("$d"transcript.*)
    shopt -u nullglob
    [ "${#t[@]}" -eq 0 ] && silent=$((silent + 1))
done

if [ "$hits" -eq 0 ]; then
    echo "  clean: no banned vocabulary found -- $reach"
else
    echo "  $hits transcript/rule combination(s), $hitlines line(s) to review above -- $reach"
fi
if [ "$silent" -gt 0 ]; then
    echo "  note: ${#actdirs[@]} act director(y/ies) present, $silent with no transcript.* and therefore unread"
fi

[ "$hits" -eq 0 ] || exit 1
exit 0
