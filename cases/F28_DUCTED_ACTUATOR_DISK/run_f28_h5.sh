#!/bin/bash
# F28 -- H5 SPATIAL-RESIDUAL LAUNCHER.  Restart from the parent's plateau.
#
# Registered by:
#   verification/campaign/F28G_H5_RESIDUAL_FIELD_PREREGISTRATION.md
#
# WHY THIS FILE EXISTS AND `run_f28.sh` COULD NOT BE USED.  `run_f28.sh` builds
# every case from templates at time 0, always runs `decomposePar -force`, and
# reconstructs with `reconstructPar -latestTime` (its lines 426-543).  This arm
# RESTARTS from the parent rung's plateau state at iteration 15000 and needs
# FIVE intermediate snapshots reconstructed, not one.  Neither is reachable from
# that launcher, so this is a separate file rather than a flag on it.
#
# THE PARENT'S GRADED RUN ROOT IS IMMUTABLE (cfd-supervisor, ruling 1).
# `F28G_L1_dp1000_U20` carries a `NOT A RESULT` verdict on the record.  A
# restart that wrote into its `processor*` directories would mutate the evidence
# for a verdict already issued.  This script therefore:
#   * copies OUT of the parent and never writes INTO it;
#   * fingerprints the parent BEFORE and AFTER and ABORTS if one byte moved --
#     immutability is PROVED per run, not promised in a comment;
#   * asserts that `scripts/solve_evidence_guard.py` REFUSES the parent.  That
#     assertion is a planted control on the guard itself: if the guard ever
#     stops recognising a completed solve as evidence, this launcher stops.
#
# THE AGE GUARD ANCHORS ON A SENTINEL WRITTEN AT THIS LAUNCH (ruling 2b).
# Standing rule 4 anchors on `0/T` because that file is touched LAST AT LAUNCH
# and so DATES THE RUN ALLOWED TO PRODUCE THE ANSWER.  In a restart `0/p` was
# written at the PARENT'S launch, so every field this run writes is necessarily
# newer than it and the guard would pass unconditionally -- VACUOUS, and a
# vacuous guard that reports green is worse than an absent one.  So this script
# writes `RESTART_SENTINEL` as its LAST action before the solver line, and the
# comparator requires every field at endTime to be strictly newer than THAT.
#
# `rc` IS CAPTURED INSIDE THIS PROCESS ON THE LINE THAT RUNS THE SOLVER, never
# around a `setsid` line: `setsid timeout cmd` exits 0 for every outcome.
#
# THIS SCRIPT LAUNCHES A SOLVER.  It is committed as part of a DRAFT
# pre-registration and MUST NOT BE RUN until cfd-supervisor's check 4 has been
# performed on that registration.  `--dry-run` builds the case, proves the
# immutability and guard limbs, and STOPS BEFORE THE SOLVER.
set -u -o pipefail

REPO="/home/ubuntu/Certonomous"
PARENT="$REPO/verification/runs/F28_runs/F28G_L1_dp1000_U20"
RUNS="$REPO/verification/runs/F28_runs"
RESTART_TIME=15000

abort() { echo "ABORT: $*" >&2; exit 1; }

usage() {
  cat >&2 <<'EOF'
usage: run_f28_h5.sh --mode {pilot-control|pilot-treatment|arm} [--dry-run]

  pilot-control    72 iterations, writeResidualFields FALSE, run root H5P_C_L1_dp1000_U20
  pilot-treatment  72 iterations, writeResidualFields TRUE,  ONE snapshot (onEnd)
  arm             200 iterations, writeResidualFields TRUE,  FIVE snapshots (every 40)

  --dry-run  assemble the case and run every guard, then STOP before the solver.
EOF
  exit 2
}

MODE=""; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --mode) MODE="${2:-}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    *) usage ;;
  esac
done
[ -n "$MODE" ] || usage

case "$MODE" in
  pilot-control)   NAME="H5P_C_L1_dp1000_U20"; NITER=72;  TREAT=0; SNAPS="" ;;
  pilot-treatment) NAME="H5P_T_L1_dp1000_U20"; NITER=72;  TREAT=1; SNAPS="onEnd" ;;
  arm)             NAME="H5A_L1_dp1000_U20";   NITER=200; TREAT=1; SNAPS="40" ;;
  *) usage ;;
esac

END_TIME=$(( RESTART_TIME + NITER ))

# AMENDMENT 1, 2026-09-04, BEFORE FIRST COMPUTE.  A `--dry-run` MUST NOT CONSUME
# THE REAL RUN ROOT NAME.  As first written this script assembled into
# `$RUNS/$NAME` even under `--dry-run`, which had two consequences, both bad:
# the virgin-directory guard would then REFUSE the real run that followed, and
# the pre-registration's §11.1 freshness claim -- that the three named run
# directories do not exist -- would have been falsified by the act of testing.
# The supervisor cites absences as evidence; a test must not manufacture a
# presence.  So a dry run assembles into a CLEARLY LABELLED scratch root and
# leaves the registered names untouched.
if [ "$DRY" = "1" ]; then
  RUN_DIR="$RUNS/${NAME}_DRYRUN"
else
  RUN_DIR="$RUNS/$NAME"
fi

echo "mode=$MODE run_dir=$RUN_DIR startTime=$RESTART_TIME endTime=$END_TIME treatment=$TREAT"

# ---------------------------------------------------------------------------
# GUARD 1 -- the parent must exist and must be recognised AS EVIDENCE.
# This is a PLANTED CONTROL ON THE GUARD: the parent is a completed solve, so
# `refuse_if_solve_evidence` MUST raise.  If it returns cleanly the guard has
# stopped working and this launcher must not proceed on its protection.
# ---------------------------------------------------------------------------
[ -d "$PARENT" ] || abort "parent run root missing: $PARENT"
[ -d "$PARENT/processor0/$RESTART_TIME" ] || \
  abort "parent has no processor0/$RESTART_TIME to restart from"

python3 - "$REPO" "$PARENT" <<'PY' || abort "solve-evidence guard control FAILED"
import sys
sys.path.insert(0, sys.argv[1] + "/scripts")
from solve_evidence_guard import refuse_if_solve_evidence, SolveEvidencePresent
try:
    refuse_if_solve_evidence(sys.argv[2], action="restart-source")
except SolveEvidencePresent:
    print("GUARD CONTROL PASS: the guard refuses the parent, as it must.")
    sys.exit(0)
print("GUARD CONTROL FAILED: solve_evidence_guard did NOT recognise the "
      "parent's completed solve as evidence.  It is not protecting anything.")
sys.exit(1)
PY

# ---------------------------------------------------------------------------
# GUARD 2 -- VIRGIN DIRECTORY.  Refuse outright if the run root already exists.
# Stricter than the evidence guard on purpose: this run is graded, and a
# directory carrying anything at all is somebody's unfinished or finished work.
# ---------------------------------------------------------------------------
[ -e "$RUN_DIR" ] && abort "run root already exists: $RUN_DIR (refusing; move it aside by hand)"

# ---------------------------------------------------------------------------
# GUARD 3 -- the target may not BE the parent, under any resolution of paths.
# ---------------------------------------------------------------------------
[ "$(readlink -f "$RUN_DIR" 2>/dev/null || echo "$RUN_DIR")" != "$(readlink -f "$PARENT")" ] || \
  abort "target resolves to the parent run root"

# ---------------------------------------------------------------------------
# PARENT FINGERPRINT, BEFORE.  Name, size, mtime of every file under the parent.
# Compared byte-for-byte after the copy and again after the solve.
# ---------------------------------------------------------------------------
FP_DIR="$(mktemp -d)"
trap 'rm -rf "$FP_DIR"' EXIT
fingerprint() { find "$PARENT" -type f -printf '%P %s %T@\n' | LC_ALL=C sort; }
fingerprint > "$FP_DIR/parent.before" || abort "could not fingerprint parent"
echo "parent fingerprint: $(wc -l < "$FP_DIR/parent.before") files"

# ---------------------------------------------------------------------------
# ASSEMBLE.  Copy OUT of the parent.  Nothing is ever written INTO it.
# Measured 2026-09-04: processor0..3 15.1 MB + constant 7.9 MB + system 24 KB
# + 0/ 24 KB = about 23 MB.  The parent holds ONE time directory per processor
# (`15000`), not 15,000 of them, because its writeInterval equalled its endTime.
# ---------------------------------------------------------------------------
mkdir -p "$RUN_DIR" || abort "mkdir $RUN_DIR failed"
cp -a "$PARENT/system"   "$RUN_DIR/" || abort "copy system failed"
cp -a "$PARENT/constant" "$RUN_DIR/" || abort "copy constant failed"
cp -a "$PARENT/0"        "$RUN_DIR/" || abort "copy 0 failed"
for p in "$PARENT"/processor*; do
  pn="$(basename "$p")"
  mkdir -p "$RUN_DIR/$pn" || abort "mkdir $pn failed"
  cp -a "$p/constant"          "$RUN_DIR/$pn/" || abort "copy $pn/constant failed"
  cp -a "$p/0"                 "$RUN_DIR/$pn/" || abort "copy $pn/0 failed"
  cp -a "$p/$RESTART_TIME"     "$RUN_DIR/$pn/" || abort "copy $pn/$RESTART_TIME failed"
done
NPROC=$(ls -d "$RUN_DIR"/processor* | wc -l)
[ "$NPROC" = "4" ] || abort "expected 4 processor dirs, assembled $NPROC"

# ---------------------------------------------------------------------------
# THE DICTIONARY DIFFERENCE.  Done in python with COUNT ASSERTIONS, not sed:
# the file carries `writeControl timeStep;` five times over (once at top level
# and once per function object) and a bare sed would silently hit all of them.
# ---------------------------------------------------------------------------
python3 - "$RUN_DIR/system/controlDict" "$RESTART_TIME" "$END_TIME" "$NITER" "$TREAT" "$SNAPS" <<'PY' \
  || abort "controlDict rewrite failed"
import sys
path, t0, t1, niter, treat, snaps = sys.argv[1:7]
src = open(path).read()

def sub_once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        print("REFUSED: %s -- expected exactly 1 occurrence of %r, found %d"
              % (what, old, n))
        sys.exit(1)
    return text.replace(old, new)

# Top-level time control.  Each of these strings occurs exactly once in the
# file; the assertion above is what makes that a fact rather than a hope.
src = sub_once(src, "startTime       0;",
                    "startTime       %s;" % t0, "startTime")
src = sub_once(src, "endTime         15000;",
                    "endTime         %s;" % t1, "endTime")
# AMENDMENT 3, 2026-09-04, AFTER THE PILOT AND BEFORE ANY ARM COMPUTE.
# THE TOP-LEVEL writeInterval IS COMPARED AGAINST THE CONTINUING timeIndex,
# NOT AGAINST THE ITERATION COUNT.  This was set to `niter`, which is correct
# only when startTime is 0.  A restart continues timeIndex from startTime, so
# the write fires when `timeIndex % writeInterval == 0` with timeIndex running
# 15001..15072 -- and 15072 % 72 = 24, so IT NEVER FIRED AT endTime.  Measured
# on both pilot limbs: the solution fields landed at 15048 (15048 % 72 == 0,
# the one multiple in range) and endTime carried ONLY the function object's
# `onEnd` residual fields.  Both limbs therefore FAILED standing rule 4 clause
# 4, and the comparator correctly refused them.
# Setting writeInterval = endTime makes `endTime % writeInterval == 0` for any
# endTime, so the write fires at endTime and nowhere else.
src = sub_once(src, "writeInterval   15000;",
                    "writeInterval   %s;" % t1, "top-level writeInterval")

# The residuals function object, replaced as a WHOLE BLOCK by exact match.
OLD_FO = """    residuals
    {
        type            solverInfo;
        libs            ("libutilityFunctionObjects.so");
        fields          (p U k omega);
        writeResidualFields false;
        writeControl    timeStep;
        writeInterval   1;
    }"""
if treat == "1":
    if snaps == "onEnd":
        wc = "        writeControl    onEnd;          // ONE snapshot"
    else:
        wc = ("        writeControl    timeStep;\n"
              "        writeInterval   %s;            // FIVE snapshots" % snaps)
    NEW_FO = """    residuals
    {
        type            solverInfo;
        libs            ("libutilityFunctionObjects.so");
        fields          (p U k omega);
        writeResidualFields true;       // THE TREATMENT
        executeControl  timeStep;       // explicit; equals the default
        executeInterval 1;              // keeps solverInfo.dat per-iteration
%s
    }""" % wc
    src = sub_once(src, OLD_FO, NEW_FO, "residuals function object")
else:
    if src.count("writeResidualFields false;") != 1:
        print("REFUSED: control limb expected exactly one "
              "`writeResidualFields false;`")
        sys.exit(1)

open(path, "w").write(src)
print("controlDict rewritten: startTime=%s endTime=%s treatment=%s snaps=%s"
      % (t0, t1, treat, snaps))
PY

# The parent must be untouched by the assembly.
fingerprint > "$FP_DIR/parent.after_copy"
diff -q "$FP_DIR/parent.before" "$FP_DIR/parent.after_copy" >/dev/null \
  || { diff "$FP_DIR/parent.before" "$FP_DIR/parent.after_copy" >&2; \
       abort "PARENT MUTATED DURING ASSEMBLY -- see diff above"; }
echo "immutability check 1/2 PASS: parent unchanged after assembly"

# No time directory beyond the restart time may exist yet (rule 4 clause 7).
STRAY=$(find "$RUN_DIR"/processor*/ -maxdepth 1 -type d -regex '.*/[0-9]+$' \
        -printf '%f\n' | awk -v t="$RESTART_TIME" '$1+0 > t+0' | head -1)
[ -z "$STRAY" ] || abort "a time directory beyond $RESTART_TIME already exists: $STRAY"

if [ "$DRY" = "1" ]; then
  echo "DRY RUN: case assembled and all guards passed.  STOPPING BEFORE THE SOLVER."
  exit 0
fi

# ---------------------------------------------------------------------------
# THE SENTINEL.  LAST action before the solver line.  This file, and not
# `0/p`, is the age-guard anchor (ruling 2b).
# ---------------------------------------------------------------------------
cd "$RUN_DIR" || abort "cd $RUN_DIR failed"
sleep 1                      # so the sentinel is strictly older than any field
                             # written after it even at 1 s filesystem
                             # timestamp granularity
date -u +%Y-%m-%dT%H:%M:%SZ > "$RUN_DIR/RESTART_SENTINEL"
[ -f "$RUN_DIR/RESTART_SENTINEL" ] || abort "sentinel not written"

# ---------------------------------------------------------------------------
# THE SOLVER.  rc captured INSIDE this process, ON this line.  NO `setsid`
# anywhere near it, and NO `decomposePar` -- the processor dirs came from the
# parent and re-decomposing would discard the plateau state this arm exists to
# sample.
# ---------------------------------------------------------------------------
mpirun -np 4 simpleFoam -parallel > log.simpleFoam 2>&1
SOLVER_RC=$?
echo "solver_rc=$SOLVER_RC"

# ---------------------------------------------------------------------------
# RECONSTRUCT.  Explicit time list -- `-latestTime` would reconstruct one of
# five and the missing four would look like a physics absence.
# ---------------------------------------------------------------------------
if [ "$MODE" = "arm" ]; then
  TIMES="15040,15080,15120,15160,15200"
else
  TIMES="$END_TIME"
fi
reconstructPar -time "$TIMES" > log.reconstructPar 2>&1
RECON_RC=$?
echo "reconstruct_rc=$RECON_RC times=$TIMES"

# ---------------------------------------------------------------------------
# IMMUTABILITY, AFTER THE SOLVE.  The strongest limb: the solver ran with the
# parent's mesh and fields as its source and must not have written a byte back.
# ---------------------------------------------------------------------------
fingerprint > "$FP_DIR/parent.after_solve"
if ! diff -q "$FP_DIR/parent.before" "$FP_DIR/parent.after_solve" >/dev/null; then
  diff "$FP_DIR/parent.before" "$FP_DIR/parent.after_solve" >&2
  abort "PARENT MUTATED BY THE SOLVE -- the graded rung's evidence has moved"
fi
echo "immutability check 2/2 PASS: parent unchanged after the solve"

cat > "$RUN_DIR/RUN_STATUS.F28.$NAME.txt" <<EOF
case=F28_DUCTED_ACTUATOR_DISK rung=$NAME mode=$MODE level=1 delta_p_Pa=1000 u_inf_m_s=20
ranks=4 start_time=$RESTART_TIME end_time=$END_TIME iterations=$NITER
treatment_writeResidualFields=$TREAT snapshots=$SNAPS
solver_rc=$SOLVER_RC reconstruct_rc=$RECON_RC
restart_source=$PARENT parent_immutable=verified_before_and_after
age_guard_anchor=RESTART_SENTINEL
end=$(date -u +%Y-%m-%dT%H:%M:%SZ)
note=rc-captured-INSIDE-this-process-ON-the-solver-line-never-around-a-setsid-line;-no-decomposePar-was-run;-the-parent-graded-run-root-was-fingerprinted-before-and-after-and-is-unchanged
EOF

echo "wrote $RUN_DIR/RUN_STATUS.F28.$NAME.txt"
[ "$SOLVER_RC" = "0" ] || abort "solver rc=$SOLVER_RC"
exit 0
