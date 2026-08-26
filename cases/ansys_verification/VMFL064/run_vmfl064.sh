#!/usr/bin/env bash
# VMFL064 graded-run driver -- Low Re flow in a channel with sudden asymmetric expansion
# (backward-facing step, manual p.195). Laminar simpleFoam, Re_D = 200. Gate: LR/s on the
# bottomWall vs the experimental Armaly target 5.0 (ceiling GATE REACHED).
#
# NO `set -u` (v2606 bashrc dereferences WM_PROJECT_DIR at line 184 before assigning it;
# MEASURED rc 127). `set -e` does not gate at a Bash tool's top level, so EVERY check gates
# EXPLICITLY with || { echo ABORT...; exit 1; }.
#
# THE COST INSTRUMENT (rule 12), RANKS in BOTH formulae:
#   timeout_s = remaining_core_min * 60 / RANKS ; core_minutes = wall_s * RANKS / 60
# CAP_CORE_MIN is the RUNNING TOTAL across all three levels, frozen in PREREGISTRATION.md.
# AN OVERRUN STOPS THE RUN; IT DOES NOT GET A NEW BUDGET.
#
# Usage:  run_vmfl064.sh <run_root>            graded run  (all three levels)
#         run_vmfl064.sh <scratch_root> smoke  exercises THIS LAUNCHER end-to-end at L1 with
#                                            a tiny endTime; grades nothing.
RANKS=1
CAP_CORE_MIN=90
ENDTIME=20000
CASE_DIR="$(cd "$(dirname "$0")" && pwd)/case"
RUN_ROOT="${1:?usage: run_vmfl064.sh <run_root> [smoke]}"
MODE="${2:-graded}"
if [ "$MODE" = "smoke" ]; then ENDTIME=50; LEVELS="L1"; else LEVELS="L1 L2 L3"; fi
# --- LAUNCH-TIME FREEZE CHECK (rule 2, template Amendment 2) --------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 1; }
PREREG_REL="cases/ansys_verification/VMFL064/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL064/grade_vmfl064.py"
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
{ echo "sampled_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "loadavg = $(cut -d' ' -f1-3 /proc/loadavg)"; echo "nproc = $(nproc)"
  echo "mem_available_MB = $(free -m | awk 'NR==2{print $7}')"
  echo "-- other solver processes on the box at launch --"
  ps -eo comm= | grep -E 'Foam|foam|python3|docker' | sort | uniq -c | sort -rn | head -12
} > "$RUN_ROOT/CONTENTION.txt" 2>&1
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: no OpenFOAM"; exit 1; }
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH after sourcing"; exit 1; }
# r = 2 grid triple: every level doubles NXU, NXD and NY.
declare -A NXU=( [L1]=64 [L2]=128 [L3]=256 )
declare -A NXD=( [L1]=64 [L2]=128 [L3]=256 )
declare -A NY=(  [L1]=16 [L2]=32  [L3]=64  )
SPENT=0; TOTAL_WALL=0
for L in $LEVELS; do
  OUT="$RUN_ROOT/$L"
  # AGE GUARD (rule 4): refuse a case where 0/ or a time dir already exists. Time dirs are
  # matched by REGEX ^[0-9]+(\.[0-9]+)?$ -- NEVER a [0-9]* glob (that matches 0.orig).
  [ -e "$OUT/0" ] && { echo "ABORT age guard: $OUT/0 already exists"; exit 1; }
  EXISTING="$(python3 - "$OUT" <<'PYAGE'
import os, re, sys
d = sys.argv[1]
if os.path.isdir(d):
    for e in sorted(os.listdir(d)):
        if re.match(r'^[0-9]+(\.[0-9]+)?$', e) and os.path.isdir(os.path.join(d, e)):
            print(e)
PYAGE
)" || { echo "ABORT: age-guard scan failed for $OUT"; exit 1; }
  [ -n "$EXISTING" ] && { echo "ABORT age guard: $OUT already holds a time directory: $EXISTING"; exit 1; }
  REMAIN=$(python3 -c "print(max(0.0, $CAP_CORE_MIN - $SPENT))") || { echo "ABORT: cannot compute remaining budget"; exit 1; }
  TIMEOUT_S=$(python3 -c "print(int($REMAIN * 60 / $RANKS))") || { echo "ABORT: cannot compute timeout"; exit 1; }
  [ "$TIMEOUT_S" -gt 0 ] || { echo "ABORT: BUDGET EXHAUSTED before $L (spent $SPENT of $CAP_CORE_MIN core-min). An overrun STOPS the run (rule 12)."; exit 1; }
  echo "--- $L timeout=${TIMEOUT_S}s (remaining $REMAIN of $CAP_CORE_MIN core-min)"
  mkdir -p "$OUT" || { echo "ABORT mkdir $OUT"; exit 1; }
  cp -r "$CASE_DIR"/{0,constant,system} "$OUT"/ || { echo "ABORT copy into $OUT"; exit 1; }
  sed -e "s/__NXU__/${NXU[$L]}/g" -e "s/__NXD__/${NXD[$L]}/g" -e "s/__NY__/${NY[$L]}/g" \
      "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo "ABORT sed blockMeshDict"; exit 1; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo "ABORT sed controlDict"; exit 1; }
  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT: blockMesh failed at $L -- a crash is a FINDING, not a retry"; exit 1; }
  ( cd "$OUT" && checkMesh > log.checkMesh 2>&1 )
  python3 - "$OUT" "$L" <<'PYBC' || { echo "ABORT: could not mint the mesh birth certificate"; exit 1; }
import json, re, sys, os, subprocess, datetime
out, lvl = sys.argv[1], sys.argv[2]
t = open(os.path.join(out, 'log.checkMesh'), errors='replace').read()
def g(pat, cast=float):
    m = re.search(pat, t)
    return cast(m.group(1)) if m else None
bc = {'level': lvl, 'cells': g(r'cells:\s+(\d+)', int), 'points': g(r'points:\s+(\d+)', int),
      'faces': g(r'faces:\s+(\d+)', int), 'max_aspect_ratio': g(r'Max aspect ratio = ([0-9.eE+-]+)'),
      'max_skewness': g(r'Max skewness = ([0-9.eE+-]+)'),
      'max_non_orthogonality': g(r'non-orthogonality Max: ([0-9.eE+-]+)'),
      'mesh_ok': 'Mesh OK' in t, 'failed_checks': g(r'Failed (\d+) mesh checks', int) or 0,
      'blockMeshDict_sha': subprocess.run(['git','hash-object',os.path.join(out,'system','blockMeshDict')],capture_output=True,text=True).stdout.strip(),
      'minted_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
json.dump(bc, open(os.path.join(out, 'birth_certificate.json'), 'w'), indent=2, sort_keys=True)
print('  birth certificate: cells=%s meshOK=%s maxSkew=%s maxAR=%s' % (bc['cells'], bc['mesh_ok'], bc['max_skewness'], bc['max_aspect_ratio']))
PYBC
  # Age guard dates the run by 0/: touch every 0/ field IMMEDIATELY before the solver.
  touch "$OUT"/0/* || { echo "ABORT: cannot touch $OUT/0"; exit 1; }
  T0=$(date +%s)
  # DETACHED SOLVER (L-336): setsid makes the solver its own session leader so it survives the
  # launching lane's death. Backgrounded + waited so rc is captured on BOTH paths. Detachment
  # VERIFIED by the WRAPPER's SID == its own PID (field 6 of /proc/<pid>/stat), NEVER by ppid.
  ( cd "$OUT" && exec setsid timeout "${TIMEOUT_S}"s simpleFoam > log.simpleFoam 2>&1 ) &
  SOLVER_PID=$!
  WSID=""
  for _try in $(seq 1 100); do WSID=$(awk '{print $6}' /proc/$SOLVER_PID/stat 2>/dev/null); [ -n "$WSID" ] && break; done
  if [ "$WSID" = "$SOLVER_PID" ]; then echo "  detach OK ($L): wrapper pid=$SOLVER_PID is a session leader (SID==PID)"; else echo "  DETACH WARN ($L): wrapper pid=$SOLVER_PID SID=$WSID -- not a session leader"; fi
  wait "$SOLVER_PID"
  RC=$?
  # The grader needs Cx, Cy at the converged time (the reattachment-length abscissae). Write
  # them with postProcess writeCellCentres on the LATEST time, only if the solve succeeded.
  if [ "$RC" -eq 0 ]; then
    ( cd "$OUT" && postProcess -func writeCellCentres -latestTime > log.writeCellCentres 2>&1 ) || echo "  WARN: writeCellCentres failed at $L (grader will refuse on missing Cx/Cy)"
  fi
  T1=$(date +%s); WALL=$((T1 - T0))
  CORE_MIN=$(python3 -c "print($WALL * $RANKS / 60.0)")
  SPENT=$(python3 -c "print($SPENT + $CORE_MIN)")
  TOTAL_WALL=$((TOTAL_WALL + WALL))
  # THE MEASURED rc GOES TO DISK on BOTH the success and abort paths.
  printf 'rc = %d\nlevel = %s\nendTime = %s\nwall_s = %d\nranks = %d\ncore_min = %s\ntimeout_s = %d\nprereg_sha = %s\ncomparator_sha = %s\nfinished_utc = %s\n' \
    "$RC" "$L" "$ENDTIME" "$WALL" "$RANKS" "$CORE_MIN" "$TIMEOUT_S" "$PREREG_HEAD" "$GRADER_HEAD" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$OUT/RUN_RC.txt" || { echo "ABORT: could not write RUN_RC.txt for $L"; exit 1; }
  if [ "$RC" -eq 124 ]; then echo "ABORT: $L hit the BUDGET TIMEOUT (rc=124) after ${WALL}s of ${TIMEOUT_S}s. Rule 12 gives it NO new budget; the row is NOT A RESULT."; exit 1; fi
  [ "$RC" -eq 0 ] || { echo "ABORT: $L exited rc=$RC after ${WALL}s. A non-zero rc is a FINDING, not a retry."; exit 1; }
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (spent ${SPENT}/${CAP_CORE_MIN})"
done
printf 'total_wall_s = %d\nranks = %d\ntotal_core_min = %s\ncap_core_min = %s\nmode = %s\ncost_basis = owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); REPORTED-BY-OWNER, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md sec.5). Dollars are DERIVED.\n' \
  "$TOTAL_WALL" "$RANKS" "$SPENT" "$CAP_CORE_MIN" "$MODE" > "$RUN_ROOT/COST.txt" || { echo "ABORT: could not write COST.txt"; exit 1; }
echo "VMFL064 $MODE complete (${SPENT}/${CAP_CORE_MIN} core-min) -> grade with grade_vmfl064.py --selftest and then a graded run"
