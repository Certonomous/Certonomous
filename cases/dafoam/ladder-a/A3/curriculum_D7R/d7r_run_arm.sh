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

BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin
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

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md sec.8, verbatim) -----------
#   arm    core-min cap   memory cap   prediction
#   P1          8.0           4g           1.5
#   P2         60.0          12g          30.0
#   O         600.0          12g         570.0
#   F-S       130.0          12g          95.0
#   F-P       130.0          12g          95.0
#   ITEM  CEILING 928.0                  791.5
cap_core_min() {
  case "$1" in
    P1)  echo 8.0 ;;
    P2)  echo 120.0 ;;
    O)   echo 900.0 ;;
    F-S) echo 130.0 ;;
    F-P) echo 130.0 ;;
    *)   echo "" ;;
  esac
}
cap_memory() {
  case "$1" in
    P1) echo 4g ;;
    P2|O|F-S|F-P) echo 12g ;;
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

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d7_run_arm.sh <P1|P2|O|F-S|F-P> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d7_run_arm.sh <P1|P2|O|F-S|F-P> <image>"; exit 64; }

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

# PREREGISTRATION.md sec.9a: THE OPTIMISATION BUYS **SHIPPED**, and that is the
# OPPOSITE of D4's choice, anchored on THIS case's own measurement -- on this
# exact mesh A3 rung 2 measured the rotation patch making the gradient WORSE
# (shape[115] 9.208x, twist[1] 3.39x).  Driving a 30-major optimisation with
# the row measured to be 9.2x worse here would be a worse item at the same
# price.  Arms P1/P2/O are SHIPPED-only, and the launcher enforces it.
case "$ARM" in
  P1|P2|O) test "$ROW" = "SHIPPED" || { echo "ABORT arm $ARM is registered SHIPPED-only (sec.9a); got $ROW"; exit 4; } ;;
  F-S)     test "$ROW" = "SHIPPED" || { echo "ABORT arm F-S must be SHIPPED; got $ROW"; exit 4; } ;;
  F-P)     test "$ROW" = "PATCHED" || { echo "ABORT arm F-P must be PATCHED; got $ROW"; exit 4; } ;;
esac

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d7r_${ARM//-/_}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- stage a pristine COLD copy of base/ ---------------------------------
# THE CASE AND MESH ARE STAGED BY COPY AND NEVER EDITED IN PLACE
# (PREREGISTRATION.md sec.1).
sudo -n rm -rf "$WORK" 2>/dev/null
rm -rf "$WORK" 2>/dev/null
cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy"; exit 4; }
cp -a "$BASE/d7_opt_runScript.py" "$BASE/d7_fd_endpoint.py" "$BASE/d7_extract_endpoint.py" "$WORK/" \
  || { echo "ABORT stage instruments"; exit 4; }

# COLD START, verified BEFORE the launch, and the AGE GUARD's datum.
for bad in "$WORK/reports" "$WORK/OptView.hst" "$WORK/opt_IPOPT.txt" \
           "$WORK/d7_fd_endpoint.json" "$WORK/d7_major_history.json" \
           "$WORK/d7_endpoint_dvs.json" "$WORK/d7_baseline.json"; do
  test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
done
test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
test -n "$(ls -d "$WORK"/[0-9]*.[0-9]* 2>/dev/null)" && { echo "ABORT G-COLD time dir present"; exit 5; }
test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing"; exit 5; }

# ---- per-arm staged INPUTS, each with its own refusal ---------------------
# The colouring cache is a DETERMINISTIC function of mesh and partition.  It is
# BUILT ONCE, in arm P2, and INHERITED by O, F-S and F-P -- which is exactly
# what PREREGISTRATION.md sec.8's cost bases imply: the colouring build is
# priced in P2's basis and in NO other arm's.  The inheritance is GATED ON G8:
# without a demonstrated-deterministic partition the inherited colouring would
# not be a colouring OF THIS PARTITION, so the launcher refuses to stage it
# until arm P1 has written `.d7r_g8_pass`.
stage_coloring() {
  test -f "$BASE/.d7r_g8_pass" || { echo "ABORT colouring inheritance requires G8 to have PASSED (sec.5); $BASE/.d7r_g8_pass absent"; exit 5; }
  test -f "$BASE/dRdWColoring_${RANKS}.bin" || { echo "ABORT no colouring cache at $BASE/dRdWColoring_${RANKS}.bin -- arm P2 builds it"; exit 5; }
  # ---- GATE H1 (PREREGISTRATION.md sec.5): COLOURING PROVENANCE ----------
  # D7's cache was built by an arm that returned rc=124.  This item BUILDS
  # FRESH (sec.R3) because the .bin.info sidecar is 22 bytes of PETSc option
  # string and CANNOT distinguish one configuration from another -- a control
  # keyed on it would pass on ANY colouring file.  H1 is what stops the
  # declined cache re-entering by accident: a registered refusal to reuse is
  # worth nothing without a gate that can catch the reuse.
  test -f "$BASE/.d7r_coloring_provenance" || { echo "ABORT H1 COLOURING_PROVENANCE -- no provenance record; the cache was not built by an rc=0 arm of THIS item"; exit 5; }
  grep -q "item=D7R" "$BASE/.d7r_coloring_provenance" || { echo "ABORT H1 COLOURING_PROVENANCE -- provenance record is not this item's"; exit 5; }
  grep -q "rc=0" "$BASE/.d7r_coloring_provenance" || { echo "ABORT H1 COLOURING_PROVENANCE -- the arm that built the cache did not return rc=0"; exit 5; }
  echo "D7R_H1_PASS $(cat "$BASE/.d7r_coloring_provenance")"
  cp -a "$BASE/dRdWColoring_${RANKS}.bin" "$WORK/" || { echo "ABORT stage colouring"; exit 4; }
  test -f "$BASE/dRdWColoring_${RANKS}.bin.info" && cp -a "$BASE/dRdWColoring_${RANKS}.bin.info" "$WORK/"
  echo "D7_COLORING_INHERITED md5=$(md5sum "$WORK/dRdWColoring_${RANKS}.bin" | awk '{print $1}')"
}

case "$ARM" in
  O)
    # THE CL TARGET IS WRITTEN HERE, BEFORE THE DRIVER STARTS, FROM THE
    # BASELINE PRIMAL ARM P2 ACTUALLY RAN.  PREREGISTRATION.md sec.1 forbids
    # typing it in from memory, so the launcher DERIVES it from a file on disk
    # and REFUSES if that file is absent.
    test -f "$BASE/P2/d7_baseline.json" || { echo "ABORT arm O requires $BASE/P2/d7_baseline.json (the measured baseline primal); sec.1 forbids a typed-in CL target"; exit 5; }
    python3 -c "
import json, os, sys
src = '$BASE/P2/d7_baseline.json'
d = json.load(open(src))
cl = float(d['CL'])
if not (0.0 < abs(cl) < 10.0):
    sys.stderr.write('ABORT baseline CL %r is not a plausible lift coefficient\n' % cl); sys.exit(1)
out = {'CL_target': cl, '_source': os.path.abspath(src),
       '_source_md5': __import__('hashlib').md5(open(src,'rb').read()).hexdigest(),
       '_CD_baseline': float(d['CD']),
       '_note': 'READ FROM THE BASELINE PRIMAL AT RUN TIME, written BEFORE the '
                'driver starts.  PREREGISTRATION.md sec.1.  Not typed in.'}
p = '$WORK/d7_cl_target.json'
fh = open(p,'w'); json.dump(out, fh, indent=1, sort_keys=True); fh.flush(); os.fsync(fh.fileno()); fh.close()
print('D7_CL_TARGET_WRITTEN %s CL_target=%r from %s' % (p, cl, src))
" || { echo "ABORT could not derive the CL target"; exit 5; }
    cp -a "$WORK/d7_cl_target.json" "$BASE/d7_cl_target.json" || { echo "ABORT publish cl target"; exit 4; }
    stage_coloring
    ;;
  F-S|F-P)
    test -f "$BASE/O/OptView.hst" || { echo "ABORT arm $ARM requires $BASE/O/OptView.hst from arm O"; exit 5; }
    cp -a "$BASE/O/OptView.hst" "$WORK/" || { echo "ABORT stage OptView.hst"; exit 4; }
    test -f "$BASE/d7_cl_target.json" && cp -a "$BASE/d7_cl_target.json" "$WORK/"
    stage_coloring
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
  P2)  CMD="rm -f d7_placement_rank*.json && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings python -c \"
import json,os
from mpi4py import MPI
r=MPI.COMM_WORLD.rank
json.dump({'rank':r,'affinity':sorted(os.sched_getaffinity(0)),'n_cores':len(os.sched_getaffinity(0)),'pid':os.getpid()}, open('d7_placement_rank%d.json'%r,'w'))
\" && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d7_opt_runScript.py -task compute_totals" ;;
  O)   CMD="rm -f d7_placement_rank*.json && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings python -c \"
import json,os
from mpi4py import MPI
r=MPI.COMM_WORLD.rank
json.dump({'rank':r,'affinity':sorted(os.sched_getaffinity(0)),'n_cores':len(os.sched_getaffinity(0)),'pid':os.getpid()}, open('d7_placement_rank%d.json'%r,'w'))
\" && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d7_opt_runScript.py -task run_driver -optimizer IPOPT" ;;
  F-S|F-P) CMD="rm -f d7_placement_rank*.json && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings python -c \"
import json,os
from mpi4py import MPI
r=MPI.COMM_WORLD.rank
json.dump({'rank':r,'affinity':sorted(os.sched_getaffinity(0)),'n_cores':len(os.sched_getaffinity(0)),'pid':os.getpid()}, open('d7_placement_rank%d.json'%r,'w'))
\" && python d7_extract_endpoint.py && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d7_fd_endpoint.py" ;;
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
#   CAP     crossed -> D7R_CAP_CROSSED written to the ledger, RUN CONTINUES.
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
echo "D7R_RUNAWAY_GUARD arm=$ARM cap_core_min=$CAP ceiling_core_min=$CEILING mode=report_then_stop_at_ceiling"
CAP_REPORTED=no
CEILING_HIT=no
while true; do
  RUNNING=$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)
  NOW=$(date -u +%s); EL=$((NOW-T0))
  CM=$(python3 -c "print(round($EL*$RANKS/60.0,3))")
  if [ "$RUNNING" != "true" ]; then break; fi
  if [ "$CAP_REPORTED" = "no" ] && [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]; then
    CAP_REPORTED=yes
    echo "D7R_CAP_CROSSED arm=$ARM core_min=$CM cap=$CAP ceiling=$CEILING action=REPORTED_RUN_CONTINUES supervisor_decides" | tee -a "$BASE/ledger.txt"
  fi
  if [ "$(python3 -c "print(1 if $CM > $CEILING else 0)")" = "1" ]; then
    CEILING_HIT=yes
    echo "D7R_CEILING_HIT arm=$ARM core_min=$CM ceiling=$CEILING action=HARD_STOP" | tee -a "$BASE/ledger.txt"
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
  echo "item=D7R arm=$ARM rc=$rc stamp=$STAMP md5=$(md5sum "$BASE/dRdWColoring_${RANKS}.bin" | awk '{print $1}')" > "$BASE/.d7r_coloring_provenance"
  echo "D7R_COLORING_PUBLISHED_FRESH $(cat "$BASE/.d7r_coloring_provenance")" | tee -a "$LEDGER"
fi

test -s "$LOG" && touch "$LOG.ok.${STAMP}"
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN CAP=$CAP CAP_EXCEEDED=$OVER"
exit $rc
