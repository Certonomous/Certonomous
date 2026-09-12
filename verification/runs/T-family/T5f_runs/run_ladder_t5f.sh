#!/bin/bash
# run_ladder_t5f.sh -- drive the T5f ladder c -> m -> f, SEQUENTIALLY, one rank
# at a time, with no supervisor round-trip between levels.
#
# WHY THIS FILE EXISTS.  The heat-transfer supervisor lifted the hold on the
# whole ladder and asked for progress rather than a permission request per
# level, while keeping the sequential ruling (which is about not adding ranks
# beside a live 100-hour T4e leg, not about caution).  A human waiting on three
# STATUS files is the round-trip this removes.
#
# IT ADDS NO AUTHORITY.  Every launch goes through `run_one_t5f.sh`, which still
# parses the cap out of the frozen registration, still refuses a disagreeing
# argv, still runs the setup assertion and the checkMesh gate, and still refuses
# to start beside another live T5f solver.  This file only decides WHEN.
#
# THE THREE REGISTERED STOPS, and nothing else stops the ladder:
#   1. a checkMesh limb other than the cell determinant fails -- registration
#      section 6 HARD STOP, a finding for the supervisor;
#   2. estimated peak RSS would exceed `free -g` available minus 4 GiB, read
#      FRESH before each level (Sanaa bumped the volume, not the memory);
#   3. a level does not complete under CLAUDE.md rule 4 -- a crash is a FINDING,
#      never something to work around.
# Not a rate anybody dislikes, not a load figure, not a cost overrun.
#
# THE MEMORY ESTIMATE IS NOT A CONSTANT IN THIS FILE.  It is recomputed from the
# most recent MEASURED `peak_rss_kb` in any T5f STATUS, divided by that case's
# own cell count, times this level's cell count.  The first level's basis is the
# partial-run measurement in the FINDING directory and is a LOWER BOUND (a peak
# read at Time=569 of 5000 is not a complete-run peak, though SIMPLE allocates
# early); every later level uses a complete-run peak.  The figure is printed with
# its basis so a reader never has to take the word "fits".
set -eu

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
REG="$(cd "$SELF_DIR/../../../.." && pwd)/docs/campaigns/T-family/T5f_PREREGISTRATION.md"
LOG="$SELF_DIR/LADDER_LOG.txt"

say() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG"; }

box() {   # the contention context, recorded at every boundary (rule 12)
    printf 'loadavg=%s procs_running=%s procs_blocked=%s nproc=%s available_GiB=%s' \
        "$(cut -d' ' -f1-3 /proc/loadavg)" \
        "$(awk '/^procs_running/{print $2}' /proc/stat)" \
        "$(awk '/^procs_blocked/{print $2}' /proc/stat)" \
        "$(nproc)" "$(free -g | awk '/^Mem:/{print $7}')"
}

cells() {  # air + epoxy cells of one built case, from the polyMesh headers
    a=$(grep -aoE 'nCells:[0-9]+' "$SELF_DIR/$1/constant/air/polyMesh/owner" | head -1 | cut -d: -f2)
    e=$(grep -aoE 'nCells:[0-9]+' "$SELF_DIR/$1/constant/epoxy/polyMesh/owner" | head -1 | cut -d: -f2)
    echo $((a + e))
}

# the newest STATUS carrying a numeric peak_rss_kb, anywhere under T5f_runs
rss_basis() {
    best=""
    for s in $(find "$SELF_DIR" -name 'STATUS.T5F_CUBE_*' -printf '%T@ %p\n' 2>/dev/null | sort -rn | cut -d' ' -f2-); do
        kb=$(awk -F= '/^peak_rss_kb=/{print $2}' "$s")
        case "$kb" in ''|*[!0-9]*) continue ;; esac
        cse=$(awk -F= '/^case=/{print $2}' "$s")
        [ -d "$SELF_DIR/$cse" ] || cse="$(basename "$(dirname "$s")")"
        [ -d "$SELF_DIR/$cse" ] || continue
        best="$kb $(cells "$cse") $cse"
        break
    done
    echo "$best"
}

solver_live() {
    for pd in /proc/[0-9]*; do
        [ -r "$pd/cmdline" ] || continue
        a0=$(tr '\0' '\n' < "$pd/cmdline" 2>/dev/null | head -1)
        [ "$(basename -- "${a0:-x}" 2>/dev/null)" = "chtMultiRegionSimpleFoam" ] || continue
        tr '\0' '\n' < "$pd/cmdline" 2>/dev/null | grep -q "^$SELF_DIR/T5F_CUBE_" && { echo "${pd#/proc/}"; return 0; }
    done
    return 1
}

reg_cap() {
    awk -v L="$1" '
      $0 ~ ("^\\| `" L "` \\| [0-9.]+ \\| \\*\\*[0-9.]+\\*\\* \\|$") { line=$0; n++ }
      END { if (n != 1) exit 1
            if (match(line, /\*\*[0-9.]+\*\*/)) print substr(line, RSTART+2, RLENGTH-4); else exit 1 }' "$REG"
}

say "LADDER START.  $(box)"

for L in c m f; do
    CASE="T5F_CUBE_$L"
    STATUS="$SELF_DIR/STATUS.$CASE"

    # --- wait for whatever is running to finish.  Sequential is the ruling. ---
    while P=$(solver_live); do
        say "waiting: solver pid=$P still live; the sequential ruling holds."
        sleep 60
    done

    if [ -f "$STATUS" ]; then
        say "$CASE already has a STATUS; skipping to the next level."
        continue
    fi

    # --- STOP 2: the memory rule, read FRESH, estimate printed with its basis --
    AVAIL=$(free -g | awk '/^Mem:/{print $7}')
    BUDGET=$((AVAIL - 4))
    B="$(rss_basis)"
    if [ -z "$B" ]; then
        say "STOP: no measured peak_rss_kb anywhere under T5f_runs, so the memory rule has no basis. Refusing to guess."
        exit 2
    fi
    set -- $B
    BKB="$1"; BCELLS="$2"; BCASE="$3"
    NC=$(cells "$CASE")
    EST_GIB=$(awk -v kb="$BKB" -v bc="$BCELLS" -v nc="$NC" 'BEGIN{printf "%.2f", (kb/bc)*nc/1048576.0}')
    say "$CASE memory: basis $BCASE measured peak ${BKB} kB over ${BCELLS} cells = $(awk -v kb="$BKB" -v bc="$BCELLS" 'BEGIN{printf "%.3f", kb/bc}') kB/cell; this level ${NC} cells -> ESTIMATE ${EST_GIB} GiB against budget ${BUDGET} GiB (available ${AVAIL} - 4)."
    OVER=$(awk -v e="$EST_GIB" -v b="$BUDGET" 'BEGIN{print (e > b) ? 1 : 0}')
    if [ "$OVER" = "1" ]; then
        say "STOP: $CASE estimated peak RSS ${EST_GIB} GiB EXCEEDS available-minus-4 (${BUDGET} GiB). This is the supervisor's registered stop and it is a finding, not something to work around."
        exit 2
    fi

    CAP="$(reg_cap "$L")" || { say "STOP: section 8 CAP row for level $L did not parse."; exit 2; }

    # --- the dry run, every precondition, leaving no trace --------------------
    say "$CASE dry run (cap $CAP core-min parsed from the frozen registration).  $(box)"
    if ! "$SELF_DIR/run_one_t5f.sh" --level "$L" --cap-core-min "$CAP" --dry-run >> "$LOG" 2>&1; then
        say "STOP: $CASE FAILED a launch precondition in the dry run. See $LOG and $SELF_DIR/$CASE/SETUP_ASSERTION.txt. STOP 1 or STOP 3 territory -- a finding for the supervisor."
        exit 2
    fi
    say "$CASE dry run PASSED every precondition."

    say "$CASE LAUNCH.  $(box)"
    "$SELF_DIR/run_one_t5f.sh" --level "$L" --cap-core-min "$CAP" >> "$LOG" 2>&1 || {
        say "STOP: $CASE launch refused. See $LOG."
        exit 2
    }

    # --- wait for it, then report the completion facts ------------------------
    while [ ! -f "$STATUS" ]; do sleep 30; done
    say "$CASE FINISHED.  $(box)"
    say "$CASE STATUS: $(tr '\n' ' ' < "$STATUS")"

    # --- STOP 3: rule 4, the parts this file can see -------------------------
    RC=$(awk -F= '/^rc=/{print $2}' "$STATUS")
    LASTT=$(grep -a '^Time = ' "$SELF_DIR/$CASE/log.solve" | tail -1 | awk '{print $3}')
    ENDT=$(awk '/^endTime/{print $2}' "$SELF_DIR/$CASE/system/controlDict" | tr -d ';')
    ENDLINE=$(grep -ac '^End' "$SELF_DIR/$CASE/log.solve" || true)
    say "$CASE rule-4 partial read: rc=$RC last_time=$LASTT endTime=$ENDT End_lines=$ENDLINE (the full rule-4 check, incl. the age guard and the field list, is the grader's)"
    if [ "$RC" != "0" ] || [ "$LASTT" != "$ENDT" ] || [ "$ENDLINE" = "0" ]; then
        say "STOP: $CASE did NOT complete under rule 4. A crash or an incomplete run is a FINDING and goes to the supervisor; the ladder stops here rather than building on it."
        exit 2
    fi
done

say "LADDER COMPLETE: c, m and f all carry a STATUS and pass the rule-4 partial read.  $(box)"
