#!/usr/bin/env bash
# ==========================================================================
# K0e LAUNCHER -- forced-convection flat plate, campaign F14 cooling ladder.
# Registered by docs/campaigns/F14-cooling-ladder/K0e_PREREGISTRATION.md.
#
# rc-CAPTURING, DETACHABLE, QUEUE-COMPATIBLE.  Modelled on
# scripts/launch_k0f_ext1.sh, whose header records the measured trap that K0d
# fell into: `setsid timeout ... ; rc=$?` writes rc=0 for a crashed solver
# because setsid forks, so the rc is the FORK's, not the solver's.  K0d had no
# launcher at all and therefore no STATUS file, and clause 1 of the strict
# completion rule was unverifiable for both of its arms
# (K0d_FORENSICS_2026-08-25.md ADDENDUM 4, section D2).  THIS FILE EXISTS SO
# THAT K0e CANNOT REPEAT THAT.
#
# ORDER OF OPERATIONS, AND WHY
#   1. guards (G2 lineage, solver resolvable, no STATUS already present)
#   2. build_k0e.py   -- builds the case; ITS OWN age guard refuses a tree that
#                        already holds 0/ or a time directory
#   3. touch 0/T      -- LAST, immediately before the solver starts.  Standing
#                        rule 4 dates the run from the case's own 0/T, and it is
#                        only a valid datum if nothing writes it afterwards.
#   4. solver, FOREGROUND, under `timeout`, so $? is genuinely the solver's
#   5. reconstructPar -latestTime, then writeCellCentres -- the grader's inputs
#   6. STATUS.<arm> written with the CAPTURED rc
#
# This file is SINGLE-REGION: one mesh, one case, no regions.  `<case>/0/T`
# is therefore the correct age-guard datum, and step 3 is what makes it so.
# ==========================================================================
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REG_END=9000          # the reference's own endTime; K0e matches it exactly
REG_RANKS=2           # the reference's own decomposition; M4 requires it

usage() { cat >&2 <<'U'
usage: launch_k0e.sh --arm FP_T10|FP_T00 --root DIR --timeout SECONDS
                     [--ranks 2] [--reference DIR] [--foam-bashrc PATH] [--no-detach]
  --arm       the registered K0e arm
  --root      K0e_runs; the case is built at <root>/<arm>, STATUS at <root>/STATUS.<arm>
  --timeout   the arm's registered per-run CAP, converted: cap_core_min x 60 / ranks
U
exit 2; }

ARM=""; ROOT=""; TIMEOUT_S=""; RANKS=$REG_RANKS; DETACH=1
SOLVER=buoyantBoussinesqSimpleFoam
REFERENCE=/home/ubuntu/certonomous-runs/tmr-flatplate-finer
FOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc
while [ $# -gt 0 ]; do case "$1" in
  --arm) ARM="${2:-}"; shift 2;; --root) ROOT="${2:-}"; shift 2;;
  --timeout) TIMEOUT_S="${2:-}"; shift 2;; --ranks) RANKS="${2:-}"; shift 2;;
  --reference) REFERENCE="${2:-}"; shift 2;;
  --foam-bashrc) FOAM_BASHRC="${2:-}"; shift 2;; --no-detach) DETACH=0; shift;;
  *) usage;; esac; done
[ -n "$ARM" ] && [ -n "$ROOT" ] && [ -n "$TIMEOUT_S" ] || usage
case "$ARM" in FP_T10|FP_T00) ;; *) echo "REFUSE: unregistered arm '$ARM'" >&2; exit 2;; esac
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout must be integer seconds" >&2; exit 2;; esac
[ "$RANKS" = "$REG_RANKS" ] || { echo "REFUSE: K0e is registered at $REG_RANKS ranks -- the momentum control M4 compares PROCESSOR-LOCAL fields against a 2-rank reference and is meaningless at any other rank count; --ranks=$RANKS" >&2; exit 2; }
[ -d "$REFERENCE" ] || { echo "REFUSE: no reference case $REFERENCE" >&2; exit 2; }

mkdir -p "$ROOT" || { echo "REFUSE: cannot create $ROOT" >&2; exit 2; }
ROOT="$(cd "$ROOT" && pwd)"
CASE_DIR="$ROOT/$ARM"; STATUS="$ROOT/STATUS.$ARM"
[ -e "$STATUS" ] && { echo "REFUSE: $STATUS exists -- this arm has already run; a second run is not authorised by the registration" >&2; exit 2; }

# G2, lineage-aware: any FOREIGN process already in the case directory refuses.
ppid_of() { sed 's/.*) //' "/proc/$1/stat" 2>/dev/null | awk '{print $2}'; }
LINEAGE=" $$ "; a="$PPID"
while [ -n "$a" ] && [ "$a" != "0" ] && [ "$a" != "1" ]; do LINEAGE="$LINEAGE$a "; a="$(ppid_of "$a")"; done
own_lineage() {
    case "$LINEAGE" in *" $1 "*) return 0;; esac
    a="$1"
    while [ -n "$a" ] && [ "$a" != "0" ] && [ "$a" != "1" ]; do
        [ "$a" = "$$" ] && return 0
        a="$(ppid_of "$a")"
    done
    return 1
}
if [ -d "$CASE_DIR" ]; then
for p in /proc/[0-9]*; do
    q="${p#/proc/}"
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CASE_DIR" ] || continue
    own_lineage "$q" && continue
    echo "REFUSE: G2: pid $q already running in $ARM" >&2; exit 2
done
fi

if [ "$DETACH" = "1" ] && [ "${K0E_DETACHED:-}" != "1" ]; then
    mkdir -p "$ROOT/launch/$ARM"
    K0E_DETACHED=1 exec setsid "$0" --arm "$ARM" --root "$ROOT" --timeout "$TIMEOUT_S" \
        --ranks "$RANKS" --reference "$REFERENCE" --foam-bashrc "$FOAM_BASHRC" \
        --no-detach </dev/null >>"$ROOT/launch/$ARM/log.launch" 2>&1 &
    echo "launched K0e $ARM detached; STATUS will appear at $STATUS"; exit 0
fi

LOGDIR="$ROOT/launch/$ARM"; mkdir -p "$LOGDIR"
T0=0
write_status() {  # rc wall note
    tmp="$STATUS.tmp.$$"
    printf 'rc=%s wall=%s checkMesh_rc=na timeout_s=%s ranks=%s solver=%s solver_path=%s case=%s arm=%s note=%s endTime=%s reconstruct_rc=%s cellcentres_rc=%s started_utc=%s ended_utc=%s\n' \
        "$1" "$2" "$TIMEOUT_S" "$RANKS" "$SOLVER" "${SOLVER_PATH:-unresolved}" "$ARM" "$ARM" "$3" "$REG_END" "${RECON_RC:-na}" "${CC_RC:-na}" \
        "$(date -u -d "@${T0:-0}" +%Y-%m-%dT%H:%M:%SZ)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$tmp"
    mv -f "$tmp" "$STATUS"
}

# --- environment; the solver must resolve BEFORE anything is built ---------
[ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
set +u; . "$FOAM_BASHRC" >/dev/null 2>&1 || true; set -u
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' is NOT RESOLVABLE; nothing ran, no STATUS written" >&2; exit 2; }

# --- build (its own age guard refuses a tree that already holds an answer) --
if ! python3 "$SELF/build_k0e.py" --arm "$ARM" --reference "$REFERENCE" \
        --out-root "$ROOT" --foam-bashrc "$FOAM_BASHRC" >>"$LOGDIR/log.build" 2>&1; then
    echo "REFUSE: build_k0e.py failed for $ARM; no solver started, no STATUS written; see $LOGDIR/log.build" >&2; exit 2; fi
[ -f "$CASE_DIR/0/T" ] || { echo "REFUSE: no 0/T after build -- the age guard would have no datum" >&2; exit 2; }

# --- 0/T touched LAST, immediately before the solver -----------------------
touch "$CASE_DIR/0/T"

cd "$CASE_DIR" || exit 2
T0=$(date +%s)
timeout "$TIMEOUT_S" mpirun -np "$RANKS" "$SOLVER_PATH" -case "$CASE_DIR" -parallel \
    > "$CASE_DIR/log.solve" 2>&1
RC=$?
T1=$(date +%s); WALL=$((T1 - T0))

# --- the grader's inputs, produced only if the solver returned cleanly -----
RECON_RC=na; CC_RC=na
if [ "$RC" = "0" ]; then
    reconstructPar -latestTime -case "$CASE_DIR" > "$CASE_DIR/log.reconstructPar" 2>&1
    RECON_RC=$?
    if [ "$RECON_RC" = "0" ]; then
        postProcess -func writeCellCentres -latestTime -case "$CASE_DIR" \
            > "$CASE_DIR/log.writeCellCentres" 2>&1
        CC_RC=$?
    fi
fi

NOTE=clean
if [ "$RC" = "124" ]; then NOTE=CAP_EXPIRED_or_child_exit_124
elif [ "$RC" -gt 128 ] 2>/dev/null; then NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then NOTE=SOLVER_NONZERO_EXIT; fi
[ "$RECON_RC" = "0" ] || [ "$RECON_RC" = "na" ] || NOTE="${NOTE}_RECONSTRUCT_FAILED"
[ "$CC_RC" = "0" ] || [ "$CC_RC" = "na" ] || NOTE="${NOTE}_CELLCENTRES_FAILED"
write_status "$RC" "$WALL" "$NOTE"
echo "K0e $ARM finished: rc=$RC wall=${WALL}s note=$NOTE -> $STATUS"
exit "$RC"
