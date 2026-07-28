#!/usr/bin/env bash
# Is this box doing real work?
#
#   ./is_idle.sh          -> prints BUSY or IDLE, exit 0 = idle, 1 = busy
#   ./is_idle.sh -v       -> also lists what it found
#
# Intended for an "auto-stop the instance when idle" watchdog. Read the three
# traps below before wiring it to anything that halts the machine.
#
# TRAP 1 -- THE KEEPER WILL RESTART THE BATCH.
#   mega_batch_keeper.sh brings the batch back whenever it is down and memory
#   has recovered. So "the batch is not running" does NOT mean the box is
#   finished; it may mean the batch stopped on its memory guard 30 seconds ago
#   and is about to come back. This script therefore counts the KEEPER ITSELF
#   as work in progress. To genuinely wind down, stop the keeper first.
#
# TRAP 2 -- `comm` IS NOT DISTINCTIVE.
#   The batch runs as comm=python3 and the keeper as comm=bash. Matching on
#   those alone would catch unrelated processes. Every check below matches the
#   full command line and then confirms the executable name.
#
# TRAP 3 -- `pgrep -f` MATCHES THE SHELL THAT ASKS.
#   A shell whose own command line contains the pattern is itself a match. This
#   produced two false "still running" readings on 2026-07-27/28, once making a
#   36-minute mesh look like a 19-second crash. Every match below excludes the
#   current process and its parent.
set -u

VERBOSE=0
[ "${1:-}" = "-v" ] && VERBOSE=1

SELF=$$
PARENT=$PPID
found=()

# Match a full-command-line pattern, excluding this script and its parent.
match() {
    local pattern="$1" label="$2" p
    for p in $(pgrep -f "$pattern" 2>/dev/null); do
        [ "$p" = "$SELF" ] && continue
        [ "$p" = "$PARENT" ] && continue
        # Skip anything whose cmdline is a shell wrapper around this script.
        case "$(tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null)" in
            *is_idle.sh*) continue ;;
        esac
        found+=("$label (pid $p)")
    done
}

# Long-lived orchestration
match "sdk/workflows/mega_batch\.py"        "mega-batch runner"
match "sdk/scripts/mega_batch_keeper\.sh"   "batch keeper (WILL RESTART THE BATCH)"

# Solvers, by executable name -- these are unambiguous
for exe in simpleFoam pimpleFoam rhoSimpleFoam rhoCentralFoam rhoPimpleFoam \
           interFoam sonicFoam blockMesh snappyHexMesh vspaero \
           decomposePar reconstructPar foamToVTK; do
    for p in $(pgrep -x "$exe" 2>/dev/null); do
        found+=("$exe (pid $p)")
    done
done

# DAFoam / containerised work
match "docker run .*dafoam"                 "DAFoam container"
match "mpirun .*runScript"                  "DAFoam mpirun"

# One-shot closure training (not a daemon, but can be running)
match "train_closure_|closure_baseline_error_gate" "closure training script"

if [ ${#found[@]} -eq 0 ]; then
    echo "IDLE"
    exit 0
fi

echo "BUSY"
if [ "$VERBOSE" = "1" ]; then
    printf '  %s\n' "${found[@]}"
fi
exit 1
