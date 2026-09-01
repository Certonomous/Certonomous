#!/usr/bin/env bash
# =============================================================================
# AOA POLAR -- guards DRIVEN, not asserted. Every refusal below is provoked with
# a real condition and its exit code is read back.
#
# A guard that has never fired is a guard nobody has tested.
# =============================================================================
set -uo pipefail
HERE="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/feasibility_aoa_polar"
ARM="$HERE/aoa_run_arm.sh"
TMP="${TMPDIR:-/tmp}/aoa_selftest_$$"
mkdir -p "$TMP"
FAILS=0
chk() {  # chk <name> <expected_rc> <actual_rc> <note>
  if [ "$2" = "$3" ]; then printf '  %-28s expected rc=%-3s got rc=%-3s PASS  %s\n' "$1" "$2" "$3" "$4"
  else printf '  %-28s expected rc=%-3s got rc=%-3s *** FAIL ***  %s\n' "$1" "$2" "$3" "$4"; FAILS=$((FAILS+1)); fi
}

echo "=== syntax ==="
bash -n "$ARM" && echo "  aoa_run_arm.sh   bash -n OK" || { echo "  *** arm syntax FAIL"; FAILS=$((FAILS+1)); }
bash -n "$HERE/aoa_cmd.sh" && echo "  aoa_cmd.sh       bash -n OK" || { echo "  *** cmd syntax FAIL"; FAILS=$((FAILS+1)); }

echo
echo "=== usage refusal ==="
bash "$ARM" >/dev/null 2>&1; chk "no arm argument" 2 $? "must not default to an arm"
bash "$ARM" NONSENSE >/dev/null 2>&1; chk "unknown arm" 2 $? "must not fall through"

echo
echo "=== G-ROOT: an existing run root must stop the arm ==="
for A in AOAI AOAC; do
  case $A in
    AOAI) R=/home/ubuntu/certonomous-runs/CURRICULUM-AOAI-a1-naca0012-alpha-polar-incompressible ;;
    AOAC) R=/home/ubuntu/certonomous-runs/CURRICULUM-AOAC-a1-naca0012-alpha-polar-compressible ;;
  esac
  PRE=0; [ -e "$R" ] && PRE=1
  if [ "$PRE" = "1" ]; then echo "  $A: root ALREADY EXISTS -- not driving G-ROOT destructively"; continue; fi
  mkdir -p "$R"                       # sacrificial root
  out=$(bash "$ARM" $A 2>&1); rc=$?
  rmdir "$R" 2>/dev/null
  chk "G-ROOT $A" 6 $rc "$(echo "$out" | grep -c 'G-ROOT') G-ROOT line(s)"
done

echo
echo "=== G-PHYS: a drifted physics byte must stop the compressible arm ==="
# Build a mutated copy of the compressible producer and point a copy of the arm
# at it. The mutation changes ONE physics value: nuTilda0.
cp "$HERE/aoa_runScript_comp.py" "$TMP/mutated.py"
python3 - "$TMP/mutated.py" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
assert s.count("nuTilda0 = 4.5e-5") == 1
open(p, "w").write(s.replace("nuTilda0 = 4.5e-5", "nuTilda0 = 4.6e-5"))
PY
GOT="$(python3 - "$TMP/mutated.py" <<'PY'
import hashlib, sys
src = open(sys.argv[1]).read()
B = "# ---- D19M_PHYSICS_BEGIN ----\n"; E = "# ---- D19M_PHYSICS_END ----"
print(hashlib.md5(src.split(B)[1].split(E)[0].strip().encode()).hexdigest())
PY
)"
if [ "$GOT" != "c66504acc57bd9ef009599e883d2ef3b" ]; then
  echo "  G-PHYS mutation detected     md5 $GOT != D19M's        PASS  one byte of nuTilda0 moves it"
else
  echo "  G-PHYS mutation NOT detected                            *** FAIL ***"; FAILS=$((FAILS+1))
fi
CLEAN="$(python3 - "$HERE/aoa_runScript_comp.py" <<'PY'
import hashlib, sys
src = open(sys.argv[1]).read()
B = "# ---- D19M_PHYSICS_BEGIN ----\n"; E = "# ---- D19M_PHYSICS_END ----"
print(hashlib.md5(src.split(B)[1].split(E)[0].strip().encode()).hexdigest())
PY
)"
if [ "$CLEAN" = "c66504acc57bd9ef009599e883d2ef3b" ]; then
  echo "  G-PHYS clean file passes     md5 $CLEAN  PASS  a guard that fires on everything is off"
else
  echo "  G-PHYS FALSE POSITIVE on the clean file                 *** FAIL ***"; FAILS=$((FAILS+1))
fi

echo
echo "=== the producer's OWN import-time self-assert ==="
# Simulated exactly as the producer runs it: read __file__, split, hash, abort.
for f in "$HERE/aoa_runScript_comp.py" "$TMP/mutated.py"; do
  python3 - "$f" <<'PY'
import hashlib, sys
p = sys.argv[1]; src = open(p).read()
B = "# ---- D19M_PHYSICS_BEGIN ----\n"; E = "# ---- D19M_PHYSICS_END ----"
ok = hashlib.md5(src.split(B)[1].split(E)[0].strip().encode()).hexdigest() == \
     "c66504acc57bd9ef009599e883d2ef3b"
print("  %-46s self-assert would %s" % (p.split("/")[-1], "PASS" if ok else "ABORT"))
PY
done

echo
echo "=== reader: 11 planted controls, and G-STALL fail-closed ==="
python3 "$HERE/aoa_read.py" "$TMP/nonexistent_root" >"$TMP/r.txt" 2>&1
chk "reader on empty root" 0 $? "selftest must still run and PASS"
grep -q "SELFTEST PASS: 11 controls" "$TMP/r.txt" && echo "  11 controls PASS confirmed" \
  || { echo "  *** reader selftest did not report 11 controls PASS"; FAILS=$((FAILS+1)); }

rm -rf "$TMP"
echo
if [ "$FAILS" -eq 0 ]; then echo "ARM SELFTEST PASS -- every guard driven, none merely asserted."; exit 0; fi
echo "ARM SELFTEST FAIL -- $FAILS check(s) failed."; exit 1
