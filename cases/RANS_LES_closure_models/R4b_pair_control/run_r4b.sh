#!/usr/bin/env bash
# R4b instrument A5 - drive the pair-control propagation cases.
#
# Registered by `R4b/PREREGISTRATION.md` sec. 11 and
# `INSTRUMENT_BUILD_PREREGISTRATION.md` sec. 2.2 / B5:
#
#   * the sec. 11.2 PRE-LAUNCH CAPACITY CHECK, and IT DOES NOT TRUST `pgrep`
#     ALONE.  L-41: fleet agents are invisible to a process sweep.  R4b sec.
#     11.2 records the measurement that forced this - 3 solvers live at 99.9%
#     CPU each AND a load average of 72.31 on 16 cores, because 16 concurrent
#     OCR processes from another workstream were consuming the rest of the box.
#     "A check that counted solver names would have reported '3 solvers, room
#     to spare' and been wrong by a factor of six."  So the check reads, in
#     addition to the process sweep: the 1-minute load average, run-directory
#     mtimes, the docket, and recent commits by live peers.
#   * `JOBS=2`, never more, under any reading (sec. 11.1);
#   * `nice -n 10` on every solve, never removed (sec. 11.1);
#   * skip-if-complete under sec. 4.2, and NEVER a re-run in place (sec. 4.3);
#   * IT NEVER KILLS A RUNNING SOLVER.  There is no `kill`, `pkill`, `killall`,
#     `--signal` or `fuser -k` anywhere in this file; `--selftest` greps this
#     file for all of them and FAILS if one appears.  Nothing is ever killed to
#     save budget (Charter sec. 18).
#   * `wall_seconds` per case, for the standing-rule-12 calibration duty.
#
# THE CONCURRENCY RULE ONLY EVER REDUCES (sec. 11.3).  No reading permits 3 or
# more, and no reading permits removing the `nice`.
#
#     load1 <  16  and fewer than 4 foreign solvers  ->  2
#     load1 >= 16  or  4 or more foreign solvers     ->  1
#     load1 >= 40                                    ->  BLOCKED, no solve starts
#
# REGISTERED LIMITATION (B5), disclosed in advance and not discovered later:
# the birth demonstration exercises this script with `R4B_SOLVER` set to a
# registered no-op.  NO `simpleFoam` IS LAUNCHED BY THE INSTRUMENT BUILD.  B5
# therefore does NOT establish that this script can drive `simpleFoam`, and it
# may not be read as having established it.  The fail-fast for that is R4b's
# own first propagation case, under R4b's registration, after Sanaa has
# directed the increment.
#
# THIS SCRIPT WRITES ONLY UNDER /home/ubuntu/closure-data/r4b_instruments/ when
# it is run by the instrument build.  `/home/ubuntu/closure-data/r4b/` is R4b's
# SOLVE run root and `guard_write_root` refuses any root inside it.

set -u -o pipefail

INSTRUMENT_ROOT="/home/ubuntu/closure-data/r4b_instruments"
SOLVE_ROOT="/home/ubuntu/closure-data/r4b"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOSURE="$(dirname "$HERE")"
REPO="$(dirname "$(dirname "$CLOSURE")")"

ROOT="$INSTRUMENT_ROOT"
CONFIG="pair"
CASES=""
MODE="run"
CHECK_DIR=""
USE_PGREP=1
MTIME_MIN=10
GIT_SINCE_MIN=60

# sec. 11.1, and these are ceilings, never defaults to be raised.
JOBS_MAX=2
NICE=10
SOLVER="${R4B_SOLVER:-simpleFoam}"
REQUIRED_FIELDS="U p k omega nut"

# The solver-name sweep.  Deliberately broad, and deliberately NOT the whole
# check.  `[F]oam` and the leading `[s]` keep the pattern from matching this
# script's own `pgrep` command line - the pkill-matches-its-own-shell trap,
# which once made a watcher report LAUNCH DETECTED because its pattern matched
# its own ssh command line.
SOLVER_PAT='([s]impleFoam|buoyant[A-Za-z]*Foam|kCorrectiveFrozen[A-Za-z]*|[A-Za-z]+[F]oam)'

die() { printf 'REFUSED [%s] %s\n' "$1" "$2" >&2; exit 2; }

guard_write_root() {
    local p; p="$(readlink -m "$1")"
    case "$p" in
        "$SOLVE_ROOT"|"$SOLVE_ROOT"/*)
            die SOLVE-ROOT-GUARD "$p is inside R4b's solve run root $SOLVE_ROOT; writing there would destroy R4b's pre-compute condition" ;;
    esac
    printf '%s' "$p"
}

usage() {
    cat <<'EOF'
run_r4b.sh [options]
  --root DIR         run root (default /home/ubuntu/closure-data/r4b_instruments)
  --config NAME      configuration subdirectory (default pair)
  --cases a,b,c      cases to drive (default: every case under --root)
  --capacity-only    print the pre-launch capacity reading and exit
  --no-pgrep         disable the process sweep entirely, to demonstrate that
                     the non-pgrep paths produce a reading BY THEMSELVES (L-41)
  --check-dir DIR    print COMPLETE / INCOMPLETE for one case directory and exit
                     (rc 0 complete, 1 incomplete)
  --dry-run          decide concurrency and print the plan; launch nothing
  --selftest         self-checks; rc 0
env R4B_SOLVER       the solver executable (default simpleFoam). B5 sets this
                     to a registered no-op; no simpleFoam is launched by the
                     instrument build.
EOF
}

# --------------------------------------------------------------- capacity
# Four readings, of which only ONE is a process sweep.
capacity_report() {
    local nproc load1 nsolv solvers top mtimes ncommits docket ndocket

    nproc="$(nproc)"
    load1="$(awk '{print $1}' /proc/loadavg)"

    # (1) the process sweep -- reported with its command lines, not just a count.
    solvers=""
    nsolv=0
    if [ "$USE_PGREP" -eq 1 ]; then
        solvers="$(pgrep -a -f "$SOLVER_PAT" 2>/dev/null \
                   | grep -v -e "run_r4b\.sh" -e "pgrep" -e "^$$ " || true)"
        [ -n "$solvers" ] && nsolv="$(printf '%s\n' "$solvers" | wc -l)"
    fi

    # (2) the top ten CPU consumers, WHATEVER THEY ARE.  sec. 11.2 step 4 is
    #     "not optional and it is why this check is not a pgrep count".
    top="$(ps -eo pid,pcpu,comm --sort=-pcpu 2>/dev/null | head -11 | tail -10)"

    # (3) run-directory mtimes -- a fleet agent writing fields is invisible to
    #     pgrep but not to the disk it is writing on.
    mtimes=0
    for r in /home/ubuntu/closure-data /home/ubuntu/certonomous-runs; do
        [ -d "$r" ] || continue
        mtimes=$(( mtimes + $(find "$r" -maxdepth 3 -type d -mmin -"$MTIME_MIN" \
                              2>/dev/null | wc -l) ))
    done

    # (4) the docket and recent commits -- live peers, also invisible to pgrep.
    ndocket=0
    docket="$REPO/docs/DOCKET.md"
    if [ -f "$docket" ]; then
        ndocket="$(grep -c -E 'RUNNING|IN FLIGHT|COMPUTING|LAUNCHED' "$docket" \
                   2>/dev/null || true)"
    fi
    ncommits="$(git -C "$REPO" log --since="$GIT_SINCE_MIN minutes ago" \
                --oneline 2>/dev/null | wc -l || true)"

    CAP_NPROC="$nproc"; CAP_LOAD1="$load1"; CAP_NSOLV="$nsolv"
    CAP_SOLVERS="$solvers"; CAP_TOP="$top"; CAP_MTIMES="$mtimes"
    CAP_NDOCKET="$ndocket"; CAP_NCOMMITS="$ncommits"

    printf 'pre-launch capacity reading (%s)\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '  nproc                       %s\n' "$nproc"
    printf '  load1 (/proc/loadavg)       %s\n' "$load1"
    printf '  foreign solvers (pgrep)     %s%s\n' "$nsolv" \
           "$([ "$USE_PGREP" -eq 1 ] || printf ' [SWEEP DISABLED]')"
    [ -n "$solvers" ] && printf '    %s\n' "$solvers"
    printf '  run dirs touched < %s min   %s\n' "$MTIME_MIN" "$mtimes"
    printf '  docket in-flight rows       %s\n' "$ndocket"
    printf '  commits < %s min            %s\n' "$GIT_SINCE_MIN" "$ncommits"
    printf '  top CPU consumers:\n'
    printf '    %s\n' "$top"
}

# sec. 11.3.  Echoes the concurrency, or "BLOCKED".  Reduces only.
decide_jobs() {
    local load1="$1" nsolv="$2" jobs
    if awk -v l="$load1" 'BEGIN{exit !(l >= 40)}'; then
        printf 'BLOCKED'; return 0
    fi
    if awk -v l="$load1" 'BEGIN{exit !(l >= 16)}' || [ "$nsolv" -ge 4 ]; then
        jobs=1
    else
        jobs="$JOBS_MAX"
    fi
    [ "$jobs" -gt "$JOBS_MAX" ] && jobs="$JOBS_MAX"   # can only ever reduce
    printf '%s' "$jobs"
}

# ------------------------------------------------------- skip-if-complete
# R4b sec. 4.2, applied through the RE-USED instruments, not re-implemented:
# `r4_lib.solve_complete` (rc, End line, converged-or-endTime, last time dir ==
# last solver iteration, required fields present AND newer than 0/ -- the age
# guard) plus `score_aposteriori.log_facts` for condition 6, the
# `Foam::sigFpe::sigHandler` frame.  The banner every OpenFOAM log opens with
# contains the phrase "Floating point exception", so matching that phrase marks
# every run diverged, healthy ones included; the handler frame is the signature
# of an actual trap.
case_complete() {
    local d="$1"
    python3 - "$d" "$CLOSURE" <<'PY'
import os, sys
d, closure = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(closure, "R4_sparta_build"))
sys.path.insert(0, os.path.join(closure, "_common"))
import r4_lib as R
import score_aposteriori as SA
ok, why, info = R.solve_complete(d)
if ok:
    lf = SA.log_facts(d)
    if lf.get("floating_point_exception"):
        ok, why = False, "Foam::sigFpe::sigHandler frame in log (sec. 4.2 cond 6)"
    else:
        why = f"{why}; stop_state={info.get('stop_state')}"
print(("COMPLETE" if ok else "INCOMPLETE") + " " + why)
sys.exit(0 if ok else 1)
PY
}

# ------------------------------------------------------------------ solve
# Nothing here signals, stops or inspects any foreign process.  The only
# process this function ever touches is the one it starts itself.
solve_one() {
    local d="$1" t0 t1 rc
    if case_complete "$d" >/dev/null 2>&1; then
        printf '[skip] %s already COMPLETE under sec. 4.2\n' "$d"
        return 0
    fi
    if [ ! -d "$d" ]; then
        printf '[miss] %s does not exist\n' "$d" >&2
        return 0
    fi
    t0="$(date +%s)"
    (
        cd "$d" || exit 97
        # rc is captured INSIDE the wrapper.  A wrapper's own exit status is
        # not the solver's; capturing it outside reports 0 for every outcome.
        nice -n "$NICE" "$SOLVER" > log.solve 2>&1
        printf '%s\n' "$?" > rc
    )
    t1="$(date +%s)"
    printf '%s\n' "$(( t1 - t0 ))" > "$d/wall_seconds"
    rc="$(cat "$d/rc" 2>/dev/null || printf 'none')"
    printf '[done] %s rc=%s wall_seconds=%s\n' "$d" "$rc" "$(( t1 - t0 ))"
}

# --------------------------------------------------------------- selftest
selftest() {
    local fails=0 n=0
    chk() { n=$((n+1)); if [ "$2" = 1 ]; then printf '  [ok ] %s %s\n' "$1" "${3:-}"
            else printf '  [FAIL] %s %s\n' "$1" "${3:-}"; fails=$((fails+1)); fi; }

    # (1) IT NEVER KILLS.  Mechanical, on this file's own bytes.
    #
    # The verbs are assembled from split literals so the PATTERN cannot match
    # the LINE THAT BUILDS IT.  The first draft of this check reported a hit on
    # its own grep -- the same shape as the watcher whose pgrep matched its own
    # ssh command line, and as pkill matching its own shell.  A check that
    # cannot exonerate a clean file is measuring itself, not the file.
    # Comment lines are excluded: the header of this script names these verbs
    # in prose, and a verb in a comment cannot execute.
    local kv1 kv2 kv3 kv4 kv5 hits
    kv1="k""ill"; kv2="pk""ill"; kv3="k""illall"; kv4="f""user"; kv5="--sig""nal"
    hits="$(grep -n -E "(^|[^[:alnum:]_])($kv1|$kv2|$kv3|$kv4)([^[:alnum:]_]|$)|$kv5" \
            "${BASH_SOURCE[0]}" | grep -v -E '^[0-9]+:[[:space:]]*#' || true)"
    [ -z "$hits" ] && chk no_kill_verbs 1 || chk no_kill_verbs 0 "$hits"

    # (1b) the PLANTED CONTROL for that check: a file that DOES carry a kill
    #      verb must be flagged.  Without it, a zero above is a zero from a
    #      reader never shown able to see a non-zero (standing rule 3).
    local plant; plant="$(mktemp)"
    printf 'x=1\n%s -9 12345\n' "$kv2" > "$plant"
    local phits
    phits="$(grep -n -E "(^|[^[:alnum:]_])($kv1|$kv2|$kv3|$kv4)([^[:alnum:]_]|$)|$kv5" \
             "$plant" | grep -v -E '^[0-9]+:[[:space:]]*#' || true)"
    rm -f "$plant"
    [ -n "$phits" ] && chk kill_check_sees_a_planted_kill 1 \
        || chk kill_check_sees_a_planted_kill 0 "reader is blind"

    # (2) the concurrency rule only ever reduces, and BLOCKS above 40.
    chk jobs_quiet_box "$([ "$(decide_jobs 1.0 0)" = 2 ] && echo 1 || echo 0)" \
        "-> $(decide_jobs 1.0 0)"
    chk jobs_loaded_box "$([ "$(decide_jobs 20.0 0)" = 1 ] && echo 1 || echo 0)" \
        "-> $(decide_jobs 20.0 0)"
    chk jobs_many_solvers "$([ "$(decide_jobs 1.0 4)" = 1 ] && echo 1 || echo 0)" \
        "-> $(decide_jobs 1.0 4)"
    chk jobs_blocked "$([ "$(decide_jobs 41.0 0)" = BLOCKED ] && echo 1 || echo 0)" \
        "-> $(decide_jobs 41.0 0)"
    chk jobs_never_above_max \
        "$([ "$(decide_jobs 0.0 0)" -le "$JOBS_MAX" ] 2>/dev/null && echo 1 || echo 0)"

    # (3) the solve-root guard refuses, and the instrument root is allowed.
    ( guard_write_root "$SOLVE_ROOT/x" >/dev/null 2>&1 )
    chk solve_root_guard "$([ $? -eq 2 ] && echo 1 || echo 0)"
    ( guard_write_root "$INSTRUMENT_ROOT/x" >/dev/null 2>&1 )
    chk instrument_root_allowed "$([ $? -eq 0 ] && echo 1 || echo 0)"

    # (4) nice is present and is 10, and JOBS_MAX is 2. sec. 11.1.
    chk nice_is_10 "$([ "$NICE" = 10 ] && echo 1 || echo 0)" "NICE=$NICE"
    chk jobs_max_is_2 "$([ "$JOBS_MAX" = 2 ] && echo 1 || echo 0)"
    chk nice_on_every_solve \
        "$(grep -cq 'nice -n "\$NICE" "\$SOLVER"' "${BASH_SOURCE[0]}" && echo 1 || echo 0)"

    # (5) the solver sweep cannot match this script's own command line.
    chk pattern_excludes_self \
        "$(printf '%s' "$SOLVER_PAT" | grep -q '\[s\]impleFoam' && echo 1 || echo 0)"

    # (6) the capacity check runs and produces all four readings, and the
    #     non-pgrep paths produce a reading BY THEMSELVES (L-41).
    local save="$USE_PGREP"
    USE_PGREP=0
    capacity_report >/dev/null 2>&1
    chk nonpgrep_paths_alone \
        "$([ -n "${CAP_LOAD1:-}" ] && [ -n "${CAP_MTIMES:-}" ] && \
           [ -n "${CAP_NDOCKET:-}" ] && [ -n "${CAP_NCOMMITS:-}" ] && \
           echo 1 || echo 0)" \
        "load1=${CAP_LOAD1:-} mtimes=${CAP_MTIMES:-} docket=${CAP_NDOCKET:-} commits=${CAP_NCOMMITS:-}"
    chk nonpgrep_mtimes_nonzero \
        "$([ "${CAP_MTIMES:-0}" -gt 0 ] 2>/dev/null && echo 1 || echo 0)" \
        "mtimes=${CAP_MTIMES:-0}"
    USE_PGREP="$save"

    printf 'run_r4b.sh --selftest: %s/%s\n' "$((n-fails))" "$n"
    [ "$fails" -eq 0 ] || return 1
    return 0
}

# ------------------------------------------------------------------- main
while [ $# -gt 0 ]; do
    case "$1" in
        --root) ROOT="$2"; shift 2 ;;
        --config) CONFIG="$2"; shift 2 ;;
        --cases) CASES="$2"; shift 2 ;;
        --capacity-only) MODE="capacity"; shift ;;
        --no-pgrep) USE_PGREP=0; shift ;;
        --check-dir) MODE="check"; CHECK_DIR="$2"; shift 2 ;;
        --dry-run) MODE="dry"; shift ;;
        --selftest) MODE="selftest"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) die USAGE "unknown option $1" ;;
    esac
done

case "$MODE" in
    selftest) selftest; exit $? ;;
    check)
        [ -n "$CHECK_DIR" ] || die USAGE "--check-dir needs a directory"
        case_complete "$CHECK_DIR"; exit $? ;;
    capacity)
        capacity_report
        printf 'registered concurrency -> %s\n' \
               "$(decide_jobs "$CAP_LOAD1" "$CAP_NSOLV")"
        exit 0 ;;
esac

ROOT="$(guard_write_root "$ROOT")"
[ -d "$ROOT" ] || die ROOT-ABSENT "$ROOT does not exist; build the cases first"

capacity_report
JOBS="$(decide_jobs "$CAP_LOAD1" "$CAP_NSOLV")"
printf 'registered concurrency -> %s\n' "$JOBS"
if [ "$JOBS" = "BLOCKED" ]; then
    printf 'BLOCKED - cause: compute capacity (load1 %s on %s cores). ' \
           "$CAP_LOAD1" "$CAP_NPROC" >&2
    printf 'Acquisition path: re-check when the box clears. No solve started.\n' >&2
    exit 3
fi

if [ -n "$CASES" ]; then
    LIST="$(printf '%s' "$CASES" | tr ',' ' ')"
else
    LIST="$(cd "$ROOT" && ls -d */ 2>/dev/null | tr -d '/' | tr '\n' ' ')"
fi

printf 'solver=%s nice=%s jobs=%s config=%s\n' "$SOLVER" "$NICE" "$JOBS" "$CONFIG"
if [ "$MODE" = "dry" ]; then
    for c in $LIST; do
        d="$ROOT/$c/$CONFIG"
        printf '[plan] %s %s\n' "$d" "$(case_complete "$d" 2>/dev/null || true)"
    done
    exit 0
fi

running=0
for c in $LIST; do
    d="$ROOT/$c/$CONFIG"
    solve_one "$d" &
    running=$((running+1))
    if [ "$running" -ge "$JOBS" ]; then wait -n 2>/dev/null || wait; running=$((running-1)); fi
done
wait
printf 'run_r4b.sh: finished %s case(s) under %s\n' \
       "$(printf '%s' "$LIST" | wc -w)" "$ROOT"
