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
#   scripts/audit_transcripts.sh
set -u

OUT=/home/ubuntu/Certonomous/mission-output

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

hits=0
for f in "$OUT"/*/transcript.*; do
    [ -f "$f" ] || continue
    act=$(basename "$(dirname "$f")")
    for label in REUSE LEAK URL; do
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
            echo "  [$label] $act"
            echo "$found" | head -4 | sed 's/^/        /'
            hits=$((hits + 1))
        fi
    done
done

echo
if [ "$hits" -eq 0 ]; then
    echo "  clean: no banned vocabulary in any act transcript"
else
    echo "  $hits transcript/rule combinations to review above"
fi
