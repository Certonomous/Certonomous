#!/usr/bin/env bash
# Act D live-meshing viability: wall-clock the real mesh pipeline that built the
# 38,304-cell grid Act D's numbers belong to.
#
# Frozen with cases/dafoam/ACTD_MESH_TIME_PREREGISTRATION.md (committed 6e911354).
#
# Rule 4 guard: refuses outright if the run root already exists.
# Rule 12: hard cap 600 s wall. Overrun STOPS the run.
# Memory (setsid parent returns zero): rc is captured INSIDE the wrapper.
set -uo pipefail

RUNROOT=/home/ubuntu/certonomous-runs/ACTD-meshtime
CASE="$RUNROOT/case"
PRISTINE=/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing
PRISTINE_MD5=2906d52a5dbed2bacbaeaf85a37d3fe8
CAP_WALL_S=600
CPUS=4

if [ -e "$RUNROOT" ]; then
    echo "REFUSED: run root already exists: $RUNROOT" >&2
    exit 2
fi

got=$(md5sum "$PRISTINE/runScript_AeroOnly.py" | cut -d' ' -f1)
if [ "$got" != "$PRISTINE_MD5" ]; then
    echo "REFUSED: pristine runScript_AeroOnly.py md5 $got != $PRISTINE_MD5" >&2
    exit 2
fi

mkdir -p "$CASE"
cp -a "$PRISTINE"/. "$CASE"/

# The surface mesh archive: reuse the one already on the box rather than
# re-downloading, so network time is not counted as mesh time.
cp /home/ubuntu/certonomous-runs/A2-mach-wing/mdolab_wing_surface_mesh.cgns.tar.gz \
   "$CASE"/ 2>/dev/null || true

# The staged mesh script. Each stage is wall-clocked on its own; nothing is
# derived from a total. Written here rather than piped so it is on disk beside
# the run.
cat > "$CASE/stage_timed_mesh.sh" <<'INNER'
set -uo pipefail
T() { date +%s.%N; }
STAGES=/mnt/stage_times.txt
: > "$STAGES"
mark() { echo "$1 $(T)" >> "$STAGES"; }

mark pipeline_start
tar -xf mdolab_wing_surface_mesh.cgns.tar.gz
mark untar_done
cgns_utils coarsen mdolab_wing_surface_mesh.cgns surfaceMesh.cgns > /mnt/log_coarsen.txt 2>&1
mark coarsen_done
python genWingMesh.py > /mnt/log_pyhyp.txt 2>&1
mark pyhyp_done
plot3dToFoam -noBlank volumeMesh.xyz > /mnt/log_plot3dToFoam.txt 2>&1
mark plot3dToFoam_done
autoPatch 60 -overwrite > /mnt/log_autoPatch.txt 2>&1
mark autoPatch_done
createPatch -overwrite > /mnt/log_createPatch.txt 2>&1
mark createPatch_done
renumberMesh -overwrite > /mnt/log_renumberMesh.txt 2>&1
mark renumberMesh_done
checkMesh > /mnt/log_checkMesh.txt 2>&1
mark checkMesh_done
INNER

date -u +%s.%N > "$RUNROOT/t0"
sudo docker run --rm --cpus=$CPUS --memory=12g -v "$RUNROOT":/mnt -w /mnt/case \
    dafoam/opt-packages:latest bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     timeout ${CAP_WALL_S}s bash stage_timed_mesh.sh; \
     echo \"INNER_RC=\$?\" > /mnt/RUN_RC.txt" \
    > "$RUNROOT/meshtime.log" 2>&1
date -u +%s.%N > "$RUNROOT/t1"

sudo chown -R ubuntu:ubuntu "$RUNROOT" 2>/dev/null || true
echo "DONE rc_file=$(cat "$RUNROOT/RUN_RC.txt" 2>/dev/null)"
