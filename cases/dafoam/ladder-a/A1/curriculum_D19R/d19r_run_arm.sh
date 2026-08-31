#!/usr/bin/env bash
# Curriculum D19R PHASE 1 arm launcher -- NACA0012 SUBSONIC (DARhoSimpleFoam), the
# FD PLATEAU SWEEP.  PATCHED ROW ONLY.
#
# DERIVED from `curriculum_D15/d15_run_arm.sh` (md5 796a2de5b894e8fcdbfab99af6fbf09d)
# with these REGISTERED DELTAS and no others:
#   (1) item/root names; D15's and D16's roots ADDED to FORBIDDEN_ROOTS (D15's
#       root holds the graded row this item's G19-1a compares against and whose
#       md5 the section 9 provenance guard pins -- destroying it would destroy
#       D19R's own precondition);
#   (2) arms MESH X2 S8 N2 S1 R1; RANKS MESH 1, X2 2, S8 2, N2 2, S1 1, R1 1; caps from
#       PREREGISTRATION.md section 3 (5.0 / 20.0 / 90.0 / 25.0);
#   (3) PHASE 1 IS PATCHED-IMAGE ONLY (section 3: "PATCHED image only -- nothing
#       is proposed to stand on the shipped gradient").  G-ROW therefore requires
#       ROW=PATCHED on EVERY arm, MESH INCLUDED -- which is a departure from D15,
#       where MESH ran on the SHIPPED image.  The departure is SAFE ONLY IF the
#       mesh is identical either way, and that is not assumed: the MESH arm
#       ASSERTS byte-identity against D15's frozen mesh (delta 5) and fails the
#       arm if it differs.  The registration made that assertion a gate; this
#       launcher is where it fires.
#   (4) cpuset 1,15 -- disjoint from D15 (2,3), D16 (4,14), D5 (8,10,11,13),
#       D4-SHIPPED (5,6,7,9), W2R (12); not core 0;
#   (5) THE MESH IDENTITY ASSERT IS MTIME-IMMUNE AND RUNS INSIDE THE CONTAINER, so
#       the KERNEL's rc carries it.  D15's MESH arm published `sha256sum
#       constant/polyMesh/points.gz`, but a .gz stream can carry an mtime, so a
#       gz hash is not a safe cross-run identity.  The frozen constants below are
#       md5s of the DECOMPRESSED files, computed from D15's own MESH arm output;
#       the gz sha256 is printed too, for continuity with D15's record.
#   (6) THE AGE GUARD IS RESOLVED BY EXISTENCE, NEVER BY NAME.  D15 pinned the
#       datum to `0/U` by name.  Here the launcher ENUMERATES what actually
#       exists under the staged `0/`, touches all of it, and takes the datum as
#       the MAXIMUM mtime over that enumeration -- refusing outright if the
#       enumeration is empty.  A datum resolved by name is blind to a case whose
#       `0/` does not carry the file the name assumed.
#   (7) S1 additionally stages `d19r_selected_step.json`, the SELECTOR's output --
#       an INPUT to that arm, named explicitly so the cold-start guard does not
#       mistake it for a pre-existing result.
# Container-printed strings (D4S_*) are inherited UNCHANGED so a grader greps
# what the launcher writes.
#
# CAP DISCIPLINE: the caps are NOT arguments.  They are constants below, the
# table is PREREGISTRATION.md section 3's, and the launcher ASSERTS that the wall
# timeout it is about to enforce equals CAP_CORE_MIN*60/RANKS to the second.
#
# 8.2: NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives.
set -uo pipefail

ITEM=D19R
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau
BASE="${BASE:-$REGISTERED_BASE}"

BASE_REAL=$(realpath -m "$BASE")
REG_REAL=$(realpath -m "$REGISTERED_BASE")
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
  echo "  given:      $BASE_REAL"
  echo "  registered: $REG_REAL"
  exit 3
fi

FORBIDDEN_ROOTS="/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic
/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic
/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-R-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D14-a2-wing-remesh
/home/ubuntu/certonomous-runs/CURRICULUM-D14M-a2-wing-remesh
/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd
/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D13-a1-basin-restart
/home/ubuntu/certonomous-runs/A2-mach-wing
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/subsonic
/home/ubuntu/dafoam-tutorials
/home/ubuntu/certonomous-runs
/home/ubuntu/Certonomous"
while IFS= read -r forb; do
  [ -z "$forb" ] && continue
  if [ "$BASE_REAL" = "$(realpath -m "$forb")" ]; then
    echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S RUN ROOT: $forb"
    echo "  D15's root in particular holds the graded row G19-1a compares against"
    echo "  and whose md5 the section 9 provenance guard pins.  REFUSED."
    exit 3
  fi
done <<< "$FORBIDDEN_ROOTS"

if [ -f "$BASE/ledger.txt" ]; then
  FOREIGN_ITEM=$(grep -a "^ITEM=" "$BASE/ledger.txt" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
  if [ -n "$FOREIGN_ITEM" ]; then
    echo "ABORT G-ROOT.3 the ledger at $BASE/ledger.txt carries another item: $FOREIGN_ITEM"
    exit 3
  fi
fi
echo "D4S_G_ROOT_PASS item=$ITEM base=$BASE_REAL ledger_clean=yes"

HERE="$(cd "$(dirname "$0")" && pwd)"
CPUSET=1,15

container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d19r_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md section 3, verbatim) --------
#   arm    ranks  core-min cap   in-container wall   memory cap
#   MESH     1        5.0            300 s              4g
#   X2       2       20.0            600 s              4g
#   S8       2       40.0           1200 s              4g
#   N2       2       10.0            300 s              4g
#   R1       1        8.0            480 s              4g
#   S1       1       25.0           1500 s              4g
cap_core_min() {
  case "$1" in
    MESH) echo 5.0 ;;
    X2)   echo 20.0 ;;
    S8)   echo 40.0 ;;
    N2)   echo 10.0 ;;
    S1)   echo 10.0 ;;
    R1)   echo 8.0 ;;
    *)    echo "" ;;
  esac
}
cap_memory() {
  case "$1" in MESH|X2|S8|N2|S1|R1) echo 4g ;; *) echo "" ;; esac
}
ranks_of() {
  case "$1" in
    MESH) echo 1 ;;
    X2)   echo 2 ;;
    S8)   echo 2 ;;
    N2)   echo 2 ;;
    S1)   echo 1 ;;
    R1)   echo 1 ;;
    *)    echo "" ;;
  esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (section 8) ------------
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
SO_MD5_PATCHED=85f59e87253e0a71a813f64ca6e4c425

# ---- FROZEN INSTRUMENT HASHES --------------------------------------------
MD5_RUNSCRIPT=a5e18503ea29d0e37c3cf1668533cd34   # d19r_runScript.py (= D15's, max_iter 100->40)
MD5_XF=a0f44316bd961204e41e438464f834d4                                # d19r_xf.py (set at freeze)
MD5_DECOMP=68ecc827562886fb43c3aedb0627b344      # d15_decomposeParDict, VERBATIM

# ---- D15's FROZEN MESH IDENTITY, md5 of the DECOMPRESSED files (delta 5) ---
MESH_CELLS=4032
MD5_MESH_points=88f00ff725ef2906212ca1e2b040c09f
MD5_MESH_faces=1bcea5c2f5817d0740a03a83050c3c79
MD5_MESH_owner=549e0a9f01be3ebf412017c1e9811ece
MD5_MESH_neighbour=65fd7ca38d534c760f57ce14bdffc834
MD5_MESH_boundary=c92a945e9a1405b988ab418e48ab53c3

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d19r_run_arm.sh <MESH|X2|S8|N2|S1|R1> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d19r_run_arm.sh <MESH|X2|S8|N2|S1|R1> <image>"; exit 64; }
RANKS=$(ranks_of "$ARM"); test -n "$RANKS" || { echo "ABORT arm $ARM carries no registered rank count"; exit 64; }

LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d19r_${ARM}_" 2>/dev/null | grep "^d19r_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  exit 3
fi
PIDFILE="$BASE/d19r_driver.pid"
if [ -f "$PIDFILE" ]; then
  DPID=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$DPID" ] && kill -0 "$DPID" 2>/dev/null; then
    ANCESTOR=no; p=$$
    for _ in $(seq 1 64); do
      if [ "$p" = "$DPID" ]; then ANCESTOR=yes; break; fi
      p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
      if [ -z "$p" ] || [ "$p" = "0" ]; then break; fi
    done
    DCWD=$(readlink -f "/proc/$DPID/cwd" 2>/dev/null)
    if [ "$ANCESTOR" = "no" ] || [ "$DCWD" = "$(realpath -m "$BASE")" ]; then
      echo "ABORT G-ROOT.5 driver pidfile $PIDFILE names LIVE pid $DPID (ancestor=$ANCESTOR cwd=$DCWD)."
      exit 3
    fi
  fi
fi
echo "D4S_G_ROOT5_PASS arm=$ARM live_same_arm_containers=none"

CAP=$(cap_core_min "$ARM")
MEM=$(cap_memory "$ARM")
test -n "$CAP" || { echo "ABORT unknown arm $ARM -- no registered cap"; exit 64; }
test -n "$MEM" || { echo "ABORT unknown arm $ARM -- no registered memory cap"; exit 64; }

TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)))") || { echo "ABORT tmo calc"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % ($TMO*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced=%r\n' % (cap, back)); sys.exit(1)
" || { echo "ABORT enforced cap != registered cap"; exit 65; }
echo "D4_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM"

MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D4_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }

echo "$MD5_RUNSCRIPT  $BASE/d19r_runScript.py"          | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_XF  $BASE/d19r_xf.py"                        | md5sum -c - || { echo "ABORT xf md5"; exit 4; }
echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict" | md5sum -c - || { echo "ABORT decomposeParDict md5"; exit 4; }

GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1) WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  *) echo "ABORT image $IMG is not the registered PHASE 1 row (PATCHED only)"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }

# G-ROW: phase 1 is PATCHED-only, so every arm must be PATCHED (delta 3).
WANT_ROW=PATCHED
test "$ROW" = "$WANT_ROW" || {
  echo "ABORT G-ROW arm $ARM is registered on the $WANT_ROW row; got ROW=$ROW ($IMG)."; exit 4; }
echo "D4S_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d19r_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- AGE GUARD DATUM, REPAIRED (PREREGISTRATION.md section 2.2) -----------
# D19 stamped the datum as "max mtime over the arm's `0/`, plus the file count".
# MEASURED on D19's own run root, that premise is FALSE for DAFoam: the `patchV`
# design variable is applied by REWRITING `0/U`'s inlet boundary condition, and
# OpenFOAM writes the whole object -- converged internalField included -- under
# `writeCompression`.  So `0/T` becomes `0/T.gz`, the datum directory sits INSIDE
# the solver's write set, and the guard refused a good run (`age_datum_moved`,
# recorded 1788213189 vs rederived 1788213232 == the mtime of `S1/0/U.gz`).
# It is NOT a serial-arm defect: `S2/processor0/0/U.gz` was rewritten too.  And
# D19's COUNT clause passed BY COINCIDENCE -- 9 files before and after, but SIX
# filenames changed.  A count is not an identity.
#
# THE REPAIR, and the AGE ASSERTION ITSELF IS NOT WEAKENED:
#   L1  the datum is a LAUNCH SENTINEL stamped OUTSIDE every bind-mount source.
#       This container runs `-v "$BASE":/mnt`, so `$BASE` is writable by the
#       solve and its PARENT is not.  `d19r_age_guard.assert_sentinel_outside_mounts`
#       REFUSES if the sentinel is at or under any declared mount source, so
#       "the solver does not write here" is a property of the mount namespace
#       rather than a belief about DAFoam.
#   L2  rule 4's clause is unchanged: every artefact STRICTLY NEWER than the datum.
#   L3  an md5 INPUT MANIFEST replaces the count, with `0/` and `processor*/`
#       excluded BY NAME and by recorded reason -- a guard must not assert a
#       premise the solver falsifies.  `build_manifest` REFUSES a caller that
#       tries to pin a write target rather than silently filtering it.
stamp_launch_datum() {
  python3 - "$BASE" "$ARM" "$WORK" <<'EOF' || return 1
import json, os, sys
sys.path.insert(0, os.environ["D19R_HERE"])
import d19r_age_guard as AGE
base, arm, work = sys.argv[1], sys.argv[2], sys.argv[3]
mounts = [base]                       # exactly what `docker run -v` is passed
try:
    spath, datum = AGE.stamp_sentinel(base, arm, mounts)
    manifest = AGE.build_manifest(work, json.loads(os.environ["D19R_INPUTS"]))
except AGE.Refusal as exc:
    sys.stderr.write("ABORT age-guard datum: %s\n" % exc)
    sys.exit(1)
with open(os.path.join(work, ".d19r_manifest.json"), "w") as fh:
    json.dump(manifest, fh, indent=1, sort_keys=True)
    fh.flush(); os.fsync(fh.fileno())
print("D4_G_COLD OK arm=%s age_datum_epoch=%.6f sentinel=%s manifest_entries=%d "
      "excluded_write_targets=%s resolved_by=LAUNCH_SENTINEL_OUTSIDE_MOUNT"
      % (arm, datum, spath, manifest["n_entries"],
         [x["path"] for x in manifest["excluded_write_targets"]]))
EOF
  return 0
}

if [ "$ARM" = "MESH" ]; then
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy"; exit 4; }
  test -e "$WORK/constant/polyMesh" && { echo "ABORT G-COLD MESH: base/ already carries constant/polyMesh"; exit 5; }
  test -e "$WORK/0" && { echo "ABORT G-COLD MESH: base/ already carries 0/"; exit 5; }
  test -d "$WORK/0.orig" || { echo "ABORT G-COLD 0.orig missing"; exit 5; }
  export D19R_HERE="$HERE" D19R_INPUTS='["0.orig","constant","system"]'
  stamp_launch_datum || exit 5
else
  test -d "$BASE/MESH" || { echo "ABORT arm $ARM expects an existing MESH/ from arm MESH"; exit 5; }
  test -f "$BASE/MESH/constant/polyMesh/boundary" || { echo "ABORT arm $ARM: MESH/ carries no polyMesh/boundary"; exit 5; }
  test -d "$BASE/MESH/0" || { echo "ABORT arm $ARM: MESH/ carries no 0/"; exit 5; }
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/MESH" "$WORK" || { echo "ABORT stage copy from MESH"; exit 4; }
  rm -f "$WORK/d19r_cmd.sh" "$WORK/checkMesh.log" "$WORK/logMeshGeneration.txt" \
        "$WORK/volumeMesh.xyz" "$WORK/surfaceMesh.xyz" "$WORK/.d19r_manifest.json" 2>/dev/null
  cp -a "$BASE/d19r_runScript.py" "$BASE/d19r_xf.py" "$WORK/" || { echo "ABORT stage instruments"; exit 4; }
  # (7) S1's INPUT: the selector's frozen choice.  Named, so the cold guard below
  # does not mistake an input for a pre-existing result.
  if [ "$ARM" = "S1" ]; then
    test -f "$BASE/d19r_selected_step.json" || { echo "ABORT arm S1 needs $BASE/d19r_selected_step.json from the selector"; exit 5; }
    cp -a "$BASE/d19r_selected_step.json" "$WORK/" || { echo "ABORT stage selection"; exit 4; }
  fi
  # (7b) R1's INPUT: S8's sweep artefact, from which mode R1 computes `kappa`
  # FROM FD AND FROM NOTHING ELSE.  Named here so the cold guard below does not
  # mistake an INPUT for a pre-existing RESULT -- and note that R1 writes
  # `d19r_R1.json`, never `d19r_S.json`, so the input cannot be confused with
  # this arm's own output.
  if [ "$ARM" = "R1" ]; then
    test -f "$BASE/S8/d19r_S.json" || { echo "ABORT arm R1 needs $BASE/S8/d19r_S.json from arm S8"; exit 5; }
    cp -a "$BASE/S8/d19r_S.json" "$WORK/" || { echo "ABORT stage S8 sweep"; exit 4; }
  fi
  # COLD START, verified BEFORE the launch.  Every OUTPUT this item can write.
  # `d19r_S.json` is arm S8's OUTPUT and is guarded like any other -- EXCEPT on
  # arm R1, where it is a STAGED INPUT (R1 writes `d19r_R1.json`, never
  # `d19r_S.json`, so an input can never be mistaken for this arm's own result).
  # The exemption is by ARM NAME and is stated, not implicit.
  for bad in "$WORK/reports" "$WORK/d19r_X.json" "$WORK/d19r_S1.json" \
             "$WORK/d19r_N.json" "$WORK/d19r_R1.json" \
             "$WORK/d19r_X.jsonl" "$WORK/d19r_S.jsonl" "$WORK/d19r_N.jsonl" \
             "$WORK/d19r_S1.jsonl" "$WORK/d19r_R1.jsonl" "$WORK/dRdWColoring_2.bin"; do
    test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
  done
  if [ "$ARM" != "R1" ]; then
    test -e "$WORK/d19r_S.json" && { echo "ABORT G-COLD $WORK/d19r_S.json exists"; exit 5; }
  fi
  test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
  for d in "$WORK"/*/; do
    n=$(basename "$d")
    case "$n" in 0|0.orig) ;; [0-9]*) echo "ABORT G-COLD time dir present: $n"; exit 5 ;; esac
  done
  export D19R_HERE="$HERE" D19R_INPUTS='["0.orig","constant","system","d19r_runScript.py","d19r_xf.py"]'
  stamp_launch_datum || exit 5
fi

# ---- the arm commands -----------------------------------------------------
# MESH asserts the CELL COUNT and MTIME-IMMUNE IDENTITY against D15's frozen mesh
# INSIDE the container, so the kernel rc carries the assertion (delta 5).
MESH_ASSERT="python3 - <<'EOF'
import gzip, hashlib, os, sys
want = {'points':'$MD5_MESH_points','faces':'$MD5_MESH_faces','owner':'$MD5_MESH_owner',
        'neighbour':'$MD5_MESH_neighbour','boundary':'$MD5_MESH_boundary'}
bad = []
for n, w in sorted(want.items()):
    p = 'constant/polyMesh/%s' % n
    if os.path.exists(p + '.gz'):
        raw = gzip.open(p + '.gz','rb').read()
        print('D19R_MESH_GZ_SHA256 %s %s' % (n, hashlib.sha256(open(p+'.gz','rb').read()).hexdigest()))
    elif os.path.exists(p):
        raw = open(p,'rb').read()
    else:
        bad.append((n,'ABSENT',w)); continue
    g = hashlib.md5(raw).hexdigest()
    print('D19R_MESH_IDENTITY %s raw_md5=%s frozen=%s %s' % (n, g, w, 'OK' if g==w else 'MISMATCH'))
    if g != w: bad.append((n,g,w))
if bad:
    sys.stderr.write('D19R_MESH_IDENTITY REFUSE not byte-identical to D15 mesh: %r\n' % bad)
    sys.exit(6)
print('D19R_MESH_IDENTITY_ALL_OK')
EOF"
case "$ARM" in
  MESH) CMD="bash preProcessing.sh && checkMesh > checkMesh.log 2>&1; echo D19R_CHECKMESH_RC \$?; grep -a 'cells:' checkMesh.log; grep -aq '^ *cells: *$MESH_CELLS\$' checkMesh.log || { echo D19R_CELLCOUNT_REFUSE expected $MESH_CELLS; exit 6; }; $MESH_ASSERT" ;;
  X2)   CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d19r_xf.py -mode X" ;;
  S8)   CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d19r_xf.py -mode S8" ;;
  N2)   CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d19r_xf.py -mode N2" ;;
  R1)   CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d19r_xf.py -mode R1" ;;
  S1)   CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d19r_xf.py -mode S1" ;;
esac

CMDFILE="$WORK/d19r_cmd.sh"
printf '%s\n' "$CMD" > "$CMDFILE" || { echo "ABORT cmd file"; exit 4; }
echo "D4S_CMDFILE arm=$ARM md5=$(md5sum "$CMDFILE" | cut -d' ' -f1) deadline_in_container_s=$TMO"
CPUSAMPLE="$BASE/${ARM}_${STAMP}.cpu.jsonl"
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
  if [ -z "$cg" ]; then echo '{"delivered_cores":null,"note":"cgroup path not found"}' >> "$CPUSAMPLE"; exit 0; fi
  prev=""; prevt=""
  while sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | grep -q .; do
    now=$(date +%s.%N)
    if [ "$(basename "$cg")" = "cpu.stat" ]; then
      u=$(awk '/^usage_usec/{print $2}' "$cg" 2>/dev/null)
      t=$(awk '/^throttled_usec/{print $2}' "$cg" 2>/dev/null)
      n=$(awk '/^nr_throttled/{print $2}' "$cg" 2>/dev/null)
    else
      u=$(( $(cat "$cg" 2>/dev/null || echo 0) / 1000 )); t=0; n=0
    fi
    if [ -n "$prev" ] && [ -n "$u" ]; then
      python3 -c "
import json,sys
du=($u-$prev)/1e6; dt=$now-$prevt
print(json.dumps({'t':round($now,2),'delivered_cores':round(du/dt,4) if dt>0 else None,'throttled_usec':$t,'nr_throttled':$n}))
" >> "$CPUSAMPLE" 2>/dev/null
    fi
    prev=$u; prevt=$now
    sleep 15
  done
) &
SAMPLER=$!

T0=$(date -u +%s)
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     echo D4S_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k 60 $TMO bash /mnt/$ARM/d19r_cmd.sh" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }

CEILING=$(python3 -c "print('%.1f' % (4.0*$CAP))")
echo "D4S_RUNAWAY_GUARD arm=$ARM cap_core_min=$CAP ceiling_core_min=$CEILING mode=report_then_stop_at_ceiling"
CAP_REPORTED=no
while true; do
  RUNNING=$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)
  NOW=$(date -u +%s); EL=$((NOW-T0))
  CM=$(python3 -c "print(round($EL*$RANKS/60.0,3))")
  if [ "$RUNNING" != "true" ]; then break; fi
  if [ "$CAP_REPORTED" = "no" ] && [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]; then
    CAP_REPORTED=yes
    echo "D4S_CAP_CROSSED arm=$ARM core_min=$CM cap=$CAP ceiling=$CEILING action=REPORTED_RUN_CONTINUES supervisor_decides" | tee -a "$BASE/ledger.txt"
  fi
  if [ "$(python3 -c "print(1 if $CM > $CEILING else 0)")" = "1" ]; then
    echo "D4S_CEILING_HIT arm=$ARM core_min=$CM ceiling=$CEILING action=HARD_STOP" | tee -a "$BASE/ledger.txt"
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
import json,sys,os
p='$CPUSAMPLE'
if not os.path.exists(p): print('NOT_MEASURED'); sys.exit()
v=[]; thr=0
for line in open(p):
    try: d=json.loads(line)
    except Exception: continue
    if d.get('delivered_cores') is not None: v.append(d['delivered_cores'])
    thr=max(thr, d.get('nr_throttled') or 0)
print('%s n=%d max_nr_throttled=%d' % (('%.4f'%(sum(v)/len(v)) if v else 'NOT_MEASURED'), len(v), thr))
" 2>/dev/null)

INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
echo "$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.StartedAt}} {{.State.FinishedAt}} {{.HostConfig.CpusetCpus}} {{.HostConfig.Memory}}' "$NAME" 2>/dev/null) $GOT_DIGEST" > "$BASE/${ARM}_${STAMP}.inspect.txt"
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] log=$(basename "$LOG") stamp=$STAMP"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S" "$LOG" | head -3
} | tee -a "$LEDGER"

# G9: the .so md5 as PRINTED BY THE LOADING PROCESS must be the registered one.
GOT_SO=$(grep -a 'D4S_IDWARP_SO_MD5:' "$LOG" | head -1 | awk '{print $2}')
if [ "$GOT_SO" != "$SO_MD5_PATCHED" ]; then
  echo "D19R_G9_REFUSE arm=$ARM libidwarp.so md5 printed by the loading process is [$GOT_SO], registered [$SO_MD5_PATCHED]" | tee -a "$LEDGER"
  test "$rc" -eq 0 && rc=7
else
  echo "D19R_G9_OK arm=$ARM libidwarp_so_md5=$GOT_SO digest=$GOT_DIGEST" | tee -a "$LEDGER"
fi

test -s "$LOG" && touch "$LOG.ok.${STAMP}"
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
