#!/bin/bash
# D6R3 FIX LAUNCHER -- arms FIX_RELTOL1 and FIX_NONGAMG1 only.  The FROZEN producer runs, in the
# PUBLISHED order, with exactly ONE staged fvSolution change per arm.  DRAFT, nothing sent (rule 7).
# Registered by D6R3_FIX_PREREGISTRATION.md before any compute (rule 2).
#
# It is d6r3_diag_agglom_arm.sh with three disclosed changes: (a) the GAMGAgglomeration debug
# switch is NOT armed -- these arms differ from P0 in exactly one staged line; (b) the fvSolution
# edit is made by the registered instrument d6r3_fix_stage_fvsolution.py, which asserts block
# scope and refuses a loosening; (c) the arm is selected by $1.
#
# usage: d6r3_fix_arm.sh <FIX_RELTOL1|FIX_NONGAMG1>
set -uo pipefail
ARM="${1:?arm: FIX_RELTOL1 | FIX_NONGAMG1}"
case "$ARM" in
  FIX_RELTOL1)  MODE=reltol;  VALUE=2.008e-03; EXPECT='relTol                         2.008e-03;' ;;
  FIX_NONGAMG1) MODE=nongamg; VALUE=PBiCGStab; EXPECT='solver                         PBiCGStab;' ;;
  *) echo "D6R3_FIX REFUSE: unknown arm $ARM"; exit 70 ;;
esac
RANKS=28
MEMG=256
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085
CASE="$ROOT/mesh/L2"
HERE="$(cd "$(dirname "$0")" && pwd)"
IMG=dafoam-idwarp-rot:v1
PRODUCER_MD5=efc3e62699690edd32e4ee910aad09c8
STAGER="$HERE/d6r3_fix_stage_fvsolution.py"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
ARMDIR="$ROOT/$ARM"; LOG="$ROOT/${ARM}_${STAMP}.log"; LEDGER="$ROOT/ledger.txt"

say(){ echo "D6R3_$1 $2" | tee -a "$LEDGER"; }

[ "$(id -u)" -ne 0 ] || { say REFUSE "G-ROOT"; exit 71; }
case "$ROOT" in *CURRICULUM-D6R3*) : ;; *) say REFUSE "G-ROOT"; exit 71;; esac

GOT=$(sudo -n docker image inspect "$IMG" --format '{{index .RepoDigests 0}}' 2>/dev/null | sed 's/.*@//')
[ -n "$GOT" ] || GOT=$(sudo -n docker image inspect "$IMG" --format '{{.Id}}' 2>/dev/null)
case "$GOT" in *2927768a16ac*) say FIX_G-IMG "OK $GOT" ;;
  *) say REFUSE "G-IMG: image is $GOT"; exit 4;; esac

# G-FREEZE: the FROZEN producer is unedited, and the registered instruments are the ones that run
HAVE=$(md5sum "$HERE/d6r3_opt_runScript.py" | cut -d' ' -f1)
[ "$HAVE" = "$PRODUCER_MD5" ] || { say REFUSE "G-FREEZE: producer md5 $HAVE, frozen $PRODUCER_MD5"; exit 4; }
STAGER_MD5=$(md5sum "$STAGER" | cut -d' ' -f1)
GRADER_MD5=$(md5sum "$HERE/d6r3_fix_grade.py" | cut -d' ' -f1)
PREREG_MD5=$(md5sum "$HERE/D6R3_FIX_PREREGISTRATION.md" | cut -d' ' -f1)
say FIX_G-FREEZE "arm=$ARM producer=$HAVE stager=$STAGER_MD5 grader=$GRADER_MD5 prereg=$PREREG_MD5"

# G-PREREG: the pre-registration must be COMMITTED before compute (rule 2).  A dirty or untracked
# pre-registration refuses the launch -- the freeze is the document's entire evidentiary content.
PREREG_BLOB=$(cd "$HERE" && git rev-parse "HEAD:cases/dafoam/ladder-a/A2/curriculum_D6R3/D6R3_FIX_PREREGISTRATION.md" 2>/dev/null)
PREREG_DISK=$(cd "$HERE" && git hash-object D6R3_FIX_PREREGISTRATION.md)
[ -n "$PREREG_BLOB" ] || { say REFUSE "G-PREREG: D6R3_FIX_PREREGISTRATION.md is not in HEAD"; exit 3; }
[ "$PREREG_BLOB" = "$PREREG_DISK" ] || { say REFUSE "G-PREREG: on-disk pre-registration ($PREREG_DISK) is NOT the committed blob ($PREREG_BLOB)"; exit 3; }
for f in d6r3_fix_stage_fvsolution.py d6r3_fix_grade.py d6r3_fix_arm.sh; do
  B=$(cd "$HERE" && git rev-parse "HEAD:cases/dafoam/ladder-a/A2/curriculum_D6R3/$f" 2>/dev/null)
  D=$(cd "$HERE" && git hash-object "$f")
  [ "$B" = "$D" ] || { say REFUSE "G-PREREG: $f on disk ($D) is not the committed blob ($B)"; exit 3; }
done
say FIX_G-PREREG "prereg+stager+grader+launcher all == HEAD blobs; freeze sha $(cd "$HERE" && git rev-parse HEAD)"

[ ! -d "$ARMDIR" ] || { say REFUSE "G-COLD: $ARMDIR exists"; exit 5; }
[ -d "$CASE/constant/polyMesh" ] || { say REFUSE "G-COLD: no published mesh at $CASE"; exit 5; }

# G-CORES-PERCORE: sample /proc/stat twice, 5 s apart, take only cores >=85% idle.
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
[ -n "$CPUSET" ] || { say REFUSE "G-CORES-PERCORE: fewer than $RANKS cores measured >=85% idle"; exit 6; }
say FIX_G-CORES "cpuset=$CPUSET ranks=$RANKS cap=min(free,96-48-20)=28"

mkdir -p "$ARMDIR"
cp -r "$CASE/." "$ARMDIR/"
rm -rf "$ARMDIR"/processor* "$ARMDIR"/[1-9]* "$ARMDIR"/OptView.hst "$ARMDIR"/opt_SLSQP.txt
[ -d "$ARMDIR/0.orig" ] || { say REFUSE "G-INPUTS: no 0.orig/"; exit 7; }
rm -rf "$ARMDIR/0"; cp -r "$ARMDIR/0.orig" "$ARMDIR/0"
cp "$HERE/d6r3_opt_runScript.py" "$ARMDIR/runScript.py"
cp "$HERE/d6r3_inrun_guards.py" "$HERE/d6r3_mesh_read_gate.py" "$ARMDIR/"
cp -r /home/ubuntu/dafoam-tutorials/CRM_Wing/FFD "$ARMDIR/"

# --- THE ONE STAGED CHANGE.  Applied by the registered instrument, to the top-level system/
# --- fvSolution, BEFORE the three condition dirs are copied from it, so all four are identical.
FVS_BEFORE=$(md5sum "$ARMDIR/system/fvSolution" | cut -d' ' -f1)
python3 "$STAGER" "$ARMDIR/system/fvSolution" "$MODE" "$VALUE" 2>&1 | tee -a "$LEDGER" || { say REFUSE "G-STAGE-FVSOL: the staging instrument refused"; exit 10; }
FVS_AFTER=$(md5sum "$ARMDIR/system/fvSolution" | cut -d' ' -f1)
[ "$FVS_BEFORE" != "$FVS_AFTER" ] || { say REFUSE "G-STAGE-FVSOL: fvSolution md5 did not move ($FVS_BEFORE)"; exit 10; }
say FIX_FVSOL "mode=$MODE before=$FVS_BEFORE after=$FVS_AFTER"
# the diff against the PUBLISHED file, recorded, so the deviation is on the record as a diff
diff "$CASE/system/fvSolution" "$ARMDIR/system/fvSolution" | tee -a "$LEDGER"
NDIFF=$(diff "$CASE/system/fvSolution" "$ARMDIR/system/fvSolution" | grep -c '^[<>]')
case "$MODE" in
  reltol)  [ "$NDIFF" -eq 2 ] || { say REFUSE "G-STAGE-FVSOL: $NDIFF changed lines, expected 2 (one replacement)"; exit 10; } ;;
  nongamg) [ "$NDIFF" -eq 4 ] || { say REFUSE "G-STAGE-FVSOL: $NDIFF changed lines, expected 4 (two replacements)"; exit 10; } ;;
esac

for d in mp04 mp05 mp06; do rm -rf "$ARMDIR/$d"; mkdir -p "$ARMDIR/$d"; cp -r "$ARMDIR/0" "$ARMDIR/constant" "$ARMDIR/system" "$ARMDIR/$d/"; done
# READ-BACK: the staged line must be present in every condition dir the solver will actually read
for d in mp04 mp05 mp06; do
  grep -qF "$EXPECT" "$ARMDIR/$d/system/fvSolution" || { say REFUSE "G-STAGE-READBACK: '$EXPECT' not readable back from $d/system/fvSolution"; exit 10; }
done
say FIX_G-STAGE-READBACK "'$EXPECT' present in mp04 mp05 mp06"

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
H4=$(cd "$ARMDIR/mp04" && find 0 constant system -type f | sort | xargs md5sum | md5sum | cut -d' ' -f1)
H5=$(cd "$ARMDIR/mp05" && find 0 constant system -type f | sort | xargs md5sum | md5sum | cut -d' ' -f1)
H6=$(cd "$ARMDIR/mp06" && find 0 constant system -type f | sort | xargs md5sum | md5sum | cut -d' ' -f1)
say FIX_STAGE_HASH "mp04=$H4 mp05=$H5 mp06=$H6"
[ "$H4" = "$H5" ] && [ "$H5" = "$H6" ] || { say REFUSE "G-STAGE: the three condition dirs are NOT identical"; exit 9; }

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
say FIX_AGE_DATUM "$DATUM"

TASK=run_model
say FIX_ARM "$ARM task=$TASK ranks=$RANKS cpuset=$CPUSET mem=${MEMG}g stamp=$STAMP"
echo "D6R3_FIX_DEADLINE_IN_CONTAINER_S: NONE" | tee -a "$LEDGER"

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
say FIX_ROW "arm=$ARM rc=$RC wall_s=$WALL ranks=$RANKS core_min=$CM log=$LOG"
exit $RC
