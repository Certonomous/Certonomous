#!/bin/bash
# D6R3 MULTIPOINT LAUNCHER -- the deliverable.  The FROZEN producer runs VERBATIM.
#
# ZERO DEVIATIONS FROM THE PUBLISHED CASE EXCEPT MULTIPOINT ITSELF (Sanaa, directive section M).
# No staged fvSolution.  No staged runScript.  primalMinResTol, primalMinResTolDiff and endTime
# are the published values and are not touched.  primalFuncStdTol is NOT used -- it is the
# registered contingency and it is not needed, because the decomposition sweep measured the
# published case CONVERGING AT ALL THREE CONDITIONS at 20 ranks:
#     DECOMP_N20, rc=0, every condition nuTilda 4.265593605364853e-08 = 4.2656 x primalMinResTol,
#     inside the PUBLISHED abort criterion (primalMinResTolDiff 1.0e2) by a factor of 23.4.
# At 28 ranks position 2 floors at 1.757696578179007e-06 and FAILS.  The defect is
# decomposition-dependent, so this arm runs at the count that has no defect.
#
# usage: d6r3_mp_r2_arm.sh <RANKS> [<EXCLUDE_CORES_CSV>]
set -uo pipefail
RANKS="${1:?ranks}"
EXCLUDE="${2:-}"
ARM=MP_R2
MEMG=120
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085
CASE="$ROOT/mesh/L2"
PUB=/home/ubuntu/dafoam-tutorials/CRM_Wing
HERE="$(cd "$(dirname "$0")" && pwd)"
IMG=dafoam-idwarp-rot:v1
PRODUCER_MD5=efc3e62699690edd32e4ee910aad09c8
CAP=28
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
ARMDIR="$ROOT/$ARM"; LOG="$ROOT/${ARM}_${STAMP}.log"; LEDGER="$ROOT/ledger.txt"
say(){ echo "D6R3_MPR2_$1 $2" | tee -a "$LEDGER"; }

[ "$(id -u)" -ne 0 ] || { say REFUSE "G-ROOT"; exit 71; }
case "$ROOT" in *CURRICULUM-D6R3*) : ;; *) say REFUSE "G-ROOT"; exit 71;; esac
[ "$RANKS" -ge 2 ] && [ "$RANKS" -le "$CAP" ] || { say REFUSE "G-CAP: ranks $RANKS outside 2..$CAP"; exit 6; }

GOT=$(sudo -n docker image inspect "$IMG" --format '{{index .RepoDigests 0}}' 2>/dev/null | sed 's/.*@//')
[ -n "$GOT" ] || GOT=$(sudo -n docker image inspect "$IMG" --format '{{.Id}}' 2>/dev/null)
case "$GOT" in *2927768a16ac*) say G-IMG "OK $GOT" ;; *) say REFUSE "G-IMG: $GOT"; exit 4;; esac

# G-FREEZE -- the producer that runs is the frozen producer, UNMODIFIED.  There is no stager here.
HAVE=$(md5sum "$HERE/d6r3_opt_runScript.py" | cut -d' ' -f1)
[ "$HAVE" = "$PRODUCER_MD5" ] || { say REFUSE "G-FREEZE: producer md5 $HAVE, frozen $PRODUCER_MD5"; exit 4; }
say G-FREEZE "producer md5 $HAVE -- RUNS VERBATIM, no staged edit of any kind"

# G-PREREG -- registration and launcher must BE the committed blobs (rule 2)
for f in D6R3_MULTIPOINT_PREREGISTRATION.md d6r3_mp_r2_arm.sh d6r3_mp_stage_r2.py; do
  B=$(cd "$HERE" && git rev-parse "HEAD:cases/dafoam/ladder-a/A2/curriculum_D6R3/$f" 2>/dev/null)
  D=$(cd "$HERE" && git hash-object "$f")
  [ -n "$B" ] || { say REFUSE "G-PREREG: $f not in HEAD"; exit 3; }
  [ "$B" = "$D" ] || { say REFUSE "G-PREREG: $f on disk ($D) is not the committed blob ($B)"; exit 3; }
done
say G-PREREG "registration+launcher == HEAD blobs; freeze sha $(cd "$HERE" && git rev-parse HEAD)"

[ ! -d "$ARMDIR" ] || { say REFUSE "G-COLD: $ARMDIR exists; never overwritten"; exit 5; }
[ -d "$CASE/constant/polyMesh" ] || { say REFUSE "G-COLD: no mesh at $CASE"; exit 5; }

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
[ -n "$CPUSET" ] || { say REFUSE "G-CORES: fewer than $RANKS cores measured >=85% idle outside the exclusion set"; exit 6; }
say G-CORES "ranks=$RANKS cpuset=$CPUSET excluded=[$EXCLUDE] cap=min(free,96-48-20)=$CAP"

mkdir -p "$ARMDIR"
cp -r "$CASE/." "$ARMDIR/"
rm -rf "$ARMDIR"/processor* "$ARMDIR"/[1-9]* "$ARMDIR"/OptView.hst "$ARMDIR"/opt_SLSQP.txt
[ -d "$ARMDIR/0.orig" ] || { say REFUSE "G-INPUTS: no 0.orig/"; exit 7; }
rm -rf "$ARMDIR/0"; cp -r "$ARMDIR/0.orig" "$ARMDIR/0"
python3 "$HERE/d6r3_mp_stage_r2.py" "$HERE/d6r3_opt_runScript.py" "$ARMDIR/runScript.py" 2>&1 | tee -a "$LEDGER"
[ "${PIPESTATUS[0]}" = "0" ] || { say REFUSE "G-STAGE: the registered stager refused"; exit 10; }
NDIFF=$(diff "$HERE/d6r3_opt_runScript.py" "$ARMDIR/runScript.py" | grep -c "^[<>]")
[ "$NDIFF" -eq 9 ] || { say REFUSE "G-STAGE: $NDIFF changed lines, expected 9 (1 replaced + 5 added + 1 replaced, as < and >)"; exit 10; }
cp "$HERE/d6r3_inrun_guards.py" "$HERE/d6r3_mesh_read_gate.py" "$ARMDIR/"
cp -r "$PUB/FFD" "$ARMDIR/"

# G-VERBATIM -- the staged runScript IS the frozen producer, and every system dict IS the published
# one.  This is the gate that makes the words "zero deviations" checkable rather than asserted.
S=$(md5sum "$ARMDIR/runScript.py" | cut -d' ' -f1)
F=$(md5sum "$HERE/d6r3_opt_runScript.py" | cut -d' ' -f1)
[ "$F" = "$PRODUCER_MD5" ] || { say REFUSE "G-FREEZE: the frozen producer itself moved: $F"; exit 4; }
grep -q '"jacMatReOrdering": "rcm",' "$ARMDIR/runScript.py" || { say REFUSE "G-VERBATIM: rcm not readable back from the staged runScript"; exit 11; }
grep -q '"jacMatReOrdering": "natural",' "$ARMDIR/runScript.py" && { say REFUSE "G-VERBATIM: natural still present"; exit 11; }
grep -q '"pcFillLevel": 1,' "$ARMDIR/runScript.py" || { say REFUSE "G-VERBATIM: pcFillLevel must stay at the published 1"; exit 11; }
grep -q "AOA0_HOTSTART\[pt\]" "$ARMDIR/runScript.py" || { say REFUSE "G-VERBATIM: hot start not wired into the patchV DV"; exit 11; }
# Scope BOTH checks to the daOptions dict and match an ASSIGNED KEY, not a bare word.  The frozen
# producer mentions primalMinResTolDiff in its RUN RECORD -- `daOptions.get("primalMinResTolDiff",
# "ABSENT-published-default")` -- and the first version of this guard matched that and refused a
# correct launch.  Same over-broad match I had already repaired in the stager: a lesson is not
# applied until EVERY call site asserts it (L-221/L-222).  It failed CLOSED, which is the right
# direction for a guard to be wrong in.
DOPT=$(python3 -c "
import sys
s=open('$ARMDIR/runScript.py').read()
body=s.split('daOptions = {')[1].split(chr(10)+'}')[0]
bad=[k for k in ('\"primalFuncStdTol\"','\"primalMinResTolDiff\"') if k in body]
print(','.join(bad))
")
[ -z "$DOPT" ] || { say REFUSE "G-VERBATIM: forbidden key(s) ASSIGNED in daOptions: $DOPT"; exit 11; }
PUBFAIL=""
for f in controlDict fvSchemes fvSolution decomposeParDict createPatchDict; do
  A=$(md5sum "$PUB/system/$f" | cut -d' ' -f1); B=$(md5sum "$ARMDIR/system/$f" | cut -d' ' -f1)
  [ "$A" = "$B" ] || PUBFAIL="$PUBFAIL $f($B!=$A)"
done
[ -z "$PUBFAIL" ] || { say REFUSE "G-VERBATIM: system dicts differ from published:$PUBFAIL"; exit 11; }
grep -q 'relTol                         0.1;' "$ARMDIR/system/fvSolution" || { say REFUSE "G-VERBATIM: published relTol 0.1 not readable back"; exit 11; }
grep -q 'endTime         2000;' "$ARMDIR/system/controlDict" || { say REFUSE "G-VERBATIM: published endTime 2000 not readable back"; exit 11; }
grep -q '"primalMinResTol": 1.0e-8' "$ARMDIR/runScript.py" || { say REFUSE "G-VERBATIM: primalMinResTol 1.0e-8 not readable back"; exit 11; }
say G-VERBATIM "staged runScript md5 $S (frozen $F + 2 registered edits); all 5 system dicts byte-identical to published; relTol 0.1, endTime 2000, primalMinResTol 1.0e-8 read back; primalFuncStdTol ABSENT; primalMinResTolDiff UNSET (published 1.0e2 stands)"

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
H4=$(cd "$ARMDIR/mp04" && find 0 constant system -type f | sort | xargs md5sum | md5sum | cut -d' ' -f1)
H5=$(cd "$ARMDIR/mp05" && find 0 constant system -type f | sort | xargs md5sum | md5sum | cut -d' ' -f1)
H6=$(cd "$ARMDIR/mp06" && find 0 constant system -type f | sort | xargs md5sum | md5sum | cut -d' ' -f1)
PTSF=""; for c in points points.gz; do [ -f "$ARMDIR/mp04/constant/polyMesh/$c" ] && PTSF="$ARMDIR/mp04/constant/polyMesh/$c" && break; done
[ -n "$PTSF" ] || { say REFUSE "G-STAGE: no polyMesh points in mp04"; exit 9; }
say STAGE_HASH "mp04=$H4 mp05=$H5 mp06=$H6 points=$(md5sum "$PTSF"|cut -d' ' -f1) from $(basename "$PTSF")"
[ "$H4" = "$H5" ] && [ "$H5" = "$H6" ] || { say REFUSE "G-STAGE: the three condition dirs are NOT identical"; exit 9; }

GM=""
for fld in T U alphat nuTilda nut p; do
  for d in "$ARMDIR" "$ARMDIR/mp04" "$ARMDIR/mp05" "$ARMDIR/mp06"; do
    [ -r "$d/0/$fld" ] || GM="$GM $d/0/$fld"
  done
done
[ -z "$GM" ] || { say REFUSE "G-INPUTS: missing:$GM"; exit 7; }

touch "$ARMDIR/0/U"
DATUM=$(stat -c%Y "$ARMDIR/0/U" 2>/dev/null)
case "$DATUM" in ''|*[!0-9]*) say REFUSE "G-DATUM: empty/non-numeric ('$DATUM')"; exit 8 ;; esac
say AGE_DATUM "$DATUM"

TASK=run_driver
say ARM "$ARM task=$TASK ranks=$RANKS cpuset=$CPUSET mem=${MEMG}g stamp=$STAMP log=$LOG"
echo "D6R3_MP_DEADLINE_IN_CONTAINER_S: NONE  (directive #17: no run is stopped by a cap)" | tee -a "$LEDGER"
echo "D6R3_MP_NO_GRADIENT_VERIFICATION: task=run_driver only.  No check_totals, no FD arm, no gradient spot-check." | tee -a "$LEDGER"

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
# L-40 LEVER ACTIVITY -- the WHOLE proof the change acted.  An unrecognised ordering string falls
# back SILENTLY to nested dissection (DALinearEqn.C:300-304), so the printed block is the evidence.
GOTORD=$(grep -m1 "^Mat ReOrdering:" "$LOG" | sed "s/.*: //")
GOTFIL=$(grep -m1 "^ILU PC Fill Level:" "$LOG" | sed "s/.*: //")
say LEVER "Mat ReOrdering=<$GOTORD> ILU PC Fill Level=<$GOTFIL>"
case "$GOTORD" in
  rcm*) say LEVER-OK "the registered change ACTED: the solver printed rcm" ;;
  "")   say LEVER-FAIL "NO 'Mat ReOrdering:' line in the log -- the change is UNPROVEN and this arm is NOT A RESULT" ;;
  *)    say LEVER-FAIL "the solver printed '$GOTORD', NOT rcm -- the change DID NOT ACT and this arm is NOT A RESULT" ;;
esac
exit $RC
