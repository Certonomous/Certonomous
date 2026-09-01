#!/usr/bin/env bash
# A2-B2R -- independent lift-trim of the twist+shape MACH Tutorial Wing.
# Frozen with cases/dafoam/A2_B2R_INDEPENDENT_TRIM_PREREGISTRATION.md.
#
# This rung repairs the STARTING POINT of A2's B2 row, not its threshold. The
# 0.5 % band on G5 is A2's, byte for byte.
#
# WHAT IS DIFFERENT FROM run_a2_decomposition.sh, AND WHY -- each item is a
# defect measured in the A2 run, not a preference:
#
#  1. THE CONTAINER CANNOT REACH THE EVIDENCE.  A2 mounted the whole run root at
#     /mnt, so the pin manifest, t0/t1 and the instrument hashes all sat inside a
#     writable mount. Here only case/ and out/ are mounted; t0, t1,
#     pin_manifest.json, instrument_sha256.txt, decomp.log and cost.txt live in
#     the run root, outside every mount, and the container cannot touch them.
#  2. THE AGE DATUM HAD 5 ms OF MARGIN.  Measured in A2: the instrument copy
#     landed at 1788224781.093 and t0 at 1788224781.098. A `sleep 1` now
#     separates the last stage write from t0, so "pinned file older than t0"
#     cannot turn on filesystem timestamp granularity.
#  3. THE SURFACE GEOMETRY IS PRE-STAGED, NOT DOWNLOADED. preProcessing.sh
#     wgets mdolab_wing_surface_mesh.cgns.tar.gz when it is absent. The tarball
#     that produced A2's mesh is on disk (sha256 bc70f99c...); it is copied in
#     and PINNED, so no network fetch can substitute a different geometry under
#     an anchor comparison that depends on the mesh being A2's.
#  4. THE PROCESS rc AND THE PER-ROW VERDICTS ARE SEPARATE.  A2's RUN_RC.txt
#     reads INNER_RC=1 -- the B2 crash -- while six rows were individually
#     clean. The rc is recorded and reported; it does not by itself condemn a
#     row, and a row is never rescued by it either.
#  5. EVERY SELFTEST RUNS BEFORE THE SOLVER, NOT AFTER.  A comparator whose
#     controls are first exercised on the run's own data is a comparator nobody
#     has tested.
#
# Rule 4 guard: refuses outright if the run root already exists.
# Rule 12: hard cap 40 core-min = 600 s wall at 4 ranks. Overrun STOPS the run.
# setsid parent returns zero (L-...): rc is captured INSIDE the wrapper.

set -uo pipefail

REPO=/home/ubuntu/Certonomous
RUNROOT=/home/ubuntu/certonomous-runs/A2B2R-independent-trim
CASE="$RUNROOT/case"
OUT="$RUNROOT/out"
PRISTINE=/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing
PRISTINE_MD5=2906d52a5dbed2bacbaeaf85a37d3fe8

GEOM_TARBALL=/home/ubuntu/certonomous-runs/ACTD-a2-decomposition/case/mdolab_wing_surface_mesh.cgns.tar.gz
GEOM_SHA=bc70f99cc4eadbfc3ab5f211b6e3d5b857e571ff419dcebdedc0a328e498c53e

DRIVER=$REPO/cases/dafoam/a2_decomposition_driver.py
DRIVER_SHA=c4f421497ae221ae1f8fb2f655530ea552e6372a935a6d3e0355ce81a4389cf0
ROWS=$REPO/cases/dafoam/a2b2r_rows.json
ROWS_SHA=40a3fe7b559d4c1f66b78f1db64caa56d5efd4b93ee3ca5c480721bd76abe487
GUARD=$REPO/cases/dafoam/a2b2r_age_guard.py
GRADER=$REPO/cases/dafoam/grade_a2b2r.py

CAP_WALL_S=600
RANKS=4
MEMCAP=12g

refuse() { echo "REFUSED: $*" >&2; exit 2; }
sha() { sha256sum "$1" | cut -d' ' -f1; }

# --- rule 4 guard: the run root must not already exist -----------------------
[ -e "$RUNROOT" ] && refuse "run root already exists: $RUNROOT"

# --- the instrument must be the instrument that was frozen -------------------
got=$(md5sum "$PRISTINE/runScript_AeroOnly.py" | cut -d' ' -f1)
[ "$got" = "$PRISTINE_MD5" ] || refuse "pristine runScript_AeroOnly.py md5 $got != $PRISTINE_MD5"

# The driver is A2's, UNCHANGED. Nothing is derived from it by rename, so the
# rename defect class (a rename moves tokens, it cannot make prose true) has no
# purchase on it. Its sha256 is asserted against the frozen value here.
got=$(sha "$DRIVER"); [ "$got" = "$DRIVER_SHA" ] || refuse "driver sha256 $got != $DRIVER_SHA"
got=$(sha "$ROWS");   [ "$got" = "$ROWS_SHA" ]   || refuse "rows sha256 $got != $ROWS_SHA"
[ -f "$GEOM_TARBALL" ] || refuse "surface geometry tarball absent: $GEOM_TARBALL"
got=$(sha "$GEOM_TARBALL"); [ "$got" = "$GEOM_SHA" ] || refuse "geometry sha256 $got != $GEOM_SHA"

# --- the controls are exercised BEFORE the solver, on synthetic data ---------
python3 "$GUARD" selftest  > /tmp/a2b2r_guard_selftest.txt 2>&1 \
    || refuse "age-guard selftest FAILED -- see /tmp/a2b2r_guard_selftest.txt"
python3 "$GRADER" --selftest > /tmp/a2b2r_grader_selftest.txt 2>&1 \
    || refuse "comparator selftest FAILED -- see /tmp/a2b2r_grader_selftest.txt"
echo "selftests PASS (guard + comparator), before any solver start"

# --- stage --------------------------------------------------------------------
mkdir -p "$CASE" "$OUT"
cp -a "$PRISTINE"/. "$CASE"/
cp -a "$GEOM_TARBALL" "$CASE"/
cp "$DRIVER" "$CASE"/a2_decomposition_driver.py
cp "$ROWS"   "$CASE"/a2b2r_rows.json
sha256sum "$CASE/a2_decomposition_driver.py" "$CASE/a2b2r_rows.json" \
          "$CASE/mdolab_wing_surface_mesh.cgns.tar.gz" > "$RUNROOT/instrument_sha256.txt"
diff "$PRISTINE/runScript_AeroOnly.py" "$CASE/a2_decomposition_driver.py" \
     > "$RUNROOT/driver_vs_pristine.diff"

# --- pin the staged tree BEFORE the datum, then the datum --------------------
python3 "$GUARD" pin "$CASE" "$RUNROOT/pin_manifest.json" || refuse "pin failed"
sleep 1                      # defect 2 above: no 5 ms age-datum margin
date -u +%s > "$RUNROOT/t0"

# --- run ---------------------------------------------------------------------
# Only case/ and out/ are mounted; the evidence in the run root is unreachable
# from inside. rc is captured INSIDE the wrapper, never around it.
sudo docker run --rm --cpus=$RANKS --memory=$MEMCAP \
    -v "$CASE":/case -v "$OUT":/out -w /case \
    dafoam/opt-packages:latest bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     ./preProcessing.sh > preproc.log 2>&1 && \
     export DECOMP_ROWS=a2b2r_rows.json && \
     timeout ${CAP_WALL_S}s mpirun --allow-run-as-root -np $RANKS \
        python a2_decomposition_driver.py -task decomp; \
     echo \"INNER_RC=\$?\" > /out/RUN_RC.txt" \
    > "$RUNROOT/decomp.log" 2>&1
date -u +%s > "$RUNROOT/t1"

sudo chown -R ubuntu:ubuntu "$RUNROOT" 2>/dev/null || true
cp "$OUT/RUN_RC.txt" "$RUNROOT/RUN_RC.txt" 2>/dev/null || echo "INNER_RC=MISSING" > "$RUNROOT/RUN_RC.txt"

t0=$(cat "$RUNROOT/t0"); t1=$(cat "$RUNROOT/t1"); wall=$((t1 - t0))
core_min=$(python3 -c "print(f'{$wall*$RANKS/60:.2f}')")
echo "wall_s=$wall ranks=$RANKS core_min=$core_min cap_core_min=40.00" | tee "$RUNROOT/cost.txt"
cat "$RUNROOT/RUN_RC.txt"
if [ "$wall" -ge "$CAP_WALL_S" ]; then
    echo "CAP REACHED: the run was stopped by the ${CAP_WALL_S}s cap. Rows not reached are"
    echo "PENDING and are never estimated. An overrun does not get a new budget."
fi

# --- the age guard, then the frozen comparator --------------------------------
python3 "$GUARD" verify "$CASE" "$RUNROOT/pin_manifest.json" "$RUNROOT/t0" \
        "$RUNROOT/decomp.log" "$RUNROOT/RUN_RC.txt" | tee "$RUNROOT/AGE_GUARD.txt"
guard_rc=${PIPESTATUS[0]}
if [ "$guard_rc" -ne 0 ]; then
    echo "AGE GUARD REFUSED (exit $guard_rc). The rung is NOT A RESULT; the refusal token"
    echo "above names which clause fired. No grade is produced." >&2
    exit "$guard_rc"
fi

python3 "$GRADER" --runroot "$RUNROOT" | tee "$RUNROOT/GRADE.txt"
