#!/bin/bash
# D6R3 LAUNCHER -- the only thing that starts a D6R3 container.
# DRAFT.  Registered by PREREGISTRATION.md (R4) section 7a.  Nothing is sent or filed (rule 7).
#
# usage: d6r3_run_arm.sh <ARM> <RANKS> <CPUSET> <MEM_G>
#   ARM = P0 | O_mp | A12
set -uo pipefail
ARM="${1:?arm}"; RANKS="${2:?ranks}"; CPUSET="${3:?cpuset}"; MEMG="${4:?memory GiB}"
ITEM=D6R3
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085
CASE="$ROOT/mesh/L2"                       # the PUBLISHED mesh, built and measured (R4 s5)
HERE="$(cd "$(dirname "$0")" && pwd)"
IMG=dafoam-idwarp-rot:v1
DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
PRODUCER_MD5=efc3e62699690edd32e4ee910aad09c8
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
ARMDIR="$ROOT/$ARM"; LOG="$ROOT/${ARM}_${STAMP}.log"; LEDGER="$ROOT/ledger.txt"
mkdir -p "$ROOT"

say(){ echo "D6R3_$1 $2" | tee -a "$LEDGER"; }

# G-ROOT -- never run as root, and never inside a foreign item's run root (Sanaa Launch item 6)
[ "$(id -u)" -ne 0 ] || { say REFUSE "G-ROOT: this launcher never runs as root"; exit 71; }
case "$ROOT" in *CURRICULUM-D6R3*) : ;; *) say REFUSE "G-ROOT: run root is not D6R3's"; exit 71;; esac

# G-IMG -- the image is pinned BY DIGEST and refused on any other
GOT=$(sudo -n docker image inspect "$IMG" --format '{{index .RepoDigests 0}}' 2>/dev/null | sed 's/.*@//')
[ -n "$GOT" ] || GOT=$(sudo -n docker image inspect "$IMG" --format '{{.Id}}' 2>/dev/null)
case "$GOT" in *2927768a16ac*) say G-IMG "OK $GOT" ;;
  *) say REFUSE "G-IMG: image is $GOT, registered $DIGEST"; exit 4;; esac

# G-FREEZE -- the producer that runs is the producer that was frozen
HAVE=$(md5sum "$HERE/d6r3_opt_runScript.py" | cut -d' ' -f1)
if [ "$PRODUCER_MD5" != "D6R3_PRODUCER_MD5_PLACEHOLDER" ] && [ "$HAVE" != "$PRODUCER_MD5" ]; then
  say REFUSE "G-FREEZE: producer md5 $HAVE, frozen $PRODUCER_MD5"; exit 4
fi
say G-FREEZE "producer md5 $HAVE"

# G-COLD -- an arm directory that already holds a solve is refused, never overwritten
[ ! -d "$ARMDIR" ] || { say REFUSE "G-COLD: $ARMDIR exists; a guard refuses a case where a time dir may exist"; exit 5; }
[ -d "$CASE/constant/polyMesh" ] || { say REFUSE "G-COLD: the published mesh is not at $CASE"; exit 5; }

# G-CORES -- refuse to START on a loaded box; never stops anything running (directive #17)
LOAD1=$(awk '{print int($1)}' /proc/loadavg); NPROC=$(nproc)
FREE=$(( NPROC - LOAD1 ))
[ "$FREE" -ge "$RANKS" ] || { say REFUSE "G-CORES: $FREE measurably free of $NPROC, need $RANKS"; exit 6; }
say G-CORES "free=$FREE of $NPROC, ranks=$RANKS"

# stage a COLD copy of the published case, then set the age datum LAST
mkdir -p "$ARMDIR"
cp -r "$CASE/." "$ARMDIR/"
rm -rf "$ARMDIR"/processor* "$ARMDIR"/[1-9]* "$ARMDIR"/OptView.hst "$ARMDIR"/opt_SLSQP.txt
# REPAIR 1 (ADDENDUM 1, 2026-09-13): instantiate the initial fields.  VERBATIM from the published
# pipeline -- CRM_Wing/preProcessing.sh:29 is `cp -r 0.orig 0`.  Its absence is what killed P0 at
# 18:58:42Z: no 0/, so no processor*/0/p, so PETSc SEGV and MPI_ABORT 59, rc=59, 21.467 core-min
# of WASTE and no measurement.  The fix is the published line, not an invention.
[ -d "$ARMDIR/0.orig" ] || { say REFUSE "G-INPUTS: no 0.orig/ to instantiate the fields from"; exit 7; }
rm -rf "$ARMDIR/0"; cp -r "$ARMDIR/0.orig" "$ARMDIR/0"
cp "$HERE/d6r3_opt_runScript.py" "$ARMDIR/runScript.py"
cp "$HERE/d6r3_inrun_guards.py" "$HERE/d6r3_mesh_read_gate.py" "$ARMDIR/"
cp -r "$CASE/../../../../dafoam-tutorials/CRM_Wing/FFD" "$ARMDIR/" 2>/dev/null || \
  cp -r /home/ubuntu/dafoam-tutorials/CRM_Wing/FFD "$ARMDIR/"
for d in mp04 mp05 mp06; do rm -rf "$ARMDIR/$d"; mkdir -p "$ARMDIR/$d"; cp -r "$ARMDIR/0" "$ARMDIR/constant" "$ARMDIR/system" "$ARMDIR/$d/"; done
# rule 10: the forces function object is an OBSERVER -- it computes and writes, it does not enter
# the equations.  Appended to each condition's controlDict, never to the published file in git.
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
# --- G-INPUTS (ADDENDUM 1) -- a LAUNCH PRECONDITION, not a grading gate.  It can only prevent a
# --- run from starting; it never changes how a completed run is graded.  G-IMG, G-FREEZE and
# --- G-CORES all passed cleanly on the failed P0 and NONE of them looks at whether the case can
# --- actually be read.  Refuses on any absence, naming the missing path.
GINPUTS_MISSING=""
for f in "$ARMDIR/constant/polyMesh/points" "$ARMDIR/constant/polyMesh/faces"          "$ARMDIR/constant/polyMesh/owner" "$ARMDIR/constant/polyMesh/neighbour"          "$ARMDIR/constant/polyMesh/boundary"          "$ARMDIR/constant/thermophysicalProperties" "$ARMDIR/constant/turbulenceProperties"          "$ARMDIR/system/controlDict" "$ARMDIR/system/fvSchemes" "$ARMDIR/system/fvSolution"          "$ARMDIR/system/decomposeParDict" "$ARMDIR/FFD/wingFFD.xyz" "$ARMDIR/runScript.py"          "$ARMDIR/d6r3_inrun_guards.py" "$ARMDIR/d6r3_mesh_read_gate.py"; do
  [ -r "$f" ] || [ -r "$f.gz" ] || GINPUTS_MISSING="$GINPUTS_MISSING $f"
done
for fld in T U alphat nuTilda nut p; do
  for d in "$ARMDIR" "$ARMDIR/mp04" "$ARMDIR/mp05" "$ARMDIR/mp06"; do
    [ -r "$d/0/$fld" ] || GINPUTS_MISSING="$GINPUTS_MISSING $d/0/$fld"
  done
done
if [ -n "$GINPUTS_MISSING" ]; then
  say REFUSE "G-INPUTS: the arm cannot be read; missing:$GINPUTS_MISSING"; exit 7
fi
say G-INPUTS "all inputs present and readable"

touch "$ARMDIR/0/U"                                  # THE AGE DATUM, set last
DATUM=$(stat -c%Y "$ARMDIR/0/U" 2>/dev/null)
# --- REPAIR 2 (ADDENDUM 1) -- AN EMPTY AGE DATUM REFUSES THE LAUNCH.  On the failed P0 the ledger
# --- printed `D6R3_AGE_DATUM ` with NO VALUE and NOTHING STOPPED: a reader with no writer, the
# --- precise disease of s22.4 clause (c) and of primal_residual.json, relocated into the launcher.
# --- Had it refused, that arm would have cost ZERO instead of 21.467 core-min.  MEASURED FAILING
# --- TO FIRE on that run, which is why it exists.
case "$DATUM" in
  ''|*[!0-9]*) say REFUSE "G-DATUM: the age datum is EMPTY or non-numeric ('$DATUM') -- the age guard has no reference and a run without one cannot be graded complete"; exit 8 ;;
esac
say AGE_DATUM "$DATUM"

case "$ARM" in
  P0)   TASK="compute_totals" ;;
  A12)  TASK="run_model" ;;
  *)    TASK="run_driver" ;;
esac
say ARM "$ARM task=$TASK ranks=$RANKS cpuset=$CPUSET mem=${MEMG}g stamp=$STAMP"
echo "D6R3_DEADLINE_IN_CONTAINER_S: NONE" | tee -a "$LEDGER"

if [ "${D6R3_DRYRUN:-0}" = "1" ]; then
  say DRYRUN "every launch precondition passed; stopping before the container"
  exit 0
fi

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
ROOTOWNED=$(find "$ARMDIR" -newermt "@$DATUM" \( -uid 0 -o -gid 0 \) 2>/dev/null | wc -l)
say ROW "arm=$ARM rc=$RC wall_s=$WALL ranks=$RANKS core_min=$CM root_owned=$ROOTOWNED log=$LOG"
exit $RC
