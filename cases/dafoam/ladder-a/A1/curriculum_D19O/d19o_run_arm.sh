#!/usr/bin/env bash
# ===========================================================================
# Curriculum D19O ARM LAUNCHER -- NACA0012 SUBSONIC (DARhoSimpleFoam, M 0.288),
# THE COMPRESSIBLE SINGLE-POINT SHAPE OPTIMISATION.  BOTH TOOLCHAIN ROWS.
# np = 1 ON EVERY ARM.
#
# DERIVED from `curriculum_D19R/d19r_run_arm.sh` with these REGISTERED DELTAS
# and no others (PREREGISTRATION.md section 7):
#   (1) item/root names; D19's, D19R's and D15's roots ADDED to FORBIDDEN_ROOTS
#       -- D19R's root holds the plateau artefact this item's s* and its whole
#       shape[7] registration are read from, and D15's holds the frozen mesh
#       identity the MESH arm asserts against.  Destroying either would destroy
#       this item's own precondition.
#   (2) ARMS MESH O-S XE-S FE-S O-P XE-P FE-P; RANKS 1 ON EVERY ONE; caps from
#       PREREGISTRATION.md section 12 (5.0 / 40.0 / 10.0 / 20.0).
#   (3) TWO ROWS, not D19R's PATCHED-only.  `DAFOAM_CHARTER.md` section 6: a
#       DAFoam verdict is two rows or it is not a verdict about DAFoam.  The row
#       is derived from the IMAGE DIGEST here and, independently, from the
#       `libidwarp.so` md5 inside the container by `d19o_xf.py`.  Two readers,
#       and `G9` compares both against the registration.
#   (4) cpuset 11.  ONE core, because every arm runs at np = 1.  NOT core 0.
#       Read from disk, not recalled: across `cases/dafoam/ladder-a/*/curriculum_*/
#       *_run_arm.sh` core 11 appears in EXACTLY ONE registered set, D5's
#       `8,10,11,13` (A2, arms finished).  It is disjoint from SO-3's `14`,
#       D19/D19R's `1,15`, D15's `2,3`, D16's `4,14`, the SO-1/SO-2 line's `9`,
#       D4's `5,6,7,9`, D6's `2,3,4,14`, D7's `2,3,4,6` and D8R's `0,1,12,15`.
#   (5) THE C-188 CAP FRAME.  The in-container wall is
#       `floor(cap*60/ranks) - CAP_MARGIN_S` with CAP_MARGIN_S = 180, NOT
#       `cap*60/ranks`.  The 180 s host-frame margin is charged to the ceiling so
#       the ledger cannot record `core_min > cap` on an arm that reaches its own
#       deadline -- a GATE FAIL manufactured by the frame rather than by the run.
#   (6) THE STALL WATCHDOG, armed on the O arms ONLY.  `CLAUDE.md` rule 12: an
#       overrun STOPS THE RUN.  The in-container deadline already bounds the
#       spend, but a wall clock cannot tell the record WHY the run ended, and
#       `DAFOAM_CHARTER.md` section 9 makes that a VERDICT difference.
#   (7) THE ENDPOINT ARMS STAGE `d19o_xopt.json` FROM THEIR OWN ROW'S O ARM.
#       Named explicitly, so the cold-start guard does not mistake an INPUT for
#       a pre-existing RESULT -- and XE/FE write `d19o_X.json`/`d19o_F.json`,
#       never `d19o_xopt.json`, so an input can never be read as this arm's own
#       output.
#
# CAP DISCIPLINE: the caps are NOT arguments.  They are constants below, the
# table is reproduced verbatim in PREREGISTRATION.md section 12, this file's md5
# is frozen there, and the launcher ASSERTS that the wall timeout it is about to
# enforce, PLUS the margin, equals CAP*60/RANKS to the second.
#
# 8.2: NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives.
# `set -e` does not gate at the top level of a harness Bash call; every step
# below gates explicitly with `|| { echo ABORT...; exit N; }`.
# ===========================================================================
set -uo pipefail

# ===========================================================================
# THE LEDGER ROW IS EMITTED BY THIS FUNCTION AND BY NOTHING ELSE, AND THE
# COMPARATOR'S SELFTEST SOURCES IT.
#
# `d19o_grade_selftest.py:_ledger_row_via_launcher` runs
#     bash -c '. d19o_run_arm.sh --source-only; d19o_ledger_row ...'
# so EVERY fixture row in the comparator's suite comes out of THESE bytes.  If
# this format and `d19o_grade.py:_LEDGER` ever diverge, the fixture rows stop
# parsing and the suite fails LOUDLY instead of passing quietly.  SO-1a's
# comparator selftest reproduced the row format in a Python constant, so a
# launcher/reader divergence would have left the suite green and the reader
# blind on the real run.
#
# 21 positional arguments, in the order the row prints them.
# ===========================================================================
d19o_ledger_row() {
  printf 'ARM=%s ROW=%s IMG=%s DIGEST=%s rc=%s wall_s=%s ranks=%s core_min=%s cap_core_min=%s enforced_wall_s=%s enforced_core_min=%s memory=%s inspect(exit,oomkilled)=[%s] memavail_pre_GiB=%s memavail_post_GiB=%s cpuset=%s delivered_cores_mean=[%s] siblings_pre=[%s] siblings_post=[%s] log=%s stamp=%s\n' \
    "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}" "${11}" "${12}" "${13}" \
    "${14}" "${15}" "${16}" "${17}" "${18}" "${19}" "${20}" "${21}"
}

# The source-only door.  It must come AFTER the writer and BEFORE anything that
# touches the disk, so sourcing this file can never stage, launch or delete.
case "${1:-}" in --source-only) return 0 2>/dev/null || exit 0 ;; esac

ITEM=D19O
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D19O-a1-naca0012-subsonic-optimisation
BASE="${BASE:-$REGISTERED_BASE}"

# ---- G-ROOT.1: BASE resolves to THIS item's registered run root ------------
# Through `realpath -m`, so a trailing slash, a `.`, a `..` or a symlink cannot
# walk around it.  The staging path below begins `rm -rf "$WORK"`;
# `d4_run_arm.sh` once hardcoded another item's root and would have deleted
# 5,085 files, 384 MB, holding the artefacts an accepted GATE REACHED rests on.
BASE_REAL=$(realpath -m "$BASE")
REG_REAL=$(realpath -m "$REGISTERED_BASE")
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
  echo "  given:      $BASE_REAL"
  echo "  registered: $REG_REAL"
  exit 3
fi

# ---- G-ROOT.2: named roots this file must never write ----------------------
# HONEST SIZE, stated here as D19R's parent states it: every one of these is
# ALREADY refused at G-ROOT.1.  This is a second line of defence that cannot
# fire while G-ROOT.1 stands, and it closed no live hole.  What a stale list
# costs is real but smaller -- a refusal naming a directory that does not exist
# says the wrong thing on the day G-ROOT.1 is weakened.  Each entry below was
# CHECKED ON DISK at this freeze and every one EXISTS.
FORBIDDEN_ROOTS="/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau
/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt
/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic
/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic
/home/ubuntu/certonomous-runs/CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient
/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt
/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt
/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/subsonic
/home/ubuntu/dafoam-tutorials
/home/ubuntu/certonomous-runs
/home/ubuntu/Certonomous"
while IFS= read -r forb; do
  [ -z "$forb" ] && continue
  if [ "$BASE_REAL" = "$(realpath -m "$forb")" ]; then
    echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S RUN ROOT: $forb"
    echo "  D19R's root in particular holds d19r_selected_step.json, from which this"
    echo "  item's s* and its entire shape[7] registration are read.  REFUSED."
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
CPUSET=11

container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d19o_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md section 12, verbatim) --------
#   arm     ranks  core-min cap   in-container wall   memory cap
#   MESH      1        5.0            120 s              12g
#   O-S       1       40.0           2220 s              12g
#   O-P       1       40.0           2220 s              12g
#   XE-S      1       10.0            420 s              12g
#   XE-P      1       10.0            420 s              12g
#   FE-S      1       20.0           1020 s              12g
#   FE-P      1       20.0           1020 s              12g
#   (wall = cap*60/ranks - CAP_MARGIN_S; see delta 5)
CAP_MARGIN_S=180
cap_core_min() {
  case "$1" in
    MESH)      echo 5.0 ;;
    O-S|O-P)   echo 40.0 ;;
    XE-S|XE-P) echo 10.0 ;;
    FE-S|FE-P) echo 20.0 ;;
    *)         echo "" ;;
  esac
}
cap_memory() {
  case "$1" in MESH|O-S|O-P|XE-S|XE-P|FE-S|FE-P) echo 12g ;; *) echo "" ;; esac
}
# np = 1 ON EVERY ARM.  A CONDITION ON THE INHERITANCE, not a setting.
ranks_of() {
  case "$1" in MESH|O-S|O-P|XE-S|XE-P|FE-S|FE-P) echo 1 ;; *) echo "" ;; esac
}
mode_of() {
  case "$1" in
    O-S|O-P)   echo O ;;
    XE-S|XE-P) echo XE ;;
    FE-S|FE-P) echo FE ;;
    *)         echo "" ;;
  esac
}
row_of_arm() {
  case "$1" in
    MESH|O-S|XE-S|FE-S) echo SHIPPED ;;
    O-P|XE-P|FE-P)      echo PATCHED ;;
    *)                  echo "" ;;
  esac
}
o_arm_of() {
  case "$1" in XE-S|FE-S) echo O-S ;; XE-P|FE-P) echo O-P ;; *) echo "" ;; esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag ------------------------
# Both RE-MEASURED at this freeze from this box's own `docker image inspect`,
# and both `.so` md5s RE-MEASURED by running each image and hashing the library
# the interpreter imported.
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc
SO_MD5_PATCHED=85f59e87253e0a71a813f64ca6e4c425
SO_MD5_SHIPPED=f0fcb488e0e98156575cd19548e91663

# ---- FROZEN INSTRUMENT HASHES (set at the freeze by d19o_repin.sh) --------
MD5_RUNSCRIPT=a5e18503ea29d0e37c3cf1668533cd34
MD5_XF=6f5e7ed9db76bf429b4031c6d87a8bf6
MD5_DECOMP=68ecc827562886fb43c3aedb0627b344

# ---- D15's FROZEN MESH IDENTITY, md5 of the DECOMPRESSED files -------------
# RE-COMPUTED at this freeze from D19R's own MESH arm output, not copied.  A
# `.gz` stream can carry an mtime, so a gz hash is not a safe cross-run
# identity; these are md5s of the DECOMPRESSED bytes.
MESH_CELLS=4032
MD5_MESH_points=88f00ff725ef2906212ca1e2b040c09f
MD5_MESH_faces=1bcea5c2f5817d0740a03a83050c3c79
MD5_MESH_owner=549e0a9f01be3ebf412017c1e9811ece
MD5_MESH_neighbour=65fd7ca38d534c760f57ce14bdffc834
MD5_MESH_boundary=c92a945e9a1405b988ab418e48ab53c3

ARM="${1:-}"; IMG="${2:-}"
USAGE="usage: d19o_run_arm.sh <MESH|O-S|XE-S|FE-S|O-P|XE-P|FE-P> <image>"
test -n "$ARM" || { echo "ABORT $USAGE"; exit 64; }
test -n "$IMG" || { echo "ABORT $USAGE"; exit 64; }
RANKS=$(ranks_of "$ARM"); test -n "$RANKS" || { echo "ABORT arm $ARM carries no registered rank count"; exit 64; }
MODE=$(mode_of "$ARM")
WANT_ROW=$(row_of_arm "$ARM")

LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d19o_${ARM}_" 2>/dev/null | grep "^d19o_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  exit 3
fi
PIDFILE="$BASE/d19o_driver.pid"
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

# ---- THE CAP ASSERT, ON THE C-188 FRAME (delta 5) -------------------------
TMO=$(python3 -c "print(int($CAP*60.0/$RANKS) - $CAP_MARGIN_S)") || { echo "ABORT tmo calc"; exit 65; }
test "$TMO" -gt 0 || { echo "ABORT cap $CAP leaves no wall after the ${CAP_MARGIN_S}s margin"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % (($TMO+$CAP_MARGIN_S)*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced+margin=%r\n' % (cap, back)); sys.exit(1)
" || { echo "ABORT enforced cap + margin != registered cap"; exit 65; }
echo "D4_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO cap_margin_s=$CAP_MARGIN_S enforced_core_min=$BACKCHECK memory=$MEM"

MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D4_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }

echo "$MD5_RUNSCRIPT  $BASE/d19o_runScript.py"          | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_XF  $BASE/d19o_xf.py"                        | md5sum -c - || { echo "ABORT xf md5"; exit 4; }
echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict"  | md5sum -c - || { echo "ABORT decomposeParDict md5"; exit 4; }

GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
if [ -z "$GOT_DIGEST" ]; then
  GOT_DIGEST=$(sudo -n docker image inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
fi
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1)        WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED; WANT_SO=$SO_MD5_PATCHED ;;
  dafoam/opt-packages:latest)  WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED; WANT_SO=$SO_MD5_SHIPPED ;;
  *) echo "ABORT image $IMG is not a registered row (PATCHED or SHIPPED)"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }

# G-ROW: the arm's row is REGISTERED, so a shipped image cannot run a patched arm.
test "$ROW" = "$WANT_ROW" || {
  echo "ABORT G-ROW arm $ARM is registered on the $WANT_ROW row; got ROW=$ROW ($IMG)."; exit 4; }
echo "D4S_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d19o_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- AGE GUARD DATUM: a LAUNCH SENTINEL, OUTSIDE every bind-mount source ----
# `d19o_age_guard.assert_sentinel_outside_mounts` REFUSES if the sentinel is at
# or under any declared mount source, so "the solver does not write here" is a
# property of the mount namespace rather than a belief about DAFoam.
stamp_launch_datum() {
  python3 - "$BASE" "$ARM" "$WORK" <<'EOF' || return 1
import json, os, sys
sys.path.insert(0, os.environ["D19O_HERE"])
import d19o_age_guard as AGE
base, arm, work = sys.argv[1], sys.argv[2], sys.argv[3]
mounts = [base]                       # exactly what `docker run -v` is passed
try:
    spath, datum = AGE.stamp_sentinel(base, arm, mounts)
    manifest = AGE.build_manifest(work, json.loads(os.environ["D19O_INPUTS"]))
except AGE.Refusal as exc:
    sys.stderr.write("ABORT age-guard datum: %s\n" % exc)
    sys.exit(1)
with open(os.path.join(work, ".d19o_manifest.json"), "w") as fh:
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
  export D19O_HERE="$HERE" D19O_INPUTS='["0.orig","constant","system"]'
  stamp_launch_datum || exit 5
else
  test -d "$BASE/MESH" || { echo "ABORT arm $ARM expects an existing MESH/ from arm MESH"; exit 5; }
  test -f "$BASE/MESH/constant/polyMesh/boundary" || { echo "ABORT arm $ARM: MESH/ carries no polyMesh/boundary"; exit 5; }
  test -d "$BASE/MESH/0" || { echo "ABORT arm $ARM: MESH/ carries no 0/"; exit 5; }
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/MESH" "$WORK" || { echo "ABORT stage copy from MESH"; exit 4; }
  rm -f "$WORK/d19o_cmd.sh" "$WORK/checkMesh.log" "$WORK/logMeshGeneration.txt" \
        "$WORK/volumeMesh.xyz" "$WORK/surfaceMesh.xyz" "$WORK/.d19o_manifest.json" 2>/dev/null
  cp -a "$BASE/d19o_runScript.py" "$BASE/d19o_xf.py" "$BASE/d19o_stall.py" "$WORK/" \
    || { echo "ABORT stage instruments"; exit 4; }

  # (7) THE ENDPOINT ARMS' INPUT: their OWN row's final design point.
  if [ "$MODE" = "XE" ] || [ "$MODE" = "FE" ]; then
    OARM=$(o_arm_of "$ARM")
    test -f "$BASE/$OARM/d19o_xopt.json" || {
      echo "ABORT arm $ARM needs $BASE/$OARM/d19o_xopt.json from arm $OARM."
      echo "  DAFOAM_CHARTER.md section 9: the FD check is at the FINAL design point."
      echo "  An endpoint arm with no optimum to stand at has nothing to check."
      exit 5; }
    cp -a "$BASE/$OARM/d19o_xopt.json" "$WORK/" || { echo "ABORT stage design point"; exit 4; }
  fi

  # COLD START, verified BEFORE the launch.  Every OUTPUT this item can write.
  # `d19o_xopt.json` is arm O's OUTPUT and is guarded like any other -- EXCEPT on
  # the endpoint arms, where it is a STAGED INPUT.  XE writes `d19o_X.json` and
  # FE writes `d19o_F.json`, never `d19o_xopt.json`, so an input can never be
  # mistaken for this arm's own result.  The exemption is BY ARM MODE and is
  # stated, not implicit.
  for bad in "$WORK/reports" "$WORK/d19o_O.json" "$WORK/d19o_X.json" "$WORK/d19o_F.json" \
             "$WORK/d19o_O.jsonl" "$WORK/d19o_X.jsonl" "$WORK/d19o_F.jsonl" \
             "$WORK/opt_IPOPT.txt" "$WORK/OptView.hst" "$WORK/dRdWColoring_1.bin"; do
    test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
  done
  if [ "$MODE" = "O" ]; then
    test -e "$WORK/d19o_xopt.json" && { echo "ABORT G-COLD $WORK/d19o_xopt.json exists"; exit 5; }
  fi
  test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
  for d in "$WORK"/*/; do
    n=$(basename "$d")
    case "$n" in 0|0.orig) ;; [0-9]*) echo "ABORT G-COLD time dir present: $n"; exit 5 ;; esac
  done
  export D19O_HERE="$HERE" D19O_INPUTS='["0.orig","constant","system","d19o_runScript.py","d19o_xf.py","d19o_stall.py"]'
  stamp_launch_datum || exit 5
fi

# ---- the arm commands -----------------------------------------------------
# MESH asserts the CELL COUNT and the MTIME-IMMUNE IDENTITY against D15's frozen
# mesh INSIDE the container, so the kernel's rc carries the assertion.
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
    print('D19O_MESH_IDENTITY %s raw_md5=%s frozen=%s %s' % (n, g, w, 'OK' if g==w else 'MISMATCH'))
    if g != w: bad.append((n,g,w))
if bad:
    sys.stderr.write('D19O_MESH_IDENTITY REFUSE not byte-identical to the D15/D19R mesh: %r\n' % bad)
    sys.exit(6)
print('D19O_MESH_IDENTITY_ALL_OK')
EOF"
case "$ARM" in
  MESH) CMD="bash preProcessing.sh && checkMesh > checkMesh.log 2>&1; echo D19O_CHECKMESH_RC \$?; grep -a 'cells:' checkMesh.log; grep -aq '^ *cells: *$MESH_CELLS\$' checkMesh.log || { echo D19O_CELLCOUNT_REFUSE expected $MESH_CELLS; exit 6; }; $MESH_ASSERT" ;;
  *)    CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d19o_xf.py -mode $MODE" ;;
esac

CMDFILE="$WORK/d19o_cmd.sh"
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
# THE CAP LIVES INSIDE THE CONTAINER: `timeout -k 60 $TMO` wraps the arm command
# file, so the deadline survives every host shell.  NO --rm, so the kernel's
# ExitCode and OOMKilled survive the arm.
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     echo D4S_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k 60 $TMO bash /mnt/$ARM/d19o_cmd.sh" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }

# ===========================================================================
# (6) THE STALL WATCHDOG -- THE REGISTERED NUMERICAL STOP, ARMED ON O ARMS ONLY.
# It reads IPOPT's own iteration table through the FROZEN detector and stops the
# container when condition A fires: `d19o_stall.N_STALL` (=8) consecutive majors
# with `alpha_pr < 1e-3`.  Condition B is registered NOT EXERCISED (it fires on
# 0 of 33 real logs) and is never reported as a passing control.
# ===========================================================================
CEILING=$(python3 -c "print('%.1f' % (4.0*$CAP))")
echo "D4S_RUNAWAY_GUARD arm=$ARM cap_core_min=$CAP ceiling_core_min=$CEILING mode=report_then_stop_at_ceiling"
if [ "$MODE" = "O" ]; then
  echo "D19O_STALL_WATCHDOG arm=$ARM armed=yes condition=A(alpha_pr<1e-3 x8) condition_B=NOT_EXERCISED"
else
  echo "D19O_STALL_WATCHDOG arm=$ARM armed=no reason=not_an_optimiser_arm"
fi
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
  if [ "$MODE" = "O" ] && [ -f "$WORK/opt_IPOPT.txt" ]; then
    SR=$(python3 -c "
import sys, json
sys.path.insert(0, '$HERE')
import d19o_stall as S
d = S.read_log('$WORK/opt_IPOPT.txt')
a = d['stall'].get('A')
print(json.dumps({'fired': bool(a), 'row': (a or {}).get('row_index'),
                  'iter': (a or {}).get('iter_label'), 'rows': d['n_rows']}))
" 2>/dev/null)
    if [ -n "$SR" ] && [ "$(python3 -c "import json;print(1 if json.loads('''$SR''')['fired'] else 0)" 2>/dev/null)" = "1" ]; then
      echo "D19O_STALL_FIRED arm=$ARM condition=A detail=$SR action=STOP core_min=$CM" | tee -a "$BASE/ledger.txt"
      sudo -n docker stop -t 30 "$NAME" >/dev/null 2>&1
      break
    fi
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
  d19o_ledger_row "$ARM" "$ROW" "$IMG" "$GOT_DIGEST" "$rc" "$WALL" "$RANKS" "$CORE_MIN" \
    "$CAP" "$TMO" "$BACKCHECK" "$MEM" "$INSPECT" "$MEMAVAIL_GIB" "$MEMAVAIL_POST" \
    "$CPUSET" "$DELIVERED" "$SIBLINGS_PRE" "$SIBLINGS_POST" "$(basename "$LOG")" "$STAMP"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S" "$LOG" | head -3
} | tee -a "$LEDGER"

# G9: the .so md5 as PRINTED BY THE LOADING PROCESS must be this row's registered one.
GOT_SO=$(grep -a 'D4S_IDWARP_SO_MD5:' "$LOG" | head -1 | awk '{print $2}')
if [ "$GOT_SO" != "$WANT_SO" ]; then
  echo "D19O_G9_REFUSE arm=$ARM row=$ROW libidwarp.so md5 printed by the loading process is [$GOT_SO], registered [$WANT_SO]" | tee -a "$LEDGER"
  test "$rc" -eq 0 && rc=7
else
  echo "D19O_G9_OK arm=$ARM libidwarp_so_md5=$GOT_SO digest=$GOT_DIGEST" | tee -a "$LEDGER"
fi

test -s "$LOG" && touch "$LOG.ok.${STAMP}"
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
