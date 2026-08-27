#!/usr/bin/env bash
# W3 G-ROOT.5 SELFTEST -- drives the chain driver's own refusals at ZERO compute:
# (a) a sacrificial RUNNING container carrying this item's prefix -> rc=3, nothing run;
# (b) an EXISTING run root with a pidfile naming a LIVE pid -> rc=3 (the sibling-driver
#     refusal), nothing run; (c) an existing run root with a STALE pidfile -> rc=6
#     (phase 1 requires an absent root), nothing run.  The temporary root is created
#     empty and removed with rmdir; its ABSENCE afterwards is the freeze condition.
# SAFETY: no leg reaches the launcher: (a) refuses before it; (b)/(c) refuse before it.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; D="$HERE/d12y_w3_chain_driver.sh"
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady
IMG=dafoam/opt-packages:latest
PASS=0; FAIL=0; ok() { echo "  [OK ] $1"; PASS=$((PASS+1)); }; bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "W3 G-ROOT.5 SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) driver_md5=$(md5sum "$D" | cut -d' ' -f1)"
# ---- W3 AMENDMENT 1 (2026-08-27), defect W3-SELFTEST-DEF-1.  The `rm -f STATUS.W3_chain`
# ---- and the `ls W3_*.out | wc -l` at the foot were written when NO W3 launch had ever
# ---- happened, so both treated "any such file" as "a file this selftest made".  On
# ---- 2026-08-27T16:35:49Z that deleted STATUS.W3_chain from the 03:43:17Z queue launch
# ---- and mis-scored the surviving W3_phase1.out as leakage.  BOTH ARTEFACTS ARE
# ---- EVIDENCE OF W3-LAUNCHER-DEF-1 AND MUST SURVIVE THE SELFTEST.  The selftest now
# ---- SNAPSHOTS what pre-exists and restores it, and scores only what it ADDED.
PRE_STATUS=""
if [ -f "$HERE/STATUS.W3_chain" ]; then PRE_STATUS=$(mktemp /tmp/d12y_w3_pre_status.XXXXXX); cp -p "$HERE/STATUS.W3_chain" "$PRE_STATUS"; fi
PRE_OUT=$(ls "$HERE"/W3_*.out 2>/dev/null | sort | tr '\n' ' ')
echo "  pre-existing artefacts SNAPSHOTTED: STATUS.W3_chain=$([ -n "$PRE_STATUS" ] && echo present || echo absent) W3_*.out=[$PRE_OUT]"
[ -e "$ROOT" ] && { bad "run root $ROOT already EXISTS -- refusing to test over a real root"; exit 2; } || ok "run root ABSENT before the test: $ROOT"

# =====================================================================================
# W3 AMENDMENT 1 (2026-08-27) -- CAP-AGREEMENT LEGS, defect W3-LAUNCHER-DEF-1.
# The launcher's A1 control compares the OPERATIVE cap against the *_REGISTERED constant
# and refused the 03:43:17Z launch at ZERO core-minutes because the operative default was
# still the DRAFT's.  These legs exist so that class cannot recur silently.  ALL SIX ARE
# ZERO COMPUTE: (d)/(e)/(f) abort inside A1/A4, which run BEFORE A6 starts any container;
# (g)/(h)/(i) are pure text reads.  A leg that FAILS here stops the whole selftest before
# a single container is started, because it runs ahead of the G-ROOT.5 legs below.
# =====================================================================================
L="$HERE/d12y_w3_stage_and_run.sh"
PREREG="$HERE/W3_PREREGISTRATION.md"

# (d) PLANTED DISAGREEMENT on CAP_CORE_MIN.  The control must SEE IT and REFUSE.
out=$(CAP_CORE_MIN=600.0 bash "$L" --phase 1 2>&1); rc=$?
if [ "$rc" -eq 1 ] && echo "$out" | grep -q '^ABORT: CAP_CORE_MIN is 600\.0, the pre-registration names 900\.0$'; then
  ok "(d) PLANTED CAP_CORE_MIN=600.0 -> exit 1, A1 REFUSED, NOTHING RUN"
else bad "(d) planted disagreement NOT seen: rc=$rc first-line='$(echo "$out" | head -1)'"; fi

# (e) PLANTED DISAGREEMENT on CAP_S8.  Note this leg ALSO proves the CAP_CORE_MIN limb
# PASSES at its registered default: if it did not, this leg would abort on that message.
out=$(CAP_S8=350.0 bash "$L" --phase 1 2>&1); rc=$?
if [ "$rc" -eq 1 ] && echo "$out" | grep -q '^ABORT: CAP_S8 is 350\.0, the pre-registration names 400\.0$'; then
  ok "(e) PLANTED CAP_S8=350.0 -> exit 1, A1 REFUSED, NOTHING RUN (and CAP_CORE_MIN passed at its default)"
else bad "(e) planted disagreement NOT seen: rc=$rc first-line='$(echo "$out" | head -1)'"; fi

# (f) NOTHING PLANTED: A1 must pass BOTH limbs at the registered defaults and the launcher
# must refuse LATER, for a reason that is not a cap.  SRC is pointed at an absent directory
# so A3 (the instrument-freeze check) fires (exit 4) BEFORE A6 would start any container.
# MEASURED 2026-08-27: A3 refuses correctly on an ABSENT instrument -- the on-disk md5 is
# the empty string and the HEAD-blob md5 is d41d8cd9... (md5 of empty input), so the two
# do NOT compare equal and the check does not silently pass on a missing file.
out=$(SRC=/nonexistent-w3-selftest-src bash "$L" --phase 1 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q 'md5.*!= committed blob' && ! echo "$out" | grep -q '^ABORT: CAP_'; then
  ok "(f) registered defaults -> A1 PASSES both limbs; refusal is A3 (exit 4), not a cap; NOTHING RUN"
else bad "(f) rc=$rc (want 4, no ABORT: CAP_ line): $(echo "$out" | grep '^ABORT' | head -1)"; fi

# (g)/(h) THE DRIFT AND DOCUMENT CHECKS -- the two readings that would have caught
# W3-LAUNCHER-DEF-1 at freeze time.  (g): the launcher's OPERATIVE defaults equal its own
# *_REGISTERED constants.  (h): those constants equal what the FROZEN pre-registration
# names, every time it names them.  THE DOCUMENT GOVERNS ITS INSTRUMENT.
cap_read () {   # cap_read <launcher> ; prints "<op_core> <reg_core> <op_s8> <reg_s8>"
  python3 - "$1" <<'PYEOF'
import re,sys
s=open(sys.argv[1]).read()
def one(pat):
    m=re.findall(pat,s)
    return m[0] if len(m)==1 else "AMBIGUOUS(%d)"%len(m)
print(one(r'^CAP_CORE_MIN="\$\{CAP_CORE_MIN:-([0-9.]+)\}"'.replace('^','(?m)^')),
      one(r'(?m)^CAP_CORE_MIN_REGISTERED="([0-9.]+)"'),
      one(r'(?m)^CAP_S8="\$\{CAP_S8:-([0-9.]+)\}"'),
      one(r'(?m)^CAP_S8_REGISTERED="([0-9.]+)"'))
PYEOF
}
doc_read () {   # doc_read <prereg> ; prints "<core> <s8>", or a refusal token
  # SCOPED TO THE FROZEN sec.4 REGISTRATION LINE, by its literal anchor -- NOT to the whole
  # document.  W3 AMENDMENT 1 (2026-08-27): the first version of this reader scanned the
  # whole file and REFUSED, correctly, on the amendment's OWN leg table, which quotes the
  # planted draft values 600.0 / 350.0 as the disagreement legs (d)/(e) plant.  A document
  # may legitimately QUOTE a value it does not register; only sec.4 REGISTERS one.  The
  # reader refuses if the anchor is missing, duplicated, or does not carry both caps once.
  python3 - "$1" <<'PYEOF'
import re,sys
anchor="Caps, registered and asserted by the launcher"
lines=[l for l in open(sys.argv[1]) if anchor in l]
if len(lines)!=1:
    print("ANCHOR_%s"%("MISSING" if not lines else "DUPLICATED(%d)"%len(lines)), "ANCHOR"); raise SystemExit
def one(name,l):
    v=re.findall(name+r'\s*=\s*([0-9]+\.?[0-9]*)',l)
    return v[0] if len(v)==1 else "NOTONCE(%d)"%len(v)
print(one('CAP_CORE_MIN',lines[0]), one('CAP_S8',lines[0]))
PYEOF
}
read OPC REGC OPS REGS <<<"$(cap_read "$L")"
read DOCC DOCS <<<"$(doc_read "$PREREG")"
echo "  cap reading: launcher operative=[$OPC,$OPS] registered=[$REGC,$REGS] document=[$DOCC,$DOCS]"
if [ "$OPC" = "$REGC" ] && [ "$OPS" = "$REGS" ]; then
  ok "(g) launcher OPERATIVE defaults == its *_REGISTERED constants ($OPC / $OPS)"
else bad "(g) DRIFT: operative [$OPC,$OPS] != registered [$REGC,$REGS] -- this is W3-LAUNCHER-DEF-1"; fi
if [ "$REGC" = "$DOCC" ] && [ "$REGS" = "$DOCS" ]; then
  ok "(h) launcher *_REGISTERED constants == the FROZEN pre-registration's caps ($DOCC / $DOCS)"
else bad "(h) the launcher does not carry the document's caps: launcher [$REGC,$REGS] vs $PREREG [$DOCC,$DOCS]"; fi

# (i) PLANTED CONTROL ON THE (g) READER.  A reader not shown able to see a DISAGREEMENT
# is not evidence (CLAUDE.md rule 3).  A sacrificial copy carrying the DRAFT's 600.0 must
# make the (g) comparison come out UNEQUAL; if it does not, (g)'s pass above means nothing.
MUT=$(mktemp /tmp/d12y_w3_mutated_launcher.XXXXXX.sh)
sed 's/^CAP_CORE_MIN="\${CAP_CORE_MIN:-900\.0}"/CAP_CORE_MIN="${CAP_CORE_MIN:-600.0}"/' "$L" > "$MUT"
read MOPC MREGC MOPS MREGS <<<"$(cap_read "$MUT")"
if [ "$MOPC" = "600.0" ] && [ "$MREGC" = "900.0" ] && [ "$MOPC" != "$MREGC" ]; then
  ok "(i) PLANTED CONTROL: mutated copy reads operative=600.0 vs registered=900.0 -- the (g) reader CAN see a disagreement"
else bad "(i) PLANTED CONTROL FAILED: mutated copy read [$MOPC,$MREGC] -- leg (g) is not evidence"; fi
rm -f "$MUT"
[ "$FAIL" -eq 0 ] || { echo "W3 CAP-AGREEMENT LEGS FAILED ($FAIL) -- stopping BEFORE any container is started"; exit 2; }

CN="d12y_w3_selftest_$(date -u +%Y%m%dT%H%M%SZ)"
sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=1 --memory=64m --memory-swap=64m "$IMG" bash -c "sleep 120" >/dev/null 2>&1 || { bad "could not start the sacrificial container"; exit 2; }
out=$(bash "$D" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "G_ROOT5_REFUSED live_prefix_containers"; then ok "(a) live prefix container $CN -> rc=3, NOTHING RUN"; else bad "(a) rc=$rc: $(echo "$out" | tail -1)"; fi
sudo -n docker rm -f "$CN" >/dev/null 2>&1
mkdir -p "$ROOT" || { bad "could not create the temporary root"; exit 2; }
( cd "$ROOT" && exec sleep 120 ) & SPID=$!
echo "$SPID" > "$ROOT/d12y_w3_driver.pid"
out=$(bash "$D" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "G_ROOT5_REFUSED live_driver_pid=$SPID"; then ok "(b) live sibling driver pid $SPID -> rc=3, NOTHING RUN"; else bad "(b) rc=$rc: $(echo "$out" | tail -1)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null; echo "999999" > "$ROOT/d12y_w3_driver.pid"
out=$(bash "$D" 2>&1); rc=$?
if [ "$rc" -eq 6 ] && echo "$out" | grep -q "ROOT_EXISTS"; then ok "(c) stale pidfile ignored; existing root -> rc=6 (phase 1 requires an absent root), NOTHING RUN"; else bad "(c) rc=$rc: $(echo "$out" | tail -1)"; fi
rm -f "$ROOT/d12y_w3_driver.pid"; rmdir "$ROOT" 2>/dev/null
[ ! -e "$ROOT" ] && ok "run root ABSENT after the test (freeze condition): test -e $ROOT -> false" || bad "run root still present"
sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q '^d12y_w3_' && bad "a d12y_w3_ container survives" || ok "no d12y_w3_ container survives"
POST_OUT=$(ls "$HERE"/W3_*.out 2>/dev/null | sort | tr '\n' ' ')
NEW_OUT=$(comm -13 <(printf '%s\n' $PRE_OUT | sort) <(printf '%s\n' $POST_OUT | sort) | tr '\n' ' ')
[ -z "$(echo "$NEW_OUT" | tr -d ' ')" ] && ok "no NEW step output was written (no leg reached the launcher); pre-existing [$PRE_OUT] PRESERVED" || bad "step output leaked: [$NEW_OUT]"
# restore, never destroy: the selftest removes only the STATUS lines IT appended.
rm -f "$HERE/STATUS.W3_chain"
if [ -n "$PRE_STATUS" ]; then cp -p "$PRE_STATUS" "$HERE/STATUS.W3_chain"; rm -f "$PRE_STATUS"; fi
[ -n "$PRE_STATUS" ] && { [ -f "$HERE/STATUS.W3_chain" ] && ok "pre-existing STATUS.W3_chain RESTORED byte-for-byte" || bad "STATUS.W3_chain NOT restored"; }
echo "W3 G-ROOT5 SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
