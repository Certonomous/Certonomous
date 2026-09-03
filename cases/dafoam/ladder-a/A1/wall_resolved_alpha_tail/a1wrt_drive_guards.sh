#!/usr/bin/env bash
# =============================================================================
# A1WRT STANDING GUARD SUITE -- drives every control this item has, on this box,
# at this moment.  ZERO CONTAINERS, ZERO COMPUTE, and it never writes inside
# A1WRT's registered run root.
#
# WHY IT IS A COMMITTED FILE AND NOT A SCRATCH SCRIPT.  It began life in a
# session scratchpad, which is wiped and is never a handoff channel (CLAUDE.md
# rule 13 / L-186).  A guard suite that only its author can re-drive is a claim
# about one box at one moment, not evidence a successor can check.  Promoted on
# the dafoam-supervisor's ruling, 2026-09-03.
#
# WHAT IT DRIVES:
#   the three instrument selftests, under BOTH `python3` and `python3 -O`
#   S0b  -- the controlDict deriver is pinned AND driven at launch   (3 legs)
#   S5b  -- the FFD staging                                          (5 legs)
#   S5c  -- the decomposeParDict staging                             (5 legs)
#
# THE SHELL BLOCKS ARE EXTRACTED FROM a1wrt_run_unit.sh'S OWN BYTES at run time,
# between its section markers -- never retyped here, so this harness cannot drift
# away from the launcher it claims to test.  The constants it drives them with
# are likewise READ OUT OF the launcher, not restated.
#
# NOT RUN IS ITS OWN COLUMN.  A leg that cannot be driven is never folded into
# PASS and never into FAIL; the closing line names the count.
#
# EXIT: 0 all driven legs as registered  |  1 a mismatch  |  2 an extraction
# refusal (the launcher's shape moved and this harness will not guess)
# =============================================================================
set -uo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LAUNCHER="$HERE/a1wrt_run_unit.sh"
WORKDIR=$(mktemp -d -t a1wrt_guards_XXXXXX) || { echo "ABORT cannot mktemp"; exit 2; }
trap 'rm -rf "$WORKDIR"' EXIT

PASS=0; FAIL=0; NOTRUN=0
ok()      { PASS=$((PASS+1));   printf '  %-30s %s\n' "$1" "PASS"; [ -n "${2:-}" ] && printf '      %s\n' "$2"; return 0; }
bad()     { FAIL=$((FAIL+1));   printf '  %-30s %s\n' "$1" "FAIL"; [ -n "${2:-}" ] && printf '      %s\n' "$2"; return 0; }
skipped() { NOTRUN=$((NOTRUN+1)); printf '  %-30s %s\n' "$1" "NOT RUN"; printf '      %s\n' "$2"; return 0; }

test -f "$LAUNCHER" || { echo "ABORT the launcher is absent at $LAUNCHER"; exit 2; }

# ---------------------------------------------------------------------------
# extract_block MARKER_START MARKER_END OUTFILE WANT_MD5SUM_LINES
# Refuses rather than guessing if the launcher's shape has moved.
# ---------------------------------------------------------------------------
extract_block() {
  local a="$1" b="$2" out="$3" want="$4" n
  awk -v A="$a" -v B="$b" 'index($0,A)==1{f=1} index($0,B)==1{f=0} f' "$LAUNCHER" > "$out"
  test -s "$out" || { echo "EXTRACT REFUSED: no block between '$a' and '$b'"; exit 2; }
  n=$(grep -c 'md5sum -c' "$out")
  test "$n" -eq "$want" || {
    echo "EXTRACT REFUSED: expected $want 'md5sum -c' assertions in the block at '$a', found $n."
    echo "  The launcher's shape has MOVED.  This harness refuses to drive a block"
    echo "  it can no longer recognise rather than reporting a pass it did not earn."
    exit 2; }
  echo "  extracted $(wc -l < "$out" | tr -d ' ') lines, $n md5 assertions"
}

# read a constant OUT OF the launcher; $A1WR_ROOT is expanded from the launcher too
launcher_const() {
  local v="$1" raw root
  raw=$(grep -oE "^$v=\"?[^\"#]*" "$LAUNCHER" | head -1 | sed "s/^$v=//; s/^\"//; s/[[:space:]]*$//")
  root=$(grep -oE '^A1WR_ROOT=[^[:space:]#]+' "$LAUNCHER" | head -1 | cut -d= -f2-)
  printf '%s' "${raw/\$A1WR_ROOT/$root}"
}

# ---------------------------------------------------------------------------
# run_leg NAME EXPECTED_RC BLOCKFILE  (caller exports the leg's environment)
# ---------------------------------------------------------------------------
run_leg() {
  local name="$1" want="$2" blk="$3" out rc
  out=$(bash -c '
    set -uo pipefail
    WORK="$W"; STAGE_EVID="$W/evid.txt"; : > "$STAGE_EVID"
    stage_say() { echo "$*"; echo "$*" >> "$STAGE_EVID"; }
    if [ -n "${CORRUPT_CP:-}" ]; then cp() { command cp "$1" "$2" && printf "CORRUPTED" >> "$2"; }; fi
    if [ -z "${LEAVE_UNSET:-}" ]; then
      FFD_SRC="${L_FFD_SRC:-}"; MD5_FFD="${L_MD5_FFD:-}"
      DPD_SRC="${L_DPD_SRC:-}"; MD5_DPD="${L_MD5_DPD:-}"
      HERE="${L_HERE:-}";       MD5_CONTROLDICT="${L_MD5_CD:-}"
    fi
    source "$B"' 2>&1)
  rc=$?
  if [ "$rc" = "$want" ]; then ok "$name" "rc=$rc as registered :: $(printf '%s' "$out" | grep -aE 'ABORT|OK' | head -1 | cut -c1-96)"
  else bad "$name" "rc=$rc, REGISTERED $want :: $(printf '%s' "$out" | tail -1 | cut -c1-96)"; fi
}

echo "A1WRT STANDING GUARD SUITE"
echo "launcher: $LAUNCHER"
echo "launcher md5 (recorded, NOT pinned here -- the registration owns the pin):"
echo "  $(md5sum "$LAUNCHER" | cut -d' ' -f1)"
echo

# =============================================================================
echo "[1] INSTRUMENT SELFTESTS -- both interpreters"
# =============================================================================
for f in a1wrt_patch_assert.py a1wrt_read.py a1wrt_controldict.py; do
  if [ ! -f "$HERE/$f" ]; then
    skipped "$f" "absent at $HERE/$f -- no verdict is taken"; continue
  fi
  for P in "python3" "python3 -O"; do
    if $P "$HERE/$f" --selftest > "$WORKDIR/st.out" 2>&1; then
      ok "$f [$P]" "$(grep -aE '^SELFTEST (PASS|NOT RUN)' "$WORKDIR/st.out" | tr '\n' ' ' | cut -c1-96)"
    else
      bad "$f [$P]" "rc!=0 :: $(tail -1 "$WORKDIR/st.out" | cut -c1-96)"
    fi
  done
done
echo

# =============================================================================
echo "[2] S0b -- the deriver is PINNED AND DRIVEN at launch"
# =============================================================================
extract_block '# ---- S0b:' '# ---- S1:' "$WORKDIR/s0b.sh" 1
L_MD5_CD=$(grep -oE '^MD5_CONTROLDICT=[0-9a-f]+' "$LAUNCHER" | cut -d= -f2)
DISK_CD=$(md5sum "$HERE/a1wrt_controldict.py" 2>/dev/null | cut -d' ' -f1)
if [ -z "$L_MD5_CD" ] || [ -z "$DISK_CD" ]; then
  skipped "S0b (all 3 legs)" "MD5_CONTROLDICT or the instrument is unreadable"
else
  [ "$L_MD5_CD" = "$DISK_CD" ] && echo "  the launcher's pin == the instrument on disk: $DISK_CD" \
                               || echo "  !! launcher pin $L_MD5_CD != disk $DISK_CD"
  W=$WORKDIR/a; mkdir -p "$W"; export W B="$WORKDIR/s0b.sh" L_HERE="$HERE" L_MD5_CD
  unset CORRUPT_CP LEAVE_UNSET
  run_leg "S0b correct pin+instrument" 0 "$WORKDIR/s0b.sh"
  export L_MD5_CD=deadbeefdeadbeefdeadbeefdeadbeef
  run_leg "S0b WRONG pin" 4 "$WORKDIR/s0b.sh"
  # a mutant whose pin MATCHES but whose own controls fail
  MUT=$WORKDIR/mut; mkdir -p "$MUT"
  sed 's/^DERIVED_MD5 = "8/DERIVED_MD5 = "9/' "$HERE/a1wrt_controldict.py" > "$MUT/a1wrt_controldict.py"
  if cmp -s "$MUT/a1wrt_controldict.py" "$HERE/a1wrt_controldict.py"; then
    skipped "S0b mutant instrument" "PLANT DID NOT LAND -- DERIVED_MD5 not found in the expected form"
  else
    echo "      PLANT LANDED: DERIVED_MD5 corrupted in the mutant deriver"
    export L_HERE="$MUT" L_MD5_CD=$(md5sum "$MUT/a1wrt_controldict.py" | cut -d' ' -f1)
    run_leg "S0b pin OK, controls BROKEN" 6 "$WORKDIR/s0b.sh"
    export L_HERE="$HERE"
  fi
fi
echo

# =============================================================================
# drive_staging_block  LABEL  MARKER_START  MARKER_END  SRCVAR  MD5VAR  DEST
#   five legs: undefined / absent / corrupt source / corrupt copy / correct
# =============================================================================
drive_staging_block() {
  local label="$1" ma="$2" mb="$3" srcvar="$4" md5var="$5" dest="$6"
  local blk="$WORKDIR/${label}.sh" src md5 got
  extract_block "$ma" "$mb" "$blk" 2
  src=$(launcher_const "$srcvar"); md5=$(launcher_const "$md5var")
  echo "  launcher says $srcvar=$src"
  echo "  launcher says $md5var=$md5"
  if [ ! -f "$src" ]; then
    skipped "$label (all 5 legs)" "the registered source is absent: $src"; return
  fi
  got=$(md5sum "$src" | cut -d' ' -f1)
  [ "$got" = "$md5" ] && echo "  on disk: $got == the launcher's pin" \
                      || echo "  !! on disk: $got != the launcher's pin $md5"
  export B="$blk"; unset CORRUPT_CP LEAVE_UNSET L_FFD_SRC L_MD5_FFD L_DPD_SRC L_MD5_DPD

  # L0 -- the constants UNDEFINED under `set -u`.  This is the blocker that
  # stopped the 2026-09-03 repair from launching: rc 127 is OUTSIDE the
  # launcher's whole registered exit-code set (0/3/4/5/6/7/64/65), the message
  # is a raw bash error, and NO stage_say reaches the record.
  W=$(mktemp -d -p "$WORKDIR"); export W LEAVE_UNSET=1
  run_leg "$label L0 undefined vars" 127 "$blk"
  if [ -s "$W/evid.txt" ]; then bad "$label L0 evidence file" "NON-EMPTY -- a stage_say did run"
  else ok "$label L0 evidence file" "EMPTY -- no stage_say, no ABORT message ever reaches the record"; fi
  unset LEAVE_UNSET

  # L1 -- absent source
  W=$(mktemp -d -p "$WORKDIR"); export W
  export L_FFD_SRC="$W/no/such/file" L_MD5_FFD="$md5" L_DPD_SRC="$W/no/such/file" L_MD5_DPD="$md5"
  run_leg "$label L1 absent source" 5 "$blk"

  # L2 -- corrupted source, PLANTED and asserted to have landed
  W=$(mktemp -d -p "$WORKDIR"); export W
  cp "$src" "$W/bad"; printf 'x' >> "$W/bad"
  if [ "$(md5sum < "$W/bad" | cut -d' ' -f1)" = "$md5" ]; then
    skipped "$label L2 corrupted source" "PLANT DID NOT LAND -- the corrupted copy still hashes to the pin"
  else
    echo "      PLANT LANDED: corrupted source md5 $(md5sum < "$W/bad" | cut -d' ' -f1) != pin"
    export L_FFD_SRC="$W/bad" L_MD5_FFD="$md5" L_DPD_SRC="$W/bad" L_MD5_DPD="$md5"
    run_leg "$label L2 corrupt source" 4 "$blk"
  fi

  # L3 -- the copy lands corrupted; the STAGED-side assertion is what catches it
  W=$(mktemp -d -p "$WORKDIR"); export W CORRUPT_CP=1
  export L_FFD_SRC="$src" L_MD5_FFD="$md5" L_DPD_SRC="$src" L_MD5_DPD="$md5"
  mkdir -p "$W/system"
  run_leg "$label L3 copy lands corrupt" 4 "$blk"
  unset CORRUPT_CP

  # L4 -- the correct source stages and reads back
  W=$(mktemp -d -p "$WORKDIR"); export W
  export L_FFD_SRC="$src" L_MD5_FFD="$md5" L_DPD_SRC="$src" L_MD5_DPD="$md5"
  mkdir -p "$W/system"
  run_leg "$label L4 correct source" 0 "$blk"
  got=$(md5sum "$W/$dest" 2>/dev/null | cut -d' ' -f1)
  if [ "$got" = "$md5" ]; then ok "$label L4 staged copy" "$dest md5 $got == pin"
  else bad "$label L4 staged copy" "$dest md5 '$got' != pin $md5"; fi
  unset L_FFD_SRC L_MD5_FFD L_DPD_SRC L_MD5_DPD
}

echo "[3] S5b -- the FFD staging"
drive_staging_block S5b '# ---- S5b:' '# ---- S5c:' FFD_SRC MD5_FFD FFD/wingFFD.xyz
echo
echo "[4] S5c -- the decomposeParDict staging"
drive_staging_block S5c '# ---- S5c:' '# ---- S6:' DPD_SRC MD5_DPD system/decomposeParDict
echo

# =============================================================================
TOT=$((PASS+FAIL))
echo "============================================================"
echo "A1WRT GUARD SUITE: $PASS/$TOT legs as registered, $FAIL mismatched, $NOTRUN NOT RUN"
if [ "$NOTRUN" -gt 0 ]; then
  echo "  NOT RUN legs are named above.  They are NOT counted as PASS and NOT as FAIL."
fi
[ "$FAIL" -eq 0 ] || exit 1
exit 0
