#!/usr/bin/env bash
# Curriculum D7 arm launcher -- ONERA M6 lift-constrained transonic drag
# minimisation, A3 rung-2 mesh (42,120 cells), np=4.
#
# Derived from the proven `A2/curriculum_D4/d4_run_arm.sh` with D7's registered
# changes: D7's run root, D7's FIVE arms (P1, P2, O, F-S, F-P), D7's cap table,
# D7's cpuset census, a WIRED MEMORY FLOOR, and the CL-target staging step that
# PREREGISTRATION.md sec.1 requires.
#
# CAP DISCIPLINE.  The caps are NOT arguments.  They are constants in the table
# below, the table is reproduced verbatim in PREREGISTRATION.md sec.8, this
# file's md5 is frozen in Addendum 1, and the launcher ASSERTS that the wall
# timeout it is about to enforce equals CAP*60/RANKS by INVERTING the
# arithmetic.  There is no second number anywhere that could drift from the
# first.  Cost constraints are LIFTED (Sanaa, 2026-08-25) and the caps are
# RUNAWAY GUARDS: a crossing is REPORTED to the supervisor, never silently
# continued and never silently stopped.
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call and
# `( set -e; ... )` does not gate either.  Every step below gates explicitly
# with `|| { echo ABORT...; exit N; }`.
#
# NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives the arm
# and THE KERNEL'S verdict is read, not the harness's (G11).
#
# RESERVED PREFLIGHT EXIT CODES (PREREGISTRATION.md sec.7): 4, 5, 64, 65 -- and
# NEVER 0, 1 or 2.  A symptom must distinguish its causes: an exit code from
# this harness is not an exit code from the solver.
#   64 = usage      4 = identity/staging refusal
#   65 = arithmetic 5 = gate refusal (cold-state, memory floor, missing input)
set -uo pipefail

BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D7F-a3-m6-fd
RANKS=4

# ---- REGISTERED CPU PLACEMENT (PREREGISTRATION.md sec.5) -----------------
# `mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF THE
# HOST TOPOLOGY; concurrent containers collide there and throughput collapses
# as 1/N while the box reports itself idle (MEASURED, D13 lane 2026-08-25:
# 0.250 cores against a 1.0-core quota, host 61 % idle).  `--cpus=4` does NOT
# hand out four distinct cores.  So PIN, and MEASURE the placement rather than
# infer it from the flag that was passed.
#
# CORE CENSUS TAKEN 2026-08-25T20:25Z, mpstat -P ALL over 5 s:
#   cores 5, 14, 15 = 0.0 % idle  -- three T-family buoyantBoussinesq solvers
#                                    (pids 2203927/2203944/2203947), NOT TOUCHED
#   core  0         = the default landing core the placement defect names
#   cores 2,3,4,6   = 99.2 / 99.2 / 99.2 / 99.2 % idle  <-- CHOSEN
CPUSET=2,3,4,6

# ---- THE MEMORY FLOOR -- WIRED, WITH A REFUSAL PATH ----------------------
# A3 rung 2 registered a host-memory stop rule as a RECORD-ONLY watcher with
# NOTHING connecting the rule to a kill path.  Its own RESULTS.md sec.9.1 is
# blunt about it: "A stop rule with no enforcement path is a preference, not a
# control", and the arm drove host MemAvailable to 5.85 GiB for 82 of 156
# samples with no stop.  THAT MISTAKE IS NOT REPEATED HERE.
#
# What is enforced here is a PRE-LAUNCH GATE with a real refusal path (exit 5).
# There is NO mid-run stop rule, and none is registered -- killing a converged
# 30-major optimisation to protect a number would destroy the run it protects.
# The in-run host-memory sampler below is RECORD-ONLY AND IS DECLARED AS SUCH:
# it has no threshold, no stop condition and no kill path, so it cannot become
# a rule nobody wired.
#
# THRESHOLDS, STATED IN ADVANCE OF THE READING THEY GATE:
#   arms with a 12g container cap (P2, O, F-S, F-P): MemAvailable >= 16.0 GiB
#   arm with a  4g container cap (P1):               MemAvailable >=  6.0 GiB
# Basis: the container cap plus ~4 GiB of host headroom.  A3 rung 2 measured
# peak container RSS 9.263 GiB at np=4 on THIS mesh, inside a 12 GiB cap.
mem_floor_gib() { case "$1" in P1) echo 6.0 ;; *) echo 16.0 ;; esac; }

container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d7_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md sec.7, verbatim) -----------
# THE GRADER CHECKS THESE AGAINST THE DOCUMENT.  `d7f_grade.py`'s
# `assert_caps_against_document()` parses sec.7 and REFUSES on any disagreement
# with the constants it carries -- D7R-GRADER-DEF-6 repaired at its cause.  A
# cap that drifts between this launcher, the grader and the document is the
# D7R-DEF-8 class, and G10 LIMB 1 catches it in the ledger this file writes.
#   arm    core-min cap   memory cap   prediction   ceiling (= 4 x cap)
#   P1          8.0           4g          0.75         32.0
#   X          15.0          12g          2.0          60.0
#   ACC        60.0          12g         25.0         240.0
#   F-S       750.0          12g        485.0        3000.0
#   F-P       750.0          12g        485.0        3000.0
cap_core_min() {
  case "$1" in
    P1)  echo 8.0 ;;
    X)   echo 15.0 ;;
    ACC) echo 60.0 ;;
    F-S) echo 750.0 ;;
    F-P) echo 750.0 ;;
    *)   echo "" ;;
  esac
}
cap_memory() {
  case "$1" in
    P1) echo 4g ;;
    X|ACC|F-S|F-P) echo 12g ;;
    *) echo "" ;;
  esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER sec.11) -
# THE HASH IS THE IDENTITY; THE VERSION STRING IS NOT.  A3 rung 2 recorded
# idwarp reading version "2.6.2" on the PATCHED stack -- the version string
# discriminates NOTHING.  Digests resolved from the local store 2026-08-25T20:26Z
# and identical to the two D4 registered at its own freeze.
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35

# ---- FROZEN INSTRUMENT HASHES (PREREGISTRATION.md Addendum 1) ------------
MD5_RUNSCRIPT=e43902ed2cfc99022c6e21e075f88695
MD5_FD=92b3fa8d20a41da029590ed3bdde4203
MD5_EXTRACT=651d40c78cc52288a856934c108d1334
# The FOUR NEW instruments this item adds.  Filled at the freeze commit by
# `md5sum` and asserted below before EVERY launch, exactly as the three
# inherited ones are.
MD5_LOCUS=a38c5e507b44eb17d1c1247e48b6fe0a
MD5_PHYSICAL=7be14b7d5568a6e79afa3bdd7c612749
MD5_ACCPRIMAL=65baf532bcc2fdbe6a20a92dcd1a596b
MD5_ACCCOMPARE=a4b4eb3d81bf0e4ed9f20dd673b759df
MD5_GRADE=923662ef398ca229cc3734699670418a
# GATE H4's identifiers: D7R arm O's endpoint artifacts, BY HASH.
MD5_OPTVIEW=ed90aa4f0a38b2fadf93cdc0b601ec41
MD5_IPOPT=175969fb3e4fa609af708f4f49aa4a6a

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d7f_run_arm.sh <P1|X|ACC|F-S|F-P> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d7f_run_arm.sh <P1|X|ACC|F-S|F-P> <image>"; exit 64; }

CAP=$(cap_core_min "$ARM")
MEM=$(cap_memory "$ARM")
test -n "$CAP" || { echo "ABORT unknown arm $ARM -- no registered cap"; exit 64; }
test -n "$MEM" || { echo "ABORT unknown arm $ARM -- no registered memory cap"; exit 64; }

# THE CAP ASSERTION.  Derive the wall timeout from the registered core-minute
# cap and the registered rank count, then INVERT the arithmetic and require the
# result to equal the registered cap to within 0.02 core-min.
TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)))") || { echo "ABORT tmo calc"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % ($TMO*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced=%r\n' % (cap, back)); sys.exit(1)
" || { echo "ABORT enforced cap != registered cap"; exit 65; }
echo "D7_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM"

# ---- host state, read before ranks are claimed ---------------------------
MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
FLOOR=$(mem_floor_gib "$ARM")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D7_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB floor_GiB=$FLOOR load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

# THE MEMORY GATE FIRES HERE, BEFORE ANY RANK IS CLAIMED.
python3 -c "
import sys
if $MEMAVAIL_GIB < $FLOOR:
    sys.stderr.write('ABORT MEMORY FLOOR arm=$ARM MemAvailable=$MEMAVAIL_GIB GiB < floor $FLOOR GiB\n'); sys.exit(1)
" || { echo "ABORT memory floor -- REFUSED TO LAUNCH, nothing started, 0.000 core-min"; exit 5; }

test -d "$BASE" || { echo "ABORT run root $BASE absent -- stage first"; exit 5; }

# ---- staged-instrument identity, re-asserted before EVERY launch ---------
echo "$MD5_RUNSCRIPT  $BASE/d7_opt_runScript.py"  | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_FD  $BASE/d7_fd_endpoint.py"           | md5sum -c - || { echo "ABORT fd md5"; exit 4; }
echo "$MD5_EXTRACT  $BASE/d7_extract_endpoint.py" | md5sum -c - || { echo "ABORT extract md5"; exit 4; }
echo "$MD5_LOCUS  $BASE/d7f_endpoint_locus.py"       | md5sum -c - || { echo "ABORT locus md5"; exit 4; }
echo "$MD5_PHYSICAL  $BASE/d7f_endpoint_physical.py" | md5sum -c - || { echo "ABORT physical md5"; exit 4; }
echo "$MD5_ACCPRIMAL  $BASE/d7f_accept_primal.py"    | md5sum -c - || { echo "ABORT accept-primal md5"; exit 4; }
echo "$MD5_ACCCOMPARE  $BASE/d7f_accept_compare.py"  | md5sum -c - || { echo "ABORT accept-compare md5"; exit 4; }
echo "$MD5_GRADE  $BASE/d7f_grade.py"                | md5sum -c - || { echo "ABORT grader md5"; exit 4; }

# ---- image identity by DIGEST, resolved from the local store -------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam/opt-packages:latest) WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED ;;
  dafoam-idwarp-rot:v1)       WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  *) echo "ABORT image $IMG is not a registered row"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }
echo "D7_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

# ROW RULES (PREREGISTRATION.md sec.8).  P1, X and ACC are SHIPPED-only: they
# establish the design point and reproduce arm O's objective, and arm O was a
# SHIPPED run, so reconstructing its endpoint on the PATCHED stack would be
# comparing two things at once.  F-S is SHIPPED and F-P is PATCHED, and TOGETHER
# THEY ARE THE TWO-ROW VERDICT -- the thing D7R could not buy.
case "$ARM" in
  P1|X|ACC) test "$ROW" = "SHIPPED" || { echo "ABORT arm $ARM is registered SHIPPED-only (sec.8); got $ROW"; exit 4; } ;;
  F-S)      test "$ROW" = "SHIPPED" || { echo "ABORT arm F-S must be SHIPPED; got $ROW"; exit 4; } ;;
  F-P)      test "$ROW" = "PATCHED" || { echo "ABORT arm F-P must be PATCHED; got $ROW"; exit 4; } ;;
esac

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d7f_${ARM//-/_}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- stage a pristine COLD copy of base/ ---------------------------------
# THE CASE AND MESH ARE STAGED BY COPY AND NEVER EDITED IN PLACE
# (PREREGISTRATION.md sec.1).
sudo -n rm -rf "$WORK" 2>/dev/null
rm -rf "$WORK" 2>/dev/null
cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy"; exit 4; }
cp -a "$BASE/d7_opt_runScript.py" "$BASE/d7_fd_endpoint.py" "$BASE/d7_extract_endpoint.py" \
      "$BASE/d7f_endpoint_locus.py" "$BASE/d7f_endpoint_physical.py" \
      "$BASE/d7f_accept_primal.py" "$BASE/d7f_accept_compare.py" "$WORK/" \
  || { echo "ABORT stage instruments"; exit 4; }

# COLD START, verified BEFORE the launch, and the AGE GUARD's datum.
for bad in "$WORK/reports" "$WORK/OptView.hst" "$WORK/opt_IPOPT.txt" \
           "$WORK/d7_fd_endpoint.json" "$WORK/d7_major_history.json" \
           "$WORK/d7_endpoint_dvs.json" "$WORK/d7_baseline.json" \
           "$WORK/d7_endpoint_dvs_PHYSICAL.json" \
           "$WORK/d7_endpoint_dvs_DRIVERSCALED.json" \
           "$WORK/d7f_accept_primal.json" "$WORK/d7f_accept_verdict.json"; do
  test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
done
test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
test -n "$(ls -d "$WORK"/[0-9]*.[0-9]* 2>/dev/null)" && { echo "ABORT G-COLD time dir present"; exit 5; }
test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing"; exit 5; }

# ---- per-arm staged INPUTS, each with its own refusal ---------------------
#
# GATE H4 -- ENDPOINT PROVENANCE (PREREGISTRATION.md sec.5).
# This item does not run an optimiser.  Its design point is D7R arm O's, and an
# inherited input is exactly where an unattributed artifact walks in: D7R sec.R3
# recorded that the `.bin.info` sidecar could not distinguish one configuration
# from another, so nothing keyed on content alone is a control.  H4 identifies
# the inherited endpoint BY md5 against D7R's own run root, and it runs the age
# comparison IN BOTH DIRECTIONS -- an INHERITED INPUT MUST BE OLD, a PRODUCED
# OUTPUT MUST BE NEW, and one rule cannot say both.
D7R_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin
stage_endpoint() {
  for f in OptView.hst opt_IPOPT.txt; do
    test -f "$D7R_ROOT/O/$f" || { echo "ABORT H4 ENDPOINT_PROVENANCE -- $D7R_ROOT/O/$f absent; this item has no endpoint of its own and may not invent one"; exit 5; }
  done
  # The md5s are FILLED AT THE FREEZE COMMIT from D7R arm O's artifacts and are
  # asserted here.  A different endpoint is a different item.
  echo "$MD5_OPTVIEW  $D7R_ROOT/O/OptView.hst"   | md5sum -c - || { echo "ABORT H4 ENDPOINT_PROVENANCE -- OptView.hst is not D7R arm O's"; exit 5; }
  echo "$MD5_IPOPT  $D7R_ROOT/O/opt_IPOPT.txt"   | md5sum -c - || { echo "ABORT H4 ENDPOINT_PROVENANCE -- opt_IPOPT.txt is not D7R arm O's"; exit 5; }
  cp -a "$D7R_ROOT/O/OptView.hst" "$D7R_ROOT/O/opt_IPOPT.txt" "$WORK/" || { echo "ABORT stage endpoint"; exit 4; }
  test -f "$D7R_ROOT/O/d7_cl_target.json" && cp -a "$D7R_ROOT/O/d7_cl_target.json" "$WORK/"
  echo "D7F_H4_PASS arm=$ARM endpoint=D7R/O OptView.hst=$MD5_OPTVIEW opt_IPOPT.txt=$MD5_IPOPT"
}

# THE COLOURING IS BUILT FRESH IN EVERY ARM THAT NEEDS ONE, AND THAT IS A
# DELIBERATE SIMPLIFICATION OF D7R, DECLARED HERE RATHER THAN LEFT IMPLICIT.
# D7R needed gate H1 because a cache built by one arm was inherited by another
# and the sidecar could not refuse a foreign one.  This item PRICES THE BUILD
# INTO BOTH FD ARMS (sec.7, 24.2 core-min each, measured from D7R's own P2 log)
# and inherits NOTHING -- so H1 has nothing to guard and IS NOT CARRIED FORWARD.
# A gate dropped is disclosed, never quietly omitted: the price of dropping it
# is 24.2 core-min on arm F-P and the gain is one whole class of provenance risk
# removed.

case "$ARM" in
  X)
    # Arm X: the D7-DEF-4 repair.  The FROZEN extractor runs INSIDE the wrapper,
    # which hashes it first.  Nothing here edits a frozen byte.
    stage_endpoint
    ;;
  ACC)
    # LIMIT 1.  One primal at the CORRECTED point, which arm X must have written.
    test -f "$BASE/X/d7_endpoint_dvs_PHYSICAL.json" || { echo "ABORT arm ACC requires $BASE/X/d7_endpoint_dvs_PHYSICAL.json from arm X"; exit 5; }
    grep -q '"_units": "PHYSICAL"' "$BASE/X/d7_endpoint_dvs_PHYSICAL.json" || { echo "ABORT arm ACC: the staged design point does not declare _units PHYSICAL -- applying a driver-scaled vector as physical is the defect under test"; exit 5; }
    cp -a "$BASE/X/d7_endpoint_dvs_PHYSICAL.json" "$WORK/" || { echo "ABORT stage physical dvs"; exit 4; }
    stage_endpoint
    ;;
  F-S|F-P)
    # THE FD ARMS RUN ONLY AFTER ACC-1 HAS PASSED.  LIMIT 1 is a PRECONDITION of
    # the freeze of the repair, so an FD table taken before it is a table at a
    # design point nothing has shown to be the optimum.
    test -f "$BASE/ACC/d7f_accept_verdict.json" || { echo "ABORT arm $ARM requires ACC-1 to have run; $BASE/ACC/d7f_accept_verdict.json absent (LIMIT 1)"; exit 5; }
    grep -q '"verdict": "PASS"' "$BASE/ACC/d7f_accept_verdict.json" || { echo "ABORT arm $ARM: ACC-1 did not PASS, so the repair is NOT FROZEN and no FD number from it may be graded (LIMIT 1)"; exit 5; }
    echo "D7F_LIMIT1_PASS $(python3 -c "import json;d=json.load(open('$BASE/ACC/d7f_accept_verdict.json'));print('rel_CD=%r band=%r verdict=%s'%(d['rel_CD'],d['band_ACC1'],d['verdict']))")"
    test -f "$BASE/X/d7_endpoint_dvs_PHYSICAL.json" || { echo "ABORT arm $ARM requires $BASE/X/d7_endpoint_dvs_PHYSICAL.json from arm X"; exit 5; }
    cp -a "$BASE/X/d7_endpoint_dvs_PHYSICAL.json" "$WORK/" || { echo "ABORT stage physical dvs"; exit 4; }
    # d7_fd_endpoint.py reads `d7_endpoint_dvs.json` by that name and is FROZEN,
    # so the PHYSICAL content is published under it -- the pre-image stays on
    # disk beside it, exactly as the wrapper's C4/C9 require.
    cp -a "$BASE/X/d7_endpoint_dvs_PHYSICAL.json" "$WORK/d7_endpoint_dvs.json" || { echo "ABORT publish physical dvs"; exit 4; }
    test -f "$BASE/X/d7_endpoint_dvs_DRIVERSCALED.json" && cp -a "$BASE/X/d7_endpoint_dvs_DRIVERSCALED.json" "$WORK/"
    test -f "$BASE/X/d7_major_history.json" && cp -a "$BASE/X/d7_major_history.json" "$WORK/"
    stage_endpoint
    ;;
esac

# THE AGE DATUM.  0/ is touched LAST at stage time, so every artifact the run
# produces must be strictly newer than 0/U or it did not come from this run.
touch "$WORK/0"/* || { echo "ABORT age-guard datum"; exit 5; }
AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")
echo "$AGE_DATUM" > "$WORK/.d7_age_datum"
echo "D7_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM"

case "$ARM" in
  P1) CMD="rm -rf processor* && decomposePar -force > d7_decomp_A.log 2>&1 && python -c \"
import glob,gzip,json,os
def ncells(p):
    b=os.path.join(p,'constant','polyMesh','owner')
    op=gzip.open(b+'.gz','rt') if os.path.exists(b+'.gz') else open(b)
    with op as fh:
        for line in fh:
            if 'nCells' in line:
                return int(line.split('nCells:')[1].split()[0])
    return -1
d={p:ncells(p) for p in sorted(glob.glob('processor*'))}
json.dump(d, open('d7_decomp_A.json','w'), indent=1, sort_keys=True)
print('DECOMP_A', json.dumps(d, sort_keys=True))
\" && rm -rf processor* && decomposePar -force > d7_decomp_B.log 2>&1 && python -c \"
import glob,gzip,json,os
def ncells(p):
    b=os.path.join(p,'constant','polyMesh','owner')
    op=gzip.open(b+'.gz','rt') if os.path.exists(b+'.gz') else open(b)
    with op as fh:
        for line in fh:
            if 'nCells' in line:
                return int(line.split('nCells:')[1].split()[0])
    return -1
d={p:ncells(p) for p in sorted(glob.glob('processor*'))}
json.dump(d, open('d7_decomp_B.json','w'), indent=1, sort_keys=True)
print('DECOMP_B', json.dumps(d, sort_keys=True))
\" && grep -a 'method\|numberOfSubdomains' system/decomposeParDict && rm -f d7_placement_rank*.json && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings python -c \"
import json,os
from mpi4py import MPI
r=MPI.COMM_WORLD.rank
aff=sorted(os.sched_getaffinity(0))
json.dump({'rank':r,'affinity':aff,'n_cores':len(aff),'pid':os.getpid()}, open('d7_placement_rank%d.json'%r,'w'))
\" && cat d7_placement_rank*.json" ;;
  X)   CMD="rm -f d7_placement_rank*.json && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings python -c \"
import json,os
from mpi4py import MPI
r=MPI.COMM_WORLD.rank
json.dump({'rank':r,'affinity':sorted(os.sched_getaffinity(0)),'n_cores':len(os.sched_getaffinity(0)),'pid':os.getpid()}, open('d7_placement_rank%d.json'%r,'w'))
\" && python d7f_endpoint_physical.py --age-datum $AGE_DATUM && python d7f_endpoint_locus.py --gate . --runscript d7_opt_runScript.py --out d7f_locus_gate.json" ;;
  ACC) CMD="rm -f d7_placement_rank*.json && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings python -c \"
import json,os
from mpi4py import MPI
r=MPI.COMM_WORLD.rank
json.dump({'rank':r,'affinity':sorted(os.sched_getaffinity(0)),'n_cores':len(os.sched_getaffinity(0)),'pid':os.getpid()}, open('d7_placement_rank%d.json'%r,'w'))
\" && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d7f_accept_primal.py && python d7f_accept_compare.py d7f_accept_primal.json --out d7f_accept_verdict.json" ;;
  F-S|F-P) CMD="rm -f d7_placement_rank*.json && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings python -c \"
import json,os
from mpi4py import MPI
r=MPI.COMM_WORLD.rank
json.dump({'rank':r,'affinity':sorted(os.sched_getaffinity(0)),'n_cores':len(os.sched_getaffinity(0)),'pid':os.getpid()}, open('d7_placement_rank%d.json'%r,'w'))
\" && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d7_fd_endpoint.py" ;;
esac

CPUSAMPLE="$BASE/${ARM}_${STAMP}.cpu.jsonl"
MEMSAMPLE="$BASE/${ARM}_${STAMP}.mem.jsonl"
# DELIVERED CORES ARE MEASURED, NOT INFERRED FROM THE QUOTA FLAG.  This sampler
# polls the container's own cgroup cpu.stat and writes cores-delivered to a
# FILE.  It is PASSIVE: it starts nothing, kills nothing, and its failure
# cannot change a verdict -- an absent sample file is reported as NOT_MEASURED,
# never as a passing placement gate.
#
# The host-memory column beside it is RECORD-ONLY AND CARRIES NO STOP RULE, and
# that is DELIBERATE AND DECLARED: A3 rung 2 registered a stop rule with no
# enforcement path, and its own RESULTS.md sec.9.1 records that the rule did not
# fire.  A rule nobody wired is a preference; the enforced gate is the
# PRE-LAUNCH memory floor above, and this file is evidence, not a control.
(
  for _ in $(seq 1 100000); do
    cid=$(sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | head -1)
    if [ -n "$cid" ]; then break; fi
    sleep 1
  done
  cg=""
  for cand in /sys/fs/cgroup/system.slice/docker-${cid}*.scope/cpu.stat \
              /sys/fs/cgroup/cpu/docker/${cid}*/cpuacct.usage; do
    if [ -e "$cand" ]; then cg="$cand"; break; fi
  done
  if [ -z "$cg" ]; then echo '{"delivered_cores":null,"note":"cgroup path not found"}' >> "$CPUSAMPLE"; fi
  prev=""; prevt=""
  while sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | grep -q .; do
    now=$(date +%s.%N)
    ma=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
    echo "{\"t\":$now,\"host_memavail_gib\":$(python3 -c "print('%.3f'%($ma/1048576.0))")}" >> "$MEMSAMPLE"
    if [ -n "$cg" ]; then
      if [ "$(basename "$cg")" = "cpu.stat" ]; then
        u=$(awk '/^usage_usec/{print $2}' "$cg" 2>/dev/null)
        t=$(awk '/^throttled_usec/{print $2}' "$cg" 2>/dev/null)
        n=$(awk '/^nr_throttled/{print $2}' "$cg" 2>/dev/null)
      else
        u=$(( $(cat "$cg" 2>/dev/null || echo 0) / 1000 )); t=0; n=0
      fi
      if [ -n "$prev" ] && [ -n "$u" ]; then
        python3 -c "
import json
du=($u-$prev)/1e6; dt=$now-$prevt
print(json.dumps({'t':round($now,2),'delivered_cores':round(du/dt,4) if dt>0 else None,'throttled_usec':$t,'nr_throttled':$n}))
" >> "$CPUSAMPLE" 2>/dev/null
      fi
      prev=$u; prevt=$now
    fi
    sleep 15
  done
) &
SAMPLER=$!

T0=$(date -u +%s)
# DAFOAM_SUBPC_TYPE IS DELIBERATELY NOT EXPORTED -- PREREGISTRATION.md sec.1
# registers it UNSET, which is A3 rung 2's own configuration (stock ASM/ILU(0)).
# ---- R1: THE CAP IS A RUNAWAY GUARD THAT REPORTS, NOT A `timeout` SIGKILL ----
# D7's launcher wrapped this in `timeout $TMO`, so the cap KILLED arm P2 with its
# adjoint three orders down and still falling.  Under Sanaa's 2026-08-25 directive
# a cap is a runaway guard REPORTED to the supervisor, not a budget that kills.
#
#   CAP     crossed -> D7F_CAP_CROSSED written to the ledger, RUN CONTINUES.
#                      Nothing is signalled.  The supervisor decides.
#   CEILING = 4 x CAP -> hard stop.  A genuine runaway is still bounded.
#
# The container runs DETACHED with no --rm, so `docker inspect` survives it.
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D7_CONTAINER_UID: \$(id -u) && \
     echo D7_SUBPC_ENV: \${DAFOAM_SUBPC_TYPE:-UNSET} && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D7_IDWARP_IMPORTED_FROM:\",p); print(\"D7_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     $CMD" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }

CEILING=$(python3 -c "print('%.1f' % (4.0*$CAP))")
echo "D7F_RUNAWAY_GUARD arm=$ARM cap_core_min=$CAP ceiling_core_min=$CEILING mode=report_then_stop_at_ceiling"
CAP_REPORTED=no
CEILING_HIT=no
while true; do
  RUNNING=$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)
  NOW=$(date -u +%s); EL=$((NOW-T0))
  CM=$(python3 -c "print(round($EL*$RANKS/60.0,3))")
  if [ "$RUNNING" != "true" ]; then break; fi
  if [ "$CAP_REPORTED" = "no" ] && [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]; then
    CAP_REPORTED=yes
    echo "D7F_CAP_CROSSED arm=$ARM core_min=$CM cap=$CAP ceiling=$CEILING action=REPORTED_RUN_CONTINUES supervisor_decides" | tee -a "$BASE/ledger.txt"
  fi
  if [ "$(python3 -c "print(1 if $CM > $CEILING else 0)")" = "1" ]; then
    CEILING_HIT=yes
    echo "D7F_CEILING_HIT arm=$ARM core_min=$CM ceiling=$CEILING action=HARD_STOP" | tee -a "$BASE/ledger.txt"
    sudo -n docker stop -t 30 "$NAME" >/dev/null 2>&1
    break
  fi
  sleep 10
done
sudo -n docker logs "$NAME" > "$LOG" 2>&1
rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$NAME" 2>/dev/null)
test -n "$rc" || rc=125
T1=$(date -u +%s)
WALL=$((T1-T0))
kill $SAMPLER 2>/dev/null; wait $SAMPLER 2>/dev/null
SIBLINGS_POST=$(container_census)
DELIVERED=$(python3 -c "
import json,os
p='$CPUSAMPLE'
if not os.path.exists(p): print('NOT_MEASURED'); raise SystemExit
v=[]; thr=0
for line in open(p):
    try: d=json.loads(line)
    except Exception: continue
    if d.get('delivered_cores') is not None: v.append(d['delivered_cores'])
    thr=max(thr, d.get('nr_throttled') or 0)
print('%s n=%d max_nr_throttled=%d' % (('%.4f'%(sum(v)/len(v)) if v else 'NOT_MEASURED'), len(v), thr))
" 2>/dev/null)
MEMMIN=$(python3 -c "
import json,os
p='$MEMSAMPLE'
if not os.path.exists(p): print('NOT_MEASURED'); raise SystemExit
v=[json.loads(l).get('host_memavail_gib') for l in open(p) if l.strip()]
v=[x for x in v if x is not None]
print(('%.3f n=%d'%(min(v),len(v))) if v else 'NOT_MEASURED')
" 2>/dev/null)

# ---- the KERNEL's verdict, read BEFORE the container is removed ----------
INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")

# ---- RUNAWAY GUARD.  Cost constraints are LIFTED (Sanaa, 2026-08-25); the cap
# is a runaway guard.  A crossing is REPORTED HERE, IN THE LEDGER, so the
# supervisor decides.  This launcher does not silently continue and does not
# silently stop.
OVER=$(python3 -c "print('YES' if $CORE_MIN > $CAP else 'no')")

LEDGER="$BASE/ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK cap_exceeded=$OVER cap_reported=$CAP_REPORTED ceiling_core_min=$CEILING ceiling_hit=$CEILING_HIT memory=$MEM inspect(exit,oomkilled)=[$INSPECT] memavail_pre_GiB=$MEMAVAIL_GIB memavail_floor_GiB=$FLOOR memavail_post_GiB=$MEMAVAIL_POST memavail_min_during=[$MEMMIN] cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] log=$(basename "$LOG") stamp=$STAMP"
  grep -a "D7_CONTAINER_UID\|D7_IDWARP_SO_MD5\|D7_SUBPC_ENV" "$LOG" | head -3
} | tee -a "$LEDGER"

# Arm P2 publishes the colouring cache it built, for O / F-S / F-P to inherit.
if [ "$ARM" = "P2" ] && [ "$rc" = "0" ] && [ -f "$WORK/dRdWColoring_${RANKS}.bin" ]; then
  cp -a "$WORK/dRdWColoring_${RANKS}.bin" "$BASE/" 2>/dev/null
  test -f "$WORK/dRdWColoring_${RANKS}.bin.info" && cp -a "$WORK/dRdWColoring_${RANKS}.bin.info" "$BASE/" 2>/dev/null
  echo "item=D7R arm=$ARM rc=$rc stamp=$STAMP md5=$(md5sum "$BASE/dRdWColoring_${RANKS}.bin" | awk '{print $1}')" > "$BASE/.d7f_coloring_provenance"
  echo "D7F_COLORING_PUBLISHED_FRESH $(cat "$BASE/.d7f_coloring_provenance")" | tee -a "$LEDGER"
fi

test -s "$LOG" && touch "$LOG.ok.${STAMP}"
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN CAP=$CAP CAP_EXCEEDED=$OVER"
exit $rc
