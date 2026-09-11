#!/bin/bash
# rc is captured INSIDE the wrapper: `setsid timeout cmd` exits 0 for every outcome.
set -u
L=$1; N=$2; S0=$3; MD=$4
R=/home/ubuntu/Certonomous/verification/runs/M6C2_runs
mkdir -p $R/MP/$L
# uid fix: container runs as 1002 (dafoamuser), host dir is 1000:1000 mode 775, so
# writeCGNS died with cgio_open_file:ADF 8 Permission denied AFTER a complete march.
chmod 0777 $R/MP/$L
/usr/bin/time -f "EXTRUDE_WALL_S %e PEAK_RSS_KB %M" -o $R/MP/$L/time.extrude \
  docker run --rm -v $R:/work dafoam-team:v1 bash -c \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; python3 /work/MP/run_extrude.py /work/surface/m6_mp_$L.xyz /work/MP/$L/m6c2_mp_${L}_vol.cgns $N $S0 $MD" \
  > $R/MP/$L/log.extrude 2>&1
echo $? > $R/MP/$L/rc.extrude
