#!/usr/bin/env bash
# =============================================================================
# F28 -- FARFIELD BC-VARIATION PROBE.  *** FEASIBILITY.  NOT THE GATED PATH. ***
#
# WHY THIS FILE EXISTS RATHER THAN A FLAG ON run_f28_feasibility.sh
# -----------------------------------------------------------------
# The feasibility launcher ASSEMBLES its case from `cases/F28_.../case/`
# templates on every invocation and REFUSES a run dir that already holds `0/`.
# The probe case at
#   verification/runs/F28_runs/FEAS_L1_dp1000_U20_A2_BCPROBE
# was assembled and frozen BEFORE its readings were written -- that ordering is
# the probe's entire evidentiary value -- so re-assembling it would overwrite
# the one variation under test with the template's own farfield form and run a
# duplicate of the parent arm wearing the probe's name.  This script therefore
# RUNS THE PRE-ASSEMBLED CASE and never rewrites a dictionary.
#
# WHAT REPLACES THE ASSEMBLY GUARANTEE
# ------------------------------------
# Assembling in-script is what normally proves "nothing else changed".  Here
# that proof is MACHINE-CHECKED INSTEAD, and is a PRECONDITION OF THE LAUNCH:
# `assert_bcprobe_single_variation.py` compares every input of the probe against
# the parent arm -- system/, constant/, constant/polyMesh recursively, and each
# 0/ field with its farfield entry excised -- and this script REFUSES to solve
# if anything but the five farfield entries differs.  That checker is driven to
# a REFUSAL on three planted perturbations (standing rule 3) and its `--selftest`
# is run here, before the real check, in this same process.  A checker not shown
# able to fail is not a control.
#
# WHAT IS KEPT IDENTICAL TO run_f28_feasibility.sh, DELIBERATELY
# --------------------------------------------------------------
#  * rc captured INSIDE this process ON THE LINE THAT RUNS THE SOLVER, never
#    around a `setsid` line (`setsid timeout cmd` exits 0 for every outcome);
#  * STATUS written by this process's own EXIT trap, into the RUN DIR, under a
#    filename the queue runner never writes (it truncates `STATUS.*` and
#    `launcher.queue.out` in its launch cwd unconditionally);
#  * a WALL CAP on the solver call itself via `timeout`, rc read on the line.
#    An overrun STOPS the probe; it does not get a second budget;
#  * the age-guard anchor: the `0/` fields are touched LAST, immediately before
#    the solver, so every field written at endTime is NEWER than `0/`.
#
# LABEL=FEASIBILITY.  Sanaa 2026-08-31T15:51Z: unregistered feasibility rungs
# are queue-legal tagged prereg=FEASIBILITY and "their outputs are never
# gradeable as verdicts".  NO GATE, THRESHOLD, BAND, GCI, OBSERVED ORDER OR
# VERDICT OF THE FIXED VOCABULARY ATTACHES TO ANYTHING THIS SCRIPT PRODUCES.
# STAGE 1 IS NOT AUTHORISED and this script does not enter the gated path:
# `run_f28.sh` still refuses without the supervisor's own --check1-token, and
# nothing here supplies, weakens or substitutes for it.
# =============================================================================
set -o pipefail

CASE_ID="F28_DUCTED_ACTUATOR_DISK"
REPO="/home/ubuntu/Certonomous"
RUN_ROOT="$REPO/verification/runs/F28_runs"
CHECKER="$REPO/cases/$CASE_ID/assert_bcprobe_single_variation.py"
LABEL="FEASIBILITY"

RUNG="FEAS_L1_dp1000_U20_A2_BCPROBE"
PARENT="FEAS_L1_dp1000_U20_A2"
RANKS=4
MAX_WALL_S=1500

while [ $# -gt 0 ]; do
  case "$1" in
    --rung) RUNG="$2"; shift 2;;
    --parent) PARENT="$2"; shift 2;;
    --ranks) RANKS="$2"; shift 2;;
    --max-wall-s) MAX_WALL_S="$2"; shift 2;;
    *) echo "ABORT: unknown argument $1" >&2; exit 1;;
  esac
done

SOLVER_RC="not-run"
PHASE="argument-parse"
WALL_S="not-run"
START_EPOCH=""
VARIATION_CHECK="not-checked"
RUN_DIR="$RUN_ROOT/$RUNG"
PARENT_DIR="$RUN_ROOT/$PARENT"
STATUS_FILE="$RUN_DIR/RUN_STATUS.F28.$RUNG.$LABEL.txt"

on_exit() {
  launcher_rc=$?
  if [ -n "$STATUS_FILE" ] && [ -d "$(dirname "$STATUS_FILE")" ]; then
    if [ -n "$START_EPOCH" ]; then WALL_S=$(( $(date +%s) - START_EPOCH )); fi
    printf 'LABEL=%s case=%s rung=%s parent=%s ranks=%s max_wall_s=%s solver_rc=%s launcher_rc=%s phase=%s wall_s=%s single_variation_check=%s decomposition_method=scotch decomposition_seed=scotch-default-v2606 run_dir=%s end=%s note=%s\n' \
      "$LABEL" "$CASE_ID" "$RUNG" "$PARENT" "$RANKS" "$MAX_WALL_S" \
      "$SOLVER_RC" "$launcher_rc" "$PHASE" "$WALL_S" "$VARIATION_CHECK" \
      "$RUN_DIR" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      "FARFIELD-BC-VARIATION-PROBE;-FEASIBILITY-NO-FREEZE-REQUIRED-SANAA-2026-08-31;-OUTPUTS-NEVER-GRADEABLE-AS-VERDICTS;-solver_rc-captured-INSIDE-this-process-on-the-solver-line-NOT-around-a-setsid-line;-launcher_rc-is-INFRASTRUCTURE-and-is-NEVER-evidence-of-a-solve" \
      > "$STATUS_FILE" 2>/dev/null
  fi
}
trap on_exit EXIT

abort() { echo "ABORT: $*" >&2; exit 1; }

PHASE="guards"
[ -d "$RUN_DIR" ]    || abort "no pre-assembled probe case at $RUN_DIR"
[ -d "$PARENT_DIR" ] || abort "no parent arm at $PARENT_DIR to compare against"
case "$RUN_DIR" in
  "$REPO"|"$REPO/"|"$REPO/cases"*|"$RUN_ROOT") abort "refusing a shared cwd: $RUN_DIR";;
esac

# AGE GUARD.  `0/` is EXPECTED here -- the case is pre-assembled -- so the guard
# is on ANSWERS, not on inputs: no numeric time directory, no processor* dir,
# no solver log.  A run is never started on top of an existing answer.
# MEASURED DEFECT IN THIS SCRIPT'S FIRST VERSION, CAUGHT BY THIS GUARD ITSELF
# AT ZERO COMPUTE, 2026-08-31T19:49:04Z.  The regex was inherited verbatim from
# run_f28_feasibility.sh as `.*/[0-9]+(\.[0-9]+)?$`, where it is correct because
# that script ASSEMBLES into an empty directory and any `0` it finds is somebody
# else's answer.  HERE `0` IS AN INPUT -- the probe case is pre-assembled and its
# initial condition is the thing under test -- so the inherited guard refused the
# only directory it was ever meant to run.  `-not -name 0` excludes EXACTLY the
# literal `0` and nothing else: `0.0`, `00`, `1`, `15000` and every other time
# directory still abort, because those ARE answers.  The guard is narrowed by one
# exact name, not weakened.
extra=$(find "$RUN_DIR" -maxdepth 1 -mindepth 1 -type d -not -name '0' \
        -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' | head -1)
[ -n "$extra" ] && abort "time directory $extra already exists in $RUN_DIR"
[ -n "$(find "$RUN_DIR" -maxdepth 1 -mindepth 1 -type d -name 'processor*' | head -1)" ] \
  && abort "processor* directories already exist in $RUN_DIR"
[ -e "$RUN_DIR/log.simpleFoam" ] && abort "$RUN_DIR already holds a log.simpleFoam"
[ -e "$RUN_DIR/launcher.queue.out" ] && abort "$RUN_DIR already carries a
  launcher.queue.out -- another case is using this cwd"
[ -f "$RUN_DIR/PRECOMMITTED_READINGS.md" ] \
  || abort "the probe's PRECOMMITTED_READINGS.md is missing from $RUN_DIR --
  the readings are the probe's evidentiary content and it does not run without them"

PHASE="single-variation-check"
# The checker is driven to a REFUSAL before it is trusted, in this process.
python3 "$CHECKER" --selftest "$PARENT_DIR" "$RUN_DIR" \
  || abort "the single-variation checker FAILED ITS OWN SELFTEST -- it was not
  shown able to refuse a planted perturbation, so its PASS means nothing (rule 3)"
python3 "$CHECKER" "$PARENT_DIR" "$RUN_DIR" \
  || abort "the probe case is NOT a single variation on its parent arm.  A probe
  that changed two things isolates no mechanism and is not worth its core-minutes."
VARIATION_CHECK="CONFIRMED-farfield-slip-only"

echo "F28 $LABEL $RUNG"
echo "  single variation vs $PARENT: farfield -> slip on U p k omega nut, MACHINE-CHECKED"
echo "  wall cap = ${MAX_WALL_S}s at $RANKS ranks (enforced ceiling $(python3 -c "print($MAX_WALL_S*$RANKS/60.0)") core-min)"
echo "  LABEL = $LABEL.  NO VERDICT IS ISSUED BY THIS SCRIPT."

PHASE="solve"
set +u
# shellcheck disable=SC1091
source /usr/lib/openfoam/openfoam2606/etc/bashrc "" >/dev/null 2>&1
set -u
command -v simpleFoam >/dev/null || abort "simpleFoam is not on PATH after
  sourcing the v2606 bashrc"

cd "$RUN_DIR" || abort "cannot cd to $RUN_DIR"

# THE AGE GUARD'S ANCHOR.  Every 0/ field is touched LAST, immediately before
# the solver, so any field written at endTime is strictly newer than 0/.
touch 0/U 0/p 0/k 0/omega 0/nut
sync

START_EPOCH=$(date +%s)
decomposePar -force > log.decomposePar 2>&1
dec_rc=$?
[ "$dec_rc" = "0" ] || abort "decomposePar rc=$dec_rc"

# rc TAKEN HERE, ON THIS LINE, INSIDE THIS PROCESS.
timeout --signal=TERM --kill-after=60 "$MAX_WALL_S" \
  mpirun -np "$RANKS" simpleFoam -parallel > log.simpleFoam 2>&1
SOLVER_RC=$?
WALL_S=$(( $(date +%s) - START_EPOCH ))

reconstructPar -latestTime > log.reconstructPar 2>&1 || true

PHASE="solved"
echo "solver rc = $SOLVER_RC   wall_s = $WALL_S   core-min = $(python3 -c "print($WALL_S*$RANKS/60.0)")"
[ "$SOLVER_RC" = "0" ] || abort "the solver returned $SOLVER_RC.  A crash is a
  FINDING until triage says otherwise (SUPERVISION_CHARTER section 3 check 2)
  and that triage is the supervisor's, personally."

echo "PROBE RUN COMPLETE.  NO VERDICT.  The reading is fixed in"
echo "$RUN_DIR/PRECOMMITTED_READINGS.md and may not be added to after the fact."
exit 0
