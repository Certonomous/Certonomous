#!/bin/bash
# Drill every branch of backstop_triple_r2.sh in a sandbox. Asks of each branch:
# WHAT RESULT WOULD HAVE FAILED THIS TEST? -- so each case below is paired with a
# counter-case that must come out differently.
BS=/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2/backstop_triple_r2.sh
T=$(mktemp -d); PASS=0; FAIL=0
ck() { if [ "$2" = "$3" ]; then echo "  [ok ] $1"; PASS=$((PASS+1)); else echo "  [FAIL] $1  got='$2' want='$3'"; FAIL=$((FAIL+1)); fi; }

mkcase() {  # $1 = name -> echoes the sandbox dir
  d=$T/$1; mkdir -p $d/fine
  cat > $d/grade.py <<'EOF'
print("STUB GRADER OUTPUT -- the frozen grader's bytes would be here")
EOF
  echo "0" > $d/fine/rc; echo "1234.56" > $d/fine/CORE_MINUTES.txt
  echo "12345" > $d/fine/WALL_SECONDS_SOLVE.txt; echo "6" > $d/fine/RANKS.txt
  echo $d
}
run() {  # run the backstop against sandbox $1 with fast intervals
  d=$1; shift
  BS_R2=$d BS_F=$d/fine BS_G=$d/grade.py \
  BS_FROZEN_BLOB=${BLOB:-$(git hash-object $d/grade.py)} \
  BS_INC=$d/INC.out BS_DUR=$d/DUR.txt BS_LOCK=$d/.lock BS_LOG=$d/bs.log \
  BS_POLL=1 BS_MAX_WAIT_RC=${MW:-5} BS_SETTLE=0 BS_GRACE=${GR:-2} BS_GRACE_POLL=1 \
  bash $BS; echo $?
}

echo "DRILL: backstop_triple_r2.sh"

# (A) incumbent produced an artifact -> PRESERVE verbatim, grade NOTHING.
d=$(mkcase a); echo "INCUMBENT-BYTES-12345" > $d/INC.out
rc=$(run $d)
ck "A rc=0" "$rc" "0"
ck "A preserved the incumbent's bytes" "$(grep -c 'INCUMBENT-BYTES-12345' $d/DUR.txt)" "1"
ck "A record is labelled a VERBATIM COPY" "$(grep -c 'VERBATIM COPY' $d/DUR.txt)" "1"
ck "A the backstop did NOT run the grader (counter-case)" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "0"

# (B) incumbent produced NOTHING -> after grace the backstop grades, once.
d=$(mkcase b)
rc=$(run $d)
ck "B rc=0" "$rc" "0"
ck "B the backstop DID grade (counter-case to A)" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "1"
ck "B record says the incumbent produced nothing" "$(grep -c 'produced NO artifact' $d/DUR.txt)" "1"
ck "B frozen-blob check printed IDENTICAL" "$(grep -c 'IDENTICAL' $d/DUR.txt)" "1"
ck "B fine sidecars copied, not computed" "$(grep -c 'core_min=1234.56' $d/DUR.txt)" "1"

# (C) grader blob DOES NOT match the frozen pin -> REFUSE, no verdict.
d=$(mkcase c); BLOB=deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
rc=$(run $d); unset BLOB
ck "C rc=2 (REFUSE)" "$rc" "2"
ck "C record REFUSES and says NOT A RESULT" "$(grep -c 'NOT A RESULT' $d/DUR.txt)" "1"
ck "C grader was NOT run on a mismatched blob" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "0"

# (D) durable record already exists -> STAND DOWN, never overwritten (idempotent).
d=$(mkcase d); echo "PRE-EXISTING RECORD" > $d/DUR.txt; echo "INC" > $d/INC.out
rc=$(run $d)
ck "D rc=0" "$rc" "0"
ck "D pre-existing record untouched" "$(cat $d/DUR.txt)" "PRE-EXISTING RECORD"
ck "D log says STAND DOWN" "$(grep -c 'STAND DOWN: durable record already exists' $d/bs.log)" "1"

# (E) another backstop holds the lock -> STAND DOWN, no record written.
d=$(mkcase e); mkdir -p $d/.lock; echo "INC" > $d/INC.out
rc=$(run $d)
ck "E rc=0" "$rc" "0"
ck "E no record written while the claim is held" "$([ -e $d/DUR.txt ] && echo yes || echo no)" "no"
ck "E log says another backstop holds the claim" "$(grep -c 'another backstop holds the claim' $d/bs.log)" "1"

# (F) fine never writes rc -> ceiling, exit 3, NO record invented.
d=$T/f; mkdir -p $d/fine; echo 'print("x")' > $d/grade.py
rc=$(MW=3 run $d)
ck "F rc=3 (ceiling, not a verdict)" "$rc" "3"
ck "F no record invented from an unfinished run" "$([ -e $d/DUR.txt ] && echo yes || echo no)" "no"
ck "F log calls it a finding, not a timeout to absorb" "$(grep -c 'not a timeout to absorb' $d/bs.log)" "1"

# (G) the lock is RELEASED on every exit path (else a rerun would stand down forever)
for c in a b d; do
  ck "G lock released in case $c" "$([ -e $T/$c/.lock ] && echo held || echo free)" "free"
done

echo; echo "$PASS passed, $FAIL failed"
rm -rf $T
[ "$FAIL" -eq 0 ]
