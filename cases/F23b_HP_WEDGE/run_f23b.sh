#!/usr/bin/env bash
# F23b -- LAUNCHER for Hagen-Poiseuille flow on an axisymmetric WEDGE (simpleFoam,
# steady, Re_D = 100, streamwise cyclic, fixed body force; three-level ladder
# 64x2048 / 128x4096 / 256x8192, FOUR RANKS at every level).
#
# Registration: verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md, frozen at
#               57d31dde; AMENDMENT 1 (pre-compute) at 440aca3d.
#
# ONE INVOCATION CARRIES THE WHOLE RUNG UNDER THE ONE SHA, in section 11's fixed
# order:
#   (0) the instrument is proved green and proved able to refuse (-O -> rc 2);
#   (1) A0, the arm-acceptance reader's ACCEPT-side BIRTH CONTROL (AMENDMENT 1
#       A1.5) -- a reader shown only able to REJECT is L-396's constant in its
#       other costume, so this is GATING;
#   (2) A4-A7, the blockMesh-path wedge control, both directions at coarse AND
#       fine -- GATING under AMENDMENT 1 A1.4.  A refusal here stops the rung
#       BEFORE ANY LADDER SOLVER RUNS;
#   (3) ARM-P, and ARM-F only if section 5.5's branch rule fires, each wrapped in
#       `timeout` at its ARM_ALLOWANCE;
#   (4) the branch rule sets N_ITER and section 9.3's FROZEN ARITHMETIC recomputes
#       the ladder cap and every wall allowance;
#   (5) the three ladder levels, `mpirun -np 4 simpleFoam -parallel`, each solver
#       wrapped in `timeout` at its CAP_ALLOWANCE.
# GRADING IS A SEPARATE INVOCATION.
#
# FIRES NOTHING WITHOUT --prereg-commit.  `--preflight` runs every guard and every
# path resolution AND STOPS AT ZERO COMPUTE, including refusing to run blockMesh:
# a gate a mesher grades is FIRED the moment the mesher runs.
#
# `set -e` DOES NOT GATE IN THIS HARNESS.  Every assertion carries an explicit
# `|| { echo ABORT ...; exit 1; }`.  `set -u` is DROPPED AROUND THE OpenFOAM
# BASHRC SOURCE ONLY (L-339: the bashrc reads an unbound WM_PROJECT_DIR and the
# shell dies there SILENTLY).
#
# NO `rm -rf`, NO `rmtree`, ON A CASE DIRECTORY, ANYWHERE IN THIS FILE.  A
# pre-existing `0/`, numeric time directory or processor* directory in the RUN
# ROOT or in a LEVEL directory is REFUSED, never deleted (here and again inside
# build_f23b.py).
#
# THE RUN ROOT IS CREATED BY THIS SCRIPT, under verification/runs/.  NO RUN OUTPUT
# IS EVER WRITTEN BESIDE THE FROZEN INPUTS UNDER cases/.
#
# THE STATUS FILE IS WRITTEN BY AN EXIT TRAP, so the rc is captured INSIDE THE
# PROCESS THAT PRODUCED IT.  `setsid timeout cmd` exits 0 for EVERY outcome of its
# child, so an rc captured around a setsid line is not the run's rc.
#
# AND IT IS DELIBERATELY NOT NAMED `STATUS.<case_id>`.  scripts/queue_runner.py:496
# writes `<cwd>/STATUS.<case_id>` itself; F27 set its own STATUS to a
# BYTE-IDENTICAL path and the runner's one-line record DESTROYED F27's richer
# record carrying cap_core_min and spent_core_min.  This launcher writes
# `RUN_STATUS.F23b_HP_WEDGE.txt`, which the runner cannot occupy, and it writes it
# under the RUN ROOT once that exists.
#
# L-342: RC.txt, box probes, MESH_LINE.txt and the allowance files are written by
# THIS shell, in the same process that ran the solver, never by an attached poller.
set -u
set -o pipefail

ROOT="/home/ubuntu/Certonomous/cases/F23b_HP_WEDGE"
CASE_SRC="$ROOT/case"
EXACT="$ROOT/exact_f23b.py"
BUILD="$ROOT/build_f23b.py"
GRADER="$ROOT/grade_f23b.py"
PROJ_MOD="$ROOT/proj_f23b.py"
FIO="$ROOT/foam_io_f23b.py"
RECEIPT="$ROOT/GWEDGE_CONTROL_RECEIPT.txt"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F23b_HP_WEDGE_runs"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

# ---- THE THREE CAPS (section 9.0).  Every one is asserted against the grader
# ---- BEFORE ANY COMPUTE, and the total must be the sum of its two parts.
CAP_CORE_MIN=293.0                 # ladder;      must equal grade_f23b.py::CAP_CORE_MIN
PRELADDER_CAP_CORE_MIN=20.0        # pre-ladder;  must equal grade_f23b.py::PRELADDER_CAP_CORE_MIN
TOTAL_RUNG_CAP_CORE_MIN=313.0      # the sum;     asserted so NOTHING is spent outside a cap.
                                   # It is NOT a third budget anything may draw on.
N_ITER=400                         # section 5.5's ONE movable input; writeInterval = N_ITER/40
RANKS=4

# name  nr  nx  ranks
LEVELS=("coarse 64 2048 4" "medium 128 4096 4" "fine 256 8192 4")
DECOMP_METHOD="simple n (1 4 1), 4 subdomains, radial bands"
DECOMP_SEED="none (simple geometric decomposition from system/decomposeParDict; deterministic; no RNG)"

PREREG_COMMIT=""
PREFLIGHT=0
SELFTEST=0
SCRATCH="${TMPDIR:-/tmp}/f23b_preladder_$$"
for a in "$@"; do
  case "$a" in
    --preflight) PREFLIGHT=1 ;;
    --selftest)  SELFTEST=1 ;;
    --prereg-commit=*) PREREG_COMMIT="${a#*=}" ;;
    --scratch=*) SCRATCH="${a#*=}" ;;
    *) echo "ABORT: unknown argument $a"; exit 1 ;;
  esac
done
say() { printf '%s\n' "$*"; }

# ---- THE EXIT TRAP.  The rc is captured INSIDE this process. ----------------
PHASE="startup"
SPENT_LADDER=0
SPENT_PRELADDER=0
STATUS_FILE="$ROOT/RUN_STATUS.F23b_HP_WEDGE.txt"     # never STATUS.<case_id>
on_exit() {
  local rc=$?
  printf 'launcher_rc=%s phase=%s preflight=%s end=%s ladder_cap_core_min=%s preladder_cap_core_min=%s total_rung_cap_core_min=%s spent_ladder_core_min=%s spent_preladder_core_min=%s n_iter=%s prereg_commit=%s run_root=%s note=%s\n' \
    "$rc" "$PHASE" "$PREFLIGHT" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$CAP_CORE_MIN" "$PRELADDER_CAP_CORE_MIN" "$TOTAL_RUNG_CAP_CORE_MIN" \
    "$SPENT_LADDER" "$SPENT_PRELADDER" "$N_ITER" "${PREREG_COMMIT:-none}" "$RUN_ROOT" \
    "rc-of-this-launcher-captured-INSIDE-the-process-by-its-own-EXIT-trap-NOT-around-a-setsid-line" \
    > "$STATUS_FILE" 2>/dev/null
  exit "$rc"
}
trap on_exit EXIT

probe_box() {   # $1 = label, $2 = destination file
  local L1 MEMKB NP FREE
  L1=$(awk '{print $1}' /proc/loadavg)
  MEMKB=$(awk '/^MemAvailable/{print $2}' /proc/meminfo)
  NP=$(nproc)
  FREE=$(python3 -c "print(max(0.5, $NP - $L1))")
  printf 'label=%s\nload1=%s\nnproc=%s\nfree_cores=%s\nMemAvailable_kB=%s\nutc=%s\n' \
    "$1" "$L1" "$NP" "$FREE" "$MEMKB" "$(date -u +%FT%TZ)" > "$2"
  echo "$FREE"
}

# REFUSE, NEVER DELETE: a `0/`, numeric time or processor* directory as a direct child of $1.
refuse_if_answered() {
  local D="$1"
  if [ -e "$D/0" ]; then
    echo "ABORT: $D/0 already exists. Standing rule 4's age guard dates every"
    echo "       endTime field against this case's own 0/U, and a pre-existing 0/"
    echo "       destroys that. REFUSED, not deleted."
    exit 1
  fi
  while IFS= read -r d; do
    echo "ABORT: $D already holds $(basename "$d"). REFUSED, not deleted."; exit 1
  done < <(find "$D" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/([0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?|processor[0-9]+)' 2>/dev/null)
}

# --------------------------------------------------------------------------
# PATH RESOLUTION against the disk IN THIS INVOCATION
# --------------------------------------------------------------------------
PHASE="paths"
for p in "$CASE_SRC" "$CASE_SRC/0" "$CASE_SRC/constant" "$CASE_SRC/system"; do
  [ -d "$p" ] || { echo "ABORT: required directory does not exist: $p"; exit 1; }
done
for f in "$CASE_SRC/0/U.template" "$CASE_SRC/0/p" \
         "$CASE_SRC/constant/transportProperties" "$CASE_SRC/constant/turbulenceProperties" "$CASE_SRC/constant/fvOptions" \
         "$CASE_SRC/system/fvSchemes" "$CASE_SRC/system/fvSolution" "$CASE_SRC/system/decomposeParDict" \
         "$CASE_SRC/system/blockMeshDict.template" "$CASE_SRC/system/controlDict" \
         "$EXACT" "$BUILD" "$GRADER" "$PROJ_MOD" "$FIO" "$FOAM_BASHRC"; do
  [ -f "$f" ] || { echo "ABORT: required file does not exist: $f"; exit 1; }
done
say "PATHS RESOLVED against disk in this invocation: 16 files, 4 directories."

# --------------------------------------------------------------------------
# THE INSTRUMENT MUST BE GREEN, AND MUST BE SHOWN ABLE TO REFUSE, BEFORE ANY
# COMPUTE.  Each module is run twice: once plain (must pass) and once under -O
# (must exit 2).  A harness that runs under -O invites an assert to be added
# later and silently deleted (L-332).
# --------------------------------------------------------------------------
PHASE="instrument"
for M in "$EXACT" "$PROJ_MOD" "$BUILD" "$GRADER"; do
  python3 "$M" --selftest > /dev/null 2>&1 \
    || { echo "ABORT: $(basename "$M") --selftest did not pass; the instrument is not established and NOTHING may be launched behind it"; exit 1; }
  python3 -O "$M" --selftest > /dev/null 2>&1
  [ $? -eq 2 ] || { echo "ABORT: $(basename "$M") did not exit 2 under python3 -O; the -O refusal is not armed"; exit 1; }
done
say "INSTRUMENT GREEN: exact_f23b, proj_f23b, build_f23b and grade_f23b selftests pass, and every one exits 2 under -O."

# --------------------------------------------------------------------------
# ALL THREE CAPS, ASSERTED ACROSS LAUNCHER AND GRADER (section 9.0)
# --------------------------------------------------------------------------
PHASE="caps"
CAP_G=$(grep -E '^CAP_CORE_MIN[[:space:]]*=' "$GRADER" | head -1 | sed -E 's/^CAP_CORE_MIN[[:space:]]*=[[:space:]]*([0-9.]+).*/\1/')
PRE_G=$(grep -E '^PRELADDER_CAP_CORE_MIN[[:space:]]*=' "$GRADER" | head -1 | sed -E 's/^PRELADDER_CAP_CORE_MIN[[:space:]]*=[[:space:]]*([0-9.]+).*/\1/')
TOT_G=$(grep -E '^TOTAL_RUNG_CAP_CORE_MIN[[:space:]]*=' "$GRADER" | head -1 | sed -E 's/^TOTAL_RUNG_CAP_CORE_MIN[[:space:]]*=[[:space:]]*([0-9.]+).*/\1/')
python3 - "$CAP_G" "$PRE_G" "$TOT_G" "$CAP_CORE_MIN" "$PRELADDER_CAP_CORE_MIN" "$TOTAL_RUNG_CAP_CORE_MIN" <<'PY' \
  || { echo "ABORT: the three caps do not agree across launcher and grader, or the total is not the sum of its two parts. The launcher REFUSES TO START."; exit 1; }
import sys
cg, pg, tg, cl, pl, tl = [float(x) for x in sys.argv[1:7]]
ok = abs(cg - cl) < 1e-9 and abs(pg - pl) < 1e-9 and abs(tg - tl) < 1e-9 and abs(tl - (cl + pl)) < 1e-9
sys.exit(0 if ok else 1)
PY
CAPS_OUT=$(python3 "$PROJ_MOD" --caps --n-iter "$N_ITER") \
  || { echo "ABORT: proj_f23b.py could not evaluate section 9.3's frozen arithmetic"; exit 1; }
python3 - "$CAPS_OUT" "$CAP_CORE_MIN" "$TOTAL_RUNG_CAP_CORE_MIN" <<'PY' \
  || { echo "ABORT: the launcher's caps disagree with section 9.3's FROZEN ARITHMETIC evaluated at N_ITER"; exit 1; }
import sys
d = dict(l.split("=", 1) for l in sys.argv[1].strip().splitlines() if "=" in l)
ok = abs(float(d["CAP_CORE_MIN"]) - float(sys.argv[2])) < 1e-9 and \
     abs(float(d["TOTAL_RUNG_CAP_CORE_MIN"]) - float(sys.argv[3])) < 1e-9
sys.exit(0 if ok else 1)
PY
say "CAPS AGREE launcher == grader == section 9.3's frozen arithmetic:"
say "  ladder     $CAP_CORE_MIN core-min      (CAP_RATIO 1.4479 x ESTIMATE 202.366, floored to 0.1)"
say "  pre-ladder $PRELADDER_CAP_CORE_MIN core-min       (BESIDE the ladder cap, never inside it; SEPARATE running totals)"
say "  total      $TOTAL_RUNG_CAP_CORE_MIN core-min      (asserted so nothing is spent outside a cap; NOT a third budget)"

# --------------------------------------------------------------------------
# THE DICTIONARIES ON DISK MUST BE THE REGISTERED ONES
# --------------------------------------------------------------------------
PHASE="dictionaries"
python3 - "$CASE_SRC" "$N_ITER" <<'PY' \
  || { echo "ABORT: nu, G, ranks, endTime, writeInterval, 'consistent yes' or the relaxation factors on disk disagree with the registration"; exit 1; }
import re, sys, os
src, n_iter = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F23b_HP_WEDGE")
import exact_f23b as EX
def rd(*p): return open(os.path.join(src, *p)).read()
m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", rd("constant", "transportProperties"), re.M)
if not m or abs(float(m.group(1)) - EX.NU) > 1e-15: sys.exit(1)
cd = rd("system", "controlDict")
m = re.search(r"^\s*endTime\s+(\d+)\s*;", cd, re.M)
if not (m and int(m.group(1)) == n_iter == EX.N_ITER): sys.exit(1)
m = re.search(r"^\s*writeInterval\s+(\d+)\s*;", cd, re.M)
if not (m and int(m.group(1)) == EX.WRITE_EVERY and int(m.group(1)) * EX.CHECKPOINTS == n_iter): sys.exit(1)
m = re.search(r"U\s+\(\(\s*([0-9eE+\-.]+)\s+0\s+0\s*\)\s+0\s*\)\s*;", rd("constant", "fvOptions"))
if not m or abs(float(m.group(1)) - EX.G) > 1e-15: sys.exit(1)
fs = rd("system", "fvSolution")
if not re.search(r"consistent\s+yes\s*;", fs): sys.exit(1)
if not re.search(r"fields\s*\{\s*p\s+1\.0;\s*\}", fs): sys.exit(1)
if not re.search(r"equations\s*\{\s*U\s+1\.0;\s*\}", fs): sys.exit(1)
if re.search(r"^\s*residualControl", fs, re.M): sys.exit(1)
m = re.search(r"numberOfSubdomains\s+(\d+)\s*;", rd("system", "decomposeParDict"))
sys.exit(0 if m and int(m.group(1)) == EX.RANKS == 4 else 1)
PY
# NOTE, AND IT IS A DEFECT THIS FILE CAUGHT IN ITSELF: the two lines above and
# below once carried BACKTICKS around `consistent yes` inside DOUBLE QUOTES, so
# the shell COMMAND-SUBSTITUTED them and printed "... writeInterval 10,  (SIMPLEC)
# ..." with the registered setting MISSING, while `consistent: command not found`
# went to stderr and the checks all still passed.  That is L-403's shape and
# e779bdc7's -- a verdict-bearing phrase eaten by the shell in a line whose
# variable substitutions were working perfectly.  Single quotes here, everywhere,
# and the general rule: NEVER a backtick inside a double-quoted shell string.
say "DICTIONARIES AGREE: nu 0.01, G 0.32, ranks 4, endTime $N_ITER, writeInterval $((N_ITER/40)), 'consistent yes' (SIMPLEC), relaxation p 1.0 / U 1.0, no residualControl."

if [ "$SELFTEST" = "1" ]; then
  PHASE="selftest"
  say ""
  say "SELFTEST ONLY -- ZERO SOLVER COMPUTE. Every module's own controls were driven above."
  exit 0
fi

if [ "$PREFLIGHT" = "1" ]; then
  PHASE="preflight"
  say ""
  say "PREFLIGHT ONLY -- ZERO COMPUTE. blockMesh was NOT run. build_f23b.py was NOT called."
  say "decomposePar was NOT run. No solver started. No run root was created."
  say "decomposition method: $DECOMP_METHOD"
  say "decomposition seed:   $DECOMP_SEED"
  say "N_ITER $N_ITER, writeInterval $((N_ITER/40)), checkpoints 40, Class C window 12 checkpoints = $((12*N_ITER/40)) iterations"
  SP=0
  for L in "${LEVELS[@]}"; do
    set -- $L
    A=$(python3 "$PROJ_MOD" --allowance --cap "$CAP_CORE_MIN" --spent "$SP" --ranks "$4" | sed -n 's/^ALLOW_S=//p')
    P=$(python3 "$PROJ_MOD" --level "$1" --cap "$CAP_CORE_MIN" --spent "$SP" --ranks "$4" --n-iter "$N_ITER" | sed -n 's/^PROJ_CORE_MIN=//p')
    say "  level $1: $3 x $2 x 1 cells, $N_ITER iterations, ranks $4 -> projected $P core-min, CAP_ALLOWANCE $A wall s, target $RUN_ROOT/$1"
    SP=$(python3 -c "print($SP + $P)")
    [ -e "$RUN_ROOT/$1/0" ] && say "    NOTE: $RUN_ROOT/$1/0 EXISTS -- a real launch would REFUSE here."
  done
  say "  ladder projected total: $SP core-min of the $CAP_CORE_MIN cap"
  say "  pre-ladder items A0, A1, A4-A7, ARM-P (and ARM-F if the branch rule fires) draw on the SEPARATE $PRELADDER_CAP_CORE_MIN cap"
  if [ -e "$RUN_ROOT" ]; then
    say "  NOTE: run root $RUN_ROOT EXISTS."
  else
    say "  run root $RUN_ROOT is ABSENT (rule-2 absence condition holds)."
  fi
  if [ -f "$RECEIPT" ]; then
    say "  G-WEDGE birth receipt PRESENT: $RECEIPT"
  else
    say "  G-WEDGE birth receipt ABSENT -- a real launch drives A4-A7 and writes it before any ladder level (AMENDMENT 1 A1.4)."
  fi
  exit 0
fi

# --------------------------------------------------------------------------
# A REAL LAUNCH
# --------------------------------------------------------------------------
PHASE="prereg"
[ -n "$PREREG_COMMIT" ] \
  || { echo "ABORT: --prereg-commit=<sha> is required. Rule 2: the gate, threshold, cap and label are committed BEFORE the solver starts."; exit 1; }
git -C /home/ubuntu/Certonomous cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "ABORT: $PREREG_COMMIT is not a commit in this repository"; exit 1; }
python3 - "$GRADER" "$PREREG_COMMIT" <<'PY' \
  || { echo "ABORT: --prereg-commit is not this rung's freeze commit, or the registration on disk is not the committed blob. The launcher REFUSES TO START."; exit 1; }
import sys, os
sys.path.insert(0, os.path.dirname(sys.argv[1]))
sys.path.insert(0, "/home/ubuntu/Certonomous/scripts")
import grade_f23b as G
G.check_prereg_commit(sys.argv[2])
PY
say "FREEZE VERIFIED: --prereg-commit resolves to this rung's freeze commit and the registration on disk carries that commit's blob as a byte-exact PREFIX (rule 2, rule 6)."

# `-u` dropped around the source ONLY (L-339).
set +u
# shellcheck disable=SC1090
. "$FOAM_BASHRC" || { echo "ABORT: could not source $FOAM_BASHRC"; exit 1; }
set -u
for c in simpleFoam blockMesh checkMesh decomposePar mpirun timeout; do
  command -v "$c" > /dev/null || { echo "ABORT: $c not on PATH after sourcing"; exit 1; }
done

# ---- THE RUN-ROOT GUARD. REFUSE, NEVER DELETE. ------------------------------
PHASE="run_root"
[ -e "$RUN_ROOT" ] && refuse_if_answered "$RUN_ROOT"
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
STATUS_FILE="$RUN_ROOT/RUN_STATUS.F23b_HP_WEDGE.txt"
mkdir -p "$SCRATCH" || { echo "ABORT: cannot create the pre-ladder scratch $SCRATCH"; exit 1; }
say "RUN ROOT CREATED: $RUN_ROOT (run output NEVER goes beside the frozen inputs under cases/)"
say "STATUS: $STATUS_FILE -- written by this shell's EXIT TRAP, and deliberately NOT named"
say "        STATUS.F23b_HP_WEDGE, which is the path scripts/queue_runner.py:496 writes itself"
say "        (F27's richer record was DESTROYED by exactly that collision)."

# ---- helper: spend one pre-ladder item against the SEPARATE pre-ladder cap.
preladder_allowance() {   # $1 = ranks
  python3 "$PROJ_MOD" --allowance --cap "$PRELADDER_CAP_CORE_MIN" --spent "$SPENT_PRELADDER" --ranks "$1" \
    | sed -n 's/^ALLOW_S=//p'
}
charge_preladder() {      # $1 = core-min
  SPENT_PRELADDER=$(python3 -c "print($SPENT_PRELADDER + $1)")
  python3 -c "import sys; sys.exit(0 if $SPENT_PRELADDER <= $PRELADDER_CAP_CORE_MIN else 1)" || {
    echo "HALT: THE REGISTERED PRE-LADDER CAP OF $PRELADDER_CAP_CORE_MIN CORE-MINUTES HAS BEEN CROSSED"
    echo "      (cumulative pre-ladder spend $SPENT_PRELADDER core-min). An overrun STOPS the run and"
    echo "      does not get a new budget (rule 12). The LADDER cap is untouched and no level launched."
    exit 3
  }
}

# ==========================================================================
# (1) A0 -- the arm-acceptance reader's ACCEPT-side BIRTH CONTROL (A1.5)
#     16 x 64, 4 ranks, 4,000 iterations, UNDER F23's alpha_U = 0.7 DICTIONARY,
#     DELIBERATELY: the accept side must not depend on the very thing ARM-P is
#     testing.  Registered at 0.350 core-min, 300 s allowance.
# ==========================================================================
PHASE="A0"
A0="$SCRATCH/A0"
ALLOW=$(preladder_allowance 4)
say "A0 (arm-acceptance reader birth control): 16 x 64, alpha_U = 0.7, ARM_ALLOWANCE $ALLOW wall s"
mkdir -p "$A0"
echo "$ALLOW" > "$A0/ARM_ALLOWANCE.txt"
python3 "$BUILD" "$A0" --scratch 16 64 --n-iter 4000 --a0-dictionary > "$A0/log.build" 2>&1 \
  || { echo "ABORT: A0 build failed; see $A0/log.build"; exit 1; }
decomposePar -case "$A0" > "$A0/log.decomposePar" 2>&1 \
  || { echo "ABORT: A0 decomposePar failed"; exit 1; }
T0=$(date +%s)
timeout "$ALLOW" mpirun -np 4 simpleFoam -parallel -case "$A0" > "$A0/log.simpleFoam" 2>&1
RC=$?; echo "$RC" > "$A0/RC.txt"
T1=$(date +%s)
charge_preladder "$(python3 -c "print(($T1 - $T0) * 4 / 60.0)")"
[ "$RC" -eq 0 ] || { echo "ABORT: A0 exited $RC (rc recorded in $A0/RC.txt). A crash is a FINDING until triage says otherwise."; exit 1; }
python3 "$GRADER" --arm-born "$A0" \
  || { echo "ABORT: A0 did not birth the arm-acceptance reader. ARM-P and ARM-F REFUSE rather than accept-or-reject and THE RUNG IS BLOCKED (AMENDMENT 1 A1.5)."; exit 1; }
say "A0 GREEN: the arm-acceptance reader is BORN -- it has now been shown able to ACCEPT through the real production path, not only to reject."

# ==========================================================================
# (2) A4-A7 -- the blockMesh-path wedge control, GATING (AMENDMENT 1 A1.4)
#     A refusal here stops the rung BEFORE ANY LADDER SOLVER RUNS.
# ==========================================================================
PHASE="A4-A7"
say "A4-A7 (G-WEDGE blockMesh-path control, both directions at coarse AND fine):"
T0=$(date +%s)
python3 "$BUILD" --gwedge-control --workdir "$SCRATCH/gwedge" --prereg-commit="$PREREG_COMMIT" --receipt "$RECEIPT" \
  || { echo "ABORT: the G-WEDGE blockMesh-path control did not pass. The guard is NOT BORN and NOTHING is graded (AMENDMENT 1 A1.4)."; exit 1; }
T1=$(date +%s)
charge_preladder "$(python3 -c "print(($T1 - $T0) / 60.0)")"
say "G-WEDGE BORN. Pre-ladder spend so far: $SPENT_PRELADDER core-min of $PRELADDER_CAP_CORE_MIN."

# ==========================================================================
# (3) ARM-P, and ARM-F only if section 5.5's branch rule fires
# ==========================================================================
run_arm() {   # $1 = name (ARM-P|ARM-F), $2 = extra build args
  local NAME="$1" EXTRA="$2" DIR ALLOW RC T0 T1 N
  DIR="$SCRATCH/$NAME"
  ALLOW=$(preladder_allowance 4)
  say "$NAME: coarse 64 x 2048, 4 ranks, ARM_ALLOWANCE $ALLOW wall s $EXTRA"
  mkdir -p "$DIR"
  echo "$ALLOW" > "$DIR/ARM_ALLOWANCE.txt"
  # the arm builds the REGISTERED coarse geometry through the real chain
  python3 "$BUILD" "$DIR" --level coarse --n-iter 400 --prereg-commit="$PREREG_COMMIT" --receipt "$RECEIPT" \
      > "$DIR/log.build" 2>&1 || { echo "ABORT: $NAME build failed; see $DIR/log.build"; return 1; }
  if [ -n "$EXTRA" ]; then
    python3 - "$DIR/system/fvSolution" <<'PY' || { echo "ABORT: $NAME could not set its registered relaxation"; return 1; }
import re, sys
p = sys.argv[1]; t = open(p).read()
n = len(re.findall(r"equations \{ U 1\.0; \}|equations\s*\{\s*U\s+1\.0;\s*\}", t))
if n != 1: sys.exit(1)
t = re.sub(r"equations\s*\{\s*U\s+1\.0;\s*\}", "equations { U 0.9; }", t)
if t.count("{ U 0.9; }") != 1: sys.exit(1)
open(p, "w").write(t)
PY
  fi
  decomposePar -case "$DIR" > "$DIR/log.decomposePar" 2>&1 || { echo "ABORT: $NAME decomposePar failed"; return 1; }
  T0=$(date +%s)
  timeout "$ALLOW" mpirun -np 4 simpleFoam -parallel -case "$DIR" > "$DIR/log.simpleFoam" 2>&1
  RC=$?; echo "$RC" > "$DIR/RC.txt"
  T1=$(date +%s)
  charge_preladder "$(python3 -c "print(($T1 - $T0) * 4 / 60.0)")"
  # BOTH ARMS ARE REPORTED, INCLUDING A FAILING ONE (section 5.5 rule 5).
  python3 "$GRADER" --arm-read "$DIR" > "$DIR/ARM_READING.txt" 2>&1
  cat "$DIR/ARM_READING.txt"
  N=$(sed -n 's/^ACCEPTED_AT=//p' "$DIR/ARM_READING.txt")
  ARM_N="$N"
  [ "$RC" -eq 0 ] || return 1
  [ -n "$N" ] || return 1
  return 0
}

PHASE="ARM-P"
ARM_N=""
ARM_USED=""
if run_arm "ARM-P" ""; then
  ARM_USED="ARM-P"
else
  say "ARM-P did NOT accept. Section 5.5 rule 3: ARM-F fires. BOTH ARMS ARE REPORTED."
  PHASE="ARM-F"
  if run_arm "ARM-F" "alpha_U = 0.9"; then
    ARM_USED="ARM-F"
  else
    echo "HALT: BOTH ARM-P AND ARM-F FAILED THEIR REGISTERED ACCEPTANCE."
    echo "      Section 5.5 rule 4: the rung is BLOCKED and is escalated to the cfd"
    echo "      supervisor WITH BOTH ARMS' MEASURED RECORDS. The outcome of that"
    echo "      escalation is a NEW REGISTRATION UNDER A NEW SHA, never a third arm"
    echo "      under this one: a third setting chosen after watching two fail is a"
    echo "      parameter hunt, and a parameter hunt is not a registration."
    exit 4
  fi
fi

# ==========================================================================
# (4) THE BRANCH RULE -- it may move ONE COUNT and nothing else
# ==========================================================================
PHASE="branch"
BR=$(python3 "$PROJ_MOD" --branch "$ARM_N") \
  || { echo "ABORT: section 5.5's branch rule refused the arm reading $ARM_N"; exit 1; }
N_ITER=$(printf '%s\n' "$BR" | sed -n 's/^N_ITER=//p')
WRITE_INTERVAL=$(printf '%s\n' "$BR" | sed -n 's/^WRITE_INTERVAL=//p')
CAP_NOW=$(printf '%s\n' "$BR" | sed -n 's/^CAP_CORE_MIN=//p')
say "$ARM_USED accepted at iteration $ARM_N. $(printf '%s\n' "$BR" | sed -n 's/^BRANCH=//p')"
say "N_ITER = $N_ITER, writeInterval = $WRITE_INTERVAL, checkpoint count 40 (FROZEN), Class C window 12 checkpoints."
say "LADDER CAP recomputed by section 9.3's FROZEN ARITHMETIC: $CAP_NOW core-min (the formula is frozen; only its input count moved)."

# ==========================================================================
# (5) THE THREE LADDER LEVELS
# ==========================================================================
for L in "${LEVELS[@]}"; do
  set -- $L
  NAME=$1; NR=$2; NX=$3; NRANK=$4
  PHASE="level:$NAME"
  CD="$RUN_ROOT/$NAME"
  [ -e "$CD" ] && refuse_if_answered "$CD"
  mkdir -p "$CD" || { echo "ABORT: cannot create $CD"; exit 1; }

  probe_box "$NAME-pre" "$CD/box_before.txt" > /dev/null

  # ---- PRE-SPEND PROJECTION from section 9.1's MEASURED rate on THIS CASE'S
  # ---- OWN meshes.  The projector reads no clock, no /proc and no disk.
  PROJ_OUT=$(python3 "$PROJ_MOD" --level "$NAME" --spent "$SPENT_LADDER" --ranks "$NRANK" \
                    --n-iter "$N_ITER" --cap "$CAP_NOW") \
    || { echo "ABORT: proj_f23b.py refused at level $NAME; an unchecked projection is not a projection"; exit 1; }

# >>> C-11 CAP HALT BLOCK -- extracted VERBATIM by grade_f23b.py and driven with an
# injected projector output; do not reformat, do not add a dependency it does not
# already have.  Needs only: say(), NAME, CAP_NOW, PROJ_OUT.
  PROJ=$(printf '%s\n' "$PROJ_OUT" | sed -n 's/^PROJ_CORE_MIN=//p')
  CUM=$(printf '%s\n' "$PROJ_OUT" | sed -n 's/^CUMULATIVE=//p')
  HALT=$(printf '%s\n' "$PROJ_OUT" | sed -n 's/^HALT=//p')
  ALLOW=$(printf '%s\n' "$PROJ_OUT" | sed -n 's/^ALLOW_S=//p')
  BASIS=$(printf '%s\n' "$PROJ_OUT" | sed -n 's/^BASIS=//p')
  [ -n "$PROJ" ] && [ -n "$HALT" ] && [ -n "$ALLOW" ] \
    || { echo "ABORT: proj_f23b.py did not print PROJ_CORE_MIN / HALT / ALLOW_S"; exit 1; }
  say "level $NAME: PROJECTED $PROJ core-min (cumulative would be $CUM of $CAP_NOW), CAP_ALLOWANCE $ALLOW wall s"
  say "  projection basis: $BASIS"
  if [ "$HALT" != "0" ]; then
    echo "HALT BEFORE SPENDING: level $NAME is PROJECTED to cross the registered"
    echo "      ladder cap of $CAP_NOW core-min. THE CAP IS NOT RAISED. Levels not"
    echo "      launched stay PENDING (CLAUDE.md rule 12)."
    exit 3
  fi
# <<< C-11 CAP HALT BLOCK

  echo "$ALLOW" > "$CD/CAP_ALLOWANCE.txt"

  # ---- BUILD: templating, blockMesh, checkMesh, G-WEDGE, 0/C, 0/V, 0/p, 0/U LAST
  python3 "$BUILD" "$CD" --level "$NAME" --n-iter "$N_ITER" --prereg-commit="$PREREG_COMMIT" \
          --receipt "$RECEIPT" > "$CD/log.build" 2>&1 \
    || { echo "ABORT: build_f23b.py REFUSED at level $NAME; see $CD/log.build. G-WEDGE is a BUILD gate: a level whose mesh fails any limb is never solved, the level is NOT A RESULT and the ladder is NOT A RESULT. The builder refuses; it does not repair and it deletes nothing."; exit 1; }
  [ -f "$CD/0/U" ] || { echo "ABORT: build did not leave $CD/0/U (the age guard's datum)"; exit 1; }
  [ -f "$CD/MESH_LINE.txt" ] || { echo "ABORT: build did not leave $CD/MESH_LINE.txt"; exit 1; }
  say "level $NAME built: $(cat "$CD/MESH_LINE.txt")"

  # ---- DECOMPOSE (after 0/U: the serial 0/U remains the age guard's datum) ----
  say "level $NAME decomposition: $DECOMP_METHOD. Decomposition seed: $DECOMP_SEED"
  decomposePar -case "$CD" > "$CD/log.decomposePar" 2>&1 \
    || { echo "ABORT: decomposePar failed at level $NAME; see $CD/log.decomposePar"; exit 1; }
  NPROC=$(find "$CD" -maxdepth 1 -type d -name 'processor[0-9]*' | wc -l)
  [ "$NPROC" -eq "$NRANK" ] || { echo "ABORT: decomposePar left $NPROC processor directories, registered $NRANK"; exit 1; }

  # ---- THE SOLVER, WRAPPED IN `timeout` AT ITS CAP_ALLOWANCE ------------------
  say "level $NAME runs on $NRANK ranks: timeout $ALLOW mpirun -np $NRANK simpleFoam -parallel"
  timeout "$ALLOW" mpirun -np "$NRANK" simpleFoam -parallel -case "$CD" > "$CD/log.simpleFoam" 2>&1
  RC=$?
  echo "$RC" > "$CD/RC.txt"
  probe_box "$NAME-post" "$CD/box_after.txt" > /dev/null
  if [ "$RC" -eq 124 ]; then
    echo "HALT: level $NAME was KILLED by its CAP_ALLOWANCE of $ALLOW wall s."
    echo "      A kill leaves an INCOMPLETE level, which rule 4 refuses and the grader"
    echo "      reports as NOT A RESULT -- the correct outcome of an overrun, not a"
    echo "      defect (C-12). THE CAP IS NEVER RAISED."
    exit 3
  fi
  [ "$RC" -eq 0 ] || { echo "ABORT: simpleFoam exited $RC at level $NAME (rc recorded in $CD/RC.txt). A crash is a FINDING until triage says otherwise; it is not retried here."; exit 1; }

  CLOCK=$(sed -n 's/.*ClockTime = \([0-9][0-9]*\) s.*/\1/p' "$CD/log.simpleFoam" | tail -1)
  [ -n "$CLOCK" ] || { echo "ABORT: no ClockTime in $CD/log.simpleFoam; the cap cannot be checked and an unchecked cap is not a cap"; exit 1; }
  SPENT_LADDER=$(python3 -c "print($SPENT_LADDER + $CLOCK * $NRANK / 60.0)")
  say "level $NAME COMPLETE: ClockTime ${CLOCK}s x $NRANK ranks -> cumulative $SPENT_LADDER core-min of $CAP_NOW"
  say "  QUANTISATION: ClockTime has INTEGER-SECOND resolution: +/- $(python3 -c "print(0.5*$NRANK/60.0)") core-min per level."
  python3 -c "import sys; sys.exit(0 if $SPENT_LADDER <= $CAP_NOW else 1)" || {
    echo "HALT: THE REGISTERED LADDER CAP OF $CAP_NOW CORE-MINUTES HAS BEEN CROSSED"
    echo "      at level $NAME; cumulative spend $SPENT_LADDER core-min."
    echo "      An overrun STOPS the run. It does not get a new budget"
    echo "      (CLAUDE.md rule 12). Levels not launched stay PENDING."
    exit 3
  }
done

PHASE="done"
say ""
say "ALL THREE LEVELS COMPLETE."
say "  ladder spend     $SPENT_LADDER core-min of $CAP_NOW"
say "  pre-ladder spend $SPENT_PRELADDER core-min of $PRELADDER_CAP_CORE_MIN (SEPARATE running total)"
say "Grading is a SEPARATE invocation:"
say "  python3 $GRADER --prereg-commit=$PREREG_COMMIT"
say "Rule 12's calibration clause: the results record must carry the estimate-versus-actual"
say "comparison, gross and cleaned stated separately, waste named separately and never absorbed"
say "into the ratio, with a row in docs/COST_CALIBRATION.md. A completion report without it is"
say "INCOMPLETE."
