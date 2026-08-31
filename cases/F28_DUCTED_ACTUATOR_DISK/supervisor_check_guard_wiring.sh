#!/usr/bin/env bash
# cfd-supervisor's OWN exercise of the guard-virgin wiring. Not the lane's suite.
# Drives the function extracted verbatim from run_f28_candidate.sh.
set -o pipefail
CAND=/home/ubuntu/Certonomous/cases/F28_DUCTED_ACTUATOR_DISK/run_f28_candidate.sh
NEW=/home/ubuntu/Certonomous/cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28_candidate.py
WORK=$(mktemp -d /tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/supchk.XXXXXX)

# THE FAIL-CLOSED LIMB IS PINNED TO THE SUPERSEDED BLOB, NOT TO WHATEVER IS
# INSTALLED.  Before installation this limb read the live `analyse_f28.py`, which
# carried `guard_virgin_case` but NO `--guard-virgin` entry point, so it exited 2
# on a virgin directory as well as a dirty one.  Installing the candidate made
# that premise false and the limb went green for a reason that had nothing to do
# with what it was testing.  A limb whose meaning changes when the tree changes
# is not a control -- so the superseded comparator is fetched BY BLOB, and the
# fail-closed property stays tested forever rather than accidentally.
LIVE="$WORK/superseded_analyse_f28.py"
# 9c223449 is the last commit before installation; its blob at the registered
# grading path IS the superseded comparator, and the md5 below is asserted, not
# assumed, so this limb cannot quietly start testing something else.
git -C /home/ubuntu/Certonomous show 9c223449:cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py > "$LIVE" 2>/dev/null
if [ "$(md5sum "$LIVE" | cut -d' ' -f1)" != "f217d293762b0a644a95f32fb63b850f" ]; then
  echo "REFUSED: could not fetch the superseded comparator blob f217d293...; the"
  echo "fail-closed limb would silently test the installed file instead."; exit 9
fi
echo "function source md5: $(md5sum "$CAND" | cut -d' ' -f1)"

# Extract the function verbatim: from its def line to the first line that is exactly '}'
FN="$WORK/fn.sh"
awk '/^guard_virgin_section_11_1\(\) \{/{f=1} f{print} f&&/^\}$/{exit}' "$CAND" > "$FN"
echo "extracted function lines: $(wc -l < "$FN")"
grep -q 'guard_virgin_section_11_1() {' "$FN" || { echo "EXTRACT FAILED"; exit 9; }

PASS=0; FAIL=0
run_limb() { # name, comparator_path_or_STUB, target_state, expect_rc, expect_text
  local name="$1" comp="$2" state="$3" exp_rc="$4" exp_txt="$5"
  local d="$WORK/$name"; mkdir -p "$d/cases/F28_DUCTED_ACTUATOR_DISK"
  case "$comp" in
    LIVE)      cp "$LIVE" "$d/cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py" ;;
    CANDIDATE) cp "$NEW"  "$d/cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py" ;;
    BLIND0)    printf '#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n' > "$d/cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py" ;;
    ALWAYS2)   printf '#!/usr/bin/env python3\nimport sys\nsys.exit(2)\n' > "$d/cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py" ;;
    MISSING)   : ;;
  esac
  [ "$comp" = MISSING ] || chmod +x "$d/cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py"

  local tgt="$d/run"
  case "$state" in
    virgin_exists) mkdir -p "$tgt" ;;
    absent)        : ;;
    has_zero)      mkdir -p "$tgt/0" ;;
    has_time)      mkdir -p "$tgt/250" ;;
    has_frac_time) mkdir -p "$tgt/0.5" ;;
    has_pp)        mkdir -p "$tgt/postProcessing" ;;
  esac

  local out rc
  out=$( REPO="$d" CASE_ID=F28_DUCTED_ACTUATOR_DISK PHASE=assemble RUN_DIR="$tgt" \
    bash -c '
      abort() { echo "ABORT: $*" >&2; exit 1; }
      source '"$FN"'
      guard_virgin_section_11_1 "$RUN_DIR"
      echo "GUARD_RETURNED_0"
    ' 2>&1 )
  rc=$?
  local ok=1
  [ "$rc" = "$exp_rc" ] || ok=0
  if [ -n "$exp_txt" ]; then echo "$out" | grep -qF "$exp_txt" || ok=0; fi
  if [ "$ok" = 1 ]; then PASS=$((PASS+1)); printf 'PASS  %-22s rc=%s\n' "$name" "$rc"
  else FAIL=$((FAIL+1)); printf 'FAIL  %-22s rc=%s (want %s / "%s")\n      out: %s\n' \
       "$name" "$rc" "$exp_rc" "$exp_txt" "$(echo "$out" | tr '\n' ' ' | cut -c1-260)"; fi
  # side-effect assertion: the guard must never create the target
  if [ "$state" = absent ] && [ -e "$tgt" ]; then
    FAIL=$((FAIL+1)); echo "FAIL  $name CREATED THE TARGET DIRECTORY"; fi
}

echo "--- fail-closed against the CURRENTLY INSTALLED comparator ---"
run_limb live_cannot_distinguish LIVE virgin_exists 1 "CANNOT DISTINGUISH"

echo "--- with the candidate installed ---"
run_limb cand_virgin_exists CANDIDATE virgin_exists 0 "VIRGIN"
run_limb cand_absent        CANDIDATE absent        0 "VIRGIN"
run_limb cand_has_zero      CANDIDATE has_zero      1 "THE VIRGIN-CASE GUARD REFUSED"
run_limb cand_has_time      CANDIDATE has_time      1 "THE VIRGIN-CASE GUARD REFUSED"
run_limb cand_frac_time     CANDIDATE has_frac_time 1 "THE VIRGIN-CASE GUARD REFUSED"

echo "--- over-refusal check: a non-time subdir must NOT trip the guard ---"
run_limb cand_postproc_ok   CANDIDATE has_pp        0 "VIRGIN"

echo "--- planted controls on the guard itself ---"
run_limb planted_blind_zero BLIND0  has_zero        1 "GUARD IS BLIND"
run_limb planted_always_two ALWAYS2 virgin_exists   1 "CANNOT DISTINGUISH"
run_limb no_instrument      MISSING virgin_exists   1 "has no instrument"

echo "--- probe-tree hygiene: no f28_guard_probe.* left behind anywhere ---"
LEFT=$(ls -d /tmp/f28_guard_probe.* "$WORK"/f28_guard_probe.* 2>/dev/null | wc -l)
if [ "$LEFT" = "0" ]; then PASS=$((PASS+1)); echo "PASS  probe_tree_cleanup    left=0"
else FAIL=$((FAIL+1)); echo "FAIL  probe_tree_cleanup    left=$LEFT"; fi

echo
echo "SUPERVISOR EXERCISE: $PASS pass, $FAIL fail"
rm -rf "$WORK" 2>/dev/null
[ "$FAIL" = 0 ]
