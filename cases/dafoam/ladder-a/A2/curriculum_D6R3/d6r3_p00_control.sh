#!/bin/bash
# P00 -- VERBATIM SMOKE CONTROL for D6R3.  Runs /home/ubuntu/dafoam-tutorials/CRM_Wing
# EXACTLY AS SHIPPED: its own preProcessing.sh, its own genWingMesh.py, its own runScript.py.
# NO lab wrapper, NO lab guards, NO staging module, NO multipoint, NO forces function object.
# ONE disclosed deviation: decomposeParDict numberOfSubdomains 72 -> RANKS, because the owner's
# allocation leaves 96-48-20 = 28 cores and 72 non-overlapping cores do not exist on this box.
set -uo pipefail
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085
SRC=/home/ubuntu/dafoam-tutorials/CRM_Wing
ARMDIR=$ROOT/P00
IMG=dafoam-idwarp-rot:v1
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
LOG=$ROOT/P00_${STAMP}.log
LEDGER=$ROOT/ledger.txt
say(){ echo "D6R3_P00_$1 $2" | tee -a "$LEDGER"; }

# --- measure what is idle, by core, at launch.  Never a remembered number.
read -r -a SEL < <(python3 - <<'PY'
import time
def rd():
    d={}
    for l in open('/proc/stat'):
        if l.startswith('cpu') and l[3].isdigit():
            p=l.split(); d[int(p[0][3:])]=(sum(int(x) for x in p[1:]), int(p[4]))
    return d
a=rd(); time.sleep(5); b=rd()
u=[]
for c in sorted(a):
    dt=b[c][0]-a[c][0]; di=b[c][1]-a[c][1]
    u.append((100.0*(1-di/dt) if dt else 0.0, c))
u.sort()
idle=[c for x,c in u if x<=50]
print(len(idle), ' '.join(str(c) for x,c in u[:28]))
PY
)
NIDLE=${SEL[0]}; CORES=("${SEL[@]:1}")
CAP=28                       # 96 total - 48 reserved propeller - 20 reserved DrivAer
RANKS=$(( NIDLE < CAP ? NIDLE : CAP ))
CPUSET=$(IFS=,; echo "${CORES[*]:0:$RANKS}")
say CORES "measured_idle=$NIDLE cap=$CAP ranks=$RANKS cpuset=$CPUSET"
[ "$RANKS" -ge 8 ] || { say REFUSE "fewer than 8 idle cores"; exit 6; }

[ ! -d "$ARMDIR" ] || { say REFUSE "P00 dir exists, never overwritten"; exit 5; }
mkdir -p "$ARMDIR"
cp -r "$SRC"/. "$ARMDIR"/
cp "$ROOT/mesh/CRM_surfMesh.cgns.tar.gz" "$ARMDIR"/     # the shipped no-download branch of preProcessing.sh
MD5_PRE=$(md5sum "$ARMDIR/runScript.py" "$ARMDIR/preProcessing.sh" "$ARMDIR/genWingMesh.py" | tr '\n' ' ')
say VERBATIM "$MD5_PRE"
sed -i 's/^numberOfSubdomains     72;/numberOfSubdomains     '"$RANKS"';/' "$ARMDIR/system/decomposeParDict"
say DEVIATION_1 "decomposeParDict numberOfSubdomains 72 -> $RANKS (only change; disclosed)"
grep -n numberOfSubdomains "$ARMDIR/system/decomposeParDict" | tee -a "$LEDGER"

T0=$(date +%s)
sudo -n docker run --rm --name "d6r3_P00_${STAMP}" \
  --user 1000:1000 --group-add 1002 -e HOME=/tmp \
  --cpuset-cpus="$CPUSET" --memory=200g --memory-swap=200g \
  -v "$ARMDIR":/work -w /work "$IMG" bash -lc \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; \
   echo '=== DAFOAM VERSION PROBE ==='; \
   python -c 'import dafoam,os;print(\"dafoam.__version__\",getattr(dafoam,\"__version__\",\"NONE\"));print(\"path\",os.path.dirname(dafoam.__file__))'; \
   pip show dafoam 2>/dev/null | head -4; \
   cat /home/dafoamuser/dafoam/repos/dafoam/dafoam/__init__.py 2>/dev/null | head -5; \
   echo '=== PREPROCESSING (shipped, verbatim) ==='; \
   bash preProcessing.sh 2>&1 | tail -20; \
   echo '=== checkMesh cells ==='; checkMesh 2>&1 | grep -m1 'cells:'; \
   echo '=== PRIMAL (shipped runScript.py, -task run_model) ==='; \
   mpirun -np $RANKS python runScript.py -task run_model 2>&1" > "$LOG" 2>&1
RC=$?
T1=$(date +%s); WALL=$((T1-T0)); CM=$(python3 -c "print('%.3f'%($WALL*$RANKS/60))")
say ROW "arm=P00 rc=$RC wall_s=$WALL ranks=$RANKS core_min=$CM log=$LOG"
