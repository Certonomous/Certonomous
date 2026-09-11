#!/bin/bash
# Runs INSIDE the dafoam container. docker run exits 0 regardless of this rc,
# so the rc is written here, by this script, and the printed log is what is believed.
. /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1
cd /work || exit 90
python3 genMesh.py > pyhyp.log 2>&1
r=$?
echo "PYHYP_RC=$r" > pyhyp_rc.txt
echo "PYHYP_RC_WRITTEN_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> pyhyp_rc.txt
if [ "$r" = "0" ] && grep -q "PYHYP_WROTE" pyhyp.log; then
  echo "EXTRUDE_MARKER_OK $(date -u +%Y-%m-%dT%H:%M:%SZ)" > DONE_EXTRUDE
fi
echo "INNER_RC=$r"
tail -3 pyhyp.log
