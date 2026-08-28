#!/usr/bin/env bash
# =============================================================================
# VMFL069 graded-run driver -- Two Phase Poiseuille Flow.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.205.
# Solver: interFoam (OpenFOAM v2606), laminar, two incompressible phases of EQUAL
# density with a flat NON-DEFORMING interface, cyclic streamwise pair driven by a
# constant -dp/dx = 0.5 Pa/m applied as an fvOptions body force.
#
# Frozen pre-registration: cases/ansys_verification/VMFL069/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL069/grade_vmfl069.py
# Run root               : verification/runs/ansys_verification/VMFL069/
#
# Modelled on cases/ansys_verification/VMFL063/run_vmfl063.sh, this family's
# reference driver, with FOUR deliberate departures, each named so none can read
# as a transcription slip:
#   (a) VMFL063's selftest gate was AMENDED after it was found UNSATISFIABLE --
#       it required BYTE-IDENTICAL --selftest output under both interpreters, and
#       the sandbox is a tempfile.mkdtemp() whose random path is quoted in the
#       output, so two runs of the SAME interpreter also differ. THIS LAUNCHER
#       CARRIES THE AMENDED FORM FROM BIRTH: PASS count, FAIL count and rc must
#       agree, and the AST-guard marker must appear under BOTH. A guard that
#       cannot pass is as broken as one that cannot fail (L-314 shape 4).
#   (b) There is no determinism twin. VMFL063 needed one because its physics limb
#       was capped at GATE REACHED; all three of VMFL069's limbs are PASS-capable
#       on their own class, so an identity limb would add a claim the case does
#       not need and a fourth solve the budget need not buy.
#   (c) setFields runs between blockMesh and the 0/ touch: the interface is
#       created by setFields, so `0/` must be touched AFTER it or the age-guard
#       datum would predate the field it dates.
#   (d) THE fvOptions MARKER CHECK. OpenFOAM v2606 reads constant/fvOptions if it
#       exists, system/fvOptions if not, and if NEITHER exists applies NOTHING
#       AND DOES NOT ERROR (fvOptions.C:50-93, read at source). The pressure
#       gradient is the ONLY forcing in this case, so a silently unread fvOptions
#       gives a quiet zero-velocity run that looks like physics -- L-339's
#       "a fix that appears applied and does nothing" in a new organ. The exact
#       log line is asserted here AND in the comparator.
#
# ---------------------------------------------------------------------------
# NO `set -u`.  CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: sourcing
# etc/bashrc dereferences WM_PROJECT_DIR before assigning it (measured rc 127,
# L-339). `set -e` is NOT relied on either: at agent-tool top level it is
# suppressed because the command is a non-final `&&` member (L-314 addendum 3),
# so EVERY check below gates EXPLICITLY with `|| { echo ABORT...; exit <n>; }`.
# A check that only prints is not a check.
# ---------------------------------------------------------------------------
# THE CAP IS A RUNNING TOTAL, NOT A PER-LEVEL CAP:
#   core_minutes = wall_s * RANKS / 60 ;  timeout_s = remaining_core_min * 60 / RANKS
# An overrun STOPS the run (rc 124); endTime is NEVER reduced to fit a cap
# (CLAUDE.md rule 12).
# =============================================================================

RANKS=1
CAP_CORE_MIN=45          # RUNNING TOTAL across all three solves (PREREGISTRATION sec.7)
ENDTIME=2000             # s; deltaT is 1 s, so this is also the step count

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmfl069.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"

# r = 2 grid triple: BOTH counts double at every level (frozen prereg sec.4).
declare -A NX=( [L1]=8  [L2]=16 [L3]=32  )
declare -A NY=( [L1]=32 [L2]=64 [L3]=128 )

echo "=== VMFL069 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT"

# --- smoke mode ----------------------------------------------------------------
# The smoke exercises the TOOLCHAIN and NEVER computes a gate quantity: it runs
# L1 for SMOKE_ENDTIME time steps, which is ~1/600 of the slowest mode's settling
# time, in a SCRATCH root only. It refuses any root that is not under a scratch
# area, so a smoke can never leave an answer where a graded run would look for one.
SMOKE_ENDTIME=3
if [ -n "$VMFL_SMOKE" ]; then
  case "$RUN_ROOT" in
    */scratchpad/*|*/scratchpad) : ;;
    *) echo "ABORT: VMFL_SMOKE refuses run_root '$RUN_ROOT' -- a smoke runs in scratch ONLY, never in the graded run root"; exit 2 ;;
  esac
  LEVELS_TO_RUN="L1"
  ENDTIME="$SMOKE_ENDTIME"
  echo "  SMOKE MODE: L1 only, endTime $SMOKE_ENDTIME IN THE SCRATCH COPY ONLY; grades nothing and computes no gate quantity"
fi

# --- 1. LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2) ---------------------------
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 2; }
PREREG_REL="cases/ansys_verification/VMFL069/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL069/grade_vmfl069.py"
FREEZE_COMMIT="$(git -C "$REPO" rev-parse HEAD)" || { echo "ABORT: cannot resolve HEAD"; exit 2; }
for REL in "$PREREG_REL" "$GRADER_REL"; do
  git -C "$REPO" cat-file -e "HEAD:$REL" 2>/dev/null || { echo "ABORT: $REL is NOT committed at HEAD -- the freeze IS the evidence (rule 2)"; exit 2; }
  HEADSHA="$(git -C "$REPO" rev-parse "HEAD:$REL")" || { echo "ABORT: cannot resolve HEAD blob of $REL"; exit 2; }
  DISKSHA="$(git -C "$REPO" hash-object "$REPO/$REL")" || { echo "ABORT: cannot hash $REL on disk"; exit 2; }
  [ "$DISKSHA" = "$HEADSHA" ] || { echo "ABORT freeze check: $REL on disk ($DISKSHA) != HEAD blob ($HEADSHA). The file that would run is NOT the file that was frozen."; exit 2; }
  echo "  freeze OK  $REL  $DISKSHA"
  case "$REL" in
    "$PREREG_REL") PREREG_BLOB="$DISKSHA" ;;
    "$GRADER_REL") GRADER_BLOB="$DISKSHA" ;;
  esac
done

# --- CASE INPUTS: every one hashed against its OWN HEAD blob -------------------
# "The mesh family, the viscosities and the forcing did not change" is a CHECK at
# launch, not a claim in a document.
NCASE=0
for F in 0/U 0/p_rgh 0/alpha.fluid1 \
         constant/transportProperties constant/turbulenceProperties constant/g \
         constant/fvOptions \
         system/blockMeshDict.template system/controlDict.template \
         system/setFieldsDict system/fvSchemes system/fvSolution; do
  A="$(git -C "$REPO" rev-parse "HEAD:cases/ansys_verification/VMFL069/case/$F" 2>/dev/null)" || { echo "ABORT: case/$F is not committed at HEAD"; exit 2; }
  B="$(git -C "$REPO" hash-object "$CASE_DIR/$F")" || { echo "ABORT: cannot hash case/$F"; exit 2; }
  [ "$A" = "$B" ] || { echo "ABORT: case/$F on disk ($B) != HEAD blob ($A) -- the case that would run is not the case that was frozen"; exit 2; }
  NCASE=$((NCASE+1))
done
[ "$NCASE" = "12" ] || { echo "ABORT: hashed $NCASE case inputs, expected 12"; exit 2; }
echo "  case inputs OK: 12 files, each byte-identical to its HEAD blob"

# --- 2. CONTROLS (rule 3) -- the comparator's own --selftest, BOTH interpreters -
# `python3 -O` deletes every assert, so a control that exists only under one flag
# is not a control (L-332). The two runs are NOT byte-identical and cannot be:
# the selftest sandbox is tempfile.mkdtemp(prefix="vmfl069_selftest_") and its
# random absolute path is quoted in the output, so two runs of the SAME
# interpreter also differ. Comparing PASS COUNT, FAIL COUNT and rc, and requiring
# the AST-guard marker under BOTH, is the SATISFIABLE form of that check.
ST="/tmp/vmfl069_selftest.$$"
rm -rf "$SCRIPT_DIR/__pycache__"
python3    "$SCRIPT_DIR/grade_vmfl069.py" --selftest > "$ST"   2>&1; RC_PLAIN=$?
[ "$RC_PLAIN" = "0" ] || { echo "ABORT: comparator --selftest is NOT green under python3 (rc $RC_PLAIN); see $ST"; exit 2; }
rm -rf "$SCRIPT_DIR/__pycache__"
python3 -O "$SCRIPT_DIR/grade_vmfl069.py" --selftest > "$ST.O" 2>&1; RC_O=$?
[ "$RC_O" = "0" ] || { echo "ABORT: comparator --selftest is NOT green under python3 -O (rc $RC_O); see $ST.O"; exit 2; }
NP_PLAIN="$(grep -c '^  \[PASS\]' "$ST")";   NP_O="$(grep -c '^  \[PASS\]' "$ST.O")"
NF_PLAIN="$(grep -c '^  \[FAIL\]' "$ST")";   NF_O="$(grep -c '^  \[FAIL\]' "$ST.O")"
AST_MARK='AST guard: ast.Assert count is 0 in this file'
[ "$NP_PLAIN" = "$NP_O" ] || { echo "ABORT: --selftest PASS COUNT differs -- python3 $NP_PLAIN vs python3 -O $NP_O -- a control that vanishes under -O is not a control (L-332)"; exit 2; }
[ "$NF_PLAIN" = "$NF_O" ] || { echo "ABORT: --selftest FAIL COUNT differs -- python3 $NF_PLAIN vs python3 -O $NF_O (L-332)"; exit 2; }
[ "$RC_PLAIN" = "$RC_O" ] || { echo "ABORT: --selftest EXIT RC differs -- python3 $RC_PLAIN vs python3 -O $RC_O (L-332)"; exit 2; }
grep -qF "$AST_MARK" "$ST"   || { echo "ABORT: --selftest did not print the AST GUARD MARKER under python3: $AST_MARK"; exit 2; }
grep -qF "$AST_MARK" "$ST.O" || { echo "ABORT: --selftest did not print the AST GUARD MARKER under python3 -O -- the guard must hold under BOTH interpreters (L-332): $AST_MARK"; exit 2; }
grep -q '^SELFTEST: all checks passed' "$ST" || { echo "ABORT: --selftest printed no all-checks-passed line"; exit 2; }
grep -q '^  \[FAIL\]' "$ST" && { echo "ABORT: --selftest printed a FAIL line"; exit 2; }
# Every control the pre-registration names must have been DRIVEN, not merely present.
for MARK in \
  'AST guard: ast.Assert count is 0 in this file' \
  'one_match REFUSES on two matches' \
  'time dirs sort NUMERICALLY: 0/950/2000 -> 2000' \
  'the LEXICOGRAPHIC maximum of 0/950/2000 really is 950 (the live hazard)' \
  'derived lower-layer mean matches the frozen REF_LOWER to 1e-12' \
  'global force balance: |tau_bottom| + |tau_top| == GRAD * H' \
  'planted zero P1a: the VELOCITY reader SEES a sized all-cell plant' \
  'planted zero P1b: the plant MOVES limb A by exactly the plant and pushes it OUT of the frozen band' \
  'planted zero REFUSES against a BLIND writer on the VELOCITY channel' \
  'planted zero P1b: the ALPHA plant makes the STATIONARITY CLAUSE refuse' \
  'planted zero REFUSES against a BLIND writer on the ALPHA channel' \
  'the blind-writer arm and the cardinality arm refuse for DIFFERENT reasons' \
  'completion REFUSES when the fvOptions markers are ABSENT' \
  'completion REFUSES when the interface moved' \
  'completion REFUSES when the field is not x-invariant' \
  'completion REFUSES when the solve has NOT PLATEAUED' \
  'completion REFUSES on an AGE-GUARD violation' \
  'rule 5 is ONE-WAY' \
  'the CEILING GUARD REFUSES when a limb would emit a verdict above its declared ceiling' \
  'the CEILING GUARD is QUIET again once the declared ceiling is PASS' \
  'end-to-end: a CONVERGING, in-band synthetic run gives ROW VERDICT PASS' \
  'end-to-end: a CONVERGING but OUT-OF-BAND synthetic run gives ROW VERDICT GATE FAIL' ; do
  grep -qF "$MARK" "$ST" || { echo "ABORT: --selftest did not DRIVE the control: $MARK"; exit 2; }
done
echo "  controls OK: --selftest $NP_PLAIN/$NP_PLAIN PASS; python3 and python3 -O agree on PASS $NP_PLAIN/$NP_O, FAIL $NF_PLAIN/$NF_O, rc $RC_PLAIN/$RC_O, and both carry the AST guard marker"
rm -f "$ST" "$ST.O"

# --- run root, contention record, launch record -------------------------------
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 2; }
{ echo "sampled_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "uptime = $(uptime)"
  echo "nproc = $(nproc)"
  echo "loadavg = $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "mem_available_MB = $(free -m | awk 'NR==2{print $7}')"
  echo "-- other solver processes on the box at launch --"
  ps -eo comm= | grep -E 'Foam|foam|python3|docker' | sort | uniq -c | sort -rn | head -12
  echo "note = contention at launch; core-minutes are wall_s*RANKS/60 and a busy box inflates wall_s (COMPUTE_BUDGET_CHARTER sec.6: waste is reported, never absorbed)"
} > "$RUN_ROOT/CONTENTION.txt" 2>&1

LR="$RUN_ROOT/LAUNCH_RECORD.txt"
{ echo "case = VMFL069"
  echo "manual_page = 205"
  echo "supersedes = nothing -- FIRST registration of this case; no prior VMFL069 register row exists"
  echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "freeze_commit_head = $FREEZE_COMMIT"
  echo "prereg = $PREREG_REL"
  echo "prereg_blob = $PREREG_BLOB"
  echo "comparator = $GRADER_REL"
  echo "comparator_blob = $GRADER_BLOB"
  echo "launcher_blob_on_disk = $(git -C "$REPO" hash-object "$0")"
  echo "levels = $LEVELS_TO_RUN"
  echo "ranks = $RANKS"
  echo "cap_core_min = $CAP_CORE_MIN  (RUNNING TOTAL across levels, PREREGISTRATION sec.7)"
  echo "endTime = $ENDTIME"
  echo "smoke_mode = ${VMFL_SMOKE:-no}"
} > "$LR" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 2; }

# --- OpenFOAM ------------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
for B in interFoam blockMesh checkMesh setFields postProcess; do
  command -v "$B" >/dev/null || { echo "ABORT: $B not on PATH after sourcing the v2606 bashrc"; exit 2; }
done
SOLVER_BIN="$(command -v interFoam)"
# NO SHIM IS INSTALLED BY THIS LAUNCHER. Sourcing the bashrc PREPENDS OpenFOAM's
# own bin to PATH, so a shim placed on PATH before this line would be silently
# OVERRIDDEN. The binary actually resolved is recorded so a reader can check it.
echo "solver_bin = $SOLVER_BIN" >> "$LR"
echo "  interFoam = $SOLVER_BIN"

TOTAL_CORE_MIN=0
OVERALL_RC=0

for L in $LEVELS_TO_RUN; do
  OUT="$RUN_ROOT/$L"
  [ -n "${NX[$L]}" ] || { echo "ABORT: no registered mesh counts for level $L"; exit 2; }

  # AGE GUARD (rule 4): refuse a level directory that already holds 0/ or a time
  # dir. NO `[0-9]*` glob anywhere -- such a glob also matches `0.orig` and reads
  # a template directory as an existing answer (L-339). Numeric dirs by REGEX.
  if [ -d "$OUT/0" ]; then echo "ABORT age guard: $OUT already holds 0/ -- a run is never launched into a tree that already holds an answer"; exit 2; fi
  EXISTING_T="$(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null | head -1)"
  [ -z "$EXISTING_T" ] || { echo "ABORT age guard: $OUT already holds a numeric time directory ($EXISTING_T)"; exit 2; }

  # --- CAP ENFORCEMENT: the RUNNING-TOTAL drawdown, in the executable path.
  REMAIN="$(python3 -c "print(max(0.0, $CAP_CORE_MIN - $TOTAL_CORE_MIN))")" || { echo "ABORT: cap arithmetic failed for $L"; exit 2; }
  TIMEOUT_S="$(python3 -c "print(int($REMAIN * 60 / $RANKS))")" || { echo "ABORT: timeout arithmetic failed for $L"; exit 2; }
  [ "$TIMEOUT_S" -gt 0 ] || { echo "ABORT: BUDGET EXHAUSTED before $L (spent $TOTAL_CORE_MIN of $CAP_CORE_MIN core-min). An overrun STOPS the run and does NOT get a new budget (rule 12)."; exit 2; }
  echo "--- $L  remaining ${REMAIN} of ${CAP_CORE_MIN} core-min  ranks ${RANKS}  timeout ${TIMEOUT_S}s"

  mkdir -p "$OUT" || { echo "ABORT: mkdir $OUT"; exit 2; }
  cp -r "$CASE_DIR"/0 "$CASE_DIR"/constant "$CASE_DIR"/system "$OUT"/ || { echo "ABORT: cannot copy the case templates into $OUT"; exit 2; }
  sed -e "s/__NX__/${NX[$L]}/g" -e "s/__NY__/${NY[$L]}/g" \
      "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo "ABORT: sed blockMeshDict for $L"; exit 2; }
  grep -q '__NX__\|__NY__' "$OUT/system/blockMeshDict" && { echo "ABORT: blockMeshDict substitution did not take at $L"; exit 2; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo "ABORT: sed controlDict for $L"; exit 2; }
  grep -qE "^endTime[[:space:]]+$ENDTIME;" "$OUT/system/controlDict" || { echo "ABORT: controlDict endTime is not the registered $ENDTIME at $L"; exit 2; }
  # NY must be EVEN or the interface would fall on a cell CENTRE, not a face.
  python3 -c "import sys; sys.exit(0 if ${NY[$L]} % 2 == 0 else 1)" || { echo "ABORT: NY=${NY[$L]} at $L is ODD -- the interface must lie on a cell FACE"; exit 2; }

  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT: blockMesh failed at $L -- a crash is a FINDING, not a retry"; exit 2; }
  ( cd "$OUT" && checkMesh > log.checkMesh 2>&1 )
  grep -q 'Mesh OK' "$OUT/log.checkMesh" || { echo "ABORT: checkMesh did not report 'Mesh OK' at $L"; exit 2; }
  ( cd "$OUT" && setFields > log.setFields 2>&1 ) || { echo "ABORT: setFields failed at $L"; exit 2; }
  grep -q 'set internal values of volScalarField: alpha.fluid1' "$OUT/log.setFields" || { echo "ABORT: setFields did not set alpha.fluid1 at $L -- the two layers would not exist"; exit 2; }

  # --- MESH BIRTH CERTIFICATE, from this level's own checkMesh (MESH_STANDARD sec.6)
  python3 - "$OUT" "$L" <<'PYBC' || { echo "ABORT: could not mint the mesh birth certificate"; exit 2; }
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
print('  birth certificate: cells=%s meshOK=%s maxSkew=%s maxAR=%s maxNonOrtho=%s' % (bc['cells'], bc['mesh_ok'], bc['max_skewness'], bc['max_aspect_ratio'], bc['max_non_orthogonality']))
PYBC

  # per-level pre-record so a killed launcher still leaves the cap it was under
  printf 'level=%s\nstate=STARTED\nranks=%d\ncap_core_min=%s\nremaining_core_min=%s\ntimeout_s=%d\nendTime=%s\nprereg_blob=%s\ncomparator_blob=%s\nstarted_utc=%s\nnote=RUNNING-TOTAL drawdown (PREREGISTRATION sec.7). L-342 INFRASTRUCTURE artifact: the comparator gates on the physics artefacts and reports rc NOT MEASURED if this file is absent.\n' \
    "$L" "$RANKS" "$CAP_CORE_MIN" "$REMAIN" "$TIMEOUT_S" "$ENDTIME" "$PREREG_BLOB" "$GRADER_BLOB" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RUN_ROOT/RUN_RC.$L" \
    || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  # 0/ is touched LAST, AFTER setFields has written the interface and immediately
  # before the solver: it is the age-guard datum that dates the run allowed to
  # produce the answer (CLAUDE.md rule 4).
  touch "$OUT"/0/* || { echo "ABORT: cannot touch $OUT/0"; exit 2; }

  T0="$(date +%s)"
  # DETACHED SOLVER (L-336): setsid makes the solver its own session leader so it
  # survives the launching lane's death. THE rc IS CAPTURED INSIDE the subshell,
  # immediately after `timeout` returns -- `setsid timeout cmd` returns 0 for
  # every outcome when its rc is taken OUTSIDE the wrapper, so it is taken inside.
  rm -f "$OUT/.solver_rc"
  (
    cd "$OUT" || exit 90
    setsid timeout "${TIMEOUT_S}"s interFoam > log.interFoam 2>&1
    SRC=$?
    echo "$SRC" > .solver_rc
    exit "$SRC"
  ) &
  SOLVER_PID=$!
  WSID=""
  for _try in $(seq 1 100); do WSID="$(awk '{print $6}' /proc/$SOLVER_PID/stat 2>/dev/null)"; [ -n "$WSID" ] && break; done
  wait "$SOLVER_PID"
  WAIT_RC=$?
  if [ -f "$OUT/.solver_rc" ]; then RC="$(cat "$OUT/.solver_rc")"; else RC="$WAIT_RC"; fi
  T1="$(date +%s)"
  WALL=$((T1-T0))
  CORE_MIN="$(python3 -c "print(round($WALL*$RANKS/60.0, 4))")"
  TOTAL_CORE_MIN="$(python3 -c "print(round($TOTAL_CORE_MIN + $CORE_MIN, 4))")"

  # --- departure (d): THE fvOptions MARKER CHECK, on the log the solver just wrote.
  # This is the only forcing in the case. Checked here as well as in the frozen
  # comparator so the failure is loud at launch instead of a quiet zero-velocity
  # field that looks like physics (L-339).
  FVOPT_OK="yes"
  for M in 'Creating finite-volume options from' 'constant/fvOptions' 'Source: streamwisePressureGradient' 'State: active'; do
    grep -qF "$M" "$OUT/log.interFoam" || FVOPT_OK="no"
  done
  [ "$FVOPT_OK" = "yes" ] || { echo "ABORT: fvOptions was NOT applied at $L -- the driving pressure gradient is absent and the run is unforced. OpenFOAM v2606 applies NOTHING and does NOT error when neither constant/fvOptions nor system/fvOptions exists (fvOptions.C:50-93)."; exit 2; }

  # Cx / Cy at the latest time: the comparator needs the cell-centre coordinates to
  # split the layers, to build the exact profile and to test x-invariance. Written
  # only on success.
  if [ "$RC" -eq 0 ]; then
    ( cd "$OUT" && postProcess -func writeCellCentres -latestTime > log.writeCellCentres 2>&1 ) || echo "  WARN: writeCellCentres failed at $L (the grader will REFUSE on missing Cx/Cy)"
  fi

  # latest numeric time directory, by REGEX and NUMERIC compare -- never a
  # `[0-9]*` glob and never a lexicographic sort. THIS CASE WRITES 500/1000/1500/
  # 2000, whose lexicographic maximum is `500`: the hazard is live here.
  ENDT_DIR=""; ENDT_OK="no"
  for D in $(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null); do
    B="$(basename "$D")"
    if python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>0 else 1)" "$B" 2>/dev/null; then
      if [ -z "$ENDT_DIR" ] || python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>float(sys.argv[2]) else 1)" "$B" "$(basename "$ENDT_DIR")"; then ENDT_DIR="$D"; fi
    fi
  done
  if [ -n "$ENDT_DIR" ] && [ -f "$ENDT_DIR/U" ] && [ "$ENDT_DIR/U" -nt "$OUT/0/U" ]; then ENDT_OK="yes"; fi
  LAST_TIME="$(grep -E '^Time = ' "$OUT/log.interFoam" 2>/dev/null | tail -1 | sed -E 's/^Time = //')"
  ENDED="$(grep -cE '^End$' "$OUT/log.interFoam" 2>/dev/null)"
  NEXEC="$(grep -c 'ExecutionTime' "$OUT/log.interFoam" 2>/dev/null)"

  printf 'rc = %s\nlevel = %s\nstate = FINISHED\nwait_rc = %d\nwall_s = %d\nranks = %d\ncore_min = %s\ntotal_core_min_so_far = %s\ntimeout_s = %d\ncap_core_min = %s\nendTime = %s\nlast_time_in_log = %s\nEnd_lines = %s\nExecutionTime_lines = %s\nfvOptions_applied = %s\nlatest_time_dir = %s\nfield_at_latest_newer_than_0_U = %s\nnx = %s\nny = %s\ndetach_wrapper_pid = %s\ndetach_wrapper_sid = %s\nprereg_blob = %s\ncomparator_blob = %s\nsolver_bin = %s\nutc = %s\nnote = rc is interFoam exit status under timeout, CAPTURED INSIDE the detached subshell; 124 means the RUNNING-TOTAL cap fired. endTime is NEVER reduced to fit a cap (rule 12). L-342: this file is INFRASTRUCTURE -- absent, the comparator reports rc NOT MEASURED and grades the physics artefacts.\n' \
    "$RC" "$L" "$WAIT_RC" "$WALL" "$RANKS" "$CORE_MIN" "$TOTAL_CORE_MIN" "$TIMEOUT_S" "$CAP_CORE_MIN" "$ENDTIME" "${LAST_TIME:-none}" "${ENDED:-0}" "${NEXEC:-0}" "$FVOPT_OK" "${ENDT_DIR:-none}" "$ENDT_OK" "${NX[$L]}" "${NY[$L]}" "$SOLVER_PID" "${WSID:-unknown}" "$PREREG_BLOB" "$GRADER_BLOB" "$SOLVER_BIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$RUN_ROOT/RUN_RC.$L" || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  # DISCLOSED, and it is the CHECK that is wrong, not the detachment: setsid is
  # applied to `timeout` INSIDE the waited-on subshell, so SID == PID can never
  # hold in this form. It can raise a false alarm, never certify a false pass, and
  # it gates nothing.
  if [ "$WSID" = "$SOLVER_PID" ]; then echo "  detach OK ($L): wrapper pid=$SOLVER_PID is a session leader (SID==PID)"; else echo "  DETACH NOTE ($L): wrapper pid=$SOLVER_PID SID=${WSID:-unknown} -- expected in this form; gates nothing"; fi
  { echo "level $L : rc=$RC wall_s=$WALL core_min=$CORE_MIN total=$TOTAL_CORE_MIN cap=$CAP_CORE_MIN timeout_s=$TIMEOUT_S last_time=${LAST_TIME:-none} End_lines=${ENDED:-0} ExecutionTime_lines=${NEXEC:-0} fvOptions=$FVOPT_OK latest_time_dir=${ENDT_DIR:-none} field_newer_than_0_U=$ENDT_OK"; } >> "$LR"

  # STOP AT THE FIRST NON-ZERO rc.
  if [ "$RC" -ne 0 ]; then
    OVERALL_RC="$RC"
    echo "STOP $L: rc=$RC after ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN} of ${CAP_CORE_MIN})."
    echo "  A non-zero rc is a FINDING, not a retry. rc=124 means the running-total cap stopped it;"
    echo "  an overrun does NOT get a new budget and endTime is NOT shrunk to fit (rule 12)."
    echo "later levels are NOT launched" >> "$LR"
    break
  fi
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN} of ${CAP_CORE_MIN}), latest time dir ${ENDT_DIR:-none}"
done

printf 'total_core_min = %s\ncap_core_min = %s\nranks = %d\noverall_rc = %s\nsmoke_mode = %s\ncost_basis = owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); REPORTED-BY-OWNER, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md sec.5). Dollars are DERIVED.\n' \
  "$TOTAL_CORE_MIN" "$CAP_CORE_MIN" "$RANKS" "$OVERALL_RC" "${VMFL_SMOKE:-no}" > "$RUN_ROOT/COST.txt" || { echo "ABORT: cannot write COST.txt"; exit 2; }
echo "total_core_min = $TOTAL_CORE_MIN" >> "$LR"
echo "finished_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LR"
echo "=== VMFL069 launcher done, overall rc=$OVERALL_RC, total ${TOTAL_CORE_MIN} core-min of ${CAP_CORE_MIN}"
echo "grade with: python3 $SCRIPT_DIR/grade_vmfl069.py --run-root $RUN_ROOT --out $RUN_ROOT/GRADING_VMFL069.json"
exit "$OVERALL_RC"
