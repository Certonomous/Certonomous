#!/usr/bin/env bash
# =============================================================================
# d12y_plan_step.sh -- THE REGISTERED COMPARATOR PLAN STEP OF D12R2-W2R, AS ONE
# LAUNCHABLE, AGENT-INDEPENDENT ARGV.  Registered by W2R_PREREGISTRATION.md ADDENDUM 3.
#
# WHY.  The frozen launcher ends each phase with a ledger line and an instruction:
#   :903-906  PHASE1_COMPLETE ... "NEXT: run the FROZEN COMPARATOR in --plan mode to
#             produce step_plan.json, then --phase 2."  (the argv is printed at :905)
#   :934-935  PHASE2_COMPLETE ... "NEXT: comparator --plan2 ..."
#   :973-976  PHASE3_COMPLETE ... "NEXT: comparator --plan3 ..."  (argv printed at :976)
# Until today only an agent typed that argv, so the chain phase -> plan -> next phase
# was not closed without a live agent -- the defect Sanaa's 7def3c6b names.  This
# file closes it.  It is NOT a new instrument: it runs the FROZEN comparator's own
# registered invocation, unchanged, after ASSERTING the comparator is the Addendum-1
# blob.  It computes nothing, chooses nothing and applies no threshold.
#
# WHAT IT DOES, in order (every wait is a line in STATUS.<case_id> in the cwd and,
# identically, in PLANSTEP.<case_id>.log, which the queue runner never overwrites):
#   1. refuses a duplicate of itself (own pidfile in the run root names a live pid) -- rc 3;
#   2. waits, bounded (--deadline-s, poll 30 s), for the PHYSICS witness of the
#      predecessor phase: the launcher's own `PHASE<n>_COMPLETE` ledger line
#      (plan <- PHASE1_COMPLETE, plan2 <- PHASE2_COMPLETE, plan3 <- PHASE3_COMPLETE);
#      at the bound: rc 6, BLOCKED, nothing run;
#   3. waits, inside the same bound, until NO running container carries the item's
#      prefix `d12y_` (the launcher removes each stage's container before it writes
#      the line, so this is normally immediate; a lingering one is waited out, never
#      refused, because a refusal would consume the queue entry);
#   4. asserts d12y_grade.py == blob aecceb4e... / md5 02a9ab62... -- rc 4 on drift, nothing run;
#   5. runs `python3 d12y_grade.py --manifest <ROOT>/manifest.jsonl --root <ROOT> --<mode>`
#      in the foreground and exits with the COMPARATOR's own rc (0 planned; 2 REFUSAL;
#      3 usage), captured here and labelled as the comparator's exit (L-342) -- it is
#      not a solver rc and there is no solver.
# Zero solver compute; no container; no `assert` (L-332); nothing deleted or edited.
# Permission for detached launches: bc0e687e.
#
# USAGE  bash d12y_plan_step.sh {plan|plan2|plan3} --deadline-s N [--case-id ID]
#        [--poll-s S] [--root DIR] [--gradepy FILE] [--blob SHA] [--md5 HEX] [--prefix P]
# The bracketed overrides exist ONLY so the selftest can point at a sacrificial root and
# a stand-in comparator; the queue entries pass none of them and the registered
# defaults below govern.
# =============================================================================
set -uo pipefail
PERMISSION=bc0e687e
MODE="${1:-}"; shift 1 2>/dev/null || true
case "$MODE" in plan|plan2|plan3) ;; *) echo "usage: d12y_plan_step.sh {plan|plan2|plan3} --deadline-s N [--case-id ID] [--poll-s S]" >&2; exit 64;; esac
SRC="/home/ubuntu/Certonomous/cases/dafoam/curriculum_D12R2"
ROOT="/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady"
GRADEPY="$SRC/d12y_grade.py"
BLOB_REGISTERED="aecceb4e874eb6d306fb273d7408e762718c87a2"   # Addendum 1, A1.3
MD5_REGISTERED="02a9ab62fc26d963886ecd0ee97457ef"             # Addendum 1, A1.3
PREFIX="d12y_"                                                 # launcher :343
DEADLINE_S=""; POLL_S=30; CASE_ID="W2R_${MODE}_wait"
while [ $# -gt 0 ]; do
  case "$1" in
    --deadline-s) DEADLINE_S="$2"; shift 2;;
    --case-id)    CASE_ID="$2"; shift 2;;
    --poll-s)     POLL_S="$2"; shift 2;;
    --root)       ROOT="$2"; shift 2;;
    --gradepy)    GRADEPY="$2"; shift 2;;
    --blob)       BLOB_REGISTERED="$2"; shift 2;;
    --md5)        MD5_REGISTERED="$2"; shift 2;;
    --prefix)     PREFIX="$2"; shift 2;;
    *) echo "usage: d12y_plan_step.sh {plan|plan2|plan3} --deadline-s N [--case-id ID] [--poll-s S]" >&2; exit 64;;
  esac
done
case "$DEADLINE_S" in ''|*[!0-9]*) echo "usage: --deadline-s N (seconds) is required" >&2; exit 64;; esac
case "$POLL_S" in ''|*[!0-9]*|0) echo "usage: --poll-s S must be a positive integer" >&2; exit 64;; esac
case "$MODE" in plan) WITNESS='^PHASE1_COMPLETE spent='; ART="step_plan.json";;
                plan2) WITNESS='^PHASE2_COMPLETE spent='; ART="step_plan2.json";;
                plan3) WITNESS='^PHASE3_COMPLETE spent='; ART="step_plan3.json";; esac
LEDGER="$ROOT/ledger.txt"; MANIFEST="$ROOT/manifest.jsonl"
CWD="$(pwd)"; STATUS="$CWD/STATUS.$CASE_ID"; PLOG="$CWD/PLANSTEP.$CASE_ID.log"
utc () { date -u +%Y-%m-%dT%H:%M:%SZ; }
rec () { local l="stamp=$(utc) planstep=d12y_plan_step.sh case=$CASE_ID mode=$MODE $*"; echo "$l" >> "$STATUS"; echo "$l" >> "$PLOG"; echo "$l"; }
live_with_prefix () { sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -- "^$PREFIX" | head -5 | tr '\n' ',' | sed 's/,$//'; }

SID=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ')
rec "event=START pid=$$ sid=${SID:-?} ppid=$PPID cwd=$CWD root=$ROOT witness=[$WITNESS] ledger=$LEDGER artifact=$ROOT/$ART deadline_s=$DEADLINE_S poll_s=$POLL_S prefix=$PREFIX permission=$PERMISSION"
[ -d "$ROOT" ] || { rec "rc=6 event=RUN_ROOT_ABSENT root=$ROOT note=nothing-run verdict=BLOCKED"; exit 6; }

# 1. duplicate refusal
OWN_PIDFILE="$ROOT/$CASE_ID.planstep.pid"
if [ -f "$OWN_PIDFILE" ]; then
  OPID=$(tr -dc '0-9' < "$OWN_PIDFILE" | head -c 12)
  if [ -n "$OPID" ] && [ "$OPID" != "$$" ] && kill -0 "$OPID" 2>/dev/null; then
    rec "rc=3 event=DUPLICATE_PLANSTEP_REFUSED own_pidfile=$OWN_PIDFILE live_pid=$OPID note=NOTHING-RUN"; exit 3
  fi
fi
echo "$$" > "$OWN_PIDFILE"; trap 'rm -f "$OWN_PIDFILE"' EXIT

# 2. the bounded wait for the physics witness
WAITED=0; N=0
while ! { [ -f "$LEDGER" ] && grep -Eq -- "$WITNESS" "$LEDGER"; }; do
  if [ "$WAITED" -ge "$DEADLINE_S" ]; then
    rec "rc=6 event=BLOCKED_AT_BOUND waited_s=$WAITED waits=$N deadline_s=$DEADLINE_S witness=[$WITNESS] note=witness-absent-at-the-registered-bound-NOTHING-RUN verdict=BLOCKED"; exit 6
  fi
  N=$((N+1)); rec "event=WAIT n=$N waited_s=$WAITED witness_present=no"
  sleep "$POLL_S"; WAITED=$((WAITED+POLL_S))
done
rec "event=WITNESS_PRESENT waited_s=$WAITED waits=$N line=[$(grep -E -- "$WITNESS" "$LEDGER" | head -1 | cut -c1-120)]"

# 3. wait out any lingering container with the prefix (never refuse here)
NC=0
while true; do
  LIVE=$(live_with_prefix); [ -z "$LIVE" ] && break
  if [ "$WAITED" -ge "$DEADLINE_S" ]; then
    rec "rc=6 event=BLOCKED_AT_BOUND waited_s=$WAITED prefix_waits=$NC live_containers_with_prefix=[$LIVE] note=prefix-never-cleared-inside-the-bound-NOTHING-RUN verdict=BLOCKED"; exit 6
  fi
  NC=$((NC+1)); rec "event=WAIT_PREFIX_CLEAR n=$NC waited_s=$WAITED live_containers_with_prefix=[$LIVE]"
  sleep "$POLL_S"; WAITED=$((WAITED+POLL_S))
done
rec "event=PREFIX_CLEAR waited_s=$WAITED prefix_waits=$NC"

# 4. the comparator must be the registered blob
GOT_BLOB=$(git -C "$SRC" hash-object "$GRADEPY" 2>/dev/null || echo unhashable)
GOT_MD5=$(md5sum "$GRADEPY" 2>/dev/null | cut -d' ' -f1)
if [ "$GOT_BLOB" != "$BLOB_REGISTERED" ] || [ "$GOT_MD5" != "$MD5_REGISTERED" ]; then
  rec "rc=4 event=COMPARATOR_BLOB_DRIFT got_blob=$GOT_BLOB registered_blob=$BLOB_REGISTERED got_md5=${GOT_MD5:-none} registered_md5=$MD5_REGISTERED note=NOTHING-RUN"; exit 4
fi
[ -f "$MANIFEST" ] || { rec "rc=6 event=MANIFEST_ABSENT manifest=$MANIFEST note=NOTHING-RUN verdict=BLOCKED"; exit 6; }
rec "event=COMPARATOR_ASSERTED blob=$GOT_BLOB md5=$GOT_MD5 gradepy=$GRADEPY"

# 5. the registered invocation, unchanged, rc captured here
OUT="$CWD/PLANSTEP.$CASE_ID.$(date -u +%Y%m%dT%H%M%SZ)_$$.out"
T0=$(date +%s)
rec "event=RUN begin=$(utc) argv=['python3' '$GRADEPY' '--manifest' '$MANIFEST' '--root' '$ROOT' '--$MODE'] out=$OUT"
python3 "$GRADEPY" --manifest "$MANIFEST" --root "$ROOT" "--$MODE" > "$OUT" 2>&1
CRC=$?
T1=$(date +%s)
PRESENT=$([ -f "$ROOT/$ART" ] && echo yes || echo no)
rec "rc=$CRC event=COMPARATOR_EXIT wall_s=$((T1-T0)) artifact=$ROOT/$ART present=$PRESENT out=$OUT note=exit-status-of-the-registered-comparator-invocation-NOT-a-solver-rc-L-342 permission=$PERMISSION"
exit "$CRC"
