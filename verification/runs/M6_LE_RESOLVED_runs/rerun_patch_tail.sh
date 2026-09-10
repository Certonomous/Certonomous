#!/bin/bash
# TASK 2 -- re-run the OpenFOAM tail from the volume PLOT3D so that THE DICT THAT SHIPS IS THE
# DICT THAT RAN.  createPatchDict was corrected at the BUILD side (name inout -> farfield,
# name sym -> symmetry, and the literal `sym` selector -- which never existed and logged
# "Cannot find any patch or group names matching sym" -- removed from the third entry).
# constant/polyMesh/boundary is NEVER hand-edited: that would fix the artifact, not the build.
#
# A RENAME MUST NOT MOVE A NUMBER.  Every checkMesh quantity is captured before and after and
# compared; a move is a STOP, not a note.
#
# Serial, 1 rank, no mpirun.  /usr/bin/time -v wraps plot3dToFoam to MEASURE its peak RSS --
# the Lf x8 feasibility question was previously answered by INFERENCE, and this converts it.
set +u
RR=/home/ubuntu/Certonomous/verification/runs/M6_LE_RESOLVED_runs
IMG=dafoam-idwarp-rot:v1
for L in Lc Lm; do
  S="$RR/$L/solve"
  # PRE-RENAME evidence is captured ONCE and never overwritten: it is the "before" side of the
  # "a rename must not move a number" comparison.
  [ -f "$S/boundary_PRERENAME.txt" ] || cp "$S/constant/polyMesh/boundary" "$S/boundary_PRERENAME.txt"
  [ -f "$S/log.checkMesh_PRERENAME" ] || cp "$S/log.checkMesh" "$S/log.checkMesh_PRERENAME"
  chmod -R 777 "$S" 2>/dev/null
  echo "=== $L: tail re-run start $(date -u +%H:%M:%SZ) ==="
  docker run --rm -u 1002:1002 -v "$S":/home/dafoamuser/mount -w /home/dafoamuser/mount \
    --name "m6gridb_tail_$L" "$IMG" bash -lc "
set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1
rm -rf constant/polyMesh
# PEAK-RSS MEASUREMENT.  GNU /usr/bin/time is ABSENT from this image (measured: rc 127), so
# peak resident set is taken TWO independent ways: a 0.2 s poller on the process's own
# /proc/<pid>/status VmHWM (the kernel's high-water mark), and the container cgroup-v2
# memory.peak delta.  Both are reported; they answer the Lf x8 feasibility question with a
# MEASUREMENT instead of the inference on the record.
cat /sys/fs/cgroup/memory.peak > MEM_cgroup_before_${L}.txt 2>/dev/null
plot3dToFoam -noBlank volumeMesh_${L}_yp1.xyz > log.plot3dToFoam 2>&1 &
P3D=\$!
HWM=0
while kill -0 \$P3D 2>/dev/null; do
  V=\$(awk '/^VmHWM:/{print \$2}' /proc/\$P3D/status 2>/dev/null)
  [ -n \"\$V\" ] && [ \"\$V\" -gt \"\$HWM\" ] && HWM=\$V
  sleep 0.2
done
wait \$P3D; RC=\$?
cat /sys/fs/cgroup/memory.peak > MEM_cgroup_after_${L}.txt 2>/dev/null
echo \"VmHWM_peak_kB=\$HWM\" > MEM_plot3dToFoam_${L}.txt
echo \"cgroup_peak_bytes=\$(cat /sys/fs/cgroup/memory.peak 2>/dev/null)\" >> MEM_plot3dToFoam_${L}.txt
echo \"rc_plot3dToFoam=\$RC\"
autoPatch 60 -overwrite     > log.autoPatch    2>&1; echo \"rc_autoPatch=\$?\"
createPatch -overwrite      > log.createPatch  2>&1; echo \"rc_createPatch=\$?\"
renumberMesh -overwrite     > log.renumberMesh 2>&1; echo \"rc_renumberMesh=\$?\"
checkMesh                   > log.checkMesh    2>&1; echo \"rc_checkMesh=\$?\"
" 2>&1 | grep -v VSPAERO | grep -v vspviewer
  echo "=== $L: tail re-run end $(date -u +%H:%M:%SZ) ==="
done
