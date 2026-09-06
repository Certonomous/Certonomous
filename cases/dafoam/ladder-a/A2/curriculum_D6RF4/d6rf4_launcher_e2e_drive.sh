#!/usr/bin/env bash
# =============================================================================
# d6rf4_launcher_e2e_drive.sh
#
# END-TO-END DRIVE of d6rf4_run_arm.sh, arm P_conv, from the run-root mode check
# at :515 THROUGH the `docker run` at ~:1281 and the post-container ledger
# finalize, WITH THE CONTAINER MOCKED.  It is the missing coverage: the
# pre-freeze 27/27 launcher guard drive (d6rf4_launcher_guard_drive.py) covered
# NONE of the staging -> delivery -> container path, so every guard on that path
# was a latent false-refusal that only fired live, one per tick.  This drives
# the whole path once, on VALID staged input, and ENUMERATES every guard that
# refuses.
#
# NOTHING REAL RUNS.  No real solver, no real container: `sudo`, `docker` and
# `mpirun` are PATH-shimmed mocks; the mock `docker run` writes the field/log/
# ledger artefacts a completed arm would, so the post-container path is
# exercised too.  The registered run root is NEVER touched -- the drive builds
# an EPHEMERAL sandbox under mktemp and points a NEUTERED COPY of the launcher
# at it.  The neutering is FOUR path constants and nothing else, asserted by a
# diff that must show exactly four changed lines; the guard LOGIC is untouched.
#
# The real, byte-correct fixture is copied READ-ONLY from D6R's preserved O_mp
# and from this item's registered `base/`, so the md5-pinned identity checks
# (S3 mesh, :518-527 instruments, S9 fvSolution) pass on REAL bytes -- the drive
# does not relax them and does not fabricate md5s.
#
# USAGE:  bash d6rf4_launcher_e2e_drive.sh [--keep]
#   --keep   leave the ephemeral sandbox on disk for inspection (path printed)
#
# The launcher under test is always the LIVE item file below, so re-running
# after a fix shows the fixed behaviour.  Exit 0 iff the full path reaches the
# mocked container and finalises the ledger AND every G-DELIVERY both-direction
# scenario lands on its expected token.
# =============================================================================
set -uo pipefail

ITEMDIR="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6RF4"
LAUNCHER="$ITEMDIR/d6rf4_run_arm.sh"
REAL_OMP="/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp"
REAL_BASE="/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe/base"
IMG="dafoam-idwarp-rot:v1"
IMG_PATCHED_DIGEST="sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"
IMG_SHIPPED_DIGEST="sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"

KEEP=no
[ "${1:-}" = "--keep" ] && KEEP=yes

fail() { echo "DRIVE-ERROR $*" >&2; exit 99; }
[ -f "$LAUNCHER" ] || fail "launcher absent: $LAUNCHER"
[ -d "$REAL_OMP" ] || fail "real source absent: $REAL_OMP"
[ -d "$REAL_BASE" ] || fail "real base absent: $REAL_BASE"

SBX=$(mktemp -d -t d6rf4_e2e.XXXXXX) || fail "mktemp"
echo "==== d6rf4 launcher e2e drive ===="
echo "sandbox: $SBX"
echo "launcher-under-test md5: $(md5sum "$LAUNCHER" | cut -d' ' -f1)"
cleanup() { [ "$KEEP" = yes ] && { echo "sandbox KEPT: $SBX"; return; }; rm -rf "$SBX"; }
trap cleanup EXIT

RUNS="$SBX/runs"
REG_BASE="$RUNS/CURRICULUM-D6RF4-a2-wing-convergence-probe"
D6R_ROOT="$RUNS/CURRICULUM-D6R-a2-wing-multipoint"
D4_ROOT="$RUNS/CURRICULUM-D4-a2-wing-cdmin"
SRC="$D6R_ROOT/O_mp"
mkdir -p "$RUNS" "$SRC" "$D4_ROOT/O" "$REG_BASE"

# ---------------------------------------------------------------------------
# 1. FIXTURE -- byte-correct, copied read-only from the real trees.
# ---------------------------------------------------------------------------
echo "-- building fixture (read-only copy of real O_mp subtrees + item instruments) --"
# top-level of O_mp
cp -a "$REAL_OMP/0" "$REAL_OMP/0.orig" "$REAL_OMP/constant" "$REAL_OMP/system" \
      "$REAL_OMP/OptView.hst" "$SRC/" || fail "copy O_mp top"
# the base-copy .py files that arrive with S4's cp -a and that G-DELIVERY check-B globs
for f in d4_extract_endpoint.py d6r_extract_endpoint.py d6r_fd_endpoint.py \
         d6r_opt_runScript.py d6r_ref_off.py; do
  [ -f "$REAL_OMP/$f" ] && cp -a "$REAL_OMP/$f" "$SRC/"
done
for mp in mp04 mp05 mp06; do
  mkdir -p "$SRC/$mp/processor0"
  cp -a "$REAL_OMP/$mp/0" "$REAL_OMP/$mp/0.orig" "$REAL_OMP/$mp/constant" \
        "$REAL_OMP/$mp/system" "$SRC/$mp/" || fail "copy $mp"
  [ -f "$REAL_OMP/$mp/dRdWColoring_4.bin" ] && cp -a "$REAL_OMP/$mp/dRdWColoring_4.bin" "$SRC/$mp/"
  # a faithful subset of processor0: 0 (kept, gzipped fields), two 0.* dirs
  # (SOURCE-INTACT needs >1 matching 0.*), one numeric time dir (S5 drops it)
  for td in 0 0.0001 0.0002 1000 constant; do
    [ -e "$REAL_OMP/$mp/processor0/$td" ] && cp -a "$REAL_OMP/$mp/processor0/$td" "$SRC/$mp/processor0/"
  done
done
# an OptView.hst under mp04/processor0? not required.  D4 hst src (unused for P_conv)
echo "dummy-hst" > "$D4_ROOT/O/OptView.hst"

# item's registered base/  (holds base/constant/polyMesh/points.gz md5 anchor)
cp -a "$REAL_BASE" "$REG_BASE/base" || fail "copy base"
# the instruments + both fvSolution files, from the item dir (real, md5-pinned bytes)
for f in d6rf4_opt_runScript.py d6rf4_fd_endpoint.py d6rf4_extract_endpoint.py \
         d6rf4_endpoint_locus.py d6rf4_endpoint_physical.py d6rf4_units_assert.py \
         d6rf4_anchor_gate.py d6rf4_fvSolution_TIGHT d6rf4_fvSolution_D6RF3_ORIGINAL; do
  cp -a "$ITEMDIR/$f" "$REG_BASE/$f" || fail "stage instrument $f"
done
# ledger seed (ITEM line only, as the real stager writes) + mode 777 (the :515 check)
printf 'ITEM=D6RF4\n' > "$REG_BASE/ledger.txt"
chmod -R u+rwX,go+rX "$REG_BASE"
chmod 777 "$REG_BASE"

# ---------------------------------------------------------------------------
# 2. NEUTERED LAUNCHER -- exactly four environment path constants redirected.
# ---------------------------------------------------------------------------
NEUT="$SBX/launcher.neutered.sh"
sed \
  -e "s#^REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe#REGISTERED_BASE=$REG_BASE#" \
  -e "s#^D6R_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint#D6R_ROOT=$D6R_ROOT#" \
  -e "s#^D4_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin#D4_ROOT=$D4_ROOT#" \
  -e "s#^RUNS_DIR=/home/ubuntu/certonomous-runs#RUNS_DIR=$RUNS#" \
  "$LAUNCHER" > "$NEUT" || fail "sed neuter"
CHANGED=$(diff "$LAUNCHER" "$NEUT" | grep -cE '^[<>]')
echo "-- neutering diff: $CHANGED changed lines (expect 8 = 4 '<' + 4 '>') --"
diff "$LAUNCHER" "$NEUT" | sed 's/^/   /'
[ "$CHANGED" = "8" ] || fail "neutering changed $CHANGED lines, not the 4 path constants -- REFUSING; the drive must not relax guard logic"

# ---------------------------------------------------------------------------
# 3. MOCK BIN -- sudo, docker (mpirun runs only inside the mocked container).
# ---------------------------------------------------------------------------
MOCKBIN="$SBX/bin"
STATE="$SBX/mockstate"
mkdir -p "$MOCKBIN" "$STATE"

cat > "$MOCKBIN/sudo" <<'SUDOEOF'
#!/usr/bin/env bash
# drop leading options (e.g. -n), then exec the rest -- docker resolves to the mock
while [ $# -gt 0 ] && [ "${1#-}" != "$1" ]; do shift; done
exec "$@"
SUDOEOF

cat > "$MOCKBIN/docker" <<DOCKEREOF
#!/usr/bin/env bash
# MOCK docker.  Handles exactly the subcommands d6rf4_run_arm.sh issues.
set -uo pipefail
STATE="$STATE"
IMG_PATCHED_DIGEST="$IMG_PATCHED_DIGEST"
IMG_SHIPPED_DIGEST="$IMG_SHIPPED_DIGEST"
DOCKEREOF
cat >> "$MOCKBIN/docker" <<'DOCKEREOF'
sub="${1:-}"; shift || true
case "$sub" in
  ps)
    # census / live-arm / sampler wait -- always report NO containers
    exit 0 ;;
  image)
    # image inspect --format '{{index .RepoDigests 0}}' <IMG>
    img=""; for a in "$@"; do img="$a"; done
    case "$img" in
      dafoam-idwarp-rot:v1)       echo "$img@$IMG_PATCHED_DIGEST" ;;
      dafoam/opt-packages:latest) echo "$img@$IMG_SHIPPED_DIGEST" ;;
      *) exit 1 ;;
    esac
    exit 0 ;;
  run)
    # parse --name, -v host:/mnt, -w /mnt/<wb>, and the image (token before 'bash')
    name=""; vol=""; wdir=""; img=""; prev=""
    for a in "$@"; do
      case "$prev" in
        --name) name="$a" ;;
        -v)     vol="$a" ;;
        -w)     wdir="$a" ;;
      esac
      [ "$a" = "bash" ] && [ -z "$img" ] && img="$prevtok"
      prevtok="$a"; prev="$a"
    done
    hostbase="${vol%%:*}"
    wb="$(basename "$wdir")"
    hostwork="$hostbase/$wb"
    # --- write the artefacts a COMPLETED arm would produce (mocked physics) ---
    if [ -d "$hostwork" ]; then
      printf '{"twist":[0.0],"shape":[0.0],"patchV_cl04":[0.0]}\n' > "$hostwork/d6rf4_endpoint_dvs.json" 2>/dev/null || true
      printf '{"mode":"P_conv","status":"MOCK_COMPLETED"}\n'        > "$hostwork/d6rf4_fd_endpoint.json" 2>/dev/null || true
      printf '{"mode":"F5_loose","status":"MOCK_COMPLETED"}\n'      > "$hostwork/d6rf4_f5_endpoint.json" 2>/dev/null || true
      mkdir -p "$hostwork/mp04/1000" 2>/dev/null || true
      printf 'MOCK U field\n' > "$hostwork/mp04/1000/U" 2>/dev/null || true
    fi
    # --- state + canned container log ---
    now=$(date -u +%Y-%m-%dT%H:%M:%S.000000000Z)
    fin=$(date -u -d '+3 seconds' +%Y-%m-%dT%H:%M:%S.000000000Z 2>/dev/null || echo "$now")
    { echo "exit=0"; echo "oom=false"; echo "running=false"; echo "started=$now"; echo "finished=$fin"; } > "$STATE/$name"
    {
      echo "D4S_CONTAINER_UID: 0"
      echo "D4S_IDWARP_IMPORTED_FROM: /home/dafoamuser/dafoam/repos/idwarp/idwarp/__init__.py"
      echo "D4S_IDWARP_SO_MD5: 00112233445566778899aabbccddeeff"
      echo "D4S_DEADLINE_IN_CONTAINER_S: 720"
      echo "D6RF4_FVSOLUTION_INSTALLED leg=L1_L2 md5=0ac5bd00c63b9109d22a8e73b0795aa4 sites=4 file=d6rf4_fvSolution_TIGHT"
      echo "D6RF4_UNITS_PASS design vector physical, all components in [-1,1]"
      echo "Time = 1000"
      echo "End"
      echo "D6RF4_FVSOLUTION_INSTALLED leg=L3 md5=9e2669956be778acf7e7d8aa67a90ff6 sites=4 file=d6rf4_fvSolution_D6RF3_ORIGINAL"
      echo "End"
    } > "$STATE/$name.log"
    echo "mockcid_$name"
    exit 0 ;;
  inspect)
    fmt=""; name=""; prev=""
    for a in "$@"; do [ "$prev" = "--format" ] && fmt="$a"; name="$a"; prev="$a"; done
    st="$STATE/$name"
    [ -f "$st" ] || { exit 1; }
    ex=$(sed -n 's/^exit=//p' "$st"); oom=$(sed -n 's/^oom=//p' "$st")
    run=$(sed -n 's/^running=//p' "$st"); sta=$(sed -n 's/^started=//p' "$st")
    fic=$(sed -n 's/^finished=//p' "$st")
    case "$fmt" in
      *Running*)                     echo "$run" ;;
      *ExitCode*OOMKilled*)          echo "$ex $oom" ;;
      *ExitCode*)                    echo "$ex" ;;
      *StartedAt*)                   echo "$sta" ;;
      *FinishedAt*)                  echo "$fic" ;;
      *) echo "" ;;
    esac
    exit 0 ;;
  logs)
    name=""; for a in "$@"; do name="$a"; done
    [ -f "$STATE/$name.log" ] && cat "$STATE/$name.log"
    exit 0 ;;
  stop) exit 0 ;;
  rm)
    name=""; for a in "$@"; do name="$a"; done
    rm -f "$STATE/$name" "$STATE/$name.log" 2>/dev/null
    exit 0 ;;
  *) exit 0 ;;
esac
DOCKEREOF
chmod +x "$MOCKBIN/sudo" "$MOCKBIN/docker"

# ---------------------------------------------------------------------------
# 4. RUN THE FULL LAUNCHER, VALID STAGED INPUT, MOCKED CONTAINER.
# ---------------------------------------------------------------------------
echo
echo "======================================================================="
echo "  FULL E2E RUN -- valid staged input, container mocked"
echo "======================================================================="
LOGOUT="$SBX/launcher.stdout.txt"
set +e
BASE="$REG_BASE" PATH="$MOCKBIN:$PATH" bash "$NEUT" P_conv "$IMG" > "$LOGOUT" 2>&1
E2E_RC=$?
set -e 2>/dev/null || true
echo "launcher rc = $E2E_RC"
echo "--- last 40 lines of launcher output ---"
tail -40 "$LOGOUT" | sed 's/^/   /'
echo "--- every ABORT / REFUSE line in the run ---"
grep -nE 'ABORT|REFUSE|MISSING|D6RF4_.*_PASS|D6RF4_G_DELIVERY|D6RF4_G_ANCHOR|D6RF4_G_COLD|D6RF4_CMD_LEGS|STAMP=' "$LOGOUT" | sed 's/^/   /' || true

# ---------------------------------------------------------------------------
# 5. G-DELIVERY BOTH-DIRECTION MATRIX -- the real guard code, extracted from
#    the launcher under test, run against controlled $WORK states.
#    Proves the fix PASSES on valid input and STILL REFUSES real defects.
# ---------------------------------------------------------------------------
echo
echo "======================================================================="
echo "  G-DELIVERY both-direction matrix (extracted derive_delivery)"
echo "======================================================================="
DDPY="$SBX/derive_delivery.py"
# extract the python heredoc body between PYEOF markers inside derive_delivery()
awk '/python3 - "\$\{BASH_SOURCE\[0\]\}" "\$ARM" "\$WORK" <<.PYEOF.$/{f=1;next} /^PYEOF$/{f=0} f' "$NEUT" > "$DDPY"
[ -s "$DDPY" ] || fail "could not extract derive_delivery python body"

WORK_STAGED="$REG_BASE/P_conv"     # the $WORK the full run staged
run_dd() {  # $1 = self(launcher) $2 = arm $3 = work ; prints the guard's line
  python3 "$DDPY" "$1" "$2" "$3" 2>&1
}

declare -A EXPECT RESULT
# (A) valid staged input -> OK
if [ -d "$WORK_STAGED" ]; then
  D_OK=$(run_dd "$NEUT" P_conv "$WORK_STAGED")
else
  D_OK="(no staged \$WORK -- full run aborted before staging completed)"
fi
EXPECT[valid]="OK "; RESULT[valid]="$D_OK"

# For the three refuse scenarios, work on a COPY of the staged tree so the
# defect is injected on an otherwise-valid tree.
if [ -d "$WORK_STAGED" ]; then
  # (B) a REQUIRED .py instrument made unparseable -> REFUSE-UNPARSEABLE must still fire
  W1="$SBX/work_corrupt"; cp -a "$WORK_STAGED" "$W1"
  printf '\ndef (this is not python\n' >> "$W1/d6rf4_opt_runScript.py"
  EXPECT[corrupt_py]="REFUSE-UNPARSEABLE"; RESULT[corrupt_py]="$(run_dd "$NEUT" P_conv "$W1")"

  # (C) a required delivered instrument removed -> MISSING
  W2="$SBX/work_missing"; cp -a "$WORK_STAGED" "$W2"
  rm -f "$W2/d6rf4_fd_endpoint.py"
  EXPECT[missing]="MISSING"; RESULT[missing]="$(run_dd "$NEUT" P_conv "$W2")"

  # (D) a real dangling reference planted -> REFUSE-DANGLING
  W3="$SBX/work_dangling"; cp -a "$WORK_STAGED" "$W3"
  printf 'DANGLER = "d6rf4_this_file_does_not_exist.py"\n' > "$W3/d6rf4_planted_dangler.py"
  EXPECT[dangling]="REFUSE-DANGLING"; RESULT[dangling]="$(run_dd "$NEUT" P_conv "$W3")"
else
  for k in corrupt_py missing dangling; do EXPECT[$k]="(skipped)"; RESULT[$k]="(no staged \$WORK)"; done
fi

MATRIX_OK=yes
printf '%-12s | %-20s | %s\n' scenario expect result_token
printf '%.0s-' {1..90}; echo
for k in valid corrupt_py missing dangling; do
  tok=$(printf '%s' "${RESULT[$k]}" | awk '{print $1}')
  exp="${EXPECT[$k]}"; expw=$(printf '%s' "$exp" | awk '{print $1}')
  mark=OK
  case "$exp" in
    "(skipped)") mark=SKIP ;;
    *) [ "$tok" = "$expw" ] || { mark=FAIL; MATRIX_OK=no; } ;;
  esac
  printf '%-12s | %-20s | [%s] %s\n' "$k" "$expw" "$mark" "$(printf '%s' "${RESULT[$k]}" | head -c 120)"
done

echo
echo "======================================================================="
echo "  VERDICT"
echo "======================================================================="
FULL_OK=no
grep -q "^STAMP=.* RC=0 " "$LOGOUT" && [ "$E2E_RC" = "0" ] && FULL_OK=yes
echo "full-path-to-mocked-container: $FULL_OK (rc=$E2E_RC)"
echo "g-delivery both-direction matrix clean: $MATRIX_OK"
if [ "$FULL_OK" = yes ] && [ "$MATRIX_OK" = yes ]; then
  echo "DRIVE RESULT: CLEAN -- full path reaches the mocked container and every G-DELIVERY direction lands as expected"
  exit 0
else
  echo "DRIVE RESULT: NOT CLEAN -- see the ABORT/REFUSE lines above"
  exit 1
fi
