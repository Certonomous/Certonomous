#!/bin/bash
# M2_kepsilon_family -- launcher.
#
# Stages one arm, then runs its 39 cases serially at ranks 1, writing a STATUS
# file at every exit (Sanaa 2026-08-27 standing directives section 2: "every
# wrapper writes STATUS at exit (rc, wall time, timestamp)").
#
# CONTRACT
#   * rc is captured INSIDE this script, never around a `setsid` line: `setsid
#     timeout cmd` exits 0 for every outcome, so an rc read outside it is a
#     fiction.
#   * 0.orig -> 0 is the LAST act before the solver starts, so that 0/k is the
#     newest file in the case and the age guard dates the run allowed to produce
#     the answer.
#   * The registered cap is carried here AND in grade_m2.py, and preflight
#     prints `CAP AGREES <n>` so a launcher/grader disagreement is caught before
#     compute rather than after.
#   * An overrun STOPS the run (standing rule 12).  It does not get a new budget.

set -u
set -o pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARM="${1:-}"
RUN_ROOT="${2:-/home/ubuntu/closure-data/m2_kepsilon_family}"

# ---- registered constants.  These must agree with PREREGISTRATION.md. -------
CAP_CORE_MIN=2600.0          # rung cap,  PREREGISTRATION.md section 8
CAP_CORE_MIN_ARM=1300.0      # per-arm cap
EST_CORE_MIN_ARM=649.0       # per-arm estimate at the 3.30e-06 s measured point
RATE_S_PER_CELL_IT=3.30e-06  # Kaandorp2020_TBRF/aposteriori/RESULTS.md:393-396
ENDTIME=20000                # PREREGISTRATION.md section 5
RANKS=1
SOLVER=simpleFoam

if [[ "$ARM" != "kEpsilon" && "$ARM" != "LaunderSharmaKE" ]]; then
    echo "REFUSE: arm must be kEpsilon or LaunderSharmaKE (got '${ARM}')" >&2
    exit 2
fi

ARM_ROOT="${RUN_ROOT}/${ARM}"
mkdir -p "$ARM_ROOT"
LOGDIR="${ARM_ROOT}/_logs"; mkdir -p "$LOGDIR"

status() {   # status <dir> <rc> <wall_s> <phase> [note]
    local d="$1" rc="$2" wall="$3" phase="$4"; shift 4
    {
        echo "rc=${rc}"
        echo "wall_s=${wall}"
        echo "ranks=${RANKS}"
        echo "core_min=$(awk -v w="$wall" -v r="$RANKS" 'BEGIN{printf "%.4f", w*r/60.0}')"
        echo "phase=${phase}"
        echo "arm=${ARM}"
        echo "endTime=${ENDTIME}"
        echo "cap_core_min_registered=${CAP_CORE_MIN}"
        echo "cap_core_min_arm=${CAP_CORE_MIN_ARM}"
        echo "timestamp_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        [[ $# -gt 0 ]] && echo "note=$*"
    } > "${d}/STATUS"
}

# ---------------------------- PREFLIGHT -------------------------------------
echo "== M2 preflight, arm ${ARM} =="
echo "CAP AGREES ${CAP_CORE_MIN}"
echo "CAP AGREES ARM ${CAP_CORE_MIN_ARM}"
grep -q "cap_core_min_registered = ${CAP_CORE_MIN}" "${HERE}/grade_m2.py" || {
    echo "REFUSE: grade_m2.py does not carry cap ${CAP_CORE_MIN}; launcher and" >&2
    echo "        grader disagree, and that is caught before compute, not after." >&2
    exit 2
}

# ---- OpenFOAM environment (L-353 / D540; PREREGISTRATION.md 13 AMENDMENT 3) --
# The queue runner launches `setsid nohup bash -c "cd <cwd> && <argv>"` and passes
# its OWN environment through unchanged; measured 2026-08-27, the live runner has
# no WM_PROJECT_DIR and no openfoam on PATH.  This script must therefore source
# the environment itself.
#
# `set -u` above makes that source FATAL AND SILENT: the v2606 bashrc reads
# WM_PROJECT_DIR unbound at its line 184 and, under nounset in a non-interactive
# shell, the shell DIES THERE -- before any trap, any `echo`, any STATUS write.
# G1's first launch died exactly this way at 2026-08-27T17:28:58Z.  Nounset is
# lifted for the source ALONE and restored immediately, and the source's own
# diagnostics are KEPT in a log instead of being sent to /dev/null -- discarding
# them is what hid the cause the first time.
FOAM_BASHRC="${FOAM_BASHRC:-/usr/lib/openfoam/openfoam2606/etc/bashrc}"
if ! command -v "$SOLVER" >/dev/null 2>&1; then
    if [[ ! -r "$FOAM_BASHRC" ]]; then
        echo "REFUSE: ${SOLVER} not on PATH and the OpenFOAM bashrc is not readable" >&2
        echo "        at ${FOAM_BASHRC}" >&2
        exit 2
    fi
    # shellcheck disable=SC1090
    set +u
    source "$FOAM_BASHRC" > "${LOGDIR}/log.foamenv" 2>&1
    FOAMENV_RC=$?
    set -u
    echo "FOAMENV rc=${FOAMENV_RC} (INFRASTRUCTURE: recorded, see ${LOGDIR}/log.foamenv;"
    echo "        the binding check is the command -v test below, not this rc)"
fi
command -v "$SOLVER" >/dev/null 2>&1 || {
    echo "REFUSE: ${SOLVER} is still not on PATH after sourcing ${FOAM_BASHRC}" >&2
    exit 2
}
echo "ENV OK  $("$SOLVER" -help 2>&1 | head -1 | tr -d '\r')"

python3 -O "${HERE}/stage_m2.py" --selftest || {
    echo "REFUSE: stage_m2.py --selftest did not pass" >&2; exit 2; }
python3 -O "${HERE}/grade_m2.py" --selftest || {
    echo "REFUSE: grade_m2.py --selftest did not pass" >&2; exit 2; }

# ---------------------------- STAGE -----------------------------------------
T0=$(date +%s)
python3 -O "${HERE}/stage_m2.py" --arm "${ARM}" --out "${RUN_ROOT}" \
    > "${LOGDIR}/log.stage" 2>&1
RC=$?
T1=$(date +%s)
status "$ARM_ROOT" "$RC" "$((T1-T0))" "stage"
if [[ $RC -ne 0 ]]; then
    echo "REFUSE: staging failed rc=${RC}; see ${LOGDIR}/log.stage" >&2
    exit 2
fi

# ---------------------------- RUN -------------------------------------------
ARM_CORE_MIN=0.0
for CASEDIR in "${ARM_ROOT}"/*/; do
    CID="$(basename "$CASEDIR")"
    [[ "$CID" == "_logs" ]] && continue
    [[ -d "${CASEDIR}/0.orig" ]] || continue

    # age guard precondition: no 0/ and no numeric time dir may pre-exist
    STALE=$(find "$CASEDIR" -maxdepth 1 -mindepth 1 -type d \
                 -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f ')
    if [[ -n "${STALE// /}" ]]; then
        status "$CASEDIR" 2 0 "refused" "pre-existing time dirs: ${STALE}"
        echo "REFUSE ${CID}: pre-existing time dirs ${STALE}; a guard refuses, it does not clean" >&2
        continue
    fi

    NCELLS=$(sed -n 's/.*nCells:[[:space:]]*\([0-9]*\).*/\1/p' \
             "${CASEDIR}/constant/polyMesh/owner" | head -1)
    CASE_CAP_S=$(awk -v n="$NCELLS" -v it="$ENDTIME" -v r="$RATE_S_PER_CELL_IT" \
                 'BEGIN{printf "%d", n*it*r*2.0}')   # per-run cap = 2x estimate

    # `timeout 0` DISABLES the timeout (coreutils: "A duration of 0 disables the
    # associated timeout").  An unparsed nCells would therefore silently remove
    # the per-run cap rather than tighten it, and standing rule 12's overrun stop
    # would not exist.  Measured 2026-08-27: all 39 shipped `owner` files carry a
    # parsable `nCells:` note, so this refusal should never fire -- which is
    # exactly why it is here rather than assumed.
    if [[ -z "${NCELLS//[!0-9]/}" ]] || [[ "$CASE_CAP_S" -le 0 ]]; then
        status "$CASEDIR" 2 0 "refused" "nCells unparsed (got '${NCELLS}') so the per-run cap computed as ${CASE_CAP_S}s; timeout 0 would DISABLE the cap"
        echo "REFUSE ${CID}: nCells unparsed; a zero cap disables the timeout, it does not tighten it" >&2
        continue
    fi

    # 0.orig -> 0 as the LAST act before launch: 0/k must be the newest file.
    cp -r "${CASEDIR}/0.orig" "${CASEDIR}/0"
    touch "${CASEDIR}/0/k"

    T0=$(date +%s)
    ( cd "$CASEDIR" && \
      /usr/bin/time -v -o mem_time.txt \
      timeout --signal=TERM --kill-after=60 "${CASE_CAP_S}" \
      "$SOLVER" -case . > log.solve 2>&1 )
    RC=$?              # captured HERE, inside the wrapper, never around setsid
    T1=$(date +%s)
    WALL=$((T1-T0))
    CM=$(awk -v w="$WALL" -v r="$RANKS" 'BEGIN{printf "%.4f", w*r/60.0}')
    ARM_CORE_MIN=$(awk -v a="$ARM_CORE_MIN" -v c="$CM" 'BEGIN{printf "%.4f", a+c}')

    NOTE=""
    if [[ $RC -eq 124 || $RC -eq 137 ]]; then
        NOTE="OVERRUN: per-run cap ${CASE_CAP_S}s reached; the run was STOPPED and does not get a new budget (standing rule 12)"
    fi
    status "$CASEDIR" "$RC" "$WALL" "solve" "$NOTE"
    echo "${CID} rc=${RC} wall=${WALL}s core_min=${CM} cells=${NCELLS} cap_s=${CASE_CAP_S} ${NOTE}"

    OVER=$(awk -v a="$ARM_CORE_MIN" -v c="$CAP_CORE_MIN_ARM" 'BEGIN{print (a>c)?1:0}')
    if [[ "$OVER" == "1" ]]; then
        status "$ARM_ROOT" 2 0 "stopped" \
            "ARM OVERRUN: ${ARM_CORE_MIN} core-min exceeds the registered arm cap ${CAP_CORE_MIN_ARM}; remaining cases NOT started"
        echo "STOP: arm ${ARM} spent ${ARM_CORE_MIN} core-min against cap ${CAP_CORE_MIN_ARM}." >&2
        echo "      An overrun stops the run; it does not get a new budget." >&2
        exit 2
    fi
done

status "$ARM_ROOT" 0 0 "complete" \
    "arm ${ARM} spent ${ARM_CORE_MIN} core-min against estimate ${EST_CORE_MIN_ARM} and cap ${CAP_CORE_MIN_ARM}"
echo "arm ${ARM} complete: ${ARM_CORE_MIN} core-min (estimate ${EST_CORE_MIN_ARM}, cap ${CAP_CORE_MIN_ARM})"
echo "estimate-versus-actual calibration is owed at completion (standing rule 12); grade_m2.py emits the row."
