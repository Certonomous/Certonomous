#!/bin/bash
# Drill every branch of backstop_triple_r2.sh in a sandbox. Asks of each branch:
# WHAT RESULT WOULD HAVE FAILED THIS TEST? -- so each case below is paired with a
# counter-case that must come out differently. A drill that only ever plants a
# COMPLETE incumbent artifact cannot distinguish the fixed script from the broken
# one (the `[ -s "$INC" ]` defect), so cases H/I/J below plant a BANNER-ONLY file
# and a partial-that-completes-mid-grace, and require opposite outcomes.
BS=/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2/backstop_triple_r2.sh
T=$(mktemp -d); PASS=0; FAIL=0
ck() { if [ "$2" = "$3" ]; then echo "  [ok ] $1"; PASS=$((PASS+1)); else echo "  [FAIL] $1  got='$2' want='$3'"; FAIL=$((FAIL+1)); fi; }

mkcase() {  # $1 = name -> echoes the sandbox dir
  d=$T/$1; mkdir -p $d/fine
  cat > $d/grade.py <<'EOF'
print("STUB GRADER OUTPUT -- the frozen grader's bytes would be here")
EOF
  echo "IMPORTED MODULE" > $d/imp.py
  echo "0" > $d/fine/rc; echo "1234.56" > $d/fine/CORE_MINUTES.txt
  echo "12345" > $d/fine/WALL_SECONDS_SOLVE.txt; echo "6" > $d/fine/RANKS.txt
  echo $d
}
# A COMPLETE incumbent artifact ends with the incumbent's own terminator line.
inc_complete_file() { { echo "### MRF R2 TRIPLE, emitted ..."; echo "INCUMBENT-BYTES-12345"; echo "### grader rc=0"; } > "$1"; }
# A BANNER-ONLY artifact is what the incumbent's shell redirect produces within
# milliseconds of starting, long before any verdict exists. It is NON-EMPTY.
inc_banner_only() { { echo "### MRF R2 TRIPLE, emitted ..."; echo "###   disk b3758cc5"; } > "$1"; }

run() {  # run the backstop against sandbox $1 with fast intervals
  d=$1; shift
  BS_R2=$d BS_F=$d/fine BS_G=$d/grade.py \
  BS_FROZEN_BLOB=${BLOB:-$(git hash-object $d/grade.py)} \
  BS_INC=$d/INC.out BS_DUR=$d/DUR.txt BS_LOCK=$d/.lock BS_LOG=$d/bs.log \
  BS_IMPORT_PINS="${PINS:-$d/imp.py=$(git hash-object $d/imp.py)}" \
  BS_EXIT_ON_CEILING=${EOC:-1} \
  BS_POLL=1 BS_MAX_WAIT_RC=${MW:-5} BS_SETTLE=0 BS_GRACE=${GR:-2} BS_GRACE_POLL=1 \
  bash $BS; echo $?
}

echo "DRILL: backstop_triple_r2.sh"

# (A) incumbent produced a COMPLETE artifact -> PRESERVE verbatim, grade NOTHING.
d=$(mkcase a); inc_complete_file $d/INC.out
rc=$(run $d)
ck "A rc=0" "$rc" "0"
ck "A preserved the incumbent's bytes" "$(grep -c 'INCUMBENT-BYTES-12345' $d/DUR.txt)" "1"
ck "A record is labelled a VERBATIM COPY" "$(grep -c 'VERBATIM COPY' $d/DUR.txt)" "1"
ck "A the backstop did NOT run the grader (counter-case)" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "0"

# (H) THE DEFECT CASE. Incumbent artifact is NON-EMPTY but has NO terminator --
# a banner and nothing else, exactly what `[ -s ]` used to accept. It must NOT be
# copied; the backstop must grade and must NAME the partial. This is the
# counter-case to (A): same file existence, opposite outcome.
d=$(mkcase h); inc_banner_only $d/INC.out
rc=$(run $d)
ck "H rc=0" "$rc" "0"
ck "H the banner-only artifact was NOT copied (the old bug would have copied it)" "$(grep -c 'INCUMBENT-BYTES-12345\|VERBATIM COPY' $d/DUR.txt)" "0"
ck "H the backstop GRADED instead" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "1"
ck "H the record names the artifact as PARTIAL" "$(grep -c 'PARTIAL artifact' $d/DUR.txt)" "1"
ck "H the record quotes the partial's byte count" "$(grep -cE '^#   [0-9]+ bytes, NO' $d/DUR.txt)" "1"
ck "H the record quotes the partial's last line" "$(grep -c 'its last line was: ###   disk b3758cc5' $d/DUR.txt)" "1"
ck "H the log says the partial was deliberately not copied" "$(grep -c 'partial is NOT copied' $d/bs.log)" "1"

# (I) the incumbent is PARTIAL when grace opens and COMPLETES during it -> the
# poll must notice and PRESERVE. This is what proves inc_complete is a live test
# and not a one-shot verdict taken at the first poll.
d=$(mkcase i); inc_banner_only $d/INC.out
( sleep 3; inc_complete_file $d/INC.out ) &
rc=$(GR=12 run $d); wait
ck "I rc=0" "$rc" "0"
ck "I the completed artifact WAS preserved" "$(grep -c 'INCUMBENT-BYTES-12345' $d/DUR.txt)" "1"
ck "I the backstop did NOT grade (counter-case to H)" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "0"

# (B) incumbent produced NOTHING AT ALL -> grade, and say ABSENT not PARTIAL.
d=$(mkcase b)
rc=$(run $d)
ck "B rc=0" "$rc" "0"
ck "B the backstop DID grade" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "1"
ck "B record says the incumbent produced NO artifact" "$(grep -c 'produced NO artifact' $d/DUR.txt)" "1"
ck "B record does NOT mis-describe absent as partial (counter-case to H)" "$(grep -c 'PARTIAL artifact' $d/DUR.txt)" "0"
ck "B frozen-blob check printed IDENTICAL" "$(grep -c 'IDENTICAL -- the frozen grader is the file that grades' $d/DUR.txt)" "1"
ck "B fine sidecars copied, not computed" "$(grep -c 'core_min=1234.56' $d/DUR.txt)" "1"

# (C) grader blob DOES NOT match the frozen pin -> REFUSE, no verdict.
d=$(mkcase c); BLOB=deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
rc=$(run $d); unset BLOB
ck "C rc=2 (REFUSE)" "$rc" "2"
ck "C record REFUSES and says NOT A RESULT" "$(grep -c 'NOT A RESULT' $d/DUR.txt)" "1"
ck "C grader was NOT run on a mismatched blob" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "0"

# (D) durable record already exists -> STAND DOWN, never overwritten (idempotent).
d=$(mkcase d); echo "PRE-EXISTING RECORD" > $d/DUR.txt; inc_complete_file $d/INC.out
rc=$(run $d)
ck "D rc=0" "$rc" "0"
ck "D pre-existing record untouched" "$(cat $d/DUR.txt)" "PRE-EXISTING RECORD"
ck "D log says STAND DOWN" "$(grep -c 'STAND DOWN: durable record already exists' $d/bs.log)" "1"

# (E) a LIVE backstop holds the lock -> STAND DOWN, no record written.
d=$(mkcase e); mkdir -p $d/.lock; sleep 30 & LIVE=$!; echo $LIVE > $d/.lock/pid
inc_complete_file $d/INC.out
rc=$(run $d)
ck "E rc=0" "$rc" "0"
ck "E no record written while a LIVE owner holds the claim" "$([ -e $d/DUR.txt ] && echo yes || echo no)" "no"
ck "E log names the live owner pid" "$(grep -c "live owner pid $LIVE" $d/bs.log)" "1"
ck "E a LIVE lock is NOT reclaimed (counter-case to J)" "$(grep -c 'STALE LOCK RECLAIMED' $d/bs.log)" "0"
kill $LIVE 2>/dev/null; wait $LIVE 2>/dev/null

# (J) a STALE lock -- owner pid recorded but DEAD -> reclaim, loudly, and proceed.
# Without this the backstop is silently disarmed forever after any SIGKILL.
d=$(mkcase j); mkdir -p $d/.lock
sleep 0.1 & DEAD=$!; wait $DEAD 2>/dev/null; echo $DEAD > $d/.lock/pid
rc=$(run $d)
ck "J rc=0" "$rc" "0"
ck "J the stale lock was RECLAIMED" "$(grep -c 'STALE LOCK RECLAIMED' $d/bs.log)" "1"
ck "J the reclamation names the dead pid" "$(grep -c "held by pid '$DEAD'" $d/bs.log)" "1"
ck "J and the backstop then actually produced the record" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "1"

# (K) a lock dir with NO pid file (a pre-fix lock) -> also stale, also reclaimed.
d=$(mkcase k); mkdir -p $d/.lock
rc=$(run $d)
ck "K rc=0" "$rc" "0"
ck "K a pid-less lock is reclaimed" "$(grep -c 'STALE LOCK RECLAIMED' $d/bs.log)" "1"
ck "K and it says no pid was recorded" "$(grep -c '<none recorded>' $d/bs.log)" "1"

# (F) fine never writes rc -> ceiling, exit 3, NO record invented.
d=$T/f; mkdir -p $d/fine; echo 'print("x")' > $d/grade.py; echo "IMPORTED MODULE" > $d/imp.py
rc=$(MW=3 run $d)   # EXIT_ON_CEILING defaults to 1
ck "F rc=3 (ceiling, not a verdict)" "$rc" "3"
ck "F no record invented from an unfinished run" "$([ -e $d/DUR.txt ] && echo yes || echo no)" "no"
ck "F log calls it a finding, not a timeout to absorb" "$(grep -c 'not a timeout to absorb' $d/bs.log)" "1"


# (L) AN IMPORTED GRADING MODULE CHANGED after the pin -> REFUSE. Nothing else in
# the chain would notice: on_triple.sh hashes only the top-level grader, and the
# top-level grader verifies no blob of its own imports.
d=$(mkcase l)
rc=$(PINS="$d/imp.py=deadbeefdeadbeefdeadbeefdeadbeefdeadbeef" run $d)
ck "L rc=2 (REFUSE on a changed import)" "$rc" "2"
ck "L record says NOT A RESULT" "$(grep -c 'NOT A RESULT' $d/DUR.txt)" "1"
ck "L names the import that moved" "$(grep -c 'IMPORTED grading module changed' $d/DUR.txt)" "1"
ck "L the grader was NOT run on a changed path" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "0"

# (M) counter-case to L: MATCHING import pins -> the grader IS run and the record
# says every import is identical. Without this, L alone could pass on a script
# that refuses unconditionally.
d=$(mkcase m)
rc=$(run $d)
ck "M rc=0 with matching import pins" "$rc" "0"
ck "M the grader WAS run (counter-case to L)" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "1"
ck "M record confirms ALL IMPORTS IDENTICAL" "$(grep -c 'ALL IMPORTS IDENTICAL' $d/DUR.txt)" "1"

# (N) THE CEILING REPORTS AND KEEPS WAITING (the default). rc is absent when the
# ceiling passes; it appears later; the backstop must still be there to grade it.
# The old behaviour would have exited 3 and produced NO RECORD for a run that
# completed -- a cap-stop in spirit. Counter-case is F, which sets EOC=1.
d=$T/n; mkdir -p $d/fine; cp $T/m/grade.py $d/grade.py 2>/dev/null || echo 'print("STUB GRADER OUTPUT -- the frozen grader'"'"'s bytes would be here")' > $d/grade.py
echo "IMPORTED MODULE" > $d/imp.py
echo "1234.56" > $d/fine/CORE_MINUTES.txt; echo "12345" > $d/fine/WALL_SECONDS_SOLVE.txt; echo "6" > $d/fine/RANKS.txt
( sleep 6; echo 0 > $d/fine/rc ) &
rc=$(MW=2 EOC=0 run $d); wait
ck "N rc=0 -- it waited through the ceiling and graded" "$rc" "0"
ck "N log REPORTS rather than giving up" "$([ "$(grep -c 'REPORTING, NOT GIVING UP' $d/bs.log)" -ge 1 ] && echo yes || echo no)" "yes"
ck "N log did NOT take the exit-3 path" "$(grep -c 'CEILING REACHED' $d/bs.log)" "0"
ck "N a record exists for the run that completed late" "$(grep -c 'STUB GRADER OUTPUT' $d/DUR.txt)" "1"

# (G) the lock is RELEASED on every exit path (else a rerun would stand down forever)
for c in a b d h i j k l m n; do
  ck "G lock released in case $c" "$([ -e $T/$c/.lock ] && echo held || echo free)" "free"
done

echo; echo "$PASS passed, $FAIL failed"
rm -rf $T
[ "$FAIL" -eq 0 ]
