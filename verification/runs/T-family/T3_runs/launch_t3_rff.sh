#!/usr/bin/env bash
# ==========================================================================
# T3 R_ff LAUNCHER -- rc-CAPTURING, DETACHED, QUEUE-COMPATIBLE.
# Modelled on scripts/launch_k0f.sh (its header records the measured trap:
# `setsid timeout ... ; rc=$?` writes rc=0 for a crashed solver because setsid
# forks).  This file is the WRAPPER: the caller (an agent, or the queue) starts
# it and returns; it re-execs itself ONCE under setsid, and inside the detached
# copy the solver runs under `timeout` in the FOREGROUND with no setsid between
# them, so $? is genuinely the solver's status.  The caller's rc is meaningless
# and is never used.
#
# Registered in docs/campaigns/T-family/T3_R_FF_PREREGISTRATION.md: the cap,
# ranks and timeout are NOT free arguments -- --timeout and --ranks must equal
# the registered values or this file REFUSES (rule 12: a cap is not widened at
# the command line).  Statuses, all measured on this box (launch_k0f.sh header):
#   child exits n -> n ; child dies on signal n -> 128+n ; cap expires -> 124.
# No --preserve-status (it collides expiry with SIGTERM).  capped = wall_s >=
# timeout_s is written as an INDEPENDENT expiry witness (run_one_t11.sh).
# ==========================================================================
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REG_RANKS=8; REG_TIMEOUT_S=205500; REG_CAP_CORE_MIN=27400     # registered, S7 of the prereg
SOLVER=buoyantBoussinesqSimpleFoam
FOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc

usage() { cat >&2 <<'U'
usage: launch_t3_rff.sh --case-dir DIR --timeout SECONDS --ranks N [--no-detach]
  --case-dir  the R_ff case directory; STATUS.<basename> is written to its PARENT
  --timeout   MUST equal the registered 205500 s (= 27400 core-min x 60 / 8)
  --ranks     MUST equal the registered 8
  --no-detach run in the foreground (selftest / ARM 2 use)
U
exit 2; }
CASE_DIR=""; TIMEOUT_S=""; RANKS=""; DETACH=1
while [ $# -gt 0 ]; do case "$1" in
  --case-dir) CASE_DIR="${2:-}"; shift 2;; --timeout) TIMEOUT_S="${2:-}"; shift 2;;
  --ranks) RANKS="${2:-}"; shift 2;; --no-detach) DETACH=0; shift;; *) usage;; esac; done
[ -n "$CASE_DIR" ] && [ -n "$TIMEOUT_S" ] && [ -n "$RANKS" ] || usage
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
[ "$RANKS" = "$REG_RANKS" ] || { echo "REFUSE: --ranks=$RANKS; R_ff is registered at $REG_RANKS ranks (prereg S7)" >&2; exit 2; }
[ "$TIMEOUT_S" = "$REG_TIMEOUT_S" ] || { echo "REFUSE: --timeout=$TIMEOUT_S; registered timeout is $REG_TIMEOUT_S s (cap $REG_CAP_CORE_MIN core-min x 60 / $REG_RANKS)" >&2; exit 2; }
CASE_DIR="$(cd "$CASE_DIR" && pwd)"; ROOT="$(dirname "$CASE_DIR")"; CASE="$(basename "$CASE_DIR")"
[ "$CASE" = "R_ff" ] || { echo "REFUSE: this launcher is registered for R_ff only; got $CASE" >&2; exit 2; }
STATUS="$ROOT/STATUS.$CASE"

# --- launch guards, BEFORE detaching and before anything is written ---------
[ -e "$STATUS" ] && { echo "REFUSE: $STATUS exists -- a completed run's record is never overwritten" >&2; exit 2; }
[ -e "$CASE_DIR/0" ] && { echo "REFUSE: G3: $CASE already has 0/ (an earlier run started); the age guard could not be evaluated" >&2; exit 2; }
while IFS= read -r d; do [ -n "$d" ] && { echo "REFUSE: G3: time directory $(basename "$d") already exists" >&2; exit 2; }; done \
  < <(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?' 2>/dev/null)
while IFS= read -r d; do [ -n "$d" ] && { echo "REFUSE: G3: processor directory $(basename "$d") already exists" >&2; exit 2; }; done \
  < <(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -name 'processor[0-9]*' 2>/dev/null)
[ -d "$CASE_DIR/0.orig" ] || { echo "REFUSE: no 0.orig to arm from" >&2; exit 2; }
[ -f "$CASE_DIR/constant/polyMesh/points" ] || { echo "REFUSE: no mesh -- the birth certificate (check_t3_mesh.py R_ff) has not been issued" >&2; exit 2; }
# AMENDMENT 2 (2026-08-26, pre-first-compute): under the queue runner's launch form
# `setsid nohup bash -c 'cd <cwd>; <argv> ...'` (scripts/queue_runner.py) the launcher's
# OWN ANCESTOR -- the runner's wrapper shell -- holds the case directory as cwd, and the
# G2 guard below refused ANY cwd-holder, its own lineage included; measured: one
# zero-compute refusal (launcher.queue.out: "REFUSE: G2: pid 313462 already running in
# R_ff").  Same repair as launch_t10aR2.sh (9fa66065) and launch_t4b.sh (51618879):
# this launcher's own lineage (itself, its ancestors up to pid 1, its descendants) is
# excluded from the scan; ANY FOREIGN process in the case directory is still refused.
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
    echo "REFUSE: G2: pid $q already running in $CASE" >&2; exit 2
done

if [ "$DETACH" = "1" ] && [ "${T3RFF_DETACHED:-}" != "1" ]; then
    T3RFF_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" --ranks "$RANKS" --no-detach \
        </dev/null >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; STATUS will appear at $STATUS"; exit 0
fi

write_status() {  # rc wall capped checkmesh_rc decompose_rc reconstruct_rc note
    tmp="$STATUS.tmp.$$"
    { echo "case=$CASE"; echo "rc=$1"; echo "wall_s=$2"; echo "ranks=$RANKS"
      echo "core_min=$(awk -v w="$2" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')"
      echo "cap_core_min=$REG_CAP_CORE_MIN"; echo "timeout_s=$TIMEOUT_S"; echo "capped=$3"
      echo "checkmesh_rc=$4"; echo "decomposepar_rc=$5"; echo "reconstructpar_rc=$6"
      echo "solver=$SOLVER"; echo "solver_path=${SOLVER_PATH:-unresolved}"; echo "note=$7"
      echo "started_utc=$(date -u -d "@${T0:-0}" +%Y-%m-%dT%H:%M:%SZ)"; echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "$tmp"; mv -f "$tmp" "$STATUS"
}

# --- environment; the solver must resolve BEFORE anything is armed ---------
[ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
set +u; . "$FOAM_BASHRC" >/dev/null 2>&1 || true; set -u
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: $SOLVER not resolvable; nothing ran, no STATUS written" >&2; exit 2; }
command -v mpirun >/dev/null 2>&1 || { echo "REFUSE: mpirun not resolvable" >&2; exit 2; }
if ! python3 "$SELF/../../../../scripts/check_case_provenance.py" --case "$CASE_DIR" >>"$CASE_DIR/log.launch" 2>&1; then
    echo "REFUSE: $CASE failed check_case_provenance.py; no solver started, no STATUS written" >&2; exit 2; fi

# --- arm: 0 from 0.orig, 0/T touched LAST (the age-guard datum) ------------
cd "$CASE_DIR" || exit 2
cp -r 0.orig 0 || { echo "REFUSE: could not create 0/ from 0.orig" >&2; exit 2; }
sleep 1; touch 0/T
checkMesh > log.checkMesh.run 2>&1; CHECKMESH_RC=$?
decomposePar -force > log.decomposePar 2>&1; DECOMP_RC=$?
if [ "$DECOMP_RC" -ne 0 ]; then T0=$(date +%s); write_status 126 0 no "$CHECKMESH_RC" "$DECOMP_RC" na DECOMPOSE_FAILED; exit 126; fi

# --- the solver, FOREGROUND, under timeout, rc captured from it ------------
T0=$(date +%s)
timeout --signal=TERM --kill-after=120 "$TIMEOUT_S" \
    mpirun -np "$RANKS" "$SOLVER_PATH" -parallel -case "$CASE_DIR" > log.solve 2>&1
RC=$?
T1=$(date +%s); WALL=$((T1 - T0))
if [ "$WALL" -ge "$TIMEOUT_S" ]; then CAPPED=yes; else CAPPED=no; fi
reconstructPar -newTimes > log.reconstructPar 2>&1; RECON_RC=$?
NOTE=clean
if [ "$RC" = "124" ]; then NOTE=CAP_EXPIRED_or_child_exit_124
elif [ "$RC" -gt 128 ] 2>/dev/null; then NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then NOTE=SOLVER_NONZERO_EXIT; fi
write_status "$RC" "$WALL" "$CAPPED" "$CHECKMESH_RC" "$DECOMP_RC" "$RECON_RC" "$NOTE"
echo "$CASE finished: rc=$RC wall=${WALL}s capped=$CAPPED reconstruct_rc=$RECON_RC note=$NOTE -> $STATUS"
exit "$RC"
