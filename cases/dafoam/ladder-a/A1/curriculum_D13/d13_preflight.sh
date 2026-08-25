#!/usr/bin/env bash
# Gate G6, run as its OWN command immediately before each launch, and READ
# before the launch command is issued -- never polled by a background process.
# free_cores = nproc - load1 >= 4  AND  MemAvailable >= 12 GiB.
# Exit 0 = OPEN, 3 = NOT OPEN.  Derived from `curriculum_D2/d2_preflight.sh`
# (md5 4e8641f93aa7ea6d40635870fdb8ccfc) with one change: BASE.
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D13-a1-basin-restart
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
L1=$(awk '{print $1}' /proc/loadavg)
N=$(nproc)
MA=$(awk '/MemAvailable/{printf "%.2f", $2/1048576}' /proc/meminfo)
FC=$(python3 -c "print(round($N-$L1,2))")
OK=$(python3 -c "print(1 if ($N-$L1)>=4 and $MA>=12 else 0)")
S=$([ "$OK" = 1 ] && echo OPEN || echo NOT_OPEN)
echo "$TS arm=${1:-?} nproc=$N load1=$L1 free_cores=$FC memavail_GiB=$MA gate=$S" | tee -a "$BASE/preflight_history.txt"
[ "$OK" = 1 ] && exit 0 || exit 3
