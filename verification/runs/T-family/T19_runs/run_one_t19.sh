#!/usr/bin/env bash
# ==========================================================================
# T19 CASE LAUNCHER (2-D laminar forced convection, buoyantBoussinesqSimpleFoam) -- run ONE registered level, capture the SOLVER's rc in
# this wrapper, write STATUS.<case>.  Modelled line-for-line on
# run_one_t11.sh's rc-in-wrapper pattern and launch_t4b.sh's queue interface:
#
#   * the solver runs in THIS wrapper's FOREGROUND under `timeout`, with no
#     `setsid` between them, so `$?` is the solver's status (measured on this
#     box: `setsid timeout ... bash -c 'exit 7'` returns 0, `setsid --wait`
#     returns 7 -- K0f header);
#   * rc is captured INSIDE and written to STATUS.<case> in the run root (the
#     file mark_done_t19.py reads);
#   * `capped` = (wall_s >= timeout_s) is the INDEPENDENT expiry witness -- rc
#     124 collides with a solver that itself exits 124, and 137 with an OOM
#     kill (measured, GNU coreutils 9.4); it is an INFRASTRUCTURE field
#     (L-342): it labels a non-zero rc, it never voids a run;
#   * a PRE-FLIGHT REFUSAL writes NO STATUS: nothing ran, so there is no rc,
#     and inventing one is the back-dating this file exists to prevent;
#   * the registered cap is READ from T19_registered.json and a --timeout that
#     is not EQUAL to it is REFUSED: a caller can neither widen a cap that rule
#     12 says stops the run nor narrow one into a manufactured cap-stop;
#     --ranks must equal the registered 1;
#   * time directories are matched by a REGEX with fullmatch semantics, NEVER a
#     shell glob (`[0-9]*` matches `0.orig`; check_launcher_can_launch.py ARM 1);
#   * the OpenFOAM bashrc is sourced with `set -u` lifted (ARM 3, L-339);
#   * an existing STATUS.<case> is REFUSED before anything is written;
#   * `exit "$RC"` is the LAST line: the wrapper reports the solver's own
#     status to its caller, never 0.
#
# usage: run_one_t19.sh --case-dir DIR --timeout SECONDS [--ranks 1]
#                       [--solver buoyantBoussinesqSimpleFoam] [--foam-bashrc F]
#                       [--no-detach]
#   --timeout   registered per-case cap in wall seconds = cap_core_min*60/ranks
#   --no-detach run in the foreground (the queue runner already detaches; the
#               queue entry passes this flag)
# ==========================================================================
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGJSON="$SELF/T19_registered.json"

usage() { sed -n '/^# usage:/,/^# ====/p' "$0" >&2; exit 2; }

CASE_DIR=""; TIMEOUT_S=""; RANKS=1
SOLVER="buoyantBoussinesqSimpleFoam"; DETACH=1
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
while [ $# -gt 0 ]; do
    case "$1" in
        --case-dir) CASE_DIR="${2:-}"; shift 2 ;;
        --timeout)  TIMEOUT_S="${2:-}"; shift 2 ;;
        --ranks)    RANKS="${2:-}"; shift 2 ;;
        --solver)   SOLVER="${2:-}"; shift 2 ;;
        --foam-bashrc) FOAM_BASHRC="${2:-}"; shift 2 ;;
        --no-detach) DETACH=0; shift ;;
        *) usage ;;
    esac
done
[ -n "$CASE_DIR" ] && [ -n "$TIMEOUT_S" ] || usage
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
case "$RANKS" in ''|*[!0-9]*) echo "REFUSE: --ranks must be an integer" >&2; exit 2;; esac
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout must be integer seconds" >&2; exit 2;; esac
[ "$RANKS" = "1" ] || { echo "REFUSE: T19 is registered SERIAL (ranks 1 on every level); --ranks=$RANKS" >&2; exit 2; }

CASE_DIR="$(cd "$CASE_DIR" && pwd)"
ROOT="$(dirname "$CASE_DIR")"
CASE="$(basename "$CASE_DIR")"
STATUS="$ROOT/STATUS.$CASE"

# --- the registered cap: a --timeout that is not EQUAL to it is refused ------
if [ -f "$REGJSON" ]; then
    REG_T=$(python3 -c "import json,sys; c=json.load(open(sys.argv[1]))['cases'].get(sys.argv[2]); print(c['timeout_s'] if c else 'UNREGISTERED')" "$REGJSON" "$CASE" 2>/dev/null || echo UNREADABLE)
    case "$REG_T" in
        UNREGISTERED) echo "REFUSE: $CASE is not a registered T19 case in $REGJSON" >&2; exit 2 ;;
        UNREADABLE)   echo "REFUSE: cannot read the registered cap from $REGJSON" >&2; exit 2 ;;
    esac
    [ "$TIMEOUT_S" -eq "$REG_T" ] || { echo "REFUSE: --timeout $TIMEOUT_S is not the registered timeout_s=$REG_T for $CASE (rule 12: a cap is neither widened nor narrowed at launch -- a narrower one manufactures a cap-stop)" >&2; exit 2; }
else
    echo "REFUSE: registered JSON $REGJSON is missing; the cap cannot be checked" >&2; exit 2
fi

# --- a completed run's record is never overwritten ---------------------------
[ -e "$STATUS" ] && { echo "REFUSE: $STATUS exists -- a completed run's record is never overwritten; nothing ran, nothing written" >&2; exit 2; }

# --- detach ONCE by re-executing this file in a new session ------------------
if [ "$DETACH" = "1" ] && [ "${T19_DETACHED:-}" != "1" ]; then
    T19_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" \
        --ranks "$RANKS" --solver "$SOLVER" --foam-bashrc "$FOAM_BASHRC" \
        --no-detach </dev/null >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; STATUS will appear at $STATUS"
    exit 0
fi

write_status() {   # rc wall checkmesh_rc capped note
    tmp="$STATUS.tmp.$$"
    {
      echo "case=$CASE"
      echo "rc=$1"
      echo "wall_s=$2"
      echo "ranks=$RANKS"
      echo "core_min=$(awk -v w="$2" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')"
      echo "timeout_s=$TIMEOUT_S"
      echo "capped=$4"
      echo "checkmesh_rc=$3"
      echo "solver=$SOLVER"
      echo "solver_path=${SOLVER_PATH:-unresolved}"
      echo "note=$5"
      echo "started_utc=$(date -u -d "@$T0" +%Y-%m-%dT%H:%M:%SZ)"
      echo "ended_utc=$(date -u -d "@$T1" +%Y-%m-%dT%H:%M:%SZ)"
    } > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

# --- 0. the solver must be reachable (K0f attempt 1: rc=127 x7) ------------
if [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
    set +u
    # shellcheck disable=SC1090
    . "$FOAM_BASHRC" >/dev/null 2>&1 || true
    set -u
fi
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' is NOT RESOLVABLE after sourcing ${FOAM_BASHRC}. Nothing ran, no STATUS written." >&2; exit 2; }

# --- 1. the launch guard: no 0/, no numeric time directory, 0.orig present ---
[ -e "$CASE_DIR/0" ] && { echo "REFUSE: $CASE already has a 0/ directory (the age guard could not be evaluated)" >&2; exit 2; }
while IFS= read -r d; do
    [ -n "$d" ] && { echo "REFUSE: $CASE already has time directory $(basename "$d")" >&2; exit 2; }
done < <(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?' 2>/dev/null)
[ -d "$CASE_DIR/0.orig" ] || { echo "REFUSE: $CASE has no 0.orig to arm from" >&2; exit 2; }
[ -f "$CASE_DIR/constant/polyMesh/owner" ] || { echo "REFUSE: $CASE has no mesh (constant/polyMesh/owner) -- run build_t19.py" >&2; exit 2; }
for f in T U p_rgh alphat; do
    [ -f "$CASE_DIR/0.orig/$f" ] || { echo "REFUSE: 0.orig/$f missing -- the registered field set is incomplete" >&2; exit 2; }
done
# LINEAGE-AWARE foreign-process guard (T10aR2 AMENDMENT 1, 9fa66065): under the
# queue runner's launch form `setsid nohup bash -c 'cd <cwd>; <argv> ...'` the
# launcher's OWN ANCESTOR -- the runner's wrapper shell -- holds the case directory
# as cwd; a guard that excluded only $$ refused its own launch (measured: three
# zero-compute refusals per rung, three rungs on 2026-08-26). This launcher's own
# lineage (itself, its ancestors up to pid 1, its descendants) is excluded from the
# scan; ANY FOREIGN process whose cwd is the case directory is still refused.
ppid_of() { sed 's/.*) //' "/proc/$1/stat" 2>/dev/null | awk '{print $2}'; }
LINEAGE=" $$ "; a="$PPID"
while [ -n "$a" ] && [ "$a" != "0" ] && [ "$a" != "1" ]; do LINEAGE="$LINEAGE$a "; a="$(ppid_of "$a")"; done
own_lineage() {   # returns 0 when pid $1 is this shell, one of its ancestors, or one of its descendants
    case "$LINEAGE" in *" $1 "*) return 0;; esac
    a="$1"
    while [ -n "$a" ] && [ "$a" != "0" ] && [ "$a" != "1" ]; do
        [ "$a" = "$$" ] && return 0
        a="$(ppid_of "$a")"
    done
    return 1
}
for p in /proc/[0-9]*; do
    q="${p#/proc/}"
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CASE_DIR" ] || continue
    own_lineage "$q" && continue
    echo "REFUSE: pid $q is already running in $CASE (foreign process, outside this launcher's lineage)" >&2; exit 2
done

# --- 1b. provenance: no compressible-family token in an incompressible case --
PROV="$SELF/../../../../scripts/check_case_provenance.py"
[ -f "$PROV" ] || PROV="/home/ubuntu/Certonomous/scripts/check_case_provenance.py"   # a scratch copy of this tree still checks the real script
[ -f "$PROV" ] || { echo "REFUSE: check_case_provenance.py not found; no solver started, no STATUS written" >&2; exit 2; }
if ! python3 "$PROV" --case "$CASE_DIR" >>"$CASE_DIR/log.launch" 2>&1; then
    echo "REFUSE: $CASE failed check_case_provenance.py; no solver started, no STATUS written" >&2; exit 2; fi

# --- 2. checkMesh, recorded rather than assumed (infrastructure) -------------
checkMesh -case "$CASE_DIR" > "$CASE_DIR/log.checkMesh" 2>&1
CHECKMESH_RC=$?

# --- 3. arm 0/ from 0.orig; 0/T touched LAST (the age-guard datum) ----------
cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/ from 0.orig" >&2; exit 2; }
sleep 1
touch "$CASE_DIR/0/U" "$CASE_DIR/0/p_rgh" "$CASE_DIR/0/alphat" && touch "$CASE_DIR/0/T" || { echo "REFUSE: could not touch 0/T" >&2; exit 2; }

# --- 4. the solver, in the FOREGROUND, rc captured from it ------------------
T0=$(date +%s)
timeout --signal=TERM --kill-after=60 "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.solve" 2>&1
RC=$?
T1=$(date +%s)
WALL=$((T1 - T0))
if [ "$WALL" -ge "$TIMEOUT_S" ]; then CAPPED=yes; else CAPPED=no; fi
NOTE=clean
if [ "$RC" = "124" ]; then NOTE=CAP_EXPIRED_or_child_exit_124
elif [ "$RC" -gt 128 ] 2>/dev/null; then NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then NOTE=SOLVER_NONZERO_EXIT
fi
write_status "$RC" "$WALL" "$CHECKMESH_RC" "$CAPPED" "$NOTE"
echo "$CASE finished: rc=$RC wall=${WALL}s capped=$CAPPED note=$NOTE  ->  $STATUS"
# EXIT WITH THE SOLVER'S OWN rc, NEVER 0: a launcher that ends `exit 0` lets a
# queue driver chaining on && march straight past a crash.
exit "$RC"
