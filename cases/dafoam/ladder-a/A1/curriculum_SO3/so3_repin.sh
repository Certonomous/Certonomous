#!/usr/bin/env bash
# =============================================================================
# SO-3 RE-PINNING.  RUN ONCE, AFTER THE LAST EDIT, ON ALL PINS TOGETHER.
#
# WHY THIS IS A SCRIPT AND NOT A HAND EDIT, AND WHY IT REFUSES TO SET A PARTIAL
# TABLE.  SO-2M LOST ITS FIRST ARM to three md5 pins inherited through an
# item-token rename: the rename rewrites the very bytes the pins pin, so they
# were STALE THE INSTANT THE RENAME RAN and they still LOOKED like pins.
# `so3_derive_from_so3ar2.sh` therefore invalidated all sixteen to a sentinel
# that CANNOT be an md5 (it is not 32 hex, so `md5sum -c` fails closed), and
# this script is the only thing that sets them.
#
# THE ORDER IS FORCED BY THE DEPENDENCY GRAPH AND IS NOT A PREFERENCE:
#   1. so3_xf.py's PRODUCER_MD5 pins so3_runScript.py  -> runScript must be final
#   2. so3_run_arm.sh's three pins include so3_xf.py   -> xf must be final (step 1)
#   3. so3_chain_driver.sh's MD5_LAUNCHER pins so3_run_arm.sh -> step 2 first
# Setting them in any other order pins a file this script is about to change,
# which is the SO-2M failure reproduced deliberately.
#
# AND THE ASSERTION THAT MAKES IT SAFE: after every write, the pin is READ BACK
# and compared against a FRESH md5 of the file it names.  A pin that agrees with
# itself in memory proves nothing.
# =============================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TUT=/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible
FAIL=0

m5() { md5sum "$1" | cut -d' ' -f1; }

setpin() {   # $1 = file to edit, $2 = pin name, $3 = file the pin names
  local F="$1" N="$2" T="$3"
  if [ ! -f "$T" ]; then echo "  ABORT $N names a file that does not exist: $T"; FAIL=1; return; fi
  local V; V=$(m5 "$T")
  sed -i -E "s#^($N)=[^ ]*#\\1=$V#" "$F"
  local GOT; GOT=$(grep -aoE "^$N=[0-9a-f]{32}" "$F" | head -1 | cut -d= -f2)
  local FRESH; FRESH=$(m5 "$T")
  if [ "$GOT" = "$FRESH" ] && [ -n "$GOT" ]; then
    printf '  [OK ] %-20s %s -> %s\n' "$N" "$GOT" "$(basename "$T")"
  else
    printf '  [FAIL] %-20s wrote [%s] but md5(%s) is [%s]\n' "$N" "$GOT" "$(basename "$T")" "$FRESH"
    FAIL=1
  fi
}

echo "SO-3 RE-PINNING -- all pins, together, after the last edit"

echo
echo "STEP 1: so3_xf.py's PRODUCER_MD5 pins so3_runScript.py"
V=$(m5 "$HERE/so3_runScript.py")
sed -i -E "s#^(PRODUCER_MD5) *= *\"[^\"]*\"#\\1 = \"$V\"#" "$HERE/so3_xf.py"
GOT=$(grep -aoE '^PRODUCER_MD5 = "[0-9a-f]{32}"' "$HERE/so3_xf.py" | head -1 | cut -d'"' -f2)
if [ "$GOT" = "$(m5 "$HERE/so3_runScript.py")" ] && [ -n "$GOT" ]; then
  printf '  [OK ] %-20s %s -> so3_runScript.py\n' PRODUCER_MD5 "$GOT"
else
  printf '  [FAIL] PRODUCER_MD5 wrote [%s]\n' "$GOT"; FAIL=1
fi

echo
echo "STEP 2: so3_run_arm.sh's staged-instrument pins (so3_xf.py is now final)"
setpin "$HERE/so3_run_arm.sh" MD5_RUNSCRIPT "$HERE/so3_runScript.py"
setpin "$HERE/so3_run_arm.sh" MD5_XF        "$HERE/so3_xf.py"
setpin "$HERE/so3_run_arm.sh" MD5_DECOMP    "$HERE/so3_decomposeParDict"

echo
echo "STEP 3: so3_chain_driver.sh's table (so3_run_arm.sh is now final)"
setpin "$HERE/so3_chain_driver.sh" MD5_LAUNCHER    "$HERE/so3_run_arm.sh"
setpin "$HERE/so3_chain_driver.sh" MD5_GRADER      "$HERE/so3_grade.py"
setpin "$HERE/so3_chain_driver.sh" MD5_RUNSCRIPT   "$HERE/so3_runScript.py"
setpin "$HERE/so3_chain_driver.sh" MD5_XF          "$HERE/so3_xf.py"
setpin "$HERE/so3_chain_driver.sh" MD5_AGG         "$HERE/so3_aggregate_memory.py"
setpin "$HERE/so3_chain_driver.sh" MD5_DECOMP      "$HERE/so3_decomposeParDict"
setpin "$HERE/so3_chain_driver.sh" MD5_STOP_MARKER "$HERE/so3_stop_marker.sh"
setpin "$HERE/so3_chain_driver.sh" MD5_STALL       "$HERE/so3_stall.py"
setpin "$HERE/so3_chain_driver.sh" MD5_AGEGUARD    "$HERE/so3_age_guard.py"

echo
echo "STEP 4: the SHIPPED TUTORIAL'S OWN INPUT BYTES, frozen because the checkout"
echo "        is not.  These are the only pins in this item that name files"
echo "        OUTSIDE the repository."
setpin "$HERE/so3_chain_driver.sh" MD5_TUT_RUNSCRIPT "$TUT/runScript.py"
setpin "$HERE/so3_chain_driver.sh" MD5_TUT_GEN       "$TUT/genAirFoilMesh.py"
setpin "$HERE/so3_chain_driver.sh" MD5_TUT_PREPROC   "$TUT/preProcessing.sh"
setpin "$HERE/so3_chain_driver.sh" MD5_TUT_PS        "$TUT/profiles/NACA0012PS.profile"
setpin "$HERE/so3_chain_driver.sh" MD5_TUT_SS        "$TUT/profiles/NACA0012SS.profile"
setpin "$HERE/so3_chain_driver.sh" MD5_TUT_FFD       "$TUT/FFD/wingFFD.xyz"

echo
echo "STEP 5: NOT ONE SENTINEL MAY SURVIVE.  A partial table is the SO2a-DRIVER-"
echo "        DEF-1 shape in the place it does the most damage -- an agreement"
echo "        control reading agreement while a file the chain executes is"
echo "        mis-pinned."
LEFT=$(grep -alE 'UNSET-PIN-SET-AFTER-THE-LAST-EDIT-FAILS-CLOSED' \
       "$HERE"/so3_chain_driver.sh "$HERE"/so3_run_arm.sh "$HERE"/so3_xf.py 2>/dev/null | tr '\n' ' ')
if [ -n "$LEFT" ]; then
  echo "  [FAIL] the sentinel survives in: $LEFT"; FAIL=1
else
  echo "  [OK ] no sentinel survives in the chain driver, the launcher or the instrument"
fi

echo
if [ "$FAIL" -eq 0 ]; then echo "SO3_REPIN OK"; else echo "SO3_REPIN FAILED"; fi
exit "$FAIL"
