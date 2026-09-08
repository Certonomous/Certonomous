#!/bin/bash
# M6 OWN-MESH FAMILY {L2, L1, L0} SOLVE DRIVER -- for the FROZEN prereg
# verification/campaign/M6_OWN_FAMILY_FINE_TRIPLE_PREREGISTRATION.md.
#
# WHAT THIS FILE IS.  It runs the steady compressible flow solve of the own-family fine triple
# into <run_root>/L{2,1,0}/solve/, using the STOCK rhoSimpleFoam (OpenFOAM-v2506) inside the
# pinned docker image dafoam-idwarp-rot:v1 as `-u 1002:1002`.  It is a SOLVER DRIVER, NOT A
# GRADER: it computes no gate, applies no threshold, prints no verdict.  Rule 2 fixes the
# grading path at the pre-registration commit; the own-family grader
# verification/runs/M6_OWN_FAMILY_runs/analyse_m6_own_family.py grades what this produces, and
# is pinned by the FREEZE ADDENDUM the cfd-supervisor applies at re-pin.  NOTHING HERE GRADES.
#
# IT IS A DRAFT.  Nothing is wired live and NOTHING is launched by this file's authoring lane.
# The cfd-supervisor takes check-1 (the grader -- measurement logic) and check-4 personally,
# and the FREEZE ADDENDUM re-pins the grading-path blob, BEFORE any queue row or solve (§12.3).
# The solve is DAEMON-ROUTED only (§8); this driver is the queue row's launch target, never a
# direct launch.
#
# L-505, AND WHY THERE IS NO `env USER=` WRAP HERE.  L-505 is a USER-SPACE (FOAM_USER_APPBIN)
# trap: a daemon with USER unset misresolves a binary under $HOME/OpenFOAM/${USER:-user}-*.
# The pinned solver here is the STOCK rhoSimpleFoam at the FOAM PLATFORM bin
# (/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/.../bin/rhoSimpleFoam), which is
# USER-INDEPENDENT -- the same reason L-505 records that "prior daemon runs only succeeded
# because they used STOCK system-path solvers".  Adding an `env USER=` wrap would be cargo-cult
# here; it is deliberately ABSENT (task brief; L-505 distinction).
#
# COST (rule 12).  Unit: core-minutes (wall s x ranks / 60).  ONE registered hard cap for the
# whole fine-triple SOLVE campaign: 2,136 core-min (prereg §7.3), a SINGLE ACCUMULATOR across
# all three levels, tracked on disk in <run_root>/SOLVE_SPENT_COREMIN.txt.  AN OVERRUN STOPS
# THE CAMPAIGN; it does not get a new budget.  The cap is enforced by THREE limbs together
# (mirroring run_m6sr_b5.sh's item-39 repair): `timeout -k` on the docker client, an
# UNCONDITIONAL `docker kill` on the recorded container name, and an overrun branch accepting
# 124 AND 137.  Dollars are DERIVED at the owner-stated c7a.4xlarge $0.0513/core-h and are
# REPORTED-BY-OWNER, not measured (the box cannot read its own billing).
#
# §9.2 BINDING (mirrored from run_m6sr_b5.sh):
#   * No `assert`, no bare `set -e`.  Every check is `... || { abort ...; }`.
#   * rc IS CAPTURED INSIDE the wrapper (a file the container writes) -- `setsid timeout cmd`
#     exits 0 for every outcome, so an rc taken from around the wrapper line is meaningless.
#   * Every reading names ONE artifact by explicit path (never `grep log.* | tail -1`).
#   * The wrapper's log lives OUTSIDE the bind mount, so the host fd and the inner command's fd
#     can never address one inode (run_m6sr_b5.sh item 32/34).
#
# NOTHING UNDER /home/ubuntu/certonomous-runs/ IS WRITTEN.  SUBMISSIONS ARE PARKED (rule 7).
#
# USAGE:  run_m6_own_family_triple.sh <L2|L1|L0> [stage|solve|all]

set +u
set +e

LEVEL="$1"
PHASE="${2:-all}"

RR=${M6OWN_RUN_ROOT:-/home/ubuntu/Certonomous/verification/runs/M6_OWN_FAMILY_runs}
CASES="$RR"                                          # own-family drivers live in the run root
IMG=${M6OWN_IMAGE:-dafoam-idwarp-rot:v1}
RATE_USD_PER_CORE_H=0.0513

# --- THE PINNED INSTRUMENT (mirrors run_m6sr_b5.sh Amendment 12 Ruling 1). ----------------
# The image and the stock solver are pinned by the M6SR registration and reused here (§5's
# solver is byte-identical to RUNG1_M6_R2 / M6SR: rhoSimpleFoam, v2506).  These are NOT
# ${VAR:-default}: $M6OWN_IMAGE may NAME an image, it may not SELECT one.
M6OWN_PINNED_IMAGE_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
M6OWN_PINNED_OF_VERSION=v2506
M6OWN_PINNED_SOLVER_PATH=/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/rhoSimpleFoam
M6OWN_PINNED_SOLVER_SHA256=d9a2a45664f519e9f6b4c34741a4c414517889b4cfbe7764b2237ebf9a01369c

# --- THE GRADING PATH, PINNED (rule 2).  The driver rehearses and hashes it BEFORE spending. -
# The own-family grader is check-1'd and pinned by the FREEZE ADDENDUM; its committed blob is
# read from HEAD at run time and compared to whatever is on disk, refusing on drift.  The M6SR
# measurement core it imports is pinned by the frozen prereg §12.3.
OWN_GRADER_REL=verification/runs/M6_OWN_FAMILY_runs/analyse_m6_own_family.py
M6SR_CORE_REL=cases/M6SR/analyse_m6sr.py
M6SR_CORE_PINNED_BLOB=8007b23da5bb3173dacb6eda1d67ca5d90ce9139     # frozen prereg §12.3
REPO=/home/ubuntu/Certonomous

# --- ONE REGISTERED HARD CAP, single accumulator across all three levels (§7.3, rule 12). ---
CAP_TOTAL_COREMIN=2136.0
SPENT_LEDGER="$RR/SOLVE_SPENT_COREMIN.txt"
CAP_KILL_GRACE_S=5

say(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }
abort(){ echo "ABORT: $1"; mkdir -p "$RR/$LEVEL" 2>/dev/null; echo "$1" > "$RR/$LEVEL/solve/STOPPED.txt" 2>/dev/null; exit "${2:-1}"; }
sha_of(){ sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

# --- 0. THE LEVEL TABLE.  Nothing here is chosen by this driver. ---------------------------
#   RANKS: L2=4, L1=8, L0=14 -- ceiling-bounded (14 fits under the ~14.4-core daemon ceiling;
#     16 would oversubscribe the 16-vCPU box against the daemon).  REGISTERED here.
#   END_TIME: 6000 iterations per level -- the frozen §7.2 cost basis (DRAFT; supervisor
#     confirms at check-4; §7.3's x2 cap covers L0 needing more to plateau).
#   MEM_FLOOR_GB: ESTIMATE, not measured -- no 4.6M-cell rhoSimpleFoam footprint exists on
#     this box.  Basis: a conservative ~2.5 GB per 1M cells for a segregated compressible
#     k-omega SST solve, so L0 ~= 4.59M x 2.5 ~= 11.5 GB -> floor 12 GB (fits the 32 GB box
#     with headroom).  LABELLED ESTIMATE.
case "$LEVEL" in
  L2) CELLS=71760   ; END_TIME=6000 ; RANKS=4  ; MEM_FLOOR_GB=1  ;;
  L1) CELLS=574080  ; END_TIME=6000 ; RANKS=8  ; MEM_FLOOR_GB=3  ;;
  L0) CELLS=4592640 ; END_TIME=6000 ; RANKS=14 ; MEM_FLOOR_GB=12 ;;
  *)  echo "ABORT: level must be one of L2 L1 L0; got '${LEVEL:-<empty>}'"; exit 2 ;;
esac
case "$PHASE" in
  stage|solve|all) : ;;
  *) echo "ABORT: phase must be one of stage solve all; got '$PHASE'"; exit 2 ;;
esac

SOLVE="$RR/$LEVEL/solve"
MESH_SRC="$RR/$LEVEL/case/constant/polyMesh"          # the already-built, screened mesh case
# The own-family solve case files (0/, system/{fvSchemes,fvSolution,controlDict,
# decomposeParDict}, constant/{thermophysicalProperties, momentumTransport/turbulenceProperties,
# transportProperties}) encode §5's byte-identical-to-RUNG1_M6_R2 configuration.  There is ONE
# writer and this driver authors no case file of its own (mirrors run_m6sr_b5.sh's rule).
OWN_CASE_WRITER="$RR/write_m6_own_family_case.py"

say "M6 own-family solve driver -- level $LEVEL, phase $PHASE"
say "run root: $RR   (nothing under /home/ubuntu/certonomous-runs is written)"
say "schedule: $CELLS cells, endTime $END_TIME, $RANKS ranks, mem floor ~${MEM_FLOOR_GB} GB (ESTIMATE)"
say "ONE hard cap: $CAP_TOTAL_COREMIN core-min, single accumulator across L2+L1+L0 (§7.3)"

# --- 1. REFUSALS BEFORE ANY WORK. ----------------------------------------------------------
# The registered case writer must exist -- this driver writes no case file of its own.
# (As of authoring it is ABSENT: an OWED dependency the cfd-supervisor is told of; the driver
# refuses cleanly rather than fabricate §5's freestream/thermophysical configuration.)
[ -f "$OWN_CASE_WRITER" ] \
  || abort "the registered own-family case writer $OWN_CASE_WRITER is ABSENT. This driver authors NO case file of its own; §5's rhoSimpleFoam configuration (k-omega SST, nutUSpaldingWallFunction, M=0.8395, alpha=3.06, Re=11.72e6) must come from that one writer. OWED before launch." 3

# Rule 4 / §8.6: REFUSE a solve case where `0` or any time directory already exists (the age
# guard dates the run from the case's own 0/U; a pre-existing 0/ makes rule 4 unprovable).
if [ -d "$SOLVE" ]; then
  [ -d "$SOLVE/0" ] && abort "$SOLVE/0 already exists. The age guard dates the run from 0/U; a pre-existing 0/ makes rule 4 unprovable. REFUSED." 4
  for D in "$SOLVE"/[0-9]*; do
    [ -d "$D" ] && abort "a time directory already exists: $D. REFUSED (rule 4)." 4
  done
fi
mkdir -p "$SOLVE" || abort "could not create $SOLVE" 3

# --- Docker preflight, both limbs recorded (mirrors run_m6sr_b5.sh item 28). ---------------
BARE_OUT=$(docker version --format '{{.Server.Version}}' 2>&1); BARE_RC=$?
SG_OUT=$(sg docker -c "docker version --format '{{.Server.Version}}'" 2>&1); SG_RC=$?
{ echo "bare_rc=$BARE_RC"; echo "bare_out=$BARE_OUT"
  echo "sg_rc=$SG_RC"; echo "sg_out=$SG_OUT"; echo "groups=$(id -G)"; } > "$SOLVE/DOCKER_PREFLIGHT.txt"
if [ $SG_RC -ne 0 ] && [ $BARE_RC -ne 0 ]; then
  abort "docker unreachable both bare and through 'sg docker -c'. This grades THE DRIVER'S ABILITY TO RUN, not the M6 -- BLOCKED, not GATE FAIL." 5
fi
if [ $BARE_RC -eq 0 ]; then DOCKER_BRANCH=bare; else DOCKER_BRANCH=sg; fi
HOST_GID=$(id -g)
DOCKER_BIN=$(command -v docker 2>/dev/null)
[ "$DOCKER_BRANCH" != "bare" ] || [ -n "$DOCKER_BIN" ] \
  || abort "the bare-docker branch was selected (bare rc=$BARE_RC) but 'docker' does not resolve on PATH; there is no program for \`timeout\` to exec. This driver will not guess a path." 5
echo "$DOCKER_BRANCH" > "$SOLVE/DOCKER_BRANCH.txt"
say "docker reachable (bare rc=$BARE_RC, sg rc=$SG_RC); branch '$DOCKER_BRANCH'${DOCKER_BIN:+ via $DOCKER_BIN}"

docker_q(){
  if [ "$DOCKER_BRANCH" = "bare" ]; then command docker "$@"; return $?; fi
  local q; q=$(printf ' %q' "$@"); sg docker -c "docker$q"
}
docker_timeout_q(){
  local tmo="$1"; shift
  if [ "$DOCKER_BRANCH" = "bare" ]; then
    timeout -k "${CAP_KILL_GRACE_S}"s "${tmo}"s "$DOCKER_BIN" "$@"; return $?
  fi
  local q; q=$(printf ' %q' "$@")
  timeout -k "${CAP_KILL_GRACE_S}"s "${tmo}"s sg docker -c "docker$q"; return $?
}

# --- 1b. THE SOLVER IS PINNED, AND THE PIN REFUSES BEFORE IT SPENDS (mirrors A12 Ruling 1). -
RESOLVED_DIGEST=$(docker_q inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
[ -n "$RESOLVED_DIGEST" ] \
  || abort "the image '$IMG' does not resolve to a digest on this daemon. REFUSED (never a fallback to whatever else is on the box)." 7
[ "$RESOLVED_DIGEST" = "$M6OWN_PINNED_IMAGE_DIGEST" ] \
  || abort "IMAGE DIGEST MISMATCH. '$IMG' resolves to $RESOLVED_DIGEST; pinned $M6OWN_PINNED_IMAGE_DIGEST. \$M6OWN_IMAGE may NAME an image; it may not SELECT one. REFUSED AT ZERO SOLVER COST." 7
IMG_PINNED="$M6OWN_PINNED_IMAGE_DIGEST"

PROBE_OUT=$(docker_q run --rm -u 1002:1002 "$IMG_PINNED" bash -lc 'set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; B=$(command -v rhoSimpleFoam); printf "VER=%s\nBIN=%s\nSHA=%s\n" "$WM_PROJECT_VERSION" "$B" "$(sha256sum "$B" 2>/dev/null | cut -d" " -f1)"' 2>&1)
P_VER=$(printf '%s\n' "$PROBE_OUT" | sed -n 's/^VER=//p')
P_BIN=$(printf '%s\n' "$PROBE_OUT" | sed -n 's/^BIN=//p')
P_SHA=$(printf '%s\n' "$PROBE_OUT" | sed -n 's/^SHA=//p')
[ -n "$P_VER" ] && [ -n "$P_BIN" ] && [ -n "$P_SHA" ] \
  || abort "the solver probe inside the pinned image failed. A probe that returns nothing is a REFUSAL, never an assumption. Output: $PROBE_OUT" 7
[ "$P_VER" = "$M6OWN_PINNED_OF_VERSION" ] \
  || abort "OPENFOAM VERSION MISMATCH: image reports '$P_VER'; pinned '$M6OWN_PINNED_OF_VERSION'. REFUSED." 7
[ "$P_BIN" = "$M6OWN_PINNED_SOLVER_PATH" ] \
  || abort "SOLVER BINARY PATH MISMATCH: PATH resolves rhoSimpleFoam to '$P_BIN'; pinned '$M6OWN_PINNED_SOLVER_PATH'. The image also carries OpenFOAM-AD builds of the same name -- a path this driver did not expect is a DIFFERENT SOLVER. REFUSED." 7
[ "$P_SHA" = "$M6OWN_PINNED_SOLVER_SHA256" ] \
  || abort "SOLVER BINARY sha256 MISMATCH: read $P_SHA, pinned $M6OWN_PINNED_SOLVER_SHA256. REFUSED." 7
say "solver pin VERIFIED: $M6OWN_PINNED_OF_VERSION at $P_BIN (sha256 ${P_SHA:0:16}...), image $RESOLVED_DIGEST"

# --- 1c. THE GRADING PATH IS HASHED AND REHEARSED BEFORE THE RUN IS PAID FOR (rule 2/3). ----
# (i) HASH the own-family grader AND the imported M6SR core against their committed blobs.  A
#     grading path that changed since the freeze is not a frozen grading path.
GRADER_DISK_BLOB=$(cd "$REPO" && git hash-object "$OWN_GRADER_REL" 2>/dev/null)
GRADER_HEAD_BLOB=$(cd "$REPO" && git rev-parse "HEAD:$OWN_GRADER_REL" 2>/dev/null)
[ -n "$GRADER_HEAD_BLOB" ] \
  || abort "the own-family grader $OWN_GRADER_REL is not committed at HEAD, so there is no frozen blob to grade against. REFUSED (rule 2)." 9
[ "$GRADER_DISK_BLOB" = "$GRADER_HEAD_BLOB" ] \
  || abort "GRADER DRIFT: $OWN_GRADER_REL on disk hashes $GRADER_DISK_BLOB, HEAD has $GRADER_HEAD_BLOB. The grading path must BE the file the freeze pinned (rule 2). REFUSED AT ZERO SOLVER COST." 9
M6SR_HEAD_BLOB=$(cd "$REPO" && git rev-parse "HEAD:$M6SR_CORE_REL" 2>/dev/null)
[ "$M6SR_HEAD_BLOB" = "$M6SR_CORE_PINNED_BLOB" ] \
  || abort "M6SR MEASUREMENT CORE DRIFT: HEAD:$M6SR_CORE_REL is $M6SR_HEAD_BLOB; the frozen prereg §12.3 pins $M6SR_CORE_PINNED_BLOB. REFUSED AT ZERO SOLVER COST." 9
say "grading path pinned: grader blob $GRADER_HEAD_BLOB; M6SR core blob $M6SR_HEAD_BLOB (§12.3)"

# (ii) REHEARSE the planted controls under BOTH interpreters (rule 3, §9.2 -O parity), so a
#      solve is never paid for and then found ungradable.  Only for phases that reach a solve.
if [ "$PHASE" = "solve" ] || [ "$PHASE" = "all" ]; then
  python3    "$REPO/$OWN_GRADER_REL" --controls > "$SOLVE/log.comparator_controls"   2>&1; CRC=$?
  python3 -O "$REPO/$OWN_GRADER_REL" --controls > "$SOLVE/log.comparator_controls_O" 2>&1; CRC_O=$?
  [ "$CRC" -eq "$CRC_O" ] \
    || abort "the grader's controls return rc $CRC (python3) vs rc $CRC_O (python3 -O). §9.2 requires identical refusals under both (L-475). REFUSED AT ZERO SOLVER COST." 8
  [ "$CRC" -eq 0 ] \
    || abort "the GRADING path's planted controls did not pass (rc $CRC; see $SOLVE/log.comparator_controls). A solve launched now would be UNGRADABLE. A zero from a reader not shown able to see a non-zero is not evidence (rule 3). REFUSED AT ZERO SOLVER COST." 8
  say "grading-path rehearsal: ALL controls passed under python3 and python3 -O"
fi

# --- 2. THE CONTAINER WRAPPER.  rc CAPTURED INSIDE (§9.2); cap enforced by three limbs. -----
# The single accumulator: read the ledger, refuse if already at/over the cap, and convert the
# REMAINING core-min into a per-step wall-second timeout at this level's rank count.
read_spent(){ [ -f "$SPENT_LEDGER" ] && cat "$SPENT_LEDGER" 2>/dev/null || echo "0"; }
add_spent(){ # $1 = core-min to add
  local cur; cur=$(read_spent)
  python3 - "$cur" "$1" "$SPENT_LEDGER" <<'PY'
import sys
cur=float(sys.argv[1]); add=float(sys.argv[2]); path=sys.argv[3]
open(path,"w").write(f"{cur+add:.6f}\n")
PY
}

run_in_container(){
  local tag="$1" ranks="$2" cmd="$3"
  local t0 t1 rc wall inner wdir wlog cname spent remain tmo
  # Cap accumulator gate: refuse before starting if the campaign cap is already exhausted.
  spent=$(read_spent)
  remain=$(python3 -c "print(max(0.0, $CAP_TOTAL_COREMIN - $spent))")
  if [ "$(python3 -c "print(1 if $remain <= 0 else 0)")" = "1" ]; then
    abort "CAP_BREACH: the single hard cap $CAP_TOTAL_COREMIN core-min is exhausted (spent $spent). AN OVERRUN STOPS THE CAMPAIGN; it does not get a new budget (rule 12)." 6
  fi
  # Per-step wall-second timeout from the REMAINING core-min at this level's ranks.
  tmo=$(python3 -c "import math; print(int(math.floor($remain*60.0/$ranks)))")
  [ "$tmo" -ge 1 ] || abort "CAP_BREACH: remaining budget ${remain} core-min < one wall second at $ranks ranks. STOPPED (rule 12)." 6
  # The wrapper log leaves the bind mount (run_m6sr_b5.sh item 32/34): the container sees only
  # $SOLVE at /case, so a log OUTSIDE it can never be opened from inside -> no head-corruption.
  wdir="$RR/_wrapper_logs/$LEVEL"; wlog="$wdir/log.$tag"
  case "$wlog" in
    "$SOLVE"|"$SOLVE"/*) abort "the wrapper log '$wlog' is INSIDE the bind mount '$SOLVE'; a client write would overwrite the artifact's head. REFUSED before the container starts (item 32/34)." 6 ;;
  esac
  mkdir -p "$wdir" || abort "could not create the wrapper-log dir $wdir (outside the bind mount)." 6
  cname="m6own_${LEVEL}_${tag}_$$"
  echo "$cname" > "$wdir/CONTAINER_NAME.$tag"
  t0=$(date +%s)
  # -u 1002:1002 (dafoamuser) + exactly one supplementary group (the host group owning $SOLVE)
  # so the container can write its outputs.  NO `env USER=` wrap (L-505: stock FOAM-platform
  # binary, USER-independent).  rc CAPTURED INSIDE via RC_${tag}.txt (setsid/timeout exits 0).
  docker_timeout_q "$tmo" run --rm --name "$cname" -u 1002:1002 \
      --group-add "$HOST_GID" \
      -v "$SOLVE":/case -w /case "$IMG_PINNED" \
      bash -c "set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; $cmd; echo \"WRAPPER_RC=\$?\" > RC_${tag}.txt" \
      > "$wlog" 2>&1
  rc=$?
  t1=$(date +%s); wall=$((t1-t0))
  # UNCONDITIONAL kill on the recorded name (the client's return says nothing about the
  # container -- run_m6sr_b5.sh item 39).  On the happy path --rm has already reaped it.
  docker_q kill "$cname" >/dev/null 2>&1
  docker_q rm -f "$cname" >/dev/null 2>&1
  inner="ABSENT"
  [ -f "$SOLVE/RC_${tag}.txt" ] && inner=$(cut -d= -f2 "$SOLVE/RC_${tag}.txt")
  # Book the spend into the SINGLE accumulator BEFORE evaluating the outcome.
  local coremin; coremin=$(python3 -c "print($wall*$ranks/60.0)")
  add_spent "$coremin"
  echo "$tag ranks=$ranks wall_s=$wall coremin=$coremin outer_rc=$rc inner_rc=$inner timeout_s=$tmo cap_remain_at_start=$remain container=$cname docker_branch=$DOCKER_BRANCH" \
      >> "$SOLVE/STEP_RC.txt"
  say "$tag: outer rc=$rc  INNER rc=$inner  wall=${wall}s  ranks=$ranks  step=${coremin} core-min  (cap spent now $(read_spent)/$CAP_TOTAL_COREMIN)"
  # 124 = client exited on SIGTERM at the cap; 137 = 128+9, client SIGKILLed by `timeout -k`
  # at cap+grace (the NORMAL containerised-overrun rc on this box).  Either STOPS the run.
  if [ "$rc" -eq 124 ] || [ "$rc" -eq 137 ]; then
    abort "$tag hit the remaining-budget cap of ${tmo} wall s at $ranks ranks (outer rc=$rc after ${wall}s). The container '$cname' was killed unconditionally. AN OVERRUN STOPS THE CAMPAIGN; it does not get a new budget (rule 12)." 6
  fi
  [ "$inner" = "0" ] || abort "$tag inner rc=$inner (outer $rc). A non-zero rc inside the container is a FAILED STEP." 6
}

# --- 3. PHASE `stage` -- the mesh into the solve case, then the case files. ----------------
if [ "$PHASE" = "stage" ] || [ "$PHASE" = "all" ]; then
  if [ -d "$SOLVE/constant/polyMesh" ]; then
    say "stage: $SOLVE/constant/polyMesh already present; NOT overwritten"
  else
    [ -d "$MESH_SRC" ] || abort "the level's mesh source is ABSENT: $MESH_SRC (the built, screened mesh case). An absent mesh is a REFUSAL, never an empty level." 3
    mkdir -p "$SOLVE/constant" || abort "could not create $SOLVE/constant" 3
    cp -a -- "$MESH_SRC" "$SOLVE/constant/polyMesh" || abort "mesh copy-out of $MESH_SRC failed" 3
    say "stage: copied $MESH_SRC -> $SOLVE/constant/polyMesh"
  fi
  # The ONE case writer writes 0/, system/, constant/*Properties for §5's configuration.
  python3 "$OWN_CASE_WRITER" --level "$LEVEL" --solve "$SOLVE" --ranks "$RANKS" \
      --end-time "$END_TIME" > "$SOLVE/log.write_case" 2>&1 \
    || abort "the own-family case writer failed for $LEVEL (see $SOLVE/log.write_case)." 3
  say "stage: case files written by $OWN_CASE_WRITER (0/, system/, constant/*Properties)"
fi

# --- 4. PHASE `solve` -- decompose / mpirun -parallel / reconstruct.  Each step booked. -----
if [ "$PHASE" = "solve" ] || [ "$PHASE" = "all" ]; then
  [ -d "$SOLVE/constant/polyMesh" ] || abort "no mesh at $SOLVE/constant/polyMesh; run phase 'stage' first." 3
  [ -d "$SOLVE/0" ] || abort "no 0/ at $SOLVE (the case writer must have written it in phase 'stage'). REFUSED." 3
  # decomposePar: hierarchical (the M6SR convention; scotch NOT used), nProcs from the writer's
  # decomposeParDict, which the writer sized to $RANKS.
  run_in_container "decomposePar" "$RANKS" "decomposePar -force > log.decomposePar 2>&1"
  # The primal.  rhoSimpleFoam in parallel at $RANKS ranks.
  run_in_container "rhoSimpleFoam" "$RANKS" "mpirun -np $RANKS rhoSimpleFoam -parallel > log.rhoSimpleFoam 2>&1"
  # reconstruct the latest time so the grader reads reconstructed fields at endTime.
  run_in_container "reconstructPar" "$RANKS" "reconstructPar -latestTime > log.reconstructPar 2>&1"
  # The solver rc, for the grader's rule-4 completion clause, written where it expects it.
  [ -f "$SOLVE/RC_rhoSimpleFoam.txt" ] \
    && cut -d= -f2 "$SOLVE/RC_rhoSimpleFoam.txt" > "$SOLVE/SOLVER_RC.txt"
  say "solve: decompose/solve/reconstruct complete for $LEVEL; grading is DEFERRED to the check-1'd own-family grader (analyse_m6_own_family.py --grade). THIS DRIVER GRADES NOTHING."
fi

say "done: level $LEVEL phase $PHASE. Cap spent $(read_spent)/$CAP_TOTAL_COREMIN core-min (single accumulator, §7.3)."
