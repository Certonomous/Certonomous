#!/usr/bin/env bash
# A2 drag decomposition -- Act D fix 2. Frozen with
# cases/dafoam/A2_DRAG_DECOMPOSITION_PREREGISTRATION.md.
#
# Evaluates the seven pre-registered design-variable rows in ONE container
# session, so the mesh build and OpenMDAO setup are paid once. The row order is
# fixed in a2_decomposition_rows.json and BOTH gate rows (A0, A4) land in the
# first five solves, so a cap-stop still decides the gates.
#
# Rule 4 guard: refuses outright if the run root already exists.
# Rule 12: hard cap 60 core-min = 900 s wall at 4 ranks. Overrun STOPS the run.
# Memory (setsid parent returns zero): rc is captured INSIDE the wrapper.
set -uo pipefail

REPO=/home/ubuntu/Certonomous
RUNROOT=/home/ubuntu/certonomous-runs/ACTD-a2-decomposition
CASE="$RUNROOT/case"
PRISTINE=/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing
PRISTINE_MD5=2906d52a5dbed2bacbaeaf85a37d3fe8
CAP_WALL_S=900
RANKS=4

# --- rule 4 guard: the run root must not already exist -----------------------
if [ -e "$RUNROOT" ]; then
    echo "REFUSED: run root already exists: $RUNROOT" >&2
    exit 2
fi

# --- the instrument must be the instrument that was frozen -------------------
got=$(md5sum "$PRISTINE/runScript_AeroOnly.py" | cut -d' ' -f1)
if [ "$got" != "$PRISTINE_MD5" ]; then
    echo "REFUSED: pristine runScript_AeroOnly.py md5 $got != $PRISTINE_MD5" >&2
    exit 2
fi

mkdir -p "$CASE"
cp -a "$PRISTINE"/. "$CASE"/
cp "$REPO/cases/dafoam/a2_decomposition_driver.py" "$CASE"/
cp "$REPO/cases/dafoam/a2_decomposition_rows.json" "$CASE"/
sha256sum "$CASE/a2_decomposition_driver.py" "$CASE/a2_decomposition_rows.json" \
    > "$RUNROOT/instrument_sha256.txt"

# The driver's own diff against the pristine script, recorded beside the run so a
# reader never has to take "one added block" on trust.
diff "$PRISTINE/runScript_AeroOnly.py" "$CASE/a2_decomposition_driver.py" \
    > "$RUNROOT/driver_vs_pristine.diff"

date -u +%s > "$RUNROOT/t0"
sudo docker run --rm --cpus=$RANKS --memory=12g -v "$RUNROOT":/mnt -w /mnt/case \
    dafoam/opt-packages:latest bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     ./preProcessing.sh > preproc.log 2>&1 && \
     export DECOMP_ROWS=a2_decomposition_rows.json && \
     timeout ${CAP_WALL_S}s mpirun --allow-run-as-root -np $RANKS \
        python a2_decomposition_driver.py -task decomp; \
     echo \"INNER_RC=\$?\" > /mnt/RUN_RC.txt" \
    > "$RUNROOT/decomp.log" 2>&1
date -u +%s > "$RUNROOT/t1"

sudo chown -R ubuntu:ubuntu "$RUNROOT" 2>/dev/null || true

t0=$(cat "$RUNROOT/t0"); t1=$(cat "$RUNROOT/t1")
wall=$((t1 - t0))
echo "wall_s=$wall core_min=$(python3 -c "print(f'{$wall*$RANKS/60:.2f}')")" \
    | tee "$RUNROOT/cost.txt"
cat "$RUNROOT/RUN_RC.txt" 2>/dev/null || echo "INNER_RC=MISSING"
grep -a "^DECOMP_RESULT\|^DECOMP_SETCHECK\|^DECOMP_REFUSE\|^DECOMP_ALL_ROWS_DONE" \
    "$RUNROOT/decomp.log" || echo "NO DECOMP LINES -- run produced nothing"
