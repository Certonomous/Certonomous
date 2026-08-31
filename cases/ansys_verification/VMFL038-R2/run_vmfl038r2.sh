#!/usr/bin/env bash
# =============================================================================
# VMFL038-R2 graded-run driver -- Falling Film Over an Inclined Plane.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.131-132.
# Solver: simpleFoam (OpenFOAM v2606), steady incompressible laminar, 2-D planar,
# pressure-driven film. Reference: Bird/Stewart/Lightfoot p.45 (EXACT solution of
# the same continuum model).
#
# Frozen pre-registration: cases/ansys_verification/VMFL038-R2/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL038-R2/grade_vmfl038r2.py
# Frozen mesh generator  : cases/ansys_verification/VMFL038-R2/make_mesh_vmfl038r2.py
# Run root               : verification/runs/ansys_verification/VMFL038-R2/
#
# WHAT CHANGED FROM R1's LAUNCHER, and each is a registered change:
#  1. THE FAMILY IS ISOTROPIC. Nx AND Ny both double per level -- (90,20)/(180,40)/
#     (360,80), cells x4, dx/dy = 4 CONSTANT. R1 pinned Nx at 180, cells went x2 and
#     the aspect ratio degraded 4 -> 8 -> 16. Substitution is delegated to
#     make_mesh_vmfl038r2.py, which applies a VALUE-POSITION discriminator instead of
#     R1's whole-file `grep -q __NY__` (PREREGISTRATION sec.8 requirement 7).
#  2. NO residualControl. Each level runs to a FIXED, PER-LEVEL endTime past the
#     momentum residual floor; the comparator decides convergence on the disjunctive
#     clause of sec.6.2. CLAUDE.md rule 4's canonical "last time == endTime" therefore
#     applies unadapted, and R1's declared adaptation is WITHDRAWN.
#  3. Two function-object HISTORY CHANNELS feed that clause, and BOTH carry
#     `writeFields` -- mandatory in v2606 though documented optional; an omission
#     MPI_ABORTs at construction (requirement 8), asserted below.
#
# NO `set -u` (incompatible with OpenFOAM v2606 bashrc); every check gates EXPLICITLY.
# THE CAP IS A RUNNING TOTAL across the three solves; an overrun STOPS the run
# (rc 124) and endTime is NEVER reduced to fit a cap (CLAUDE.md rule 12).
#
# THE OPERATIVE CAP GUARD IS THE PER-LEVEL `timeout ${TIMEOUT_S}s` BELOW. The queue
# runner's own cap enforcement is NOT relied on and is NOT claimed to be ENFORCE:
# docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md:3 records it ADVISORY/INERT/OFF.
# =============================================================================

RANKS=1
CAP_CORE_MIN=90         # RUNNING TOTAL across L1+L2+L3 (PREREGISTRATION sec.7.2)
HIST=100                # history-channel sampling interval, all levels (sec.7.1)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmfl038r2.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"

# THE ISOTROPIC FAMILY, r = 2 IN BOTH DIRECTIONS (frozen sec.4.1).
declare -A NX=( [L1]=90   [L2]=180  [L3]=360 )
declare -A NY=( [L1]=20   [L2]=40   [L3]=80 )
# Per-level endTime (frozen sec.7.1); each is 2.4x-5.4x the iteration at which the Ux
# residual was MEASURED to cross ITER_RES_FLOOR = 1e-10 in the sec.0.1 probe.
declare -A ET=( [L1]=8000 [L2]=16000 [L3]=32000 )

echo "=== VMFL038-R2 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT"

# --- smoke mode (CHARTER Amendment 1.4 Clause B): scratch ONLY -----------------
if [ -n "$VMFL_SMOKE" ]; then
  case "$RUN_ROOT" in
    */scratchpad/*|*/scratchpad) : ;;
    *) echo "ABORT: VMFL_SMOKE refuses run_root '$RUN_ROOT' -- a smoke runs in scratch ONLY, never in the graded run root"; exit 2 ;;
  esac
  LEVELS_TO_RUN="L1"
  ET[L1]=200
  echo "  SMOKE MODE: L1 only, endTime 200 IN THE SCRATCH COPY ONLY; grades nothing."
  echo "  It proves the toolchain STARTS and that all three function objects CONSTRUCT"
  echo "  (the writeFields trap aborts at construction). It proves NOTHING about the"
  echo "  numerics: VMFL069-R1 passed a 3-step smoke and diverged at step 65."
fi

# --- 1. LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2) ---------------------------
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 2; }
PREREG_REL="cases/ansys_verification/VMFL038-R2/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL038-R2/grade_vmfl038r2.py"
MESHER_REL="cases/ansys_verification/VMFL038-R2/make_mesh_vmfl038r2.py"
FREEZE_COMMIT="$(git -C "$REPO" rev-parse HEAD)" || { echo "ABORT: cannot resolve HEAD"; exit 2; }
for REL in "$PREREG_REL" "$GRADER_REL" "$MESHER_REL"; do
  git -C "$REPO" cat-file -e "HEAD:$REL" 2>/dev/null || { echo "ABORT: $REL is NOT committed at HEAD -- the freeze IS the evidence (rule 2)"; exit 2; }
  HEADSHA="$(git -C "$REPO" rev-parse "HEAD:$REL")" || { echo "ABORT: cannot resolve HEAD blob of $REL"; exit 2; }
  DISKSHA="$(git -C "$REPO" hash-object "$REPO/$REL")" || { echo "ABORT: cannot hash $REL on disk"; exit 2; }
  [ "$DISKSHA" = "$HEADSHA" ] || { echo "ABORT freeze check: $REL on disk ($DISKSHA) != HEAD blob ($HEADSHA). The file that would run is NOT the file that was frozen."; exit 2; }
  echo "  freeze OK  $REL  $DISKSHA"
  case "$REL" in
    "$PREREG_REL") PREREG_BLOB="$DISKSHA" ;;
    "$GRADER_REL") GRADER_BLOB="$DISKSHA" ;;
    "$MESHER_REL") MESHER_BLOB="$DISKSHA" ;;
  esac
done

# --- CASE INPUTS: every one hashed against its OWN HEAD blob -------------------
# ASSERTED AGAINST `git rev-parse HEAD:<path>`, NEVER against `git status` or
# `git diff HEAD` (ANSYS CHARTER sec.11.5): the shared index is stale and holds foreign
# staged deletions, so porcelain reports intact files as deleted.
for F in 0/U 0/p constant/transportProperties constant/momentumTransport \
         constant/turbulenceProperties system/blockMeshDict.template \
         system/controlDict.template system/fvSchemes system/fvSolution; do
  A="$(git -C "$REPO" rev-parse "HEAD:cases/ansys_verification/VMFL038-R2/case/$F" 2>/dev/null)" || { echo "ABORT: case/$F is not committed at HEAD"; exit 2; }
  B="$(git -C "$REPO" hash-object "$CASE_DIR/$F")" || { echo "ABORT: cannot hash case/$F"; exit 2; }
  [ "$A" = "$B" ] || { echo "ABORT: case/$F on disk ($B) != HEAD blob ($A) -- the case that would run is not the case that was frozen"; exit 2; }
done
echo "  case inputs OK: 9 files, each byte-identical to its HEAD blob"

# --- TOKEN-SUBSET CONTAINMENT (requirement 7, the half the value-position check
#     cannot see): every __TOKEN__ in a template must be one THIS launcher substitutes.
python3 - "$CASE_DIR" <<'PYTOK' || { echo "ABORT: template token-subset check failed"; exit 2; }
import re, sys, os
case = sys.argv[1]
allowed = {
    'system/blockMeshDict.template': {'__NX__', '__NY__'},
    'system/controlDict.template':   {'__ENDTIME__', '__HIST__'},
}
bad = 0
for rel, ok in sorted(allowed.items()):
    text = open(os.path.join(case, rel)).read()
    found = set(re.findall(r'__[A-Z0-9_]+__', text))
    extra = found - ok
    if extra:
        print('  TOKEN-SUBSET REFUSAL: %s carries %s outside the launcher sed set %s' % (rel, sorted(extra), sorted(ok)))
        bad = 1
    else:
        print('  token-subset OK: %s tokens %s subset of sed set %s' % (rel, sorted(found), sorted(ok)))
sys.exit(bad)
PYTOK

# --- MESH GENERATOR selftest, both interpreters -------------------------------
rm -rf "$SCRIPT_DIR/__pycache__"
python3    "$SCRIPT_DIR/make_mesh_vmfl038r2.py" --selftest > /tmp/vmfl038r2_mg.$$   2>&1; MG_RC=$?
rm -rf "$SCRIPT_DIR/__pycache__"
python3 -O "$SCRIPT_DIR/make_mesh_vmfl038r2.py" --selftest > /tmp/vmfl038r2_mg.$$.O 2>&1; MG_RC_O=$?
[ "$MG_RC" = "0" ] || { echo "ABORT: mesh generator --selftest not green under python3 (rc $MG_RC)"; exit 2; }
[ "$MG_RC_O" = "0" ] || { echo "ABORT: mesh generator --selftest not green under python3 -O (rc $MG_RC_O)"; exit 2; }
grep -qF 'MARKER_MESHGEN_VALUEPOS' /tmp/vmfl038r2_mg.$$   || { echo "ABORT: mesh generator did not DRIVE the value-position discriminator"; exit 2; }
grep -qF 'MARKER_MESHGEN_ASPECT'   /tmp/vmfl038r2_mg.$$   || { echo "ABORT: mesh generator did not DRIVE the aspect-ratio guard"; exit 2; }
grep -qF 'MARKER_MESHGEN_TOKENSET' /tmp/vmfl038r2_mg.$$   || { echo "ABORT: mesh generator did not DRIVE the token-subset guard"; exit 2; }
grep -qF 'MARKER_MESHGEN_AST assert_count=0' /tmp/vmfl038r2_mg.$$.O || { echo "ABORT: mesh generator AST marker absent under python3 -O"; exit 2; }
echo "  mesh generator OK: --selftest green under both interpreters, all three guards driven"
rm -f /tmp/vmfl038r2_mg.$$ /tmp/vmfl038r2_mg.$$.O

# --- CONTROLS: the comparator's own --selftest, BOTH interpreters --------------
ST="/tmp/vmfl038r2_selftest.$$"
rm -rf "$SCRIPT_DIR/__pycache__"
python3    "$SCRIPT_DIR/grade_vmfl038r2.py" --selftest > "$ST"   2>&1; RC_PLAIN=$?
[ "$RC_PLAIN" = "0" ] || { echo "ABORT: comparator --selftest is NOT green under python3 (rc $RC_PLAIN); see $ST"; exit 2; }
rm -rf "$SCRIPT_DIR/__pycache__"
python3 -O "$SCRIPT_DIR/grade_vmfl038r2.py" --selftest > "$ST.O" 2>&1; RC_O=$?
[ "$RC_O" = "0" ] || { echo "ABORT: comparator --selftest is NOT green under python3 -O (rc $RC_O); see $ST.O"; exit 2; }
NP_PLAIN="$(grep -c '^  \[PASS\]' "$ST")";   NP_O="$(grep -c '^  \[PASS\]' "$ST.O")"
NF_PLAIN="$(grep -c '^  \[FAIL\]' "$ST")";   NF_O="$(grep -c '^  \[FAIL\]' "$ST.O")"
AST_MARK='AST guard: ast.Assert count is 0 in this file'
[ "$NP_PLAIN" = "$NP_O" ] || { echo "ABORT: --selftest PASS COUNT differs -- python3 $NP_PLAIN vs python3 -O $NP_O (L-332)"; exit 2; }
[ "$NF_PLAIN" = "$NF_O" ] || { echo "ABORT: --selftest FAIL COUNT differs (L-332)"; exit 2; }
[ "$RC_PLAIN" = "$RC_O" ] || { echo "ABORT: --selftest EXIT RC differs (L-332)"; exit 2; }
grep -qF "$AST_MARK" "$ST"   || { echo "ABORT: --selftest did not print the AST GUARD MARKER under python3"; exit 2; }
grep -qF "$AST_MARK" "$ST.O" || { echo "ABORT: --selftest did not print the AST GUARD MARKER under python3 -O (L-332)"; exit 2; }
grep -q '^SELFTEST: all checks passed' "$ST" || { echo "ABORT: --selftest printed no all-checks-passed line"; exit 2; }
grep -q '^  \[FAIL\]' "$ST" && { echo "ABORT: --selftest printed a FAIL line"; exit 2; }
for MARK in \
  'AST guard: ast.Assert count is 0 in this file' \
  'one_match REFUSES on two matches' \
  'one_match REFUSES on zero matches' \
  'time dirs sort NUMERICALLY' \
  'PLANT-A fired at ALL THREE levels' \
  'PLANT-B fired at ALL THREE levels' \
  'PLANTS PRECEDE every refusing clause' \
  'BLIND writer' \
  'identically-zero channel' \
  'C1 DESCENDED accepted' \
  'C2 FLOORED-AND-FLAT accepted on a NULL RANGE' \
  'still-descending REFUSED' \
  'the two limbs cannot both fail on a converged level' \
  'LIMB A floor REFUSES' \
  'wall-shear REFUSES a non-developed' \
  'GATE FAIL: CONVERGING but the value is OUTSIDE' \
  'EXACT triple, even with the value' \
  'GCI > GCI_MAX' \
  'p < P_MIN' \
  'JSON grading record' ; do
  grep -qF "$MARK" "$ST" || { echo "ABORT: --selftest did not DRIVE the control: $MARK"; exit 2; }
done
NCHK="$(grep -c '^  \[PASS\]' "$ST")"
echo "  controls OK: --selftest $NCHK/$NCHK PASS; python3 and python3 -O agree on PASS $NP_PLAIN/$NP_O, FAIL $NF_PLAIN/$NF_O, rc $RC_PLAIN/$RC_O; AST marker in both; 20 named controls DRIVEN"
rm -f "$ST" "$ST.O"

# --- run root, contention record, launch record -------------------------------
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 2; }
{ echo "sampled_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "uptime = $(uptime)"; echo "nproc = $(nproc)"
  echo "loadavg = $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "mem_available_MB = $(free -m | awk 'NR==2{print $7}')"
  echo "-- other solver processes at launch --"
  ps -eo comm= | grep -E 'Foam|foam|python3|docker' | sort | uniq -c | sort -rn | head -12
  echo "note = a busy box inflates wall_s; core-min = wall_s*RANKS/60 (COMPUTE_BUDGET_CHARTER sec.6)."
  echo "note = the cost bracket in PREREGISTRATION sec.7.2 is 17.0 (uncontended) to 46.4 (contended) core-min; this file is the evidence for which end applies."
} > "$RUN_ROOT/CONTENTION.txt" 2>&1

LR="$RUN_ROOT/LAUNCH_RECORD.txt"
{ echo "case = VMFL038-R2"; echo "manual_page = 131-132"
  echo "supersedes = VMFL038-R1 as a PLAN. R1's register row #47 NOT A RESULT STANDS and R1's frozen files are untouched."
  echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "freeze_commit_head = $FREEZE_COMMIT"
  echo "prereg = $PREREG_REL"; echo "prereg_blob = $PREREG_BLOB"
  echo "comparator = $GRADER_REL"; echo "comparator_blob = $GRADER_BLOB"
  echo "mesh_generator = $MESHER_REL"; echo "mesh_generator_blob = $MESHER_BLOB"
  echo "launcher_blob_on_disk = $(git -C "$REPO" hash-object "$0")"
  echo "levels = $LEVELS_TO_RUN"; echo "ranks = $RANKS"
  echo "cap_core_min = $CAP_CORE_MIN  (RUNNING TOTAL across levels; the operative guard is the per-level timeout below, NOT the runner's cap, which is ADVISORY/INERT/OFF)"
  echo "family = ISOTROPIC r=2: (Nx,Ny) = (90,20)/(180,40)/(360,80); cells 1800/7200/28800 x4; dx/dy = 4 CONSTANT"
  echo "endTime = L1 ${ET[L1]}  L2 ${ET[L2]}  L3 ${ET[L3]}   hist_interval = $HIST"
  echo "smoke_mode = ${VMFL_SMOKE:-no}"
} > "$LR" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 2; }

# --- OpenFOAM ------------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source openfoam2606 bashrc"; exit 2; }
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH"; exit 2; }
command -v blockMesh  >/dev/null || { echo "ABORT: blockMesh not on PATH"; exit 2; }
SOLVER_BIN="$(command -v simpleFoam)"
echo "solver_bin = $SOLVER_BIN" >> "$LR"; echo "  simpleFoam = $SOLVER_BIN"

TOTAL_CORE_MIN=0
OVERALL_RC=0

for L in $LEVELS_TO_RUN; do
  OUT="$RUN_ROOT/$L"
  [ -n "${NX[$L]}" ] || { echo "ABORT: no registered Nx for level $L"; exit 2; }
  [ -n "${NY[$L]}" ] || { echo "ABORT: no registered Ny for level $L"; exit 2; }
  [ -n "${ET[$L]}" ] || { echo "ABORT: no registered endTime for level $L"; exit 2; }
  ENDTIME="${ET[$L]}"

  # endTime must be an exact multiple of the history interval, or the last sample and
  # the written field are at different iterations (sec.7.1).
  python3 -c "import sys; sys.exit(0 if int(sys.argv[1]) % int(sys.argv[2]) == 0 else 1)" "$ENDTIME" "$HIST" \
    || { echo "ABORT: endTime $ENDTIME is not a multiple of the history interval $HIST at $L"; exit 2; }

  # PER-LEVEL AGE GUARD (rule 4). It is scoped to THIS LEVEL'S OWN directory: the
  # datum is $OUT/0/U, touched below immediately before THIS level's solver, so a
  # stale field from another level can never satisfy it.
  if [ -d "$OUT/0" ]; then echo "ABORT age guard ($L): $OUT already holds 0/"; exit 2; fi
  EXISTING_T="$(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null | head -1)"
  [ -z "$EXISTING_T" ] || { echo "ABORT age guard ($L): $OUT already holds a numeric time directory ($EXISTING_T)"; exit 2; }

  # CAP: RUNNING-TOTAL drawdown in the executable path.
  REMAIN="$(python3 -c "print(max(0.0, $CAP_CORE_MIN - $TOTAL_CORE_MIN))")" || { echo "ABORT: cap arithmetic failed for $L"; exit 2; }
  TIMEOUT_S="$(python3 -c "print(int($REMAIN * 60 / $RANKS))")" || { echo "ABORT: timeout arithmetic failed for $L"; exit 2; }
  [ "$TIMEOUT_S" -gt 0 ] || { echo "ABORT: BUDGET EXHAUSTED before $L (spent $TOTAL_CORE_MIN of $CAP_CORE_MIN core-min). An overrun STOPS the run (rule 12)."; exit 2; }
  echo "--- $L  Nx=${NX[$L]} Ny=${NY[$L]} cells=$(( NX[$L] * NY[$L] ))  endTime=$ENDTIME  remaining ${REMAIN} of ${CAP_CORE_MIN} core-min  timeout ${TIMEOUT_S}s"

  mkdir -p "$OUT" || { echo "ABORT: mkdir $OUT"; exit 2; }
  cp -r "$CASE_DIR"/0 "$CASE_DIR"/constant "$CASE_DIR"/system "$OUT"/ || { echo "ABORT: cannot copy case templates into $OUT"; exit 2; }

  # MESH: delegated to the frozen generator, which applies the VALUE-POSITION
  # discriminator and refuses if dx/dy is not the frozen constant 4.
  python3 "$SCRIPT_DIR/make_mesh_vmfl038r2.py" --level "$L" \
      --template "$OUT/system/blockMeshDict.template" --out "$OUT/system/blockMeshDict" \
      || { echo "ABORT: mesh generator REFUSED at $L"; exit 2; }

  # controlDict: substitute, then check IN VALUE POSITION -- never a whole-file grep.
  sed -e "s/__ENDTIME__/$ENDTIME/g" -e "s/__HIST__/$HIST/g" \
      "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo "ABORT: sed controlDict for $L"; exit 2; }
  python3 - "$OUT/system/controlDict" "$ENDTIME" "$HIST" <<'PYCD' || { echo "ABORT: controlDict value-position / writeFields check failed at $L"; exit 2; }
import re, sys
path, endtime, hist = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
text = open(path).read()
rc = 0
# 1. VALUE POSITION: endTime, writeInterval(runTime), and every history interval.
m = re.search(r'^endTime\s+([^\s;]+);', text, re.M)
if not m or not re.fullmatch(r'[0-9]+', m.group(1)) or int(m.group(1)) != endtime:
    print('  VALUE-POSITION REFUSAL: endTime is %r, registered %d' % (m and m.group(1), endtime)); rc = 1
m = re.search(r'^writeInterval\s+([^\s;]+);', text, re.M)
if not m or not re.fullmatch(r'[0-9]+', m.group(1)) or int(m.group(1)) != endtime:
    print('  VALUE-POSITION REFUSAL: top-level writeInterval is %r, registered %d' % (m and m.group(1), endtime)); rc = 1
iv = re.findall(r'^\s+(?:execute|write)Interval\s+([^\s;]+);', text, re.M)
if not iv:
    print('  VALUE-POSITION REFUSAL: no function-object execute/writeInterval found'); rc = 1
for v in iv:
    if not re.fullmatch(r'[0-9]+', v) or int(v) != hist:
        print('  VALUE-POSITION REFUSAL: function-object interval %r, registered %d' % (v, hist)); rc = 1
# 2. requirement 8: writeFields on EVERY surfaceFieldValue / volFieldValue block.
blocks = re.findall(r'\n    (\w+)\s*\n    \{(.*?)\n    \}', text, re.S)
nfv = 0
for name, body in blocks:
    if re.search(r'type\s+(surfaceFieldValue|volFieldValue)\s*;', body):
        nfv += 1
        if not re.search(r'writeFields\s+(true|false)\s*;', body):
            print('  REQUIREMENT-8 REFUSAL: fieldValue block %r has no writeFields key -- v2606 MPI_ABORTs at construction' % name); rc = 1
        else:
            print('  writeFields OK in fieldValue block %r' % name)
if nfv != 2:
    print('  REQUIREMENT-8 REFUSAL: expected 2 fieldValue blocks, found %d' % nfv); rc = 1
if rc == 0:
    print('  controlDict OK: endTime=%d writeInterval=%d fo_intervals=%s writeFields on %d/%d fieldValue blocks'
          % (endtime, endtime, sorted(set(iv)), nfv, nfv))
sys.exit(rc)
PYCD

  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT: blockMesh failed at $L -- a crash is a FINDING, not a retry"; exit 2; }
  ( cd "$OUT" && checkMesh > log.checkMesh 2>&1 )

  # MESH BIRTH CERTIFICATE (MESH_STANDARD sec.6)
  python3 - "$OUT" "$L" "${NX[$L]}" "${NY[$L]}" <<'PYBC' || { echo "ABORT: could not mint the mesh birth certificate"; exit 2; }
import json, re, sys, os, subprocess, datetime
out, lvl, nx, ny = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
t = open(os.path.join(out, 'log.checkMesh'), errors='replace').read()
def g(pat, cast=float):
    m = re.search(pat, t); return cast(m.group(1)) if m else None
bc = {'level': lvl, 'nx': nx, 'ny': ny, 'cells_expected': nx * ny,
      'cell_aspect_ratio_dx_dy': (0.18 / nx) / (0.01 / ny),
      'cells': g(r'cells:\s+(\d+)', int), 'points': g(r'points:\s+(\d+)', int),
      'faces': g(r'faces:\s+(\d+)', int), 'max_aspect_ratio': g(r'Max aspect ratio = ([0-9.eE+-]+)'),
      'max_skewness': g(r'Max skewness = ([0-9.eE+-]+)'),
      'max_non_orthogonality': g(r'non-orthogonality Max: ([0-9.eE+-]+)'),
      'mesh_ok': 'Mesh OK' in t, 'failed_checks': g(r'Failed (\d+) mesh checks', int) or 0,
      'blockMeshDict_sha': subprocess.run(['git','hash-object',os.path.join(out,'system','blockMeshDict')],capture_output=True,text=True).stdout.strip(),
      'minted_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
if bc['cells'] != bc['cells_expected']:
    print('  BIRTH-CERTIFICATE REFUSAL: blockMesh built %s cells, the frozen family says %s' % (bc['cells'], bc['cells_expected']))
    sys.exit(1)
json.dump(bc, open(os.path.join(out, 'birth_certificate.json'), 'w'), indent=2, sort_keys=True)
print('  birth certificate: cells=%s (expected %s) dx/dy=%.6f meshOK=%s maxSkew=%s maxAR=%s maxNonOrtho=%s'
      % (bc['cells'], bc['cells_expected'], bc['cell_aspect_ratio_dx_dy'], bc['mesh_ok'], bc['max_skewness'], bc['max_aspect_ratio'], bc['max_non_orthogonality']))
PYBC

  printf 'level=%s\nstate=STARTED\nranks=%d\ncap_core_min=%s\nremaining_core_min=%s\ntimeout_s=%d\nendTime=%s\nnx=%s\nny=%s\nprereg_blob=%s\ncomparator_blob=%s\nmesh_generator_blob=%s\nstarted_utc=%s\nnote=RUNNING-TOTAL drawdown. L-342 INFRASTRUCTURE artifact.\n' \
    "$L" "$RANKS" "$CAP_CORE_MIN" "$REMAIN" "$TIMEOUT_S" "$ENDTIME" "${NX[$L]}" "${NY[$L]}" "$PREREG_BLOB" "$GRADER_BLOB" "$MESHER_BLOB" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RUN_ROOT/RUN_RC.$L" \
    || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  # 0/ touched LAST, immediately before THIS LEVEL's solver: the per-level age-guard
  # datum (rule 4). Each level has its own $OUT/0/U, so the guard is per-level by
  # construction and no field can pass it on another level's clock.
  touch "$OUT"/0/* || { echo "ABORT: cannot touch $OUT/0"; exit 2; }

  T0="$(date +%s)"
  rm -f "$OUT/.solver_rc"
  (
    cd "$OUT" || exit 90
    setsid timeout "${TIMEOUT_S}"s simpleFoam > log.simpleFoam 2>&1
    SRC=$?
    echo "$SRC" > .solver_rc
    exit "$SRC"
  ) &
  SOLVER_PID=$!
  WSID=""
  for _try in $(seq 1 100); do WSID="$(awk '{print $6}' /proc/$SOLVER_PID/stat 2>/dev/null)"; [ -n "$WSID" ] && break; done
  wait "$SOLVER_PID"; WAIT_RC=$?
  if [ -f "$OUT/.solver_rc" ]; then RC="$(cat "$OUT/.solver_rc")"; else RC="$WAIT_RC"; fi
  T1="$(date +%s)"; WALL=$((T1-T0))
  CORE_MIN="$(python3 -c "print(round($WALL*$RANKS/60.0, 4))")"
  TOTAL_CORE_MIN="$(python3 -c "print(round($TOTAL_CORE_MIN + $CORE_MIN, 4))")"

  if [ "$RC" -eq 0 ]; then
    ( cd "$OUT" && postProcess -func writeCellCentres -latestTime > log.writeCellCentres 2>&1 ) || echo "  WARN: writeCellCentres failed at $L (the grader will REFUSE on missing Cx/Cy)"
  fi

  ENDT_DIR=""
  for D in $(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null); do
    B="$(basename "$D")"
    if python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>0 else 1)" "$B" 2>/dev/null; then
      if [ -z "$ENDT_DIR" ] || python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>float(sys.argv[2]) else 1)" "$B" "$(basename "$ENDT_DIR")"; then ENDT_DIR="$D"; fi
    fi
  done
  LAST_TIME="$(grep -E '^Time = ' "$OUT/log.simpleFoam" 2>/dev/null | tail -1 | sed -E 's/^Time = //')"
  ENDED="$(grep -cE '^End$' "$OUT/log.simpleFoam" 2>/dev/null)"
  UX_FINAL="$(grep 'Solving for Ux' "$OUT/log.simpleFoam" 2>/dev/null | tail -1 | sed -E 's/.*Initial residual = ([^,]+),.*/\1/')"

  printf 'rc = %s\nlevel = %s\nstate = FINISHED\nwait_rc = %d\nwall_s = %d\nranks = %d\ncore_min = %s\ntotal_core_min_so_far = %s\ntimeout_s = %d\ncap_core_min = %s\nendTime = %s\nlast_time_in_log = %s\nEnd_lines = %s\nux_final_initial_residual = %s\nlatest_time_dir = %s\nnx = %s\nny = %s\ncells = %s\ndetach_wrapper_pid = %s\ndetach_wrapper_sid = %s\nprereg_blob = %s\ncomparator_blob = %s\nmesh_generator_blob = %s\nsolver_bin = %s\nutc = %s\nnote = rc captured INSIDE the detached subshell; 124 = the RUNNING-TOTAL cap fired. endTime is NEVER reduced to fit a cap (rule 12). L-342 INFRASTRUCTURE.\n' \
    "$RC" "$L" "$WAIT_RC" "$WALL" "$RANKS" "$CORE_MIN" "$TOTAL_CORE_MIN" "$TIMEOUT_S" "$CAP_CORE_MIN" "$ENDTIME" "${LAST_TIME:-none}" "${ENDED:-0}" "${UX_FINAL:-none}" "${ENDT_DIR:-none}" "${NX[$L]}" "${NY[$L]}" "$(( NX[$L] * NY[$L] ))" "$SOLVER_PID" "${WSID:-unknown}" "$PREREG_BLOB" "$GRADER_BLOB" "$MESHER_BLOB" "$SOLVER_BIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$RUN_ROOT/RUN_RC.$L" || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  { echo "level $L : rc=$RC wall_s=$WALL core_min=$CORE_MIN total=$TOTAL_CORE_MIN cap=$CAP_CORE_MIN timeout_s=$TIMEOUT_S endTime=$ENDTIME last_time=${LAST_TIME:-none} End_lines=${ENDED:-0} ux_final=${UX_FINAL:-none} latest_time_dir=${ENDT_DIR:-none}"; } >> "$LR"

  if [ "$RC" -ne 0 ]; then
    OVERALL_RC="$RC"
    echo "STOP $L: rc=$RC after ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN} of ${CAP_CORE_MIN})."
    echo "  A non-zero rc is a FINDING, not a retry. rc=124 means the running-total cap stopped it (rule 12)."
    echo "later levels are NOT launched" >> "$LR"
    break
  fi
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN} of ${CAP_CORE_MIN}), last time ${LAST_TIME:-none}, final Ux residual ${UX_FINAL:-none}"
done

printf 'total_core_min = %s\ncap_core_min = %s\nranks = %d\noverall_rc = %s\nsmoke_mode = %s\nestimate_bracket_core_min = 17.0 to 46.4 (PREREGISTRATION sec.7.2, EXTRAPOLATED)\ncost_basis = owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); REPORTED-BY-OWNER, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md sec.5). Dollars are DERIVED.\nnote = estimate-versus-actual calibration is OWED at completion (CLAUDE.md rule 12) and lands as a row in docs/COST_CALIBRATION.md.\n' \
  "$TOTAL_CORE_MIN" "$CAP_CORE_MIN" "$RANKS" "$OVERALL_RC" "${VMFL_SMOKE:-no}" > "$RUN_ROOT/COST.txt" || { echo "ABORT: cannot write COST.txt"; exit 2; }
echo "total_core_min = $TOTAL_CORE_MIN" >> "$LR"
echo "finished_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LR"
echo "=== VMFL038-R2 launcher done, overall rc=$OVERALL_RC, total ${TOTAL_CORE_MIN} core-min of ${CAP_CORE_MIN}"
echo "grade with: python3 $SCRIPT_DIR/grade_vmfl038r2.py --run-root $RUN_ROOT"
exit "$OVERALL_RC"
