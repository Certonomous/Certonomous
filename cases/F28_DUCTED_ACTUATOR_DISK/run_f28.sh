#!/usr/bin/env bash
# =============================================================================
# F28 -- DUCTED ACTUATOR DISK.  LAUNCHER.
#
# Registration: verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md
#               FROZEN at 76ce0ed5.  Sections 11.1 - 11.4.
#
# >>> THIS LAUNCHER HAS NOT BEEN FIRED FOR RECORD.  It refuses to launch any
# >>> gated solve without --prereg-commit AND a supervisor check-1 token,
# >>> because Stage 1 onward is gated behind the supervisor's personal read of
# >>> `analyse_f28.py` as a diff (SUPERVISION_CHARTER section 3 check 1).
#
# -----------------------------------------------------------------------------
# THE THREE THINGS THIS FILE EXISTS TO GET RIGHT
# -----------------------------------------------------------------------------
# 1. rc IS CAPTURED INSIDE THIS PROCESS, BY THIS PROCESS'S OWN EXIT TRAP.
#    `setsid timeout cmd` EXITS 0 FOR EVERY OUTCOME of its child, including a
#    solver that died.  An rc taken AROUND a setsid line reads 0 and certifies
#    a corpse as a completion.  So: the solver's rc is captured on the line
#    that runs the solver, inside this script; the STATUS file is written by
#    this script's EXIT trap; and THE SOLVER rc IS KEPT DISTINCT FROM THE
#    LAUNCHER rc, which is an infrastructure record and is NEVER offered as
#    evidence of a solve (section 11.3).
#
# 2. THE STATUS PATH IS ONE THE QUEUE RUNNER CANNOT OCCUPY (section 11.4).
#    `scripts/queue_runner.py` `launch()` writes `<cwd>/STATUS.<case_id>` and
#    `<cwd>/launcher.queue.out` itself, BOTH WITH UNCONDITIONAL SHELL `>`
#    TRUNCATION, and the `launcher.queue.out` redirection truncates at argv
#    start rather than after argv completes.  Two cases sharing a `cwd`
#    therefore destroy each other's records SILENTLY.  This launcher writes
#    `RUN_STATUS.F28.<rung_id>.txt`, which the runner never writes, and every
#    rung gets its OWN cwd of the registered form
#    `verification/runs/F28_runs/<rung_id>/`.  NO RUNG OF THIS CASE EVER USES
#    THE REPOSITORY ROOT, `cases/`, OR A SHARED PARENT AS ITS cwd.
#
# 3. THE COMPLETION RULE AND THE AGE GUARD (CLAUDE.md rule 4, section 11.1).
#    `0/U` is touched LAST at launch, so it DATES the run that was allowed to
#    produce the answer; a field older than it is a field from a previous run.
#    A guard refuses a case where `0` or any time directory already exists.
#
# -----------------------------------------------------------------------------
# SHELL DISCIPLINE
# -----------------------------------------------------------------------------
# `set -e` DOES NOT GATE HERE.  Every assertion carries its own explicit
# `|| { echo ABORT ...; exit 1; }`.  `set -u` is DROPPED AROUND THE OpenFOAM
# BASHRC SOURCE ONLY (L-339: the bashrc reads an unbound WM_PROJECT_DIR and the
# shell dies there SILENTLY).
#
# NO `rm -rf` ON A CASE DIRECTORY ANYWHERE IN THIS FILE.  Nothing this script
# deletes is a run record.
#
# Actuator-disk representation; no rotor.
# =============================================================================
set -o pipefail

CASE_ID="F28_DUCTED_ACTUATOR_DISK"
REPO="/home/ubuntu/Certonomous"
CASE_SRC="$REPO/cases/$CASE_ID/case"
RUN_ROOT="$REPO/verification/runs/F28_runs"
PREREG="$REPO/verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md"

# Registered physics (section 4).  NAMED CONSTANTS, never inlined below.
RHO=1.2
T_DISK=0.005
WEDGE_SCALE=72.0          # = 360/5, section 2.6
ITER_CAP=15000            # section 8.  RIGOR CLAUSE, not a budget cap.

RUNG=""; LEVEL=""; DELTA_P=""; U_INF=""; PREREG_COMMIT=""; CHECK1_TOKEN=""
RELAX_U="0.7"; PREFLIGHT=0; RANKS=4

usage() {
  cat <<'USAGE'
usage: run_f28.sh --rung <id> --level <1|2|3> --delta-p <Pa> --u-inf <m/s>
                  --prereg-commit <sha> --check1-token <string>
                  [--relax-u 0.7|0.5] [--ranks 4] [--preflight]

  --preflight       runs every guard and every path resolution AND STOPS AT
                    ZERO COMPUTE.  It will not run blockMesh either: a mesh
                    gate that a mesher grades is FIRED the moment the mesher
                    runs.
  --check1-token    the supervisor's own record that they have read
                    `analyse_f28.py` AS A DIFF (SUPERVISION_CHARTER 3 check 1).
                    NO AGENT MAY SUPPLY THIS ON A SUPERVISOR'S BEHALF -- a
                    delegate's test is evidence, not the supervisor's read
                    (CLAUDE.md rule 9).
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --rung) RUNG="$2"; shift 2;;
    --level) LEVEL="$2"; shift 2;;
    --delta-p) DELTA_P="$2"; shift 2;;
    --u-inf) U_INF="$2"; shift 2;;
    --prereg-commit) PREREG_COMMIT="$2"; shift 2;;
    --check1-token) CHECK1_TOKEN="$2"; shift 2;;
    --relax-u) RELAX_U="$2"; shift 2;;
    --ranks) RANKS="$2"; shift 2;;
    --preflight) PREFLIGHT=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "ABORT: unknown argument $1"; usage; exit 1;;
  esac
done

# -----------------------------------------------------------------------------
# THE EXIT TRAP.  rc IS CAPTURED INSIDE THIS PROCESS.
# -----------------------------------------------------------------------------
SOLVER_RC="not-run"
PHASE="argument-parse"
RUN_DIR=""
STATUS_FILE=""

on_exit() {
  launcher_rc=$?
  if [ -n "$STATUS_FILE" ]; then
    printf 'case=%s rung=%s level=%s delta_p_Pa=%s u_inf_m_s=%s ranks=%s relax_U=%s iter_cap=%s solver_rc=%s launcher_rc=%s phase=%s preflight=%s prereg_commit=%s run_dir=%s end=%s note=%s\n' \
      "$CASE_ID" "$RUNG" "$LEVEL" "$DELTA_P" "$U_INF" "$RANKS" "$RELAX_U" \
      "$ITER_CAP" "$SOLVER_RC" "$launcher_rc" "$PHASE" "$PREFLIGHT" \
      "$PREREG_COMMIT" "$RUN_DIR" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      "solver_rc-captured-INSIDE-this-process-on-the-line-that-ran-the-solver;-launcher_rc-captured-by-this-process-own-EXIT-trap;-NEITHER-taken-around-a-setsid-line;-launcher_rc-is-an-INFRASTRUCTURE-record-and-is-NEVER-evidence-of-a-solve" \
      > "$STATUS_FILE" 2>/dev/null
  fi
}
trap on_exit EXIT

abort() { echo "ABORT: $*" >&2; exit 1; }

# -----------------------------------------------------------------------------
# GUARDS -- every one of them before any compute
# -----------------------------------------------------------------------------
PHASE="guards"
[ -n "$RUNG" ]    || abort "--rung is required; it names this rung's OWN cwd (section 11.4)"
[ -n "$LEVEL" ]   || abort "--level is required"
[ -n "$DELTA_P" ] || abort "--delta-p is required"
[ -n "$U_INF" ]   || abort "--u-inf is required"
case "$LEVEL" in 1|2|3) ;; *) abort "--level must be 1, 2 or 3";; esac
case "$RUNG" in *[!A-Za-z0-9_]*) abort "--rung must be [A-Za-z0-9_]";; esac
case "$RELAX_U" in 0.7|0.5) ;; *) abort "--relax-u is 0.7 or 0.5 (section 8); whichever is used is RECORDED PER RUN and HELD FIXED ACROSS THE TRIPLE";; esac

[ -n "$PREREG_COMMIT" ] || abort "--prereg-commit is required.  The gate, the
  threshold, the cap and the label were committed BEFORE the solver starts, and
  the freeze is the document's entire evidentiary content (CLAUDE.md rule 2)."
[ -f "$PREREG" ] || abort "the frozen pre-registration is not on disk: $PREREG"

# The frozen document must BE the document that was frozen.  Hash the file on
# disk against the committed blob -- rule 2: "verify the frozen file IS the file
# that ran by hashing it against the committed blob."
have_blob=$(cd "$REPO" && git rev-parse --verify --quiet \
  "${PREREG_COMMIT}:verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md" 2>/dev/null)
[ -n "$have_blob" ] || abort "commit $PREREG_COMMIT does not carry the pre-registration"
disk_blob=$(cd "$REPO" && git hash-object "$PREREG")
[ "$have_blob" = "$disk_blob" ] || abort "THE PRE-REGISTRATION ON DISK IS NOT THE
  ONE COMMITTED AT $PREREG_COMMIT (blob $disk_blob vs $have_blob).  A frozen
  file is never edited; a departure lands as a dated amendment (rule 6)."

[ -n "$CHECK1_TOKEN" ] || abort "--check1-token is required.  The comparator
  \`analyse_f28.py\` is a MEASUREMENT SCRIPT and the supervisor reads it AS A
  DIFF, personally, before any number out of it is believed
  (SUPERVISION_CHARTER section 3 check 1; that check MAY NOT BE DELEGATED).
  Stage 1 onward is gated behind it and this launcher will not fire without it."

MESH_SRC="$RUN_ROOT/mesh_L$LEVEL"
[ -d "$MESH_SRC/constant/polyMesh" ] || abort "no built mesh at $MESH_SRC"
BIRTH="$REPO/cases/$CASE_ID/case/mesh/BIRTH_L$LEVEL.json"
[ -f "$BIRTH" ] || abort "no birth certificate for level $LEVEL: $BIRTH.
  MESH_STANDARD section 6: a mesh whose birth certificate is missing is
  QUARANTINED FROM NEW WORK."
python3 - "$BIRTH" <<'PY' || abort "level $LEVEL is not admissible; no solve is launched on it (section 5)"
import json, sys
c = json.load(open(sys.argv[1]))
g = c["registered_gates_section_5"]
bad = [k for k, v in g.items() if not v]
if bad:
    sys.stderr.write("ABORT: birth certificate gates failed: %s\n" % bad)
    sys.exit(1)
if c["stage0_verdict"] != "GATE REACHED":
    sys.stderr.write("ABORT: stage0_verdict is %r\n" % c["stage0_verdict"])
    sys.exit(1)
PY

RUN_DIR="$RUN_ROOT/$RUNG"
STATUS_FILE="$RUN_DIR/RUN_STATUS.F28.$RUNG.txt"

# Section 11.1: a guard refuses a case where `0` or any time directory already
# exists.  NO RUN IN THIS CASE IS EVER STARTED ON TOP OF AN EXISTING ONE.
if [ -d "$RUN_DIR" ]; then
  [ -d "$RUN_DIR/0" ] && abort "$RUN_DIR/0 already exists -- no run in this case
    is ever started on top of an existing time directory (section 11.1)"
  extra=$(find "$RUN_DIR" -maxdepth 1 -mindepth 1 -type d \
          -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' | head -1)
  [ -n "$extra" ] && abort "time directory $extra already exists in $RUN_DIR"
fi
# Section 11.4: this rung's cwd is ITS OWN and is never shared.
case "$RUN_DIR" in
  "$REPO"|"$REPO/"|"$REPO/cases"*|"$RUN_ROOT") abort "refusing a shared cwd: $RUN_DIR";;
esac
[ -e "$RUN_DIR/launcher.queue.out" ] && abort "$RUN_DIR already carries a
  launcher.queue.out -- another case is using this cwd and the queue runner
  truncates that file unconditionally (section 11.4)"

# Derived source strength.  delta_p / (rho * t) in m/s^2 -- an ACCELERATION,
# because simpleFoam is INCOMPRESSIBLE and its momentum equation is divided by
# rho.  The directive's N/m^3 is a FORCE density and is off by rho = 1.2 here.
SU_X=$(python3 -c "print(repr($DELTA_P/($RHO*$T_DISK)))") \
  || abort "cannot derive the source strength"
U_REF=$(python3 -c "print(repr(max(abs($U_INF), 1.0)))")
K_INIT=$(python3 -c "print(repr(1.5*(0.01*$U_REF)**2))")
OMEGA_INIT=$(python3 -c "
import math; k=1.5*(0.01*$U_REF)**2
print(repr(math.sqrt(k)/(0.09**0.25*0.1*0.25)))")

echo "F28 $RUNG: level=L$LEVEL delta_p=$DELTA_P Pa U_inf=$U_INF m/s"
echo "  Su_x = delta_p/(rho*t) = $SU_X m/s^2   (volumeMode specific)"
echo "  WEDGE_SCALE = $WEDGE_SCALE   iteration cap = $ITER_CAP (RIGOR, not budget)"
echo "  run dir = $RUN_DIR"
echo "  STATUS  = $STATUS_FILE  (NOT STATUS.$CASE_ID, which queue_runner writes)"

if [ "$PREFLIGHT" = "1" ]; then
  PHASE="preflight-complete-zero-compute"
  mkdir -p "$RUN_DIR" || abort "cannot create $RUN_DIR"
  echo "PREFLIGHT COMPLETE AT ZERO COMPUTE.  Nothing was meshed and nothing solved."
  exit 0
fi

# -----------------------------------------------------------------------------
# ASSEMBLE THE CASE
# -----------------------------------------------------------------------------
PHASE="assemble"
mkdir -p "$RUN_DIR/system" "$RUN_DIR/constant" "$RUN_DIR/0" \
  || abort "cannot create $RUN_DIR"
cp -a "$MESH_SRC/constant/polyMesh" "$RUN_DIR/constant/" || abort "mesh copy failed"
cp "$CASE_SRC/system/fvSchemes" "$CASE_SRC/system/fvSolution" \
   "$CASE_SRC/system/decomposeParDict" "$RUN_DIR/system/" || abort "system copy failed"
cp "$CASE_SRC/constant/transportProperties" \
   "$CASE_SRC/constant/turbulenceProperties" "$RUN_DIR/constant/" \
   || abort "constant copy failed"

sed -e "s|__END_TIME__|$ITER_CAP|g" -e "s|__WRITE_INTERVAL__|$ITER_CAP|g" \
    "$CASE_SRC/system/controlDict.template" > "$RUN_DIR/system/controlDict" \
    || abort "controlDict substitution failed"
sed -e "s|__SU_X__|$SU_X|g" -e "s|__DELTA_P__|$DELTA_P|g" \
    "$CASE_SRC/constant/fvOptions.template" > "$RUN_DIR/constant/fvOptions" \
    || abort "fvOptions substitution failed"
sed -e "s|__U_INF__|$U_INF|g" "$CASE_SRC/0/U.template" > "$RUN_DIR/0/U.pending"
sed -e "s|__K_INIT__|$K_INIT|g" "$CASE_SRC/0/k.template" > "$RUN_DIR/0/k"
sed -e "s|__OMEGA_INIT__|$OMEGA_INIT|g" "$CASE_SRC/0/omega.template" > "$RUN_DIR/0/omega"
cp "$CASE_SRC/0/p" "$CASE_SRC/0/nut" "$RUN_DIR/0/"
sed -i -e "s|p 0.3|p 0.3|" -e "s|U 0.7|U $RELAX_U|" "$RUN_DIR/system/fvSolution" \
  || abort "relaxation substitution failed"

grep -q 'volumeMode      specific;' "$RUN_DIR/constant/fvOptions" \
  || abort "the assembled fvOptions does NOT state \`volumeMode specific;\`.
  Section 2.4: under \`absolute\` the supplied number is divided by the
  cell-zone volume and the case still meshes, still runs, still converges and
  produces an entirely wrong map."
grep -q "__" "$RUN_DIR/constant/fvOptions" "$RUN_DIR/system/controlDict" \
  "$RUN_DIR/0/k" "$RUN_DIR/0/omega" \
  && abort "an unsubstituted __PLACEHOLDER__ survived into the assembled case"

# THE AGE GUARD'S ANCHOR.  `0/U` is written LAST, so its mtime dates the run
# that was allowed to produce the answer (CLAUDE.md rule 4, section 11.1
# clause 6).  Nothing between this line and the solver launch touches the case.
mv "$RUN_DIR/0/U.pending" "$RUN_DIR/0/U" || abort "cannot place 0/U"
touch "$RUN_DIR/0/U"
sync

# -----------------------------------------------------------------------------
# SOLVE.  rc CAPTURED ON THE LINE THAT RUNS THE SOLVER.
# -----------------------------------------------------------------------------
PHASE="solve"
set +u
# shellcheck disable=SC1091
source /usr/lib/openfoam/openfoam2606/etc/bashrc "" >/dev/null 2>&1
set -u
command -v simpleFoam >/dev/null || abort "simpleFoam is not on PATH after
  sourcing the v2606 bashrc.  The Bash tool runs NON-LOGIN shells, so the
  environment must be sourced IN THE SAME INVOCATION as the launch
  (docs/OPENFOAM.md re-scope note); this trap has already cost one run."

cd "$RUN_DIR" || abort "cannot cd to $RUN_DIR"
decomposePar -force > log.decomposePar 2>&1
dec_rc=$?
[ "$dec_rc" = "0" ] || abort "decomposePar rc=$dec_rc"

# THE rc IS TAKEN HERE, ON THIS LINE, INSIDE THIS PROCESS.  It is NOT taken
# around a `setsid` line: `setsid timeout cmd` exits 0 for every outcome of its
# child and would certify a corpse as a completion.
mpirun -np "$RANKS" simpleFoam -parallel > log.simpleFoam 2>&1
SOLVER_RC=$?

reconstructPar -latestTime > log.reconstructPar 2>&1 || true

PHASE="solved"
echo "solver rc = $SOLVER_RC   (captured inside this process, on the solver line)"
[ "$SOLVER_RC" = "0" ] || abort "the solver returned $SOLVER_RC.  A crash is a
  FINDING until triage says otherwise (SUPERVISION_CHARTER section 3 check 2)
  and that triage is the supervisor's, personally."

echo "GRADING IS A SEPARATE INVOCATION.  This launcher issues no verdict."
exit 0
