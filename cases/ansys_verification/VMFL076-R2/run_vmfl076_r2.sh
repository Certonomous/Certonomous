#!/bin/bash
# ===========================================================================
# VMFL076 -- Forced Convection Over a Flat Plate (VM2026R1 p.219).  LAUNCHER.
#
# ONE LEVEL PER INVOCATION.  Each level is launched separately under `setsid`
# so it survives this lane, the session and any fleet kill.
#
# NO `set -u`.  REASON, MEASURED BY THIS TEAM: OpenFOAM v2606's etc/bashrc
# dereferences WM_PROJECT_DIR at line 184 BEFORE assigning it, so `set -u`
# aborts the source with rc 127 and no solver ever starts.  `set -e` is ALSO
# not relied on -- it does not gate at a Bash tool top level nor inside
# `( set -e; ... )` -- so EVERY check gates explicitly with `|| { ...; exit; }`.
#
# Non-droppable list carried here:
#   Amendment 2  launch-time freeze verification of prereg AND comparator
#   Amendment 3  cap in the EXECUTABLE path; no set -u; mesh birth certificate;
#                planted-control selftest; a smoke mode that exercises THIS file
#   Amendment 5  consumer-side field completeness, REFUSING BY NAME
#   Amendment 5a required = fvSolution solver blocks INTERSECT closure MINUS phi
#   rule 4       a pre-existing 0/ or time directory REFUSES (exit 2)
#   RUN_RC.txt is written on the SUCCESS path AND on every abort path, so a
#   timeout-fired rc=124 is on disk too.
#
# usage:  run_vmfl076_r2.sh <graded|smoke> <L1|L2|L3|ALL>
# ===========================================================================
REPO=/home/ubuntu/Certonomous
CASE=$REPO/cases/ansys_verification/VMFL076-R2
RUNROOT=$REPO/verification/runs/ansys_verification/VMFL076-R2
SCRATCH=/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad
PREREG=cases/ansys_verification/VMFL076-R2/PREREGISTRATION.md
GRADER=cases/ansys_verification/VMFL076-R2/grade_vmfl076.py
RANKS=1

MODE="${1:-graded}"
LEVEL="${2:-}"

# ---------------------------------------------------------------------------
# THE ONE CHANGE THIS R2 MAKES: a COARSER r = 2 triple whose FINEST level is
# byte-identical to attempt 1's COARSEST (160 x 60 at endTime 2000).  Register
# row #27 diagnosed the R1 triple as refined PAST its own asymptotic range
# (e21 = -5.007461e-05, e32 = +3.511790e-06, R = -0.070131, OSCILLATORY), and
# its RESULTS.md sec.7 names the repair by name: "a COARSER triple that sits
# inside the asymptotic range -- e.g. 40x15, 80x30, 160x60, with L1 of this run
# as its finest level."  That is exactly this table and nothing else.
#
# endTime is 2000 AT EVERY LEVEL, and the justification does NOT read any R1
# ANSWER: 2000 was REGISTERED (not measured) as sufficient for the 160 x 60 mesh
# in the R1 freeze, and at a fixed relaxation a COARSER mesh needs no MORE
# iterations than a finer one, so 2000 is an upper bound for 80 x 30 and 40 x 15.
# WRITEINTERVAL and SAMPLEINTERVAL are carried character for character from the
# R1 L1 row (250 / 50), so "last time == endTime" stays literally testable and
# the 201-point gate line is sampled on the same schedule.
#
# CAP is carried character for character from the R1 L1 row (10 core-min) at
# EVERY level -- a PER-LEVEL cap, never a shared drawdown.  It is not tightened
# to the new estimate: a cap is a runaway guard, and tightening it from a
# prediction would convert it into one.
# ---------------------------------------------------------------------------
case "$LEVEL" in
  L1) NX=40;  NY=15; ENDTIME=2000; WRITEINTERVAL=250; SAMPLEINTERVAL=50; CAP=10 ;;
  L2) NX=80;  NY=30; ENDTIME=2000; WRITEINTERVAL=250; SAMPLEINTERVAL=50; CAP=10 ;;
  L3) NX=160; NY=60; ENDTIME=2000; WRITEINTERVAL=250; SAMPLEINTERVAL=50; CAP=10 ;;
  ALL)
      # Run the registered triple in order, coarsest first, by re-invoking THIS
      # script once per level.  Nothing per-level is duplicated here: every
      # check, guard, cap and record below runs exactly as it does for a single
      # level.  A non-zero rc STOPS the ladder -- a later level is never launched
      # after an earlier one failed, and an overrun does not get a new budget
      # (rule 12).
      RC_ALL=0
      for LV in L1 L2 L3; do
        echo "=== VMFL076-R2 ALL: launching $LV"
        bash "$0" "$MODE" "$LV" || { RC_ALL=$?; echo "STOP at $LV: rc=$RC_ALL -- later levels are NOT launched"; break; }
      done
      echo "=== VMFL076-R2 ALL done, overall rc=$RC_ALL"
      exit $RC_ALL ;;
  *) echo "ABORT: level must be L1, L2, L3 or ALL (got '$LEVEL')"; exit 1 ;;
esac
GY=200

cd $REPO || { echo "ABORT: cannot cd $REPO"; exit 1; }

# ------------------------------------------------- AMENDMENT 2: the freeze --
H=$(git rev-parse HEAD) || { echo "ABORT: cannot read HEAD"; exit 1; }
GD=$(git hash-object $GRADER) || { echo "ABORT: cannot hash $GRADER"; exit 1; }
PD=$(git hash-object $PREREG 2>/dev/null)

if [ "$MODE" = "smoke" ]; then
    # The smoke test EXERCISES THIS LAUNCHER (Amendment 3 item 6). It may run
    # BEFORE the freeze is committed, so it CANNOT prove the freeze -- and it
    # says so instead of printing a claim it did not earn (Amendment 6a item 1).
    RUNROOT=$SCRATCH/vmfl076_smokeroot
    case "$RUNROOT" in
      /tmp/claude-1000/*) : ;;
      *) echo "ABORT: smoke mode refuses a run root outside the scratchpad"; exit 1 ;;
    esac
    ENDTIME=60; WRITEINTERVAL=30; SAMPLEINTERVAL=10
    echo "SMOKE MODE: THE FREEZE IS NOT PROVED HERE. HEAD=$H prereg_disk=$PD comparator_disk=$GD"
else
    PB=$(git rev-parse $H:$PREREG 2>/dev/null) || { echo "ABORT: $PREREG is NOT committed at HEAD -- the freeze must be committed BEFORE compute"; exit 1; }
    GB=$(git rev-parse $H:$GRADER 2>/dev/null) || { echo "ABORT: $GRADER is NOT committed at HEAD"; exit 1; }
    [ -n "$PD" ] || { echo "ABORT: cannot hash $PREREG on disk"; exit 1; }
    [ "$PB" = "$PD" ] || { echo "ABORT: pre-registration on disk ($PD) != HEAD blob ($PB)"; exit 1; }
    [ "$GB" = "$GD" ] || { echo "ABORT: comparator on disk ($GD) != HEAD blob ($GB)"; exit 1; }
    echo "FREEZE VERIFIED  HEAD=$H  prereg=$PB  comparator=$GB"
fi

# ------------------------------------- the planted control must be live -----
STLOG=$(mktemp -d) || { echo "ABORT: cannot make a selftest log dir"; exit 1; }
python3 $GRADER --selftest > $STLOG/selftest.log 2>&1 \
    || { echo "ABORT: comparator --selftest is NOT green (log $STLOG/selftest.log)"; exit 1; }
python3 -O $GRADER --selftest > $STLOG/selftest_O.log 2>&1 \
    || { echo "ABORT: comparator --selftest is NOT green under python3 -O (log $STLOG/selftest_O.log)"; exit 1; }
echo "COMPARATOR SELFTEST GREEN under python3 AND python3 -O"

# ------------------------------------------- no `assert` in the instrument --
NASSERT=$(grep -cE '^[[:space:]]*assert[[:space:]]' $GRADER)
[ "$NASSERT" = "0" ] || { echo "ABORT: $GRADER carries $NASSERT assert statement(s) -- Amendment 6 forbids an assert that carries a guard"; exit 1; }
echo "ASSERT SWEEP CLEAN: 0 assert statements in the comparator"

# L-343 USER PIN, before the bashrc is sourced.  etc/bashrc:190 reads
#   export WM_PROJECT_USER_DIR="$HOME/$WM_PROJECT/${USER:-user}-$WM_PROJECT_VERSION"
# and a cron-started queue runner carries LOGNAME but no USER, so FOAM_USER_LIBBIN
# would resolve to a user-v2606 directory that does not exist.  This case links no
# user-built library, so the pin CANNOT change a number here; it is applied because
# the launcher must be correct under the runner that will actually launch it, and
# USER / id -un / FOAM_USER_LIBBIN are RECORDED as infrastructure fields (L-342).
export USER="${USER:-${LOGNAME:-$(id -un)}}"
[ -n "$USER" ] || { echo "ABORT: cannot resolve USER for the OpenFOAM bashrc (L-343)"; exit 1; }
source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>&1
[ -n "$WM_PROJECT_DIR" ] || { echo "ABORT: OpenFOAM environment did not load"; exit 1; }

D=$RUNROOT/$LEVEL

# ------------------------------------------------ rule 4's pre-run guard ----
if [ -d "$D" ]; then
    if [ -d "$D/0" ] || ls -d $D/[0-9]* > /dev/null 2>&1; then
        echo "ABORT: $D already holds a 0/ or a time directory -- rule 4's guard refuses it"
        exit 2
    fi
fi
mkdir -p $D || { echo "ABORT: cannot make $D"; exit 1; }

# RUN_RC.txt is written on EVERY exit path, including the aborts above this
# point being the only ones that precede the run directory existing.
write_rc() {
    cat > $D/RUN_RC.txt <<EOF
rc                 = $1
stage              = $2
dir                = $D
mode               = $MODE
level              = $LEVEL
nx                 = $NX
ny                 = $NY
gy                 = $GY
endTime            = $ENDTIME
writeInterval      = $WRITEINTERVAL
sampleInterval     = $SAMPLEINTERVAL
wall_s             = $3
ranks              = $RANKS
core_min           = $4
cap_core_min       = $CAP
timeout_s_granted  = $5
head               = $H
prereg_disk_blob   = $PD
comparator_disk_blob = $GD
finished_utc       = $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF
}
abort() { echo "ABORT[$LEVEL]: $2"; write_rc "$1" "$3" 0 0.0000 0; exit 1; }

cat > $D/LAUNCH_RECORD.txt <<EOF
utc            = $(date -u +%Y-%m-%dT%H:%M:%SZ)
mode           = $MODE
level          = $LEVEL
HEAD           = $H
prereg_blob    = ${PB:-NOT_PROVED_IN_SMOKE_MODE}
comparator_blob= ${GB:-NOT_PROVED_IN_SMOKE_MODE}
prereg_disk    = $PD
comparator_disk= $GD
nx             = $NX
ny             = $NY
gy             = $GY
endTime        = $ENDTIME
writeInterval  = $WRITEINTERVAL
sampleInterval = $SAMPLEINTERVAL
ranks          = $RANKS
cap_core_min   = $CAP
user_env       = $USER
id_un          = $(id -un)
foam_user_libbin = ${FOAM_USER_LIBBIN:-unset}
pid            = $$
EOF

cp -r $CASE/case/* $D/ || abort 91 "cannot stage the case into $D" stage

sed -e "s/__NX__/$NX/" -e "s/__NY__/$NY/" -e "s/__GY__/$GY/" \
    $D/system/blockMeshDict.template > $D/system/blockMeshDict || abort 92 "blockMeshDict templating failed" stage
rm -f $D/system/blockMeshDict.template
sed -e "s/__ENDTIME__/$ENDTIME/" -e "s/__WRITEINTERVAL__/$WRITEINTERVAL/" \
    -e "s/__SAMPLEINTERVAL__/$SAMPLEINTERVAL/" \
    $D/system/controlDict.template > $D/system/controlDict || abort 93 "controlDict templating failed" stage
rm -f $D/system/controlDict.template
grep -q "__" $D/system/blockMeshDict && abort 94 "blockMeshDict still holds an unsubstituted placeholder" stage
grep -q "__" $D/system/controlDict  && abort 95 "controlDict still holds an unsubstituted placeholder" stage

# --- endTime must be an EXACT multiple of BOTH intervals, checked BEFORE the solve
python3 -c "
import sys
et, wi, si = $ENDTIME, $WRITEINTERVAL, $SAMPLEINTERVAL
if wi <= 0 or si <= 0 or et % wi != 0 or et % si != 0:
    sys.exit(1)
" || abort 96 "endTime $ENDTIME is not an exact multiple of writeInterval $WRITEINTERVAL and sampleInterval $SAMPLEINTERVAL -- the run would write nothing gradeable at endTime" stage

# --- AMENDMENT 5 / 5a: what the CONSUMER needs, from its ACTUAL configuration
NEED=$(python3 - "$D" <<'PYNEED'
import os, re, sys
d = sys.argv[1]
fvs = open(os.path.join(d, "system", "fvSolution")).read()
fvs = re.sub(r"//.*", "", fvs)
blk = fvs[fvs.index("solvers"):]
keys = re.findall(r'^\s*"?\(?([A-Za-z|()]+)\)?"?\s*$', blk, flags=re.M)
cand = set()
for k in keys:
    for part in k.strip("()").split("|"):
        p = part.strip("()")
        if p and p not in ("solvers", "SIMPLE"):
            cand.add(p)
tp = open(os.path.join(d, "constant", "turbulenceProperties")).read()
m = re.search(r"simulationType\s+(\w+)\s*;", tp)
if not m:
    sys.stderr.write("no simulationType\n"); sys.exit(1)
closure = m.group(1)
creates = {"laminar": set(), "kEpsilon": {"k", "epsilon", "nut"},
           "kOmegaSST": {"k", "omega", "nut"}, "RAS": set(), "LES": set()}
if closure not in creates:
    sys.stderr.write("closure %r has no registered field set -- REFUSED, never guessed\n" % closure)
    sys.exit(1)
required = (cand & ({"p", "U", "T"} | creates[closure])) | {"p", "U", "T"}
required -= {"phi"}
print(" ".join(sorted(required)))
PYNEED
) || abort 97 "consumer-side field enumeration failed" stage
[ -n "$NEED" ] || abort 98 "the consumer-side field enumeration returned nothing" stage
for F in $NEED; do
    [ -f "$D/0/$F" ] || [ -f "$D/0/$F.gz" ] || abort 99 "required field '$F' is MISSING from 0/ (consumer needs: $NEED)" stage
done
echo "FIELD COMPLETENESS OK: $NEED"

( cd $D && blockMesh > log.blockMesh 2>&1 ) || abort 101 "blockMesh failed" mesh
( cd $D && checkMesh > log.checkMesh 2>&1 ) || abort 102 "checkMesh failed" mesh
grep -q "Mesh OK" $D/log.checkMesh || abort 103 "checkMesh did not report Mesh OK" mesh

# ---- AMENDMENT 3 item 5: mesh birth certificate, READ OFF THE MESH
( cd $D && postProcess -func writeCellCentres -time 0 > log.writeCellCentres0 2>&1 ) \
    || abort 104 "writeCellCentres at time 0 failed" mesh
python3 $CASE/mesh_birth_vmfl076.py "$D" > $D/MESH_BIRTH_CERTIFICATE.txt 2> $D/log.birthcert || abort 105 "mesh birth certificate failed" mesh
echo "MESH BIRTH CERTIFICATE WRITTEN"

# ---- AMENDMENT 3 item 2: the cap, in the EXECUTABLE path
TIMEOUT_S=$(python3 -c "print(int($CAP*60/$RANKS))") || abort 106 "cap arithmetic failed" mesh
echo "LAUNCH $LEVEL nx=$NX ny=$NY endTime=$ENDTIME cap=${CAP} core-min timeout=${TIMEOUT_S}s pid=$$ cwd=$D"
T0=$(date +%s)
( cd $D && timeout ${TIMEOUT_S}s simpleFoam > log.simpleFoam 2>&1 )
RC=$?
T1=$(date +%s)
WALL=$((T1-T0))
CORE_MIN=$(python3 -c "print('%.4f' % ($WALL*$RANKS/60.0))")

if [ $RC -eq 124 ]; then
    echo "CAP CROSSED[$LEVEL]: the ${CAP} core-min runaway guard stopped the run at ${WALL}s (${CORE_MIN} core-min). REPORTED, not absorbed."
fi

write_rc "$RC" "solver" "$WALL" "$CORE_MIN" "$TIMEOUT_S"

if [ $RC -ne 0 ]; then
    echo "LEVEL $LEVEL ENDED rc=$RC after ${WALL}s (${CORE_MIN} core-min) -- a non-zero exit is a FINDING, not a retry"
    exit $RC
fi

[ -d "$D/$ENDTIME" ] || { echo "ABORT[$LEVEL]: no field directory at endTime $ENDTIME"; write_rc 107 "endtime-missing" "$WALL" "$CORE_MIN" "$TIMEOUT_S"; exit 1; }
for F in $NEED; do
    [ -f "$D/$ENDTIME/$F" ] || [ -f "$D/$ENDTIME/$F.gz" ] || { echo "ABORT[$LEVEL]: field '$F' MISSING at endTime"; write_rc 108 "field-missing" "$WALL" "$CORE_MIN" "$TIMEOUT_S"; exit 1; }
done
echo "LEVEL $LEVEL rc=0 wall=${WALL}s ${CORE_MIN} core-min; fields at endTime: $NEED"
