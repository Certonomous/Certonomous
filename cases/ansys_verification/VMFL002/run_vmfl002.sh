#!/usr/bin/env bash
# VMFL002 graded-run driver -- Laminar Flow Through a Pipe with Uniform Heat Flux (manual p.17), axisymmetric wedge
#
# NO `set -u`.  It is CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: sourcing
# etc/bashrc dereferences WM_PROJECT_DIR (bashrc line 184) BEFORE assigning it.
# MEASURED on this box: with set -u -> rc 127, "WM_PROJECT_DIR: unbound variable".
# `set -e` also does NOT gate at a Bash tool's top level and `( set -e; ... )` fails
# silently, so EVERY check below gates EXPLICITLY with || { echo ABORT...; exit 1; }.
# A check that only prints is not a check.
#
# THE COST INSTRUMENT (CLAUDE.md rule 12).  RANKS is in BOTH formulae so a parallel
# copy inherits a correct cap automatically:
#     timeout_s    = remaining_core_min * 60 / RANKS
#     core_minutes = wall_s * RANKS / 60
# CAP_CORE_MIN is the RUNNING TOTAL across all three levels, frozen in
# PREREGISTRATION.md sec.12.  AN OVERRUN STOPS THE RUN; IT DOES NOT GET A NEW BUDGET.
#
# Usage:  run_vmfl002.sh <run_root>            graded run
#         run_vmfl002.sh <scratch_root> smoke  exercises THIS LAUNCHER end-to-end
#                                            (template Amendment 3 item 6) at L1 with
#                                            a tiny endTime; grades nothing.
RANKS=1
CAP_CORE_MIN=40
ENDTIME=5000
CASE_DIR="$(cd "$(dirname "$0")" && pwd)/case"
RUN_ROOT="${1:?usage: run_vmfl002.sh <run_root> [smoke]}"
MODE="${2:-graded}"
if [ "$MODE" = "smoke" ]; then ENDTIME=20; LEVELS="L1"; else LEVELS="L1 L2 L3"; fi
# --- LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2, template Amendment 2) ----------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 1; }
PREREG_REL="cases/ansys_verification/VMFL002/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL002/grade_vmfl002.py"
git -C "$REPO" cat-file -e "HEAD:$PREREG_REL" 2>/dev/null || { echo "ABORT: $PREREG_REL is not committed at HEAD -- the freeze is the evidence"; exit 1; }
git -C "$REPO" cat-file -e "HEAD:$GRADER_REL" 2>/dev/null || { echo "ABORT: $GRADER_REL is not committed at HEAD"; exit 1; }
PREREG_HEAD="$(git -C "$REPO" rev-parse "HEAD:$PREREG_REL")" || { echo "ABORT: cannot resolve HEAD:$PREREG_REL"; exit 1; }
GRADER_HEAD="$(git -C "$REPO" rev-parse "HEAD:$GRADER_REL")" || { echo "ABORT: cannot resolve HEAD:$GRADER_REL"; exit 1; }
PREREG_DISK="$(git -C "$REPO" hash-object "$REPO/$PREREG_REL")" || { echo "ABORT: cannot hash $PREREG_REL"; exit 1; }
GRADER_DISK="$(git -C "$REPO" hash-object "$REPO/$GRADER_REL")" || { echo "ABORT: cannot hash $GRADER_REL"; exit 1; }
[ "$PREREG_DISK" = "$PREREG_HEAD" ] || { echo "ABORT: $PREREG_REL on disk ($PREREG_DISK) differs from HEAD ($PREREG_HEAD)"; exit 1; }
[ "$GRADER_DISK" = "$GRADER_HEAD" ] || { echo "ABORT: $GRADER_REL on disk ($GRADER_DISK) differs from HEAD ($GRADER_HEAD)"; exit 1; }
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
{ echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "mode = $MODE"
  echo "prereg = $PREREG_REL";     echo "prereg_sha_head = $PREREG_HEAD"; echo "prereg_sha_disk = $PREREG_DISK"
  echo "comparator = $GRADER_REL"; echo "comparator_sha_head = $GRADER_HEAD"; echo "comparator_sha_disk = $GRADER_DISK"
  echo "launcher_sha_disk = $(git -C "$REPO" hash-object "$0")"
  echo "cap_core_min = $CAP_CORE_MIN"; echo "endTime = $ENDTIME"; echo "ranks = $RANKS"
} > "$RUN_ROOT/LAUNCH_RECORD.txt" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 1; }
echo "freeze check OK: prereg $PREREG_HEAD ; comparator $GRADER_HEAD"
# --- CONTENTION DISCLOSURE (contention is disclosed, never hidden) --------------
{ echo "sampled_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "loadavg = $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "nproc = $(nproc)"
  echo "mem_available_MB = $(free -m | awk 'NR==2{print $7}')"
  echo "-- other solver processes on the box at launch --"
  ps -eo comm= | grep -E 'Foam|foam|python3|docker' | sort | uniq -c | sort -rn | head -12
} > "$RUN_ROOT/CONTENTION.txt" 2>&1
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: no OpenFOAM"; exit 1; }
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH after sourcing"; exit 1; }
declare -A A=( [L1]=60 [L2]=120 [L3]=240 )
declare -A B=( [L1]=15 [L2]=30 [L3]=60 )
SPENT=0; TOTAL_WALL=0
for L in $LEVELS; do
  OUT="$RUN_ROOT/$L"
  # AGE GUARD (rule 4): refuse a case where 0/ or a time dir already exists.
  [ -e "$OUT/0" ] && { echo "ABORT age guard: $OUT/0 already exists"; exit 1; }
  [ -n "$(ls -d $OUT/[1-9]* 2>/dev/null)" ] && { echo "ABORT age guard: $OUT already holds a time directory"; exit 1; }
  # CAP ENFORCEMENT (rule 12): running-total drawdown, REFUSE at zero.
  REMAIN=$(python3 -c "print(max(0.0, $CAP_CORE_MIN - $SPENT))") || { echo "ABORT: cannot compute remaining budget"; exit 1; }
  TIMEOUT_S=$(python3 -c "print(int($REMAIN * 60 / $RANKS))") || { echo "ABORT: cannot compute timeout"; exit 1; }
  [ "$TIMEOUT_S" -gt 0 ] || { echo "ABORT: BUDGET EXHAUSTED before $L (spent $SPENT of $CAP_CORE_MIN core-min). An overrun STOPS the run; it does not get a new budget (rule 12)."; exit 1; }
  echo "--- $L timeout=${TIMEOUT_S}s (remaining $REMAIN of $CAP_CORE_MIN core-min)"
  mkdir -p "$OUT" || { echo "ABORT mkdir $OUT"; exit 1; }
  cp -r "$CASE_DIR"/{0,constant,system} "$OUT"/ || { echo "ABORT copy into $OUT"; exit 1; }
  sed -e "s/__NX__/${A[$L]}/g" -e "s/__NR__/${B[$L]}/g" "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo "ABORT sed blockMeshDict"; exit 1; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo "ABORT sed controlDict"; exit 1; }
  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT: blockMesh failed at $L -- a crash is a FINDING, not a retry"; exit 1; }
  ( cd "$OUT" && checkMesh > log.checkMesh 2>&1 )
  # MESH BIRTH CERTIFICATE (MESH_STANDARD sec.6) -- minted from checkMesh, not asserted.
  python3 - "$OUT" "$L" <<'PYBC' || { echo "ABORT: could not mint the mesh birth certificate"; exit 1; }
import json, re, sys, os, subprocess, datetime
out, lvl = sys.argv[1], sys.argv[2]
t = open(os.path.join(out, 'log.checkMesh'), errors='replace').read()
def g(pat, cast=float):
    m = re.search(pat, t)
    return cast(m.group(1)) if m else None
bc = {'level': lvl,
      'cells': g(r'cells:\s+(\d+)', int),
      'points': g(r'points:\s+(\d+)', int),
      'faces': g(r'faces:\s+(\d+)', int),
      'max_aspect_ratio': g(r'Max aspect ratio = ([0-9.eE+-]+)'),
      'max_skewness': g(r'Max skewness = ([0-9.eE+-]+)'),
      'max_non_orthogonality': g(r'non-orthogonality Max: ([0-9.eE+-]+)'),
      'mesh_ok': 'Mesh OK' in t,
      'failed_checks': g(r'Failed (\d+) mesh checks', int) or 0,
      'blockMeshDict_sha': subprocess.run(['git','hash-object',os.path.join(out,'system','blockMeshDict')],capture_output=True,text=True).stdout.strip(),
      'minted_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
json.dump(bc, open(os.path.join(out, 'birth_certificate.json'), 'w'), indent=2, sort_keys=True)
print('  birth certificate: cells=%s meshOK=%s maxSkew=%s' % (bc['cells'], bc['mesh_ok'], bc['max_skewness']))
PYBC
  # The age guard dates the run by 0/: touch every 0/ field IMMEDIATELY before the
  # solver, so "field at endTime newer than 0/" is a real test of THIS run.
  touch "$OUT"/0/* || { echo "ABORT: cannot touch $OUT/0"; exit 1; }
  T0=$(date +%s)
  ( cd "$OUT" && timeout "$TIMEOUT_S" simpleFoam > log.simpleFoam 2>&1 )
  RC=$?
  T1=$(date +%s); WALL=$((T1 - T0))
  CORE_MIN=$(python3 -c "print($WALL * $RANKS / 60.0)")
  SPENT=$(python3 -c "print($SPENT + $CORE_MIN)")
  TOTAL_WALL=$((TOTAL_WALL + WALL))
  # THE MEASURED rc GOES TO DISK.  Strict completion (rule 4) requires rc = 0, and a
  # rule you cannot evaluate is a rule you are not applying.
  printf 'rc = %d\nlevel = %s\nendTime = %s\nwall_s = %d\nranks = %d\ncore_min = %s\ntimeout_s = %d\nprereg_sha = %s\ncomparator_sha = %s\nfinished_utc = %s\n' \
    "$RC" "$L" "$ENDTIME" "$WALL" "$RANKS" "$CORE_MIN" "$TIMEOUT_S" "$PREREG_HEAD" "$GRADER_HEAD" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$OUT/RUN_RC.txt" || { echo "ABORT: could not write RUN_RC.txt for $L"; exit 1; }
  if [ "$RC" -eq 124 ]; then echo "ABORT: $L hit the BUDGET TIMEOUT (rc=124) after ${WALL}s of ${TIMEOUT_S}s. Rule 12 gives it NO new budget; the ladder is incomplete and the row is NOT A RESULT."; exit 1; fi
  [ "$RC" -eq 0 ] || { echo "ABORT: $L exited rc=$RC after ${WALL}s. A non-zero rc is a FINDING, not a retry."; exit 1; }
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (spent ${SPENT}/${CAP_CORE_MIN})"
done
printf 'total_wall_s = %d\nranks = %d\ntotal_core_min = %s\ncap_core_min = %s\nmode = %s\ncost_basis = owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); REPORTED-BY-OWNER, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md sec.5). Dollars are DERIVED.\n' \
  "$TOTAL_WALL" "$RANKS" "$SPENT" "$CAP_CORE_MIN" "$MODE" > "$RUN_ROOT/COST.txt" || { echo "ABORT: could not write COST.txt"; exit 1; }
echo "VMFL002 $MODE complete (${SPENT}/${CAP_CORE_MIN} core-min) -> grade with grade_vmfl002.py --run-root $RUN_ROOT"
