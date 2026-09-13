#!/bin/bash
# D6R3 DIAGNOSTIC LAUNCHER -- arm DIAG_ORDER1 only.  DRAFT, nothing is sent or filed (rule 7).
# Registered by D6R3_DIAG_ORDER_PREREGISTRATION.md before any compute (rule 2).
# It is d6r3_run_arm.sh with three disclosed changes: the producer is the DIAGNOSTIC script and its
# md5 is frozen separately; the task is run_model; and G-CORES measures PER-CORE idle instead of
# loadavg, because the 1-minute loadavg cannot tell an allocated core from a busy one and that gap
# is already on this lab's record.
set -uo pipefail
ARM=DIAG_ORDER1
RANKS=28
MEMG=256
ITEM=D6R3
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085
CASE="$ROOT/mesh/L2"
HERE="$(cd "$(dirname "$0")" && pwd)"
IMG=dafoam-idwarp-rot:v1
DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
PRODUCER_MD5=5d6ce829a3d552669e708a6ebf2ea7a2
FROZEN_MD5=efc3e62699690edd32e4ee910aad09c8
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
ARMDIR="$ROOT/$ARM"; LOG="$ROOT/${ARM}_${STAMP}.log"; LEDGER="$ROOT/ledger.txt"

say(){ echo "D6R3_$1 $2" | tee -a "$LEDGER"; }

[ "$(id -u)" -ne 0 ] || { say REFUSE "G-ROOT"; exit 71; }
case "$ROOT" in *CURRICULUM-D6R3*) : ;; *) say REFUSE "G-ROOT"; exit 71;; esac

GOT=$(sudo -n docker image inspect "$IMG" --format '{{index .RepoDigests 0}}' 2>/dev/null | sed 's/.*@//')
[ -n "$GOT" ] || GOT=$(sudo -n docker image inspect "$IMG" --format '{{.Id}}' 2>/dev/null)
case "$GOT" in *2927768a16ac*) say DIAG_G-IMG "OK $GOT" ;;
  *) say REFUSE "G-IMG: image is $GOT"; exit 4;; esac

# G-FREEZE-DIAG: the diagnostic producer is the one registered ...
HAVE=$(md5sum "$HERE/d6r3_diag_order.py" | cut -d' ' -f1)
[ "$HAVE" = "$PRODUCER_MD5" ] || { say REFUSE "G-FREEZE-DIAG: diag producer md5 $HAVE, registered $PRODUCER_MD5"; exit 4; }
# ... AND the FROZEN producer is still untouched by this diagnostic.
HAVEF=$(md5sum "$HERE/d6r3_opt_runScript.py" | cut -d' ' -f1)
[ "$HAVEF" = "$FROZEN_MD5" ] || { say REFUSE "G-FROZEN: the frozen D6R3 producer has MOVED ($HAVEF, was $FROZEN_MD5)"; exit 4; }
say DIAG_G-FREEZE "diag=$HAVE frozen-untouched=$HAVEF"

[ ! -d "$ARMDIR" ] || { say REFUSE "G-COLD: $ARMDIR exists"; exit 5; }
[ -d "$CASE/constant/polyMesh" ] || { say REFUSE "G-COLD: no published mesh at $CASE"; exit 5; }

# G-CORES-PERCORE: sample /proc/stat twice, 5 s apart, and take only cores >=85% idle.
CPUSET=$(python3 - "$RANKS" <<'PY'
import sys, time
def snap():
    d={}
    for ln in open('/proc/stat'):
        if ln.startswith('cpu') and ln[3].isdigit():
            f=ln.split(); d[int(f[0][3:])]=[int(x) for x in f[1:]]
    return d
a=snap(); time.sleep(5); b=snap()
idle={}
for c in a:
    da=[y-x for x,y in zip(a[c],b[c])]
    tot=sum(da); idl=da[3]+da[4]
    idle[c]= idl/tot if tot else 1.0
free=sorted([c for c,v in idle.items() if v>=0.85])
n=int(sys.argv[1])
sys.stderr.write("MEASURED_IDLE_CORES=%d of %d\n"%(len(free),len(idle)))
print(",".join(str(c) for c in free[:n]) if len(free)>=n else "")
PY
) 2> >(tee -a "$LEDGER" >&2)
[ -n "$CPUSET" ] || { say REFUSE "G-CORES-PERCORE: fewer than $RANKS cores measured >=85% idle; not starting"; exit 6; }
say DIAG_G-CORES "cpuset=$CPUSET ranks=$RANKS cap=min(free,96-48-20)=28"

mkdir -p "$ARMDIR"
cp -r "$CASE/." "$ARMDIR/"
rm -rf "$ARMDIR"/processor* "$ARMDIR"/[1-9]* "$ARMDIR"/OptView.hst "$ARMDIR"/opt_SLSQP.txt
[ -d "$ARMDIR/0.orig" ] || { say REFUSE "G-INPUTS: no 0.orig/"; exit 7; }
rm -rf "$ARMDIR/0"; cp -r "$ARMDIR/0.orig" "$ARMDIR/0"
cp "$HERE/d6r3_diag_order.py" "$ARMDIR/runScript.py"
cp "$HERE/d6r3_inrun_guards.py" "$HERE/d6r3_mesh_read_gate.py" "$ARMDIR/"
cp -r /home/ubuntu/dafoam-tutorials/CRM_Wing/FFD "$ARMDIR/"
for d in mp04 mp05 mp06; do rm -rf "$ARMDIR/$d"; mkdir -p "$ARMDIR/$d"; cp -r "$ARMDIR/0" "$ARMDIR/constant" "$ARMDIR/system" "$ARMDIR/$d/"; done
for d in mp04 mp05 mp06; do
cat >> "$ARMDIR/$d/system/controlDict" <<'FO'

functions
{
    forces
    {
        type                forces;
        libs                ("libforces.so");
        writeControl        timeStep;
        timeInterval        1;
        log                 yes;
        patches             (wing);
        pName               p;
        UName               U;
        rho                 rhoInf;
        rhoInf              1.176829;
        CofR                (0 0 0);
    }
}
FO
done
# the three condition directories must be BYTE-IDENTICAL after staging -- asserted, not assumed
H4=$(cd "$ARMDIR/mp04" && find 0 constant system -type f | sort | xargs md5sum | md5sum | cut -d' ' -f1)
H5=$(cd "$ARMDIR/mp05" && find 0 constant system -type f | sort | xargs md5sum | md5sum | cut -d' ' -f1)
H6=$(cd "$ARMDIR/mp06" && find 0 constant system -type f | sort | xargs md5sum | md5sum | cut -d' ' -f1)
say DIAG_STAGE_HASH "mp04=$H4 mp05=$H5 mp06=$H6"
[ "$H4" = "$H5" ] && [ "$H5" = "$H6" ] || { say REFUSE "G-STAGE: the three condition dirs are NOT identical after staging"; exit 9; }

GINPUTS_MISSING=""
for fld in T U alphat nuTilda nut p; do
  for d in "$ARMDIR" "$ARMDIR/mp04" "$ARMDIR/mp05" "$ARMDIR/mp06"; do
    [ -r "$d/0/$fld" ] || GINPUTS_MISSING="$GINPUTS_MISSING $d/0/$fld"
  done
done
[ -z "$GINPUTS_MISSING" ] || { say REFUSE "G-INPUTS: missing:$GINPUTS_MISSING"; exit 7; }

touch "$ARMDIR/0/U"
DATUM=$(stat -c%Y "$ARMDIR/0/U" 2>/dev/null)
case "$DATUM" in ''|*[!0-9]*) say REFUSE "G-DATUM: empty/non-numeric ('$DATUM')"; exit 8 ;; esac
say DIAG_AGE_DATUM "$DATUM"

TASK=run_model
say DIAG_ARM "$ARM task=$TASK ranks=$RANKS cpuset=$CPUSET mem=${MEMG}g stamp=$STAMP"
echo "D6R3_DIAG_DEADLINE_IN_CONTAINER_S: NONE" | tee -a "$LEDGER"

T0=$(date +%s)
sudo -n docker run --rm --name "d6r3_${ARM}_${STAMP}" \
  --user 1000:1000 --group-add 1002 -e HOME=/tmp \
  -e D6R3_PUBLISHED_RUNSCRIPT=/pub/runScript.py \
  --cpuset-cpus="$CPUSET" --memory="${MEMG}g" --memory-swap="${MEMG}g" \
  -v "$ARMDIR":/work -v /home/ubuntu/dafoam-tutorials/CRM_Wing:/pub:ro -w /work \
  "$IMG" bash -lc "source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; \
     mpirun -np $RANKS python runScript.py -task $TASK 2>&1" > "$LOG" 2>&1
RC=$?
T1=$(date +%s); WALL=$((T1-T0)); CM=$(python3 -c "print('%.3f'%($WALL*$RANKS/60))")
say DIAG_ROW "arm=$ARM rc=$RC wall_s=$WALL ranks=$RANKS core_min=$CM log=$LOG"
exit $RC
