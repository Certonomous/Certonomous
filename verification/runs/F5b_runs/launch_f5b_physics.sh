#!/bin/bash
# F5b PHYSICS RUNG -- the launch wrapper registered by
# verification/campaign/F5b_PHYSICS_PREREGISTRATION.md section 3.
#
# It exists because of defect D-1: E2's ``run_case`` does ``shutil.rmtree(case)``
# when the case directory already exists, which is the OPPOSITE of CLAUDE.md rule 4's
# guard -- it destroys the evidence the guard exists to protect.  This wrapper asserts
# non-existence and REFUSES (exit 2) BEFORE ``run_case`` is ever called.  E2 is not
# edited; that is a separate docket item.
#
# Runs section 3's pre-launch assertion block in ONE invocation, then launches the
# registered command detached under setsid so the solver survives the launching agent.
#
# Every assertion below either passes or stops the launch.  A non-empty diff on E2-E5
# STOPS THE LAUNCH; it is inspected, never reverted (rule 10).
set -u

REPO=/home/ubuntu/Certonomous
RUN="$REPO/verification/runs/F5b_runs/physics_p1"
CASE="$RUN/case"

# Frozen blobs, from the two freeze commits c1ba1845 (stage 1) and a80d5f36 (stage 2).
PREREG_BLOB=f1cbc96d26846ea583da6d897e914b37a5f576a4
READER_BLOB=6c6d34d02e6de925457dbfdbf75a0e004168f345
GENER_BLOB=10f5e475fd2887e0120b4c44dd5fe2dce808349b
FIXTURE_BLOB=641b2e1c2db75238d428b6b45b15af878b948116

# Section 1 evidence-base md5s.  E1 is prose; E2-E5 are the code that runs.
declare -A EMD5=(
  ["verification/campaign/F5bc_unsteady_statistics.md"]=50c19cb65d912bd40de7a0949bfa288e
  ["sdk/workflows/pitching_airfoil_case.py"]=06bfcfd40bc011cf2cb2fd41370b5c4b
  ["verification/runs/F5b_runs/run_pitch.py"]=96886e9efa84a09332dad45eef4d71d5
  ["sdk/workflows/tmr_verification.py"]=118671e25ca648d068321d8a1e401374
  ["sdk/workflows/transonic_airfoil.py"]=06a56a1411bb60a4f60889ff154ccdd5
)
# E2-E5 only: these are the files that execute.
CODE=(sdk/workflows/pitching_airfoil_case.py
      verification/runs/F5b_runs/run_pitch.py
      sdk/workflows/tmr_verification.py
      sdk/workflows/transonic_airfoil.py)

END_TIME=21.9440
DT0=0.002
MAX_CO=1.0
TIMEOUT=4200          # section 3 defect D-3: E3's default is 1800 s, BELOW the
                      # 1730-2880 s this arm needs, and would kill a healthy run.
CAP_CORE_MIN=72.0     # section 8 RUN CAP.  4200 s x 1 rank / 60 = 70.0, inside it.

cd "$REPO" || { echo "REFUSE (exit 2): cannot cd $REPO"; exit 2; }
echo "=============================================================================="
echo "F5b PHYSICS -- SECTION 3 PRE-LAUNCH ASSERTION BLOCK"
echo "stamp   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=============================================================================="

# --- ASSERTION 1: the run directory must not exist ---------------------------
if [ -e "$RUN" ]; then
  echo "REFUSE (exit 2): $RUN EXISTS.  The freeze condition (section 9) is void and"
  echo "  run_case would rmtree the evidence (D-1).  Nothing is launched."
  exit 2
fi
echo "A1  physics_p1 ABSENT                                          OK"

# --- ASSERTION 2: E2-E5 clean and unchanged ----------------------------------
PORC=$(git status --porcelain -- "${CODE[@]}")
if [ -n "$PORC" ]; then
  echo "REFUSE (exit 2): git status --porcelain over E2-E5 is NOT empty:"
  echo "$PORC"
  echo "  A non-empty diff STOPS THE LAUNCH.  Inspect it; never revert it (rule 10)."
  exit 2
fi
echo "A2a git status --porcelain over E2-E5 EMPTY                    OK"
for p in "${!EMD5[@]}"; do
  got=$(md5sum "$p" | cut -d' ' -f1)
  if [ "$got" != "${EMD5[$p]}" ]; then
    echo "REFUSE (exit 2): $p md5 $got != section 1's ${EMD5[$p]}"
    exit 2
  fi
done
echo "A2b E1-E5 md5s equal section 1 (5/5)                           OK"

# --- ASSERTION 3: HEAD, and the frozen files hashed against their blobs -------
HEAD=$(git rev-parse HEAD)
fail=0
check_blob () {                       # rule 2: verify the frozen file IS the file that ran
  got=$(git hash-object "$1")
  if [ "$got" != "$2" ]; then
    echo "REFUSE (exit 2): $1 hashes to $got, not the frozen blob $2"
    fail=1
  fi
}
check_blob verification/campaign/F5b_PHYSICS_PREREGISTRATION.md "$PREREG_BLOB"
check_blob verification/runs/F5b_runs/analyse_f5b_physics.py     "$READER_BLOB"
check_blob verification/runs/F5b_runs/make_theodorsen_fixture.py "$GENER_BLOB"
check_blob verification/runs/F5b_runs/controls/theodorsen_attached_fixture.dat "$FIXTURE_BLOB"
[ "$fail" -eq 0 ] || exit 2
echo "A3  frozen prereg + reader + generator + fixture match blobs   OK"

# The run directory is created HERE, by the launcher, after every assertion above.
mkdir -p "$RUN" || { echo "REFUSE (exit 2): cannot create $RUN"; exit 2; }

{
  echo "HEAD at launch: $HEAD"
  echo "frozen pre-registration blob: $PREREG_BLOB  (verified against the disk file)"
  echo "frozen reader blob:           $READER_BLOB  (verified against the disk file)"
  echo "fixture generator blob:       $GENER_BLOB"
  echo "C-N1 fixture blob:            $FIXTURE_BLOB"
  echo "stage 1 freeze commit: c1ba18453b1333c052075f5cc366aeba5c27df79"
  echo "stage 2 freeze commit: a80d5f36ab7d36cc51c8991e97aada10abc30b61"
  echo "launcher md5: $(md5sum "$0" | cut -d' ' -f1)"
} > "$RUN/LAUNCH_HEAD.txt"

# --- ASSERTION 4: the load the run actually started at ------------------------
# The C-4 calibration lesson (docs/COST_CALIBRATION.md row C-4) applied at the launch
# end as well as the basis end: a per-unit cost basis without its load is uncalibratable,
# and section 8 records the basis load as NOT RECORDED, so this end must be.
{
  echo "uptime at launch: $(uptime)"
  echo "nproc: $(nproc)"
  echo "NOTE section 8: the BASIS load is NOT RECORDED (E1 gives contention only"
  echo "  qualitatively).  This figure bounds the contention attribution at close-out;"
  echo "  it does not measure it."
} > "$RUN/LAUNCH_LOAD.txt"

# --- ASSERTION 5 (part): the resolved command, timeout echoed -----------------
CMD=(python3 "$REPO/verification/runs/F5b_runs/run_pitch.py"
     --level coarse --out "$RUN"
     --end-time "$END_TIME" --dt0 "$DT0" --max-co "$MAX_CO" --timeout "$TIMEOUT")
{
  echo "resolved command:"
  printf '  %q' "${CMD[@]}"; echo
  echo "resolved --timeout: $TIMEOUT s   (E3's DEFAULT IS 1800 s -- defect D-3;"
  echo "  launching on the default would kill a healthy run and manufacture a false"
  echo "  NOT A RESULT)"
  echo "ranks: 1 (serial; no decomposePar, no mpirun) -- core-minutes = wall s / 60"
  echo "cap: $CAP_CORE_MIN core-min (section 8).  The timeout fires at 70.0 core-min,"
  echo "  INSIDE the cap.  An overrun stops the run; it does not get a new budget."
} > "$RUN/LAUNCH_CMD.txt"
echo "A4  LAUNCH_HEAD/LOAD/CMD written                               OK"

# --- ASSERTION 5: the lever echo ---------------------------------------------
# Section 3 assertion 5 says "before pimpleFoam starts, cat the six dictionaries into
# log.levers", adopted from F5c's binding instrumentation ruling (E1:126-140, "THE
# SWITCH YOU SET IS NOT THE SWITCH THAT RAN").
#
# TAKEN LITERALLY AT DRIVER START THAT WOULD CAPTURE THE WRONG FILE, and the reason is
# in E2 itself: run_case OVERWRITES system/fvSolution with a potentialFoam-specific
# dictionary (E2:270-272, _generic_fv_solution(potential=True)), runs potentialFoam,
# and only RESTORES the PIMPLE dictionary at E2:282, on the line before pimpleFoam is
# invoked.  A lever echo taken any earlier records a dictionary pimpleFoam never saw --
# which is precisely the failure the F5c ruling exists to prevent, reproduced by
# obeying it naively.
#
# So the capture waits for log.pimpleFoam to appear -- the restore strictly precedes
# the pimpleFoam invocation in the same Python thread -- and then VERIFIES what it
# captured: the fvSolution it records must contain the moving-mesh `pcorr` block and
# must NOT be the potentialFoam one.  A capture that cannot prove which dictionary it
# holds is not a lever echo.
(
  for _ in $(seq 1 3000); do
    if [ -f "$CASE/log.pimpleFoam" ]; then
      {
        echo "# log.levers -- F5b Physics, captured $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "# captured at the appearance of log.pimpleFoam, i.e. AFTER E2:282 restored"
        echo "# the PIMPLE fvSolution over the potentialFoam one it swapped in at E2:270."
        echo "# NOTE: _foam ALSO writes a hash-bound lever echo into log.pimpleFoam"
        echo "# itself (Verification Charter v1.5 section 9); the two are independent"
        echo "# and may be cross-checked."
        for d in system/controlDict system/fvSolution system/fvSchemes \
                 constant/dynamicMeshDict constant/transportProperties \
                 constant/turbulenceProperties; do
          echo; echo "===== BEGIN $d ====="
          echo "# md5 $(md5sum "$CASE/$d" 2>/dev/null | cut -d' ' -f1)"
          cat "$CASE/$d" 2>/dev/null || echo "(ABSENT)"
          echo "===== END $d ====="
        done
        echo
        if grep -q 'pcorr' "$CASE/system/fvSolution" 2>/dev/null; then
          echo "LEVER CHECK: fvSolution contains 'pcorr' -> this IS the PIMPLE"
          echo "  moving-mesh dictionary, the one pimpleFoam ran.  OK"
        else
          echo "LEVER CHECK: *** fvSolution has NO 'pcorr' block.  This is NOT the"
          echo "  PIMPLE dictionary -- the capture raced the E2:270/:282 swap and the"
          echo "  echo above does not describe the run.  TREAT AS unverifiable."
        fi
      } > "$CASE/log.levers" 2>&1
      break
    fi
    sleep 0.2
  done
) &
LEVER_WATCHER=$!
echo "A5  lever watcher armed (pid $LEVER_WATCHER), fires at pimpleFoam start"

# --- LAUNCH -------------------------------------------------------------------
date -u +%Y-%m-%dT%H:%M:%SZ > "$RUN/LAUNCH_STAMP.txt"
setsid nohup "${CMD[@]}" > "$RUN/log.driver" 2>&1 < /dev/null &
SETSID_PID=$!
echo "$SETSID_PID" > "$RUN/PID.txt"
echo
echo "LAUNCHED  setsid pid $SETSID_PID   cwd $REPO"
echo "run dir   $RUN"
echo "stamp     $(cat "$RUN/LAUNCH_STAMP.txt")"
echo "driver    $RUN/log.driver"
echo "ONE RUN ONLY.  No relaunch without the supervisor's word."
exit 0
