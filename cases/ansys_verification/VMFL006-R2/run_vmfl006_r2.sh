#!/usr/bin/env bash
# VMFL006-R2 graded-run driver -- Multicomponent Species Transport in Pipe Flow
# (Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 27-28).
# R2 succeeds R1 (register row #49, NOT A RESULT): endTime 3000 -> 8000 so L3 reaches
# the convergence floor, and the comparator's convergence clause is rebuilt. The case
# inputs under case/ are BYTE-IDENTICAL to R1 (endTime is substituted here, not in the
# template), so this launcher's ENDTIME is the only place the iteration count changed.
# scalarTransportFoam on an axisymmetric wedge, steady, with the fully developed
# Poiseuille profile IMPOSED (make_u_vmfl006.py). Gate: the mixing-cup average of
# the normalized mass fraction of species A at ten axial stations.
#
# NO `set -u` -- the v2606 bashrc dereferences WM_PROJECT_DIR at line 184 before
# assigning it (MEASURED rc 127; L-339). `set -e` does not gate at a Bash tool's
# top level and `( set -e; ... )` fails silently, so EVERY check gates EXPLICITLY
# with || { echo ABORT...; exit 1; }.
#
# THE COST INSTRUMENT (CLAUDE.md rule 12), RANKS in BOTH formulae:
#   timeout_s = remaining_core_min * 60 / RANKS ; core_minutes = wall_s * RANKS / 60
# CAP_CORE_MIN is the RUNNING TOTAL across all three levels, frozen in
# PREREGISTRATION.md sec.15. AN OVERRUN STOPS THE RUN; IT GETS NO NEW BUDGET.
#
# L-342 / Sanaa's universal rule of 2026-08-26 (commit d4d0c29d): A BOOKKEEPING
# FAILURE INVALIDATES THE BOOKKEEPING, NEVER THE PHYSICS ARTEFACTS. Every write
# that happens AFTER the solver has completed -- RUN_RC.txt, COST.txt -- is an
# INFRASTRUCTURE write: it is attempted, a failure is echoed as
# "WARNING [INFRA]" and the launcher's exit code stays the SOLVER's rc. Only
# PRE-COMPUTE gates (freeze check, age guard, budget, mesh, field completeness)
# abort, and they abort before any compute exists to be voided.
#
# Usage:  run_vmfl006.sh <run_root>            graded run (all three levels)
#         run_vmfl006.sh <scratch_root> smoke  exercises THIS LAUNCHER end-to-end
#                                              at L1 with a tiny endTime; grades
#                                              nothing and must run OUTSIDE
#                                              verification/runs/ (charter v1.4
#                                              clause B).
RANKS=1
CAP_CORE_MIN=18
ENDTIME=8000
RGRAD=0.25
CASE_DIR="$(cd "$(dirname "$0")" && pwd)/case"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_ROOT="${1:?usage: run_vmfl006.sh <run_root> [smoke]}"
MODE="${2:-graded}"
if [ "$MODE" = "smoke" ]; then ENDTIME=20; LEVELS="L1"; else LEVELS="L1 L2 L3"; fi

# --- LAUNCH-TIME FREEZE CHECK (rule 2, PREREG_TEMPLATE Amendment 2) -------------
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 1; }
PREREG_REL="cases/ansys_verification/VMFL006-R2/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL006-R2/grade_vmfl006_r2.py"
MAKEU_REL="cases/ansys_verification/VMFL006-R2/make_u_vmfl006.py"
if [ "$MODE" = "smoke" ]; then
  # The smoke proves the LAUNCHER, and it runs BEFORE the freeze exists. It still
  # exercises the freeze-check code path, but a missing HEAD blob is reported and
  # skipped rather than aborting -- otherwise the one artifact nothing was testing
  # (PREREG_TEMPLATE Amendment 3) could never be tested before it is frozen.
  FREEZE_MODE="report"
else
  FREEZE_MODE="gate"
fi
check_freeze() {   # $1 = repo-relative path
  local rel="$1" head disk
  git -C "$REPO" cat-file -e "HEAD:$rel" 2>/dev/null || {
      if [ "$FREEZE_MODE" = "gate" ]; then echo "ABORT: $rel is not committed at HEAD -- the freeze is the evidence"; exit 1; fi
      echo "  freeze check SKIPPED (smoke): $rel not yet at HEAD"; echo "NOT-AT-HEAD"; return 0; }
  head="$(git -C "$REPO" rev-parse "HEAD:$rel")" || { echo "ABORT: cannot resolve HEAD:$rel"; exit 1; }
  disk="$(git -C "$REPO" hash-object "$REPO/$rel")" || { echo "ABORT: cannot hash $rel"; exit 1; }
  if [ "$head" != "$disk" ]; then
      if [ "$FREEZE_MODE" = "gate" ]; then echo "ABORT: $rel on disk ($disk) differs from HEAD ($head)"; exit 1; fi
      echo "  freeze check MISMATCH (smoke, not gating): $rel disk $disk vs HEAD $head"
  fi
  echo "$head"
}
PREREG_HEAD="$(check_freeze "$PREREG_REL")" || exit 1
GRADER_HEAD="$(check_freeze "$GRADER_REL")" || exit 1
MAKEU_HEAD="$(check_freeze "$MAKEU_REL")"   || exit 1
echo "freeze check ($FREEZE_MODE): prereg $PREREG_HEAD ; comparator $GRADER_HEAD ; U-writer $MAKEU_HEAD"

mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
{ echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "mode = $MODE"
  echo "prereg = $PREREG_REL";     echo "prereg_sha_head = $PREREG_HEAD"
  echo "comparator = $GRADER_REL"; echo "comparator_sha_head = $GRADER_HEAD"
  echo "u_writer = $MAKEU_REL";    echo "u_writer_sha_head = $MAKEU_HEAD"
  echo "launcher_sha_disk = $(git -C "$REPO" hash-object "$0")"
  echo "cap_core_min = $CAP_CORE_MIN"; echo "endTime = $ENDTIME"; echo "ranks = $RANKS"
  echo "rgrad = $RGRAD"
  echo "launch_authority = bc0e687e (Sanaa's permission boarded verbatim)"
} > "$RUN_ROOT/LAUNCH_RECORD.txt" || echo "WARNING [INFRA]: cannot write LAUNCH_RECORD.txt -- bookkeeping only, the run proceeds (L-342)"
{ echo "sampled_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "loadavg = $(cut -d' ' -f1-3 /proc/loadavg)"; echo "nproc = $(nproc)"
  echo "mem_available_MB = $(free -m | awk 'NR==2{print $7}')"
  echo "-- other solver processes on the box at launch --"
  ps -eo comm= | grep -E 'Foam|foam|python3|docker' | sort | uniq -c | sort -rn | head -12
} > "$RUN_ROOT/CONTENTION.txt" 2>&1 || echo "WARNING [INFRA]: cannot write CONTENTION.txt (L-342)"

source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: no OpenFOAM"; exit 1; }
command -v scalarTransportFoam >/dev/null || { echo "ABORT: scalarTransportFoam not on PATH after sourcing"; exit 1; }
command -v blockMesh >/dev/null || { echo "ABORT: blockMesh not on PATH"; exit 1; }
command -v topoSet   >/dev/null || { echo "ABORT: topoSet not on PATH"; exit 1; }

# r = 2 grid triple: NX and NR both double at every level. NX stays a multiple of
# 10 so a mesh FACE sits exactly on each gate station at every level.
declare -A NX=( [L1]=200 [L2]=400 [L3]=800 )
declare -A NR=( [L1]=20  [L2]=40  [L3]=80  )
SPENT=0; TOTAL_WALL=0; LAST_RC=0

for L in $LEVELS; do
  OUT="$RUN_ROOT/$L"
  # AGE GUARD (rule 4): refuse a case where 0/ or a time dir already exists. Time
  # dirs are matched by REGEX ^[0-9]+(\.[0-9]+)?$ -- NEVER a [0-9]* glob, which
  # also matches 0.orig (L-339).
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
  sed -e "s/__NX__/${NX[$L]}/g" -e "s/__NR__/${NR[$L]}/g" -e "s/__RGRAD__/$RGRAD/g" \
      "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo "ABORT sed blockMeshDict"; exit 1; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo "ABORT sed controlDict"; exit 1; }

  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT: blockMesh failed at $L -- a crash is a FINDING, not a retry"; exit 1; }
  ( cd "$OUT" && checkMesh > log.checkMesh 2>&1 )
  python3 - "$OUT" "$L" "${NX[$L]}" "${NR[$L]}" <<'PYBC' || { echo "ABORT: could not mint the mesh birth certificate"; exit 1; }
import json, re, sys, os, subprocess, datetime
out, lvl, nx, nr = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
t = open(os.path.join(out, 'log.checkMesh'), errors='replace').read()
def g(pat, cast=float):
    m = re.search(pat, t)
    return cast(m.group(1)) if m else None
bc = {'level': lvl, 'cells': g(r'cells:\s+(\d+)', int), 'points': g(r'points:\s+(\d+)', int),
      'faces': g(r'faces:\s+(\d+)', int), 'max_aspect_ratio': g(r'Max aspect ratio = ([0-9.eE+-]+)'),
      'max_skewness': g(r'Max skewness = ([0-9.eE+-]+)'),
      'max_non_orthogonality': g(r'non-orthogonality Max: ([0-9.eE+-]+)'),
      'mesh_ok': 'Mesh OK' in t, 'failed_checks': g(r'Failed (\d+) mesh checks', int) or 0,
      'nx': nx, 'nr': nr, 'cells_expected': nx*nr,
      'blockMeshDict_sha': subprocess.run(['git','hash-object',os.path.join(out,'system','blockMeshDict')],capture_output=True,text=True).stdout.strip(),
      'minted_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
json.dump(bc, open(os.path.join(out, 'birth_certificate.json'), 'w'), indent=2, sort_keys=True)
if bc['cells'] != nx*nr:
    print('  MESH REFUSED: %s cells, expected %d' % (bc['cells'], nx*nr)); sys.exit(1)
print('  birth certificate: cells=%s meshOK=%s maxSkew=%s maxAR=%s maxNonOrtho=%s'
      % (bc['cells'], bc['mesh_ok'], bc['max_skewness'], bc['max_aspect_ratio'], bc['max_non_orthogonality']))
PYBC

  ( cd "$OUT" && postProcess -func writeCellCentres -time 0 > log.writeCellCentres 2>&1 ) || { echo "ABORT: writeCellCentres failed at $L"; exit 1; }
  python3 "$SCRIPT_DIR/make_u_vmfl006.py" "$OUT" "${NR[$L]}" "$RGRAD" || { echo "ABORT: make_u_vmfl006.py refused at $L"; exit 1; }
  ( cd "$OUT" && topoSet > log.topoSet 2>&1 ) || { echo "ABORT: topoSet failed at $L"; exit 1; }

  # CONSUMER-SIDE FIELD COMPLETENESS (PREREG_TEMPLATE Amendment 5/5a): enumerate
  # what scalarTransportFoam ACTUALLY needs -- the field named in fvSolution's
  # solver block, plus U (it builds phi from U) -- and refuse NAMING the missing
  # field. `phi` is solver-generated and is never staged in 0/. Every lookup
  # resolves X or X.gz (writeCompression).
  MISSING=""
  for f in T U; do
    [ -f "$OUT/0/$f" ] || [ -f "$OUT/0/$f.gz" ] || MISSING="$MISSING $f"
  done
  [ -z "$MISSING" ] || { echo "ABORT: 0/ is INCOMPLETE for scalarTransportFoam at $L -- missing:$MISSING"; exit 1; }
  echo "  field completeness OK ($L): 0/T and 0/U present for scalarTransportFoam"

  # The age guard dates the run by 0/: touch every 0/ field IMMEDIATELY before the solver.
  touch "$OUT"/0/* || { echo "ABORT: cannot touch $OUT/0"; exit 1; }
  T0=$(date +%s)
  # DETACHED SOLVER (L-336): setsid makes the wrapper its own session leader so the
  # solve survives the launching lane's death. Backgrounded + waited so rc is
  # captured on BOTH paths. Detachment is VERIFIED by the WRAPPER's SID == its own
  # PID (field 6 of /proc/<pid>/stat), NEVER by ppid.
  ( cd "$OUT" && exec setsid timeout "${TIMEOUT_S}"s scalarTransportFoam > log.scalarTransportFoam 2>&1 ) &
  SOLVER_PID=$!
  WSID=""
  for _try in $(seq 1 100); do WSID=$(awk '{print $6}' /proc/$SOLVER_PID/stat 2>/dev/null); [ -n "$WSID" ] && break; done
  if [ "$WSID" = "$SOLVER_PID" ]; then echo "  detach OK ($L): wrapper pid=$SOLVER_PID is a session leader (SID==PID)"; else echo "  DETACH WARN ($L): wrapper pid=$SOLVER_PID SID=$WSID -- not a session leader"; fi
  wait "$SOLVER_PID"
  RC=$?
  LAST_RC=$RC
  T1=$(date +%s); WALL=$((T1 - T0))
  CORE_MIN=$(python3 -c "print($WALL * $RANKS / 60.0)")
  SPENT=$(python3 -c "print($SPENT + $CORE_MIN)")
  TOTAL_WALL=$((TOTAL_WALL + WALL))

  # --- INFRASTRUCTURE WRITE (L-342): attempted, WARNED on failure, NEVER fatal now
  #     that the solver has already produced its artefacts.
  printf 'rc = %d\nlevel = %s\nendTime = %s\nwall_s = %d\nranks = %d\ncore_min = %s\ntimeout_s = %d\nnx = %s\nnr = %s\nrgrad = %s\nprereg_sha = %s\ncomparator_sha = %s\nfinished_utc = %s\n' \
    "$RC" "$L" "$ENDTIME" "$WALL" "$RANKS" "$CORE_MIN" "$TIMEOUT_S" "${NX[$L]}" "${NR[$L]}" "$RGRAD" "$PREREG_HEAD" "$GRADER_HEAD" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$OUT/RUN_RC.txt" || echo "WARNING [INFRA]: could not write RUN_RC.txt for $L -- the solver's rc was $RC and the physics artefacts stand (L-342)"

  if [ "$RC" -eq 124 ]; then echo "ABORT: $L hit the BUDGET TIMEOUT (rc=124) after ${WALL}s of ${TIMEOUT_S}s. Rule 12 gives it NO new budget; the row is NOT A RESULT."; exit 124; fi
  [ "$RC" -eq 0 ] || { echo "ABORT: $L exited rc=$RC after ${WALL}s. A non-zero rc is a FINDING, not a retry."; exit "$RC"; }
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (spent ${SPENT}/${CAP_CORE_MIN})"
done

printf 'total_wall_s = %d\nranks = %d\ntotal_core_min = %s\ncap_core_min = %s\nmode = %s\ncost_basis = owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); REPORTED-BY-OWNER, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md sec.5). Dollars are DERIVED.\n' \
  "$TOTAL_WALL" "$RANKS" "$SPENT" "$CAP_CORE_MIN" "$MODE" > "$RUN_ROOT/COST.txt" \
  || echo "WARNING [INFRA]: could not write COST.txt -- bookkeeping only; the verdict is unaffected (L-342)"
echo "VMFL006 $MODE complete (${SPENT}/${CAP_CORE_MIN} core-min); solver rc = $LAST_RC"
exit "$LAST_RC"
