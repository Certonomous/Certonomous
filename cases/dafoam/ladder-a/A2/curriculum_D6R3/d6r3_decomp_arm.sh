#!/bin/bash
# D6R3 DECOMP LAUNCHER -- one cell of the decomposition sweep.  The FROZEN producer runs the
# PUBLISHED configuration with ZERO staged file edits.  The ONLY thing this launcher varies
# between cells is `mpirun -np <RANKS>` and the cpuset it is pinned to.
#
# WHY THAT IS SUFFICIENT, and it is a source fact, not an inference:
#   pyDAFoam.py:2228 writes `numberOfSubdomains %d` from self.nProcs -- the MPI comm size --
#   over system/decomposeParDict before calling decomposePar (pyDAFoam.py:1456-1467).  The
#   number in the dict on disk is therefore inert; the rank count IS the decomposition.
#   Measured: the published dict says 72 and the P0 log printed `scotch [28]` under -np 28.
#
# DRAFT, nothing sent or filed (rule 7).  Registered by D6R3_DECOMP_PREREGISTRATION.md before
# any compute (rule 2).
#
# usage: d6r3_decomp_arm.sh <RANKS> [<EXCLUDE_CORES_CSV>]
set -uo pipefail
RANKS="${1:?ranks}"
EXCLUDE="${2:-}"
ARM=$(printf "DECOMP_N%02d" "$RANKS")
MEMG=120
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085
CASE="$ROOT/mesh/L2"
PUB=/home/ubuntu/dafoam-tutorials/CRM_Wing
HERE="$(cd "$(dirname "$0")" && pwd)"
IMG=dafoam-idwarp-rot:v1
PRODUCER_MD5=efc3e62699690edd32e4ee910aad09c8
CAP=28                         # 96 total - 48 RESERVED propeller - 20 RESERVED DrivAer
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
ARMDIR="$ROOT/$ARM"; LOG="$ROOT/${ARM}_${STAMP}.log"; LEDGER="$ROOT/ledger.txt"

say(){ echo "D6R3_DEC_$1 $2" | tee -a "$LEDGER"; }

[ "$(id -u)" -ne 0 ] || { say REFUSE "G-ROOT: never as root"; exit 71; }
case "$ROOT" in *CURRICULUM-D6R3*) : ;; *) say REFUSE "G-ROOT: run root is not D6R3's"; exit 71;; esac
[ "$RANKS" -ge 2 ] && [ "$RANKS" -le "$CAP" ] || { say REFUSE "G-CAP: ranks $RANKS outside 2..$CAP"; exit 6; }

GOT=$(sudo -n docker image inspect "$IMG" --format '{{index .RepoDigests 0}}' 2>/dev/null | sed 's/.*@//')
[ -n "$GOT" ] || GOT=$(sudo -n docker image inspect "$IMG" --format '{{.Id}}' 2>/dev/null)
case "$GOT" in *2927768a16ac*) say G-IMG "OK $GOT" ;;
  *) say REFUSE "G-IMG: image is $GOT"; exit 4;; esac

# G-FREEZE: the frozen producer is unedited
HAVE=$(md5sum "$HERE/d6r3_opt_runScript.py" | cut -d' ' -f1)
[ "$HAVE" = "$PRODUCER_MD5" ] || { say REFUSE "G-FREEZE: producer md5 $HAVE, frozen $PRODUCER_MD5"; exit 4; }
say G-FREEZE "arm=$ARM producer=$HAVE grader=$(md5sum "$HERE/d6r3_decomp_grade.py" | cut -d' ' -f1)"

# G-PREREG: the pre-registration and the whole grading path must BE the committed blobs (rule 2)
for f in D6R3_DECOMP_PREREGISTRATION.md d6r3_decomp_grade.py d6r3_decomp_arm.sh d6r3_decomp_sweep.sh; do
  B=$(cd "$HERE" && git rev-parse "HEAD:cases/dafoam/ladder-a/A2/curriculum_D6R3/$f" 2>/dev/null)
  D=$(cd "$HERE" && git hash-object "$f")
  [ -n "$B" ] || { say REFUSE "G-PREREG: $f is not in HEAD"; exit 3; }
  [ "$B" = "$D" ] || { say REFUSE "G-PREREG: $f on disk ($D) is not the committed blob ($B)"; exit 3; }
done
FREEZE=$(cd "$HERE" && git rev-parse HEAD)
say G-PREREG "prereg+grader+launcher+sweep all == HEAD blobs; freeze sha $FREEZE"

[ ! -d "$ARMDIR" ] || { say REFUSE "G-COLD: $ARMDIR exists; never overwritten"; exit 5; }
[ -d "$CASE/constant/polyMesh" ] || { say REFUSE "G-COLD: no mesh at $CASE"; exit 5; }

# G-CORES-PERCORE: sample /proc/stat twice 5 s apart; take only cores >=85% idle, never a core
# in EXCLUDE (a sibling cell of this sweep that has not yet loaded its cores).  Refuses to START
# on a loaded box; it never stops anything running (directive #17).
CPUSET=$(python3 - "$RANKS" "$EXCLUDE" <<'PY'
import sys, time
def snap():
    d={}
    for ln in open('/proc/stat'):
        if ln.startswith('cpu') and ln[3].isdigit():
            f=ln.split(); d[int(f[0][3:])]=[int(x) for x in f[1:]]
    return d
a=snap(); time.sleep(5); b=snap()
ex=set(int(x) for x in sys.argv[2].split(',') if x.strip())
idle={}
for c in a:
    da=[y-x for x,y in zip(a[c],b[c])]
    tot=sum(da); idl=da[3]+da[4]
    idle[c]= idl/tot if tot else 1.0
free=sorted([c for c,v in idle.items() if v>=0.85 and c not in ex])
n=int(sys.argv[1])
sys.stderr.write("MEASURED_IDLE_CORES=%d of %d (excluded %d)\n"%(len(free),len(idle),len(ex)))
print(",".join(str(c) for c in free[:n]) if len(free)>=n else "")
PY
) 2> >(tee -a "$LEDGER" >&2)
[ -n "$CPUSET" ] || { say REFUSE "G-CORES-PERCORE: fewer than $RANKS cores measured >=85% idle outside the exclusion set"; exit 6; }
say G-CORES "arm=$ARM ranks=$RANKS cpuset=$CPUSET excluded=[$EXCLUDE] cap=min(free,96-48-20)=$CAP"
echo "$CPUSET" > "$ROOT/$ARM.cpuset"   # so a sibling cell of the same batch can EXCLUDE these cores

mkdir -p "$ARMDIR"
cp -r "$CASE/." "$ARMDIR/"
rm -rf "$ARMDIR"/processor* "$ARMDIR"/[1-9]* "$ARMDIR"/OptView.hst "$ARMDIR"/opt_SLSQP.txt
[ -d "$ARMDIR/0.orig" ] || { say REFUSE "G-INPUTS: no 0.orig/"; exit 7; }
rm -rf "$ARMDIR/0"; cp -r "$ARMDIR/0.orig" "$ARMDIR/0"
cp "$HERE/d6r3_opt_runScript.py" "$ARMDIR/runScript.py"
cp "$HERE/d6r3_inrun_guards.py" "$HERE/d6r3_mesh_read_gate.py" "$ARMDIR/"
cp -r "$PUB/FFD" "$ARMDIR/"

# --- G-PUBLISHED -- THE CONTROL THAT MAKES "NOTHING ELSE CHANGED" CHECKABLE.  Every system
# --- dictionary this cell will run must be BYTE-IDENTICAL to the published tutorial's.  This
# --- is the gate that would catch a leftover staged fvSolution from a previous arm, and it is
# --- the whole evidentiary content of the word "published" in this sweep.
PUBFAIL=""
for f in controlDict fvSchemes fvSolution decomposeParDict createPatchDict; do
  A=$(md5sum "$PUB/system/$f" | cut -d' ' -f1); B=$(md5sum "$ARMDIR/system/$f" | cut -d' ' -f1)
  [ "$A" = "$B" ] && say G-PUBLISHED "system/$f $A IDENTICAL to published" || PUBFAIL="$PUBFAIL $f($B!=$A)"
done
[ -z "$PUBFAIL" ] || { say REFUSE "G-PUBLISHED: staged system dicts DIFFER from published:$PUBFAIL"; exit 11; }
grep -q 'relTol                         0.1;' "$ARMDIR/system/fvSolution" || { say REFUSE "G-PUBLISHED: published p relTol 0.1 not readable back"; exit 11; }
grep -q 'endTime         2000;' "$ARMDIR/system/controlDict" || { say REFUSE "G-PUBLISHED: published endTime 2000 not readable back"; exit 11; }
grep -q '"primalMinResTol": 1.0e-8' "$ARMDIR/runScript.py" || { say REFUSE "G-PUBLISHED: primalMinResTol 1.0e-8 not readable back from the producer"; exit 11; }

for d in mp04 mp05 mp06; do rm -rf "$ARMDIR/$d"; mkdir -p "$ARMDIR/$d"; cp -r "$ARMDIR/0" "$ARMDIR/constant" "$ARMDIR/system" "$ARMDIR/$d/"; done
# The forces function object is an OBSERVER: it computes and writes, it does not enter the
# equations.  Appended per condition exactly as P0/DIAG/FIX did, so the cells stay comparable.
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
# REPAIR 1 (ADDENDUM 1): this recorder looked only for polyMesh/points and the mesh is GZIPPED,
# so it printed mp04_points= EMPTY.  It now names the file it hashed and REFUSES on neither.
PTSF=""; for c in points points.gz; do [ -f "$ARMDIR/mp04/constant/polyMesh/$c" ] && PTSF="$ARMDIR/mp04/constant/polyMesh/$c" && break; done
[ -n "$PTSF" ] || { say REFUSE "G-STAGE: neither polyMesh/points nor points.gz present in mp04"; exit 9; }
PTS=$(md5sum "$PTSF" | cut -d' ' -f1)
say STAGE_HASH "arm=$ARM mp04=$H4 mp05=$H5 mp06=$H6 mp04_points=$PTS from $(basename "$PTSF")"
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
say AGE_DATUM "arm=$ARM $DATUM"

TASK=run_model
say ARM "$ARM task=$TASK ranks=$RANKS cpuset=$CPUSET mem=${MEMG}g stamp=$STAMP log=$LOG"
echo "D6R3_DEC_DEADLINE_IN_CONTAINER_S: NONE  (directive #17: no run is stopped by a cap)" | tee -a "$LEDGER"

T0=$(date +%s)
sudo -n docker run --rm --name "d6r3_${ARM}_${STAMP}" \
  --user 1000:1000 --group-add 1002 -e HOME=/tmp \
  -e D6R3_PUBLISHED_RUNSCRIPT=/pub/runScript.py \
  --cpuset-cpus="$CPUSET" --memory="${MEMG}g" --memory-swap="${MEMG}g" \
  -v "$ARMDIR":/work -v "$PUB":/pub:ro -w /work \
  "$IMG" bash -lc "source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; \
     mpirun -np $RANKS python runScript.py -task $TASK 2>&1" > "$LOG" 2>&1
RC=$?
T1=$(date +%s); WALL=$((T1-T0)); CM=$(python3 -c "print('%.3f'%($WALL*$RANKS/60))")
say ROW "arm=$ARM rc=$RC wall_s=$WALL ranks=$RANKS core_min=$CM cpuset=$CPUSET log=$LOG"
python3 "$HERE/d6r3_decomp_grade.py" "$ARM" "$RANKS" "$LOG" "$ARMDIR" "$RC" > "$ROOT/${ARM}_GRADE.json" 2>"$ROOT/${ARM}_GRADE.err"
say GRADED "arm=$ARM -> $ROOT/${ARM}_GRADE.json"
exit $RC
