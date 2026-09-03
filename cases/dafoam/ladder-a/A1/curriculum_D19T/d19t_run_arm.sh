#!/usr/bin/env bash
# =============================================================================
# Curriculum D19T -- THE ARM LAUNCHER.
#
# Structure is D19M's, proven on that item; the item-specific tables, the
# tolerance argument and the decomposeParDict PRE-NORMALISATION are new.
#
# WHAT IS NEW HERE AND WHY
# ------------------------
# 1. THE TOLERANCE IS A LAUNCH ARGUMENT AND IS ASSERTED AGAINST A REGISTERED
#    TABLE.  `primalMinResTol` is this item's entire independent variable.  An
#    arm cannot be launched at a tolerance that is not the one registered for
#    it, and the tolerance is echoed into the ledger so the grader reads it
#    from the record rather than from this file.
#
# 2. `system/decomposeParDict` IS PRE-NORMALISED, AND NO GATE IS WIDENED.
#    D19R2 measured this file mutating in exactly the three np=2 arms -- five
#    `kahipCoeffs` lines that `decomposePar` writes back into the dictionary it
#    read -- and REFUSED, correctly, because narrowing the manifest would have
#    been a gate-design decision reserved to Sanaa.  D19T does NOT exclude the
#    path and does NOT widen `SOLVER_WRITE_TARGETS`.  It stages the file
#    ALREADY NORMALISED, so the bytes the manifest pins are the bytes
#    decomposePar will write, and `G-MANIFEST` still requires ZERO mismatches.
#
#    THE FIXED POINT IS MEASURED, NOT ASSUMED: D19R's X2 and S8 arms wrote this
#    file INDEPENDENTLY and both landed on md5 c3f5f05d45f0b9a70d645b107a837727
#    from the same 68ecc827562886fb43c3aedb0627b344 input.  Two independent
#    writes, one result.  Staging asserts that md5 before the manifest is built.
#
# 8.2: NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives.
# =============================================================================
set -u
case "${1:-}" in --source-only) return 0 2>/dev/null || exit 0 ;; esac

ITEM=D19T
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D19T-a1-naca0012-shape7-primal-tightening
BASE="${BASE:-$REGISTERED_BASE}"

# ---- G-ROOT.1: BASE resolves to THIS item's registered run root -------------
BASE_REAL=$(realpath -m "$BASE")
REG_REAL=$(realpath -m "$REGISTERED_BASE")
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE=$BASE_REAL is not this item's registered root $REG_REAL"
  exit 3
fi

# ---- G-ROOT.2: named roots this file must NEVER write -----------------------
# Siblings whose artefacts are cited by landed records.  An item that can write
# into a sibling's run root can invalidate a published number.
FORBIDDEN_ROOTS="/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau
/home/ubuntu/certonomous-runs/CURRICULUM-D19O-a1-naca0012-subsonic-optimisation
/home/ubuntu/certonomous-runs/CURRICULUM-D19M-a1-naca0012-subsonic-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt"
for f in $FORBIDDEN_ROOTS; do
  case "$BASE_REAL/" in "$(realpath -m "$f")/"*) echo "ABORT G-ROOT.2 $BASE_REAL is inside $f"; exit 3 ;; esac
done

HERE="$(cd "$(dirname "$0")" && pwd)"
# REGISTERED CPUSET.  Distinct from D19R's (1,15) and D19M's (13) so a
# concurrent sibling cannot share a core with this item.
CPUSET=5,13

container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d19t_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md section 6, verbatim) ----------
#   arm    ranks  core-min cap  in-container wall  memory   primalMinResTol
#   MESH     1        3.0            120 s          4g          n/a
#   T08      2        4.0             ...           4g         1e-8
#   T10      2        4.0             ...           4g         1e-10
#   T12      2        4.0             ...           4g         1e-12
#   XT10     2        5.0             ...           4g         1e-10
#   (wall = cap*60/ranks - CAP_MARGIN_S)
#
# MEMORY IS SIZED FROM A MEASUREMENT, NOT INHERITED.  The A1 4,032-cell adjoint
# peaked at 1137-1189 MiB (`cases/dafoam/ADJOINT_MEMORY_ENVELOPE.json`, options
# 1 v1/v2) and D12R2's measured peak RSS is 1.3461 GiB.  4g is ~3.0x the
# measured peak.  The 20g inherited elsewhere in this family is ~15x oversized
# and has already caused one avoidable memory-guard collision.
CAP_MARGIN_S=60
cap_core_min() {
  case "$1" in
    MESH)          echo 3.0 ;;
    T08|T10|T12)   echo 4.0 ;;
    XT10)          echo 5.0 ;;
    *)             echo "" ;;
  esac
}
cap_memory() {
  case "$1" in MESH|T08|T10|T12|XT10) echo 4g ;; *) echo "" ;; esac
}
# np = 2 ON EVERY SOLVER ARM.  A CONDITION, NOT A CONVENIENCE: the reproduction
# arm T08 is compared value-against-value with D19R's LANDED numbers, which were
# measured at np=2 with `scotch` on 2 subdomains.  Changing np would confound
# the tolerance with the decomposition (A4 measured a 16,600x spread between two
# decompositions of one mesh), and there would then be no way to attribute a
# change to the thing this item varies.
ranks_of() {
  case "$1" in MESH) echo 1 ;; T08|T10|T12|XT10) echo 2 ;; *) echo "" ;; esac
}
mode_of() {
  case "$1" in T08|T10|T12) echo T ;; XT10) echo X ;; *) echo "" ;; esac
}
# THE INDEPENDENT VARIABLE, REGISTERED PER ARM.
tol_of() {
  case "$1" in T08) echo 1e-8 ;; T10|XT10) echo 1e-10 ;; T12) echo 1e-12 ;; *) echo "" ;; esac
}
row_of_arm() {
  case "$1" in MESH|T08|T10|T12|XT10) echo PATCHED ;; *) echo "" ;; esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag --------------------------
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
SO_MD5_PATCHED=85f59e87253e0a71a813f64ca6e4c425

# ---- FROZEN INSTRUMENT HASHES ----------------------------------------------
MD5_RUNSCRIPT=a5e18503ea29d0e37c3cf1668533cd34      # D19R's producer, BORROWED UNEDITED
MD5_DECOMP_RAW=68ecc827562886fb43c3aedb0627b344     # as `base/` carries it
MD5_DECOMP_NORM=c3f5f05d45f0b9a70d645b107a837727    # after decomposePar, the FIXED POINT

# ---- D15's FROZEN MESH IDENTITY, md5 of the DECOMPRESSED files -------------
MESH_CELLS=4032
MD5_MESH_points=88f00ff725ef2906212ca1e2b040c09f
MD5_MESH_faces=1bcea5c2f5817d0740a03a83050c3c79
MD5_MESH_owner=549e0a9f01be3ebf412017c1e9811ece
MD5_MESH_neighbour=65fd7ca38d534c760f57ce14bdffc834
MD5_MESH_boundary=c92a945e9a1405b988ab418e48ab53c3

# =============================================================================
ARM="${1:-}"; IMG="${2:-}"
USAGE="usage: d19t_run_arm.sh <MESH|T08|T10|T12|XT10> <image>"
test -n "$ARM" -a -n "$IMG" || { echo "$USAGE"; exit 64; }
RANKS=$(ranks_of "$ARM");  test -n "$RANKS" || { echo "ABORT arm $ARM carries no registered rank count"; exit 64; }
CAP=$(cap_core_min "$ARM"); test -n "$CAP" || { echo "ABORT arm $ARM carries no registered cap"; exit 64; }
MEM=$(cap_memory "$ARM")
MODE=$(mode_of "$ARM")
TOL=$(tol_of "$ARM")
WANT_ROW=$(row_of_arm "$ARM")
if [ "$ARM" != "MESH" ]; then
  test -n "$MODE" || { echo "ABORT arm $ARM carries no registered mode"; exit 64; }
  test -n "$TOL"  || { echo "ABORT arm $ARM carries no registered tolerance -- the "\
"independent variable may not default"; exit 64; }
fi

# ---- do not touch a running solver -----------------------------------------
LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d19t_${ARM}_" 2>/dev/null | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT arm $ARM already has a live container: $LIVE_SAME_ARM"; exit 7
fi

# ---- THE CAP ASSERT: the in-container deadline BACKS OUT to the cap ---------
TMO=$(python3 -c "print(int($CAP*60.0/$RANKS) - $CAP_MARGIN_S)") || { echo "ABORT tmo calc"; exit 65; }
test "$TMO" -gt 0 || { echo "ABORT arm $ARM cap $CAP core-min at $RANKS ranks leaves no wall budget"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % (($TMO+$CAP_MARGIN_S)*$RANKS/60.0))")
python3 -c "
import sys
if abs($BACKCHECK - $CAP) > 1e-6:
    sys.stderr.write('ABORT cap assert: deadline %ds x %d ranks backs out to %s core-min, not the registered %s\n' % ($TMO, $RANKS, '$BACKCHECK', '$CAP')); sys.exit(1)
" || exit 65
echo "D19T_CAP arm=$ARM cap_core_min=$CAP ranks=$RANKS deadline_in_container_s=$TMO backs_out_to=$BACKCHECK"

MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D19T_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

# ---- G-ROW: the image is the REGISTERED ROW, by digest ---------------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
if [ -z "$GOT_DIGEST" ]; then
  GOT_DIGEST=sha256:$(sudo -n docker image inspect --format '{{.Id}}' "$IMG" 2>/dev/null | sed 's/^sha256://')
fi
case "$GOT_DIGEST" in
  "$IMG_PATCHED_DIGEST") ROW=PATCHED ;;
  *) echo "ABORT image $IMG digest $GOT_DIGEST is not the registered PATCHED row $IMG_PATCHED_DIGEST"; exit 4 ;;
esac
test "$ROW" = "$WANT_ROW" || { echo "ABORT arm $ARM is registered $WANT_ROW but the image is $ROW"; exit 4; }
echo "D19T_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d19t_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- AGE GUARD DATUM: a LAUNCH SENTINEL, OUTSIDE every bind-mount source ----
stamp_launch_datum() {
  python3 - "$BASE" "$ARM" "$WORK" <<'EOF' || return 1
import json, os, sys
sys.path.insert(0, os.environ["D19T_HERE"])
import d19t_age_guard as AGE
base, arm, work = sys.argv[1], sys.argv[2], sys.argv[3]
mounts = [base]                       # exactly what `docker run -v` is passed
try:
    spath, datum = AGE.stamp_sentinel(base, arm, mounts)
    manifest = AGE.build_manifest(work, json.loads(os.environ["D19T_INPUTS"]))
except AGE.Refusal as exc:
    sys.stderr.write("ABORT age-guard datum: %s\n" % exc)
    sys.exit(1)
with open(os.path.join(work, ".d19t_manifest.json"), "w") as fh:
    json.dump(manifest, fh, indent=1, sort_keys=True)
    fh.flush(); os.fsync(fh.fileno())
print("D19T_G_COLD OK arm=%s age_datum_epoch=%.6f sentinel=%s manifest_entries=%d "
      "excluded_write_targets=%s resolved_by=LAUNCH_SENTINEL_OUTSIDE_MOUNT"
      % (arm, datum, spath, manifest["n_entries"],
         [x["path"] for x in manifest["excluded_write_targets"]]))
EOF
  return 0
}

# ---- THE PRE-NORMALISATION.  No gate is widened; the bytes are settled first.
normalise_decompose_dict() {
  local f="$WORK/system/decomposeParDict"
  test -f "$f" || { echo "ABORT no system/decomposeParDict to normalise"; return 1; }
  local raw; raw=$(md5sum < "$f" | cut -d' ' -f1)
  if [ "$raw" = "$MD5_DECOMP_NORM" ]; then
    echo "D19T_DECOMP_ALREADY_NORMALISED md5=$raw"; return 0
  fi
  test "$raw" = "$MD5_DECOMP_RAW" || {
    echo "ABORT decomposeParDict md5 $raw is neither the registered raw ($MD5_DECOMP_RAW) nor the registered normalised ($MD5_DECOMP_NORM)"; return 1; }
  # The five lines decomposePar itself writes back, measured identically by
  # D19R's X2 and S8 arms.  Inserted at the registered offset, then VERIFIED by
  # md5 -- if the result is not the measured fixed point this REFUSES rather
  # than proceeding with a dictionary that will move under the run.
  python3 - "$f" <<'EOF' || return 1
import sys
p = sys.argv[1]
lines = open(p).read().splitlines(True)
# EXACT BYTES, transcribed from D19R's X2/system/decomposeParDict.  Two of
# these five lines carry a TRAILING SPACE that OpenFOAM writes and that a
# hand-retyped block does not -- the first attempt at this reconstruction
# produced md5 d5a844d94d93929888b4879d189f48e0 instead of the measured
# c3f5f05d45f0b9a70d645b107a837727 for exactly that reason, and the md5
# assert below is what caught it.
block = ["kahipCoeffs \n", "{ \n", "    config                  fast;\n",
         "    imbalance              0.01;\n", "} \n"]
lines[21:21] = block
open(p, "w").write("".join(lines))
EOF
  local now; now=$(md5sum < "$f" | cut -d' ' -f1)
  test "$now" = "$MD5_DECOMP_NORM" || {
    echo "ABORT pre-normalisation produced md5 $now, not the measured fixed point $MD5_DECOMP_NORM"; return 1; }
  echo "D19T_DECOMP_NORMALISED $MD5_DECOMP_RAW -> $now (the fixed point measured by D19R X2 and S8)"
  return 0
}

if [ "$ARM" = "MESH" ]; then
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy"; exit 4; }
  test -e "$WORK/constant/polyMesh" && { echo "ABORT G-COLD MESH: base/ already carries constant/polyMesh"; exit 5; }
  test -e "$WORK/0" && { echo "ABORT G-COLD MESH: base/ already carries 0/"; exit 5; }
  test -d "$WORK/0.orig" || { echo "ABORT G-COLD 0.orig missing"; exit 5; }
  export D19T_HERE="$HERE" D19T_INPUTS='["0.orig","constant","system"]'
  stamp_launch_datum || exit 5
else
  test -d "$BASE/MESH" || { echo "ABORT arm $ARM expects an existing MESH/ from arm MESH"; exit 5; }
  test -f "$BASE/MESH/constant/polyMesh/boundary" || { echo "ABORT arm $ARM: MESH/ carries no polyMesh/boundary"; exit 5; }
  test -d "$BASE/MESH/0" || { echo "ABORT arm $ARM: MESH/ carries no 0/"; exit 5; }
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/MESH" "$WORK" || { echo "ABORT stage copy from MESH"; exit 4; }
  rm -rf "$WORK/processor"* 2>/dev/null
  # the producer is BORROWED FROM D19R UNEDITED and its md5 is asserted here
  cp "$BASE/d19r_runScript.py" "$WORK/" || { echo "ABORT producer copy"; exit 4; }
  cp "$HERE/d19t_xf.py" "$WORK/" || { echo "ABORT xf copy"; exit 4; }
  GOT_RS=$(md5sum < "$WORK/d19r_runScript.py" | cut -d' ' -f1)
  test "$GOT_RS" = "$MD5_RUNSCRIPT" || { echo "ABORT producer md5 $GOT_RS != frozen $MD5_RUNSCRIPT"; exit 4; }
  normalise_decompose_dict || exit 5
  export D19T_HERE="$HERE" D19T_INPUTS='["0.orig","constant","system","d19r_runScript.py","d19t_xf.py"]'
  stamp_launch_datum || exit 5
fi

# ---- the arm commands -------------------------------------------------------
MESH_ASSERT="python3 - <<'EOF'
import gzip, hashlib, os, sys
want = {'points':'$MD5_MESH_points','faces':'$MD5_MESH_faces','owner':'$MD5_MESH_owner',
        'neighbour':'$MD5_MESH_neighbour','boundary':'$MD5_MESH_boundary'}
bad = []
for n, w in sorted(want.items()):
    p = 'constant/polyMesh/%s' % n
    if os.path.exists(p + '.gz'):
        raw = gzip.open(p + '.gz','rb').read()
    elif os.path.exists(p):
        raw = open(p,'rb').read()
    else:
        bad.append((n,'ABSENT',w)); continue
    g = hashlib.md5(raw).hexdigest()
    print('D19T_MESH_IDENTITY %s raw_md5=%s frozen=%s %s' % (n, g, w, 'OK' if g==w else 'MISMATCH'))
    if g != w: bad.append((n,g,w))
if bad:
    sys.stderr.write('D19T_MESH_IDENTITY REFUSE not byte-identical to the D15/D19R mesh: %r\n' % bad)
    sys.exit(6)
print('D19T_MESH_IDENTITY_OK')
EOF"
case "$ARM" in
  MESH) CMD="bash preProcessing.sh && checkMesh > checkMesh.log 2>&1; echo D19T_CHECKMESH_RC \$?; grep -a 'cells:' checkMesh.log; grep -aq '^ *cells: *$MESH_CELLS\$' checkMesh.log || { echo D19T_CELLCOUNT_REFUSE expected $MESH_CELLS; exit 6; }; $MESH_ASSERT" ;;
  *)    CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d19t_xf.py -mode $MODE -tol $TOL" ;;
esac

CMDFILE="$WORK/d19t_cmd.sh"
printf '%s\n' "$CMD" > "$CMDFILE" || { echo "ABORT cmd file"; exit 4; }
echo "D19T_CMDFILE arm=$ARM mode=${MODE:-n/a} tol=${TOL:-n/a} md5=$(md5sum "$CMDFILE" | cut -d' ' -f1) deadline_in_container_s=$TMO"

T0=$(date +%s)
sudo -n docker run -d --name "$NAME" \
  --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
  -v "$BASE":"$BASE" -w "$WORK" "$IMG" \
  bash -lc "source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1 || true; \
     echo D19T_CONTAINER_UID: \$(id -u) && \
     echo D19T_DEADLINE_IN_CONTAINER_S: $TMO && \
     python3 -c 'import idwarp,os,hashlib;p=os.path.join(os.path.dirname(idwarp.__file__),\"libidwarp.so\");print(\"D19T_IDWARP_SO_MD5:\",hashlib.md5(open(p,\"rb\").read()).hexdigest())' && \
     timeout -s TERM -k 30 $TMO bash d19t_cmd.sh" >/dev/null || { echo "ABORT docker run"; exit 8; }

# ---- wait, with the registered deadline plus a grace window ----------------
GRACE=$((TMO + 120))
ELAPSED=0
while sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | grep -q .; do
  sleep 2; ELAPSED=$((ELAPSED + 2))
  if [ "$ELAPSED" -gt "$GRACE" ]; then
    echo "D19T_DEADLINE_EXCEEDED arm=$ARM elapsed=${ELAPSED}s grace=${GRACE}s -- STOPPING"
    sudo -n docker stop -t 30 "$NAME" >/dev/null 2>&1
    break
  fi
done
T1=$(date +%s)
WALL=$((T1-T0))

sudo -n docker logs "$NAME" > "$LOG" 2>&1
rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$NAME" 2>/dev/null)
sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.StartedAt}} {{.State.FinishedAt}} {{.HostConfig.CpusetCpus}} {{.HostConfig.Memory}}' "$NAME" > "$BASE/${ARM}_${STAMP}.inspect.txt" 2>/dev/null
echo "$GOT_DIGEST" >> "$BASE/${ARM}_${STAMP}.inspect.txt"
sudo -n docker rm "$NAME" >/dev/null 2>&1

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
SIBLINGS_POST=$(container_census)
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")

# ---- THE OVERRUN RULE: an overrun STOPS the run, it does not get a budget ---
OVER=$(python3 -c "print('YES' if $CORE_MIN > $CAP else 'NO')")

LEDGER="$BASE/ledger.txt"
{
  printf 'ARM=%s ROW=%s IMG=%s DIGEST=%s rc=%s wall_s=%s ranks=%s core_min=%s cap_core_min=%s over_cap=%s tol=%s mode=%s memory=%s cpuset=%s memavail_pre_GiB=%s memavail_post_GiB=%s siblings_pre=[%s] siblings_post=[%s] log=%s stamp=%s\n' \
    "$ARM" "$ROW" "$IMG" "$GOT_DIGEST" "${rc:-NA}" "$WALL" "$RANKS" "$CORE_MIN" "$CAP" "$OVER" \
    "${TOL:-n/a}" "${MODE:-n/a}" "$MEM" "$CPUSET" "$MEMAVAIL_GIB" "$MEMAVAIL_POST" \
    "$SIBLINGS_PRE" "$SIBLINGS_POST" "$(basename "$LOG")" "$STAMP"
  grep -a "D19T_CONTAINER_UID\|D19T_IDWARP_SO_MD5\|D19T_DEADLINE_IN_CONTAINER_S" "$LOG" | head -3
} >> "$LEDGER"

GOT_SO=$(grep -a 'D19T_IDWARP_SO_MD5:' "$LOG" | head -1 | awk '{print $2}')
if [ -n "$GOT_SO" ] && [ "$GOT_SO" != "$SO_MD5_PATCHED" ]; then
  echo "D19T_G9_MISMATCH arm=$ARM libidwarp_so_md5=$GOT_SO want=$SO_MD5_PATCHED" | tee -a "$LEDGER"
else
  echo "D19T_G9_OK arm=$ARM libidwarp_so_md5=$GOT_SO digest=$GOT_DIGEST" | tee -a "$LEDGER"
fi

# ---- the tolerance assert, READ FROM THE SOLVER'S OWN STATEMENT ------------
if [ "$ARM" != "MESH" ]; then
  N_TOL=$(grep -ac "satisfied the prescribed tolerance" "$LOG" || true)
  N_WRONG=$(grep -a "satisfied the prescribed tolerance" "$LOG" | grep -avc "tolerance $TOL\$" || true)
  echo "D19T_TOL_SEEN arm=$ARM registered=$TOL n_lines=$N_TOL n_wrong=$N_WRONG" | tee -a "$LEDGER"
fi

echo "D19T_ARM_DONE arm=$ARM rc=${rc:-NA} wall_s=$WALL core_min=$CORE_MIN cap=$CAP over_cap=$OVER log=$(basename "$LOG")"
if [ "$OVER" = "YES" ]; then
  echo "D19T_OVERRUN arm=$ARM $CORE_MIN core-min > cap $CAP -- CLAUDE.md rule 12: the run STOPS, it does not get a new budget"
  exit 9
fi
exit "${rc:-1}"
