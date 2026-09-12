#!/bin/bash
# T5f LAUNCHER -- the cap comes from the FROZEN REGISTRATION, the rc comes from
# the solver, and the setup is asserted before a single iteration is paid for.
#
# ===========================================================================
# WHAT THIS FILE CHANGES FROM `../T5b_runs/run_one_t5b.sh`, AND WHY
# ===========================================================================
# The detach architecture, the driven cap-kill proof, the arming guard, the age
# guard and the wall-clock `capped` witness are ADOPTED from run_one_t5b.sh.
# Five things are different, each because a measurement says so.
#
# 1. THE CAP IS READ OUT OF THE FROZEN REGISTRATION, NOT OUT OF A SIDE FILE.
#    T5b kept its caps in `T5B_CAPS.txt`, a SECOND copy of a registered number.
#    The board's standing finding (T26 S19/S20) is that an instrument holding
#    its own COPY of a registered quantity IS the defect and the fix is to stop
#    copying.  So this file parses section 8's CAP table out of
#    `docs/campaigns/T-family/T5f_PREREGISTRATION.md` at launch and REFUSES
#    unless the level matches exactly one row.  There is no cap file to drift,
#    and `--cap-core-min` is a CONFIRMATION the caller must state and that must
#    equal the registered value -- an argv still cannot widen a cap.
#
# 2. `checkMesh_rc` IS ACTUALLY THE checkMesh rc.  run_one_t5b.sh:179-180 reads
#
#        checkMesh ... > log 2>&1 || true
#        CHECKMESH_RC=$?
#
#    `$?` there is the rc of the `||` compound, which is 0 for every outcome.
#    Every `STATUS.T5_CUBE_*` in T5b_runs carries `checkMesh_rc=0`, and that
#    zero was never able to be anything else.  This file captures the rc INSIDE
#    the compound, and then passes the LOG through the same gate the builder
#    uses -- because checkMesh exits 0 on a FAILED check, so even a true rc is
#    not the control.  Registration S6: every limb but the cell determinant is a
#    HARD STOP.
#
# 3. THE LAUNCH-TIME checkMesh DOES NOT OVERWRITE THE BUILD-TIME LOG.
#    run_one_t5b.sh:179 wrote `log.checkMesh`, destroying the build's strict
#    `-allTopology -allGeometry` log and replacing it with a weaker one that
#    carries no determinant limb at all.  This file writes
#    `log.checkMesh.launch` and runs the SAME strict flags.
#
# 4. THE SETUP ASSERTION IS A LAUNCH PRECONDITION.  `assert_t5f_setup.py` reads
#    the built dictionaries and compares them against the frozen registration.
#    A case that is not the registered case does not get to spend core-minutes
#    proving it.  `__pycache__` is cleared first (stale-bytecode lesson: a clean
#    control can fail and a mutated case pass on stale .pyc).
#
# 5. THE SEQUENTIAL RULING IS ENFORCED, NOT TRUSTED.  The heat-transfer
#    supervisor ruled [lab-attributed] that the three levels run SEQUENTIALLY,
#    one rank at a time, on a box already at load ~15 with a 100-hour T4e leg
#    live.  This file REFUSES to start if another T5f solver is already running.
#    It touches nothing outside its own case directory, ever.
#
# STILL NOT `timeout --preserve-status` -- run_one_t5.sh's measurement stands:
# expiry and a genuine SIGTERM death become indistinguishable.  `capped` is
# taken from the WALL CLOCK, an independent witness no dying process can forge.
#
# THE rc IS CAPTURED INSIDE THE DETACHED WRAPPER.  `setsid timeout cmd` exits 0
# for every outcome, so the parent's rc is worthless.  The parent re-execs this
# script under `setsid` with `--no-detach` and exits 0 immediately; the CHILD
# runs the solver, captures `RC=$?` on the line after it, and writes STATUS.
# No rc is ever captured around the `setsid` line.
# ===========================================================================
set -eu

usage() {
    cat >&2 <<'U'
usage: run_one_t5f.sh --level c|m|f --cap-core-min N [--no-detach]
       run_one_t5f.sh --drive-cap-kill     (driven proof that the cap KILLS)
       run_one_t5f.sh --show-caps          (print the registered caps + arithmetic)
       run_one_t5f.sh --level L --cap-core-min N --dry-run
                  EVERY launch precondition -- cap agreement, the sequential
                  guard, the solver path, the arming guard, the setup assertion
                  and the checkMesh gate -- then STOP. Nothing is armed and no
                  solver starts. USE THIS to drive the refusal paths: a test
                  argv that can reach the launch is how this lane started a
                  solver under a hold on 2026-09-12 (see the FINDING directory).
  --cap-core-min  the caller's statement of the REGISTERED cap.  It must equal
                  the row for this level in section 8 of the frozen
                  registration.  Wall seconds are derived HERE as
                  cap*60/ranks, with ranks also parsed from the registration.
                  There is no --timeout and no --ranks: an argv cannot set them.
U
    exit 2
}

LEVEL=""; CAP_CORE_MIN=""; DETACH=1; DRIVE_KILL=0; SHOW_CAPS=0; DRY_RUN=0
SOLVER_OVERRIDE=""
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
while [ $# -gt 0 ]; do
    case "$1" in
        --level)        LEVEL="${2:-}"; shift 2 ;;
        --cap-core-min) CAP_CORE_MIN="${2:-}"; shift 2 ;;
        --foam-bashrc)  FOAM_BASHRC="${2:-}"; shift 2 ;;
        --solver)       SOLVER_OVERRIDE="${2:-}"; shift 2 ;;
        --no-detach)    DETACH=0; shift ;;
        --dry-run)      DRY_RUN=1; DETACH=0; shift ;;
        --drive-cap-kill) DRIVE_KILL=1; shift ;;
        --show-caps)    SHOW_CAPS=1; shift ;;
        *) usage ;;
    esac
done

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$SELF_DIR/../../../.." && pwd)"
REG="$REPO/docs/campaigns/T-family/T5f_PREREGISTRATION.md"

# --- THE DRIVEN CAP PROOF (adopted from run_one_t5b.sh) -------------------
# A cap that cannot be shown to kill is an assertion.  L-314: every guard ships
# its planted-failure proof, and the negative arm too.
if [ "$DRIVE_KILL" = "1" ]; then
    echo "run_one_t5f.sh --drive-cap-kill"
    F=0
    T0=$(date +%s); set +e
    timeout --kill-after=120 --signal=TERM 5 bash -c 'sleep 600'
    RC=$?; set -e
    T1=$(date +%s); W=$((T1 - T0))
    echo "  arm 1 : a WELL-BEHAVED 'sleep 600' under a 5 s cap -- wall ${W}s rc ${RC}"
    [ "$W" -ge 5 ] && [ "$W" -le 20 ] || { echo "  FAIL the cap did not stop a 600 s child"; F=1; }
    [ "$RC" -ne 0 ] || { echo "  FAIL the capped child returned rc 0"; F=1; }
    [ "$F" = "0" ] && echo "  ok    STOPPED AT THE CAP by SIGTERM"
    T0=$(date +%s); set +e
    timeout --kill-after=3 --signal=TERM 5 bash -c 'trap "" TERM; sleep 600'
    RC3=$?; set -e
    T1=$(date +%s); W3=$((T1 - T0))
    echo "  arm 2 : a SIGTERM-IGNORING child, kill-after 3 s -- wall ${W3}s rc ${RC3}"
    [ "$W3" -ge 5 ] && [ "$W3" -le 25 ] || { echo "  FAIL a SIGTERM-ignoring child outlived the cap"; F=1; }
    [ "$RC3" -ne 0 ] || { echo "  FAIL the SIGKILLed child returned rc 0"; F=1; }
    [ "$F" = "0" ] && echo "  ok    A SIGTERM-IGNORING CHILD IS STILL KILLED (SIGKILL after the grace)"
    T0=$(date +%s); set +e
    timeout --kill-after=120 --signal=TERM 30 bash -c 'sleep 2'
    RC2=$?; set -e
    T1=$(date +%s); W2=$((T1 - T0))
    [ "$RC2" = "0" ] && [ "$W2" -lt 30 ] || { echo "  FAIL a child INSIDE the cap was disturbed"; F=1; }
    [ "$F" = "0" ] && echo "  ok    a child INSIDE the cap runs to completion untouched (wall ${W2}s)"
    # arm 4: the DEFECT THIS FILE DOES NOT INHERIT.  `cmd || true; $?` is 0 for
    # every outcome, which is why every T5b STATUS carries checkMesh_rc=0.
    set +e; ( exit 7 ) > /dev/null 2>&1 || true ; BAD=$?
    ( exit 7 ) > /dev/null 2>&1 ; GOOD=$?
    set -e
    echo "  arm 4 : rc capture -- T5b idiom (\`|| true\` then \$?) gives ${BAD}; this file's gives ${GOOD}"
    [ "$BAD" = "0" ] && [ "$GOOD" = "7" ] || { echo "  FAIL the rc-capture demonstration did not reproduce"; F=1; }
    [ "$F" = "0" ] && echo "  ok    THE T5b checkMesh_rc DEFECT IS REPRODUCED AND NOT INHERITED"
    echo "CAP-KILL PROOF $([ "$F" = "0" ] && echo PASS || echo FAIL)"
    exit "$F"
fi

# --- EVERY REGISTERED QUANTITY IS PARSED OUT OF THE FROZEN DOCUMENT -------
[ -f "$REG" ] || { echo "REFUSE: the frozen registration is not on disk at $REG" >&2; exit 2; }

reg_cap() {      # section 8: | `<lvl>` | <point> | **<cap>** |
    awk -v L="$1" '
      $0 ~ ("^\\| `" L "` \\| [0-9.]+ \\| \\*\\*[0-9.]+\\*\\* \\|$") { line=$0; n++ }
      END { if (n != 1) exit 1
            if (match(line, /\*\*[0-9.]+\*\*/)) print substr(line, RSTART+2, RLENGTH-4)
            else exit 1 }' "$REG"
}
reg_ranks() {    # section 3.3: ... **1 rank**
    awk '/solver, model, `Prt`, interface scheme, ranks/ {
            if (match($0, /\*\*[0-9]+ rank\*\*/)) { print substr($0, RSTART+2, RLENGTH-9); n++ } }
         END { if (n != 1) exit 1 }' "$REG"
}
reg_solver() {   # section 3.3: `chtMultiRegionSimpleFoam`
    awk '/solver, model, `Prt`, interface scheme, ranks/ {
            if (match($0, /`chtMultiRegionSimpleFoam`/)) { print "chtMultiRegionSimpleFoam"; n++ } }
         END { if (n != 1) exit 1 }' "$REG"
}
reg_case() {     # the rule-2 block: T5F_CUBE_<lvl>
    awk -v L="$1" -v pat="T5F_CUBE_" '
      { s=$0; while (match(s, /T5F_CUBE_[cmf]/)) { seen[substr(s, RSTART, RLENGTH)]=1;
                                                   s=substr(s, RSTART+RLENGTH) } }
      END { k=0; for (c in seen) k++
            if (k != 3) exit 1
            want = pat L; if (!(want in seen)) exit 1; print want }' "$REG"
}

if [ "$SHOW_CAPS" = "1" ]; then
    R="$(reg_ranks)" || { echo "REFUSE: section 3.3 ranks did not parse" >&2; exit 2; }
    case "$R" in ''|*[!0-9]*) echo "REFUSE: section 3.3 ranks parsed as '$R', not an integer" >&2; exit 2;; esac
    echo "registered ranks: $R   (parsed from section 3.3 of $REG)"
    for L in c m f; do
        C="$(reg_cap "$L")" || { echo "REFUSE: section 8 CAP row for $L did not parse" >&2; exit 2; }
        T=$(awk -v c="$C" -v r="$R" 'BEGIN{printf "%d", (c*60.0)/r}')
        printf "  level %s  CAP %8s core-min  x 60 s/core-min / %s rank(s) = %6d wall s  (%.2f h)\n" \
               "$L" "$C" "$R" "$T" "$(awk -v t="$T" 'BEGIN{print t/3600.0}')"
    done
    exit 0
fi

[ -n "$LEVEL" ] && [ -n "$CAP_CORE_MIN" ] || usage
case "$LEVEL" in c|m|f) ;; *) echo "REFUSE: --level must be c, m or f" >&2; exit 2;; esac
case "$CAP_CORE_MIN" in ''|*[!0-9.]*) echo "REFUSE: --cap-core-min must be numeric" >&2; exit 2;; esac

CASE="$(reg_case "$LEVEL")" || { echo "REFUSE: the registration does not name exactly three T5F_CUBE_* cases including level $LEVEL" >&2; exit 2; }
RANKS="$(reg_ranks)" || { echo "REFUSE: section 3.3 ranks did not parse from $REG" >&2; exit 2; }
case "$RANKS" in ''|*[!0-9]*) echo "REFUSE: section 3.3 ranks parsed as '$RANKS', which is not an integer. A quantity this launcher could not read cleanly is never coerced." >&2; exit 2;; esac
SOLVER="$(reg_solver)" || { echo "REFUSE: section 3.3 solver did not parse from $REG" >&2; exit 2; }
[ -n "$SOLVER_OVERRIDE" ] && SOLVER="$SOLVER_OVERRIDE"
REG_CAP="$(reg_cap "$LEVEL")" || { echo "REFUSE: section 8 CAP row for level $LEVEL did not parse from $REG" >&2; exit 2; }

AGREE=$(awk -v a="$CAP_CORE_MIN" -v b="$REG_CAP" 'BEGIN{print (a+0==b+0)?"1":"0"}')
[ "$AGREE" = "1" ] || { echo "REFUSE: --cap-core-min $CAP_CORE_MIN DISAGREES with the cap $REG_CAP registered for level $LEVEL in section 8. This is the T5 CAP_OVERRUN shape and it stops here." >&2; exit 2; }
TIMEOUT_S=$(awk -v c="$CAP_CORE_MIN" -v r="$RANKS" 'BEGIN{printf "%d", (c*60.0)/r}')
[ "$TIMEOUT_S" -gt 0 ] || { echo "REFUSE: derived timeout is not positive" >&2; exit 2; }

CASE_DIR="$SELF_DIR/$CASE"
[ -d "$CASE_DIR" ] || { echo "REFUSE: no built case at $CASE_DIR" >&2; exit 2; }
case "$CASE_DIR" in "$SELF_DIR"/*) ;; *) echo "REFUSE: $CASE_DIR is outside $SELF_DIR; this launcher touches nothing else" >&2; exit 2;; esac
STATUS="$SELF_DIR/STATUS.$CASE"
echo "CAP AGREES $CASE $CAP_CORE_MIN core-min at $RANKS rank(s) -> timeout ${TIMEOUT_S} s  [parsed from $REG]"

# --- THE SEQUENTIAL RULING, ENFORCED --------------------------------------
# MEASURED 2026-09-12: `pgrep -f "$SELF_DIR/T5F_CUBE_"` matches ANY shell whose
# command line merely mentions the path -- an inspecting `ps`/`find` one-liner
# self-matched during development (the pkill-matches-its-own-shell trap in pgrep
# form). A guard that fires on a bystander is a guard nobody will trust. So this
# walks /proc and requires the NUL-separated argv itself to be the solver: argv[0]
# basename == the registered solver AND some later argv == "-case" with a
# T5F_CUBE_* path. A shell can mention the string; it cannot BE that argv.
OTHER=""
for pd in /proc/[0-9]*; do
    pid="${pd#/proc/}"
    [ "$pid" = "$$" ] && continue
    [ -r "$pd/cmdline" ] || continue
    argv0="$(tr '\0' '\n' < "$pd/cmdline" 2>/dev/null | head -1)"
    [ "$(basename -- "${argv0:-x}" 2>/dev/null)" = "$SOLVER" ] || continue
    tr '\0' '\n' < "$pd/cmdline" 2>/dev/null | grep -qx -- "-case" || continue
    tr '\0' '\n' < "$pd/cmdline" 2>/dev/null | grep -q "^$SELF_DIR/T5F_CUBE_" || continue
    OTHER="$OTHER pid=$pid"
done
[ -z "$OTHER" ] || { echo "REFUSE: a T5f solver is ALREADY RUNNING ($OTHER). The heat-transfer supervisor ruled the three levels run SEQUENTIALLY, one rank at a time. Wait for it to finish." >&2; exit 2; }

if [ "$DRY_RUN" != "1" ] && [ "$DETACH" = "1" ] && [ "${T5F_DETACHED:-}" != "1" ]; then
    T5F_DETACHED=1 exec setsid "$0" --level "$LEVEL" --cap-core-min "$CAP_CORE_MIN" \
        --foam-bashrc "$FOAM_BASHRC" ${SOLVER_OVERRIDE:+--solver "$SOLVER_OVERRIDE"} \
        --no-detach </dev/null >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; STATUS will appear at $STATUS"
    exit 0
fi

# ==========================================================================
# FROM HERE DOWN WE ARE THE DETACHED CHILD.  Every rc is captured on the line
# after the command that produced it.
# ==========================================================================
write_status() {   # rc wall capped checkmesh_rc note
    tmp="$STATUS.tmp.$$"
    rss="absent"
    [ -f "$CASE_DIR/log.solve.time" ] && rss="$(awk -F': ' '/Maximum resident set size/{print $2}' "$CASE_DIR/log.solve.time")"
    printf 'case=%s\nlevel=%s\nrc=%s\nwall_s=%s\nranks=%s\ncore_min=%s\ncap_core_min=%s\ntimeout_s=%s\ncapped=%s\ncheckMesh_rc=%s\nsolver=%s\nsolver_path=%s\nregistration=%s\nregistration_sha256=%s\npeak_rss_kb=%s\nload_at_start=%s\nload_at_end=%s\nprocs_running_at_start=%s\nnproc=%s\nnote=%s\n' \
        "$CASE" "$LEVEL" "$1" "$2" "$RANKS" \
        "$(awk -v w="$2" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')" \
        "$CAP_CORE_MIN" "$TIMEOUT_S" "$3" "$4" "$SOLVER" "${SOLVER_PATH:-unresolved}" \
        "docs/campaigns/T-family/T5f_PREREGISTRATION.md" "$REG_SHA" "$rss" \
        "$LOAD_START" "$(cut -d' ' -f1-3 /proc/loadavg)" "$PR_START" "$(nproc)" "$5" > "$tmp"
    mv -f "$tmp" "$STATUS"
}

REG_SHA="$(sha256sum "$REG" | cut -d' ' -f1)"
cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

if [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
    set +u
    # shellcheck disable=SC1090
    . "$FOAM_BASHRC" >/dev/null 2>&1 || true
    set -u
fi
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' NOT RESOLVABLE. Nothing ran, so no STATUS is written and no rc is invented." >&2; exit 2; }

# --- THE ARMING GUARD (rule 4: a guard refuses a case where 0 or a time dir
#     already exists) --------------------------------------------------------
[ -e "$CASE_DIR/0" ] && { echo "REFUSE: $CASE_DIR/0 already exists -- armed before" >&2; exit 2; }
STALE=$(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f ' 2>/dev/null || true)
[ -n "$STALE" ] && { echo "REFUSE: $CASE_DIR already holds time directories: $STALE" >&2; exit 2; }
[ -e "$CASE_DIR/log.solve" ] && { echo "REFUSE: $CASE_DIR/log.solve exists -- this case has already been run and its evidence is not overwritten" >&2; exit 2; }
[ -d "$CASE_DIR/0.orig" ] || { echo "REFUSE: no 0.orig to arm from" >&2; exit 2; }

# --- THE SETUP ASSERTION, BEFORE ANY CORE-MINUTE IS SPENT -----------------
# __pycache__ first: a stale .pyc can make a clean control fail and a mutated
# case pass, which inverts exactly this check.
find "$SELF_DIR" -maxdepth 2 -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
set +e
python3 "$SELF_DIR/assert_t5f_setup.py" --level "$LEVEL" > "$CASE_DIR/SETUP_ASSERTION.txt" 2>&1
ASSERT_RC=$?
set -e
[ "$ASSERT_RC" = "0" ] || { echo "REFUSE: the setup assertion FAILED (rc $ASSERT_RC). $CASE is not the registered case and does not get to spend core-minutes proving it. See $CASE_DIR/SETUP_ASSERTION.txt" >&2; exit 2; }
echo "SETUP ASSERTION PASS for $CASE (see SETUP_ASSERTION.txt)"

# --- checkMesh AT LAUNCH: real rc, strict flags, its OWN log, same gate ----
# NOT `log.checkMesh` -- that is the build's strict log and it is evidence.
#
# MEASURED 2026-09-12: `checkMesh -allTopology` on a mappedWall case WRITES
# `postProcessing/<region>/checkMesh/*.vtp` AMI debug surfaces into the case.
# `build_t5.py` deletes `postProcessing` after meshing for exactly this reason,
# and a `--dry-run` of this launcher was re-creating it -- a directory under the
# NAME the solver's own function objects write into, describing a mesh check
# rather than a solve. That is the "artifact for a version that no longer
# exists, under the name its replacement will use" shape. So:
#   - a `postProcessing` that PREDATES this launch is a REFUSAL (stale output of
#     some earlier run of this case; a grader cannot tell which run it meant);
#   - one that checkMesh creates HERE is removed again, in both dry and real
#     runs, so the solver starts on a case with no postProcessing at all.
HAD_PP=no
[ -e "$CASE_DIR/postProcessing" ] && HAD_PP=yes
[ "$HAD_PP" = "no" ] || { echo "REFUSE: $CASE_DIR/postProcessing already exists before this launch. It is output from an earlier run of this case and a grader sweeping postProcessing/air/yPlus cannot tell which run it belongs to. Inspect it and move it aside by hand; it is not deleted here." >&2; exit 2; }
set +e
checkMesh -case "$CASE_DIR" -allRegions -allTopology -allGeometry > "$CASE_DIR/log.checkMesh.launch" 2>&1
CHECKMESH_RC=$?
set -e
set +e
python3 "$SELF_DIR/build_t5f.py" --drive-checkmesh "$CASE_DIR/log.checkMesh.launch" >> "$CASE_DIR/SETUP_ASSERTION.txt" 2>&1
GATE_RC=$?
set -e
# checkMesh's own AMI debug output, created seconds ago by the line above and by
# nothing else, goes again.  It is not evidence; log.checkMesh.launch is.
[ "$HAD_PP" = "no" ] && rm -rf "$CASE_DIR/postProcessing"
[ -e "$CASE_DIR/postProcessing" ] && { echo "REFUSE: could not clear the checkMesh postProcessing output at $CASE_DIR/postProcessing" >&2; exit 2; }
[ "$GATE_RC" = "0" ] || { echo "REFUSE: a checkMesh limb other than the cell determinant FAILED at launch. Registration S6 makes that a HARD STOP and a FINDING for the supervisor; it is not worked around. See $CASE_DIR/SETUP_ASSERTION.txt" >&2; exit 2; }

if [ "$DRY_RUN" = "1" ]; then
    echo "DRY RUN: every launch precondition PASSES for $CASE."
    echo "DRY RUN: postProcessing/ left absent (checkMesh's AMI debug output cleared)."
    echo "DRY RUN: nothing is armed (no 0/ created), no solver started, no STATUS written."
    echo "DRY RUN: an authorised launch would run $SOLVER_PATH under timeout ${TIMEOUT_S} s."
    exit 0
fi

cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/" >&2; exit 2; }
AGE_DATUM="$(find "$CASE_DIR/0" -name T -type f | head -1)"
[ -n "$AGE_DATUM" ] || { echo "REFUSE: no 0/**/T, so the age guard has no datum" >&2; exit 2; }
sleep 1
touch "$AGE_DATUM"

# --- THE SOLVER, UNDER AN ENFORCED CAP ------------------------------------
# rc is captured HERE, inside the detached child, on the line after the solver.
# THE PEAK-RSS RECORD.  Measured 2026-09-12: NO artifact anywhere under
# verification/runs/T-family records a peak RSS for chtMultiRegionSimpleFoam, so
# every memory figure this lab has quoted for the T5 ladder is an estimate.  The
# only E4 `log.solve.time` records are simpleFoam at 4,050 cells.  `/usr/bin/time
# -v` costs nothing and ends that: `log.solve.time` carries `Maximum resident set
# size (kbytes)` for the solver, so the NEXT rung scales from a measurement.
# GNU time propagates the child's exit status, so RC is still the SOLVER's; if it
# is absent the solver runs bare and STATUS says `rss_record=absent`.
# Rule 12: contention is attributed separately and never absorbed into the
# actual/predicted ratio, so the box's state at launch is part of the record.
LOAD_START="$(cut -d' ' -f1-3 /proc/loadavg)"
PR_START="$(awk '/^procs_running/{print $2}' /proc/stat)"
TIME_BIN=""
[ -x /usr/bin/time ] && TIME_BIN=/usr/bin/time
set +e
T0=$(date +%s)
if [ -n "$TIME_BIN" ]; then
    timeout --kill-after=120 --signal=TERM "$TIMEOUT_S" \
        "$TIME_BIN" -v -o "$CASE_DIR/log.solve.time" \
        "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.solve" 2>&1
    RC=$?
else
    timeout --kill-after=120 --signal=TERM "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.solve" 2>&1
    RC=$?
fi
T1=$(date +%s)
set -e
WALL=$((T1 - T0))

CAPPED=0
[ "$WALL" -ge "$TIMEOUT_S" ] && CAPPED=1

NOTE=clean
if [ "$CAPPED" = "1" ]; then
    NOTE=CAP_ENFORCED_run_STOPPED_at_registered_cap
    printf '%s CAP ENFORCED: %s was STOPPED at the registered cap %s core-min (%s s wall at %s rank(s)). CLAUDE.md rule 12: an overrun stops the run; it does not get a new budget. This is a right-censored PENDING, not a failure.\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$CASE" "$CAP_CORE_MIN" "$TIMEOUT_S" "$RANKS" > "$CASE_DIR/CAP_ENFORCED.txt"
elif [ "$RC" = "124" ]; then
    NOTE=CHILD_EXIT_124_NOT_an_expiry_wall_under_cap
elif [ "$RC" -gt 128 ] 2>/dev/null; then
    NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then
    NOTE=SOLVER_NONZERO_EXIT
fi
write_status "$RC" "$WALL" "$CAPPED" "$CHECKMESH_RC" "$NOTE"
echo "$CASE finished: rc=$RC wall=${WALL}s capped=$CAPPED checkMesh_rc=$CHECKMESH_RC note=$NOTE -> $STATUS"
exit "$RC"
