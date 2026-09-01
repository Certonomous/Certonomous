#!/usr/bin/env bash
# =============================================================================
# JF1 RUN WATCHER -- AN OS-LEVEL DAEMON, NOT AN AGENT-HELD MONITOR.
#
# WHY THIS EXISTS.  An agent's watcher dies with the agent, every time.  Two
# agent-held monitors were armed on these same runs on 2026-09-01 and both died
# the moment their agent finished a report, while the solvers carried on.  The
# lab's standing ruling is that watchers and queues run as OS-level daemons,
# independent of agents.  This is that daemon: launch it with `setsid` and it
# outlives every agent in the session.
#
# WHERE IT WRITES.  `JF1_WATCH_FINDINGS.log`, BESIDE THE RUNS IT WATCHES.  Not
# the scratchpad: the scratchpad is temp-only, is not a handoff channel, and was
# wiped three times in one day (L-186).  A successor agent reads the findings
# file and needs no knowledge of this process.
#
# ## THE setsid TRAP, AND IT HAS BITTEN THIS LAB ##
# `setsid timeout cmd` exits 0 for EVERY outcome -- success, timeout and kill --
# so a return code taken AROUND a setsid line is not the command's return code,
# and a crashed run then produces evidence identical to a clean one.  This script
# therefore captures ITS OWN rc INSIDE itself, in an EXIT trap, and writes it to
# the findings file.  Nothing infers this watcher's fate from the setsid line.
#
# ## THE CRASH FILTER IS VALIDATED BOTH WAYS BEFORE IT IS TRUSTED ##
# A filter that greps for a word is not a crash detector.  The previous attempt
# keyed on `SIGFPE` and `bounding`; measured on a HEALTHY completed run those
# match 1 and 10,453 times respectively -- OpenFOAM prints `trapFpe: Floating
# point exception trapping enabled (FOAM_SIGFPE)` in its startup banner at line
# 18, and `bounding` is the ordinary clipping message.  That filter would have
# fired 10,454 times on a run with nothing wrong with it.
#
# The filter below keys on STACK FRAMES (`^#N Foam::`) and fatal-error headers.
# Validated before arming:
#   known-good -> 0 : completed C1 log, live C2 log, and the banner line itself
#   known-bad  -> 6, 8, 6 : verification/runs/FPE_DIAG_runs/{BP1,BP2,HP1}
# Keying on `FOAM FATAL ERROR` ALONE would have MISSED BP1, which carries zero
# of that string and twelve stack frames.  The frames are what make it work.
# `--selftest` re-runs both halves and REFUSES to arm if either fails.
#
# THIS WATCHER GRADES NOTHING.  It records terminal states.  Verdicts in the
# fixed vocabulary are a comparator's job and an agent's responsibility.
# =============================================================================
set -u

R="/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap"
OUT="${R}/JF1_WATCH_FINDINGS.log"

# WHAT IS WATCHED IS AN ARGUMENT, NOT A CONSTANT.  The first arming of this
# daemon hardcoded the E1 chain; when that chain finished, re-arming it on the
# next rung meant editing the file, and an edited watcher is a watcher whose
# validated selftest has to be re-earned.  The tracked set and the chain log are
# now passed in, so the same validated binary watches every rung.
#
#   --track="A B C"     run roots under ${R} to watch
#   --chainlog=NAME     the driver log under ${R} whose terminal lines are read
#
# The defaults are the E1 set, so an argument-free invocation behaves exactly as
# the validated 2026-09-01 arming did.
TRACK="JF1G_P0_C2_CMU010_A0 JF1E_E1_CMU010_A0 JF1E_E1_CMU020_A0 JF1E_E1_CMU040_A0"
CHAINLOG="JF1E_E1_CHAIN.log"
for a in "$@"; do
  case "$a" in
    --track=*)    TRACK="${a#*=}" ;;
    --chainlog=*) CHAINLOG="${a#*=}" ;;
    --selftest)   : ;;
    *) echo "REFUSED: unrecognised argument '$a'"; exit 3 ;;
  esac
done
NTRACK=$(echo ${TRACK} | wc -w | tr -d ' ')
[ "${NTRACK}" -ge 1 ] || { echo "REFUSED: --track is empty -- a watcher with nothing to watch"; exit 3; }

# Stack frames and fatal headers.  NOT bare words.
STRICT='^#[0-9]+ +(Foam::|\?\?)|FOAM FATAL ERROR|FOAM FATAL IO ERROR|sigFpe::sigHandler|sigSegv::sigHandler|Out of memory|std::bad_alloc'

log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "${OUT}"; }

# ---- selftest: the filter must see a real crash before its silence counts ----
#
# The control set is CLASSIFIED FROM THE LOGS THEMSELVES, never from directory
# names.  A first attempt hardcoded "everything under FPE_DIAG_runs is a crash"
# and the selftest refused to arm, correctly: BL1 (53,999 lines) and HL1 (70,666
# lines) both carry an `End` line and ZERO stack frames -- they are HEALTHY
# COMPLETED RUNS sitting in a directory named for a crash investigation.  The
# expected class is therefore derived per log:
#     `End` present and no frames  -> healthy, filter MUST return 0
#     no `End` and frames present  -> crashed, filter MUST return > 0
# Measured on this box: BP1 6 frames / 2,050 lines, BP2 8 / 1,881, HP1 6 / 758,
# each ending mid-stack-trace with no `End`.
#
# AND NOTE WHAT THIS PROVES ABOUT THE FILTER'S SHAPE: not one of those three
# crash logs contains `FOAM FATAL` anywhere (measured: 0, 0, 0).  A filter keyed
# on the fatal-error string would miss EVERY REAL CRASH ON THIS BOX.  The stack
# frames are the only reliable signal, which is why they lead the pattern.
selftest() {
  local fail=0 n seen_bad=0 seen_good=0 cls
  n=$(echo "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)." \
      | grep -acE "${STRICT}" || true)
  echo "  banner line (the false positive that started this): ${n} (expect 0)"
  [ "${n:-0}" -eq 0 ] || fail=1

  for lg in "${R}/JF1G_P0_C1_CMU010_A0/log.simpleFoam" \
            /home/ubuntu/Certonomous/verification/runs/FPE_DIAG_runs/*/log.simpleFoam; do
    [ -f "$lg" ] || continue
    local ends frames
    ends=$(grep -ac '^End' "$lg" || true)
    frames=$(grep -acE '^#[0-9]+ +(Foam::|\?\?)' "$lg" || true)
    if [ "${ends:-0}" -gt 0 ] && [ "${frames:-0}" -eq 0 ]; then cls="healthy"
    elif [ "${ends:-0}" -eq 0 ] && [ "${frames:-0}" -gt 0 ]; then cls="crashed"
    else cls="ambiguous"; fi
    n=$(grep -acE "${STRICT}" "$lg" || true)
    case "$cls" in
      healthy) echo "  known-GOOD $(basename $(dirname $lg)): ${n} (expect 0)"
               [ "${n:-0}" -eq 0 ] && seen_good=1 || fail=1 ;;
      crashed) echo "  known-BAD  $(basename $(dirname $lg)): ${n} (expect > 0)"
               [ "${n:-0}" -gt 0 ] && seen_bad=1 || fail=1 ;;
      *)       echo "  SKIPPED (ambiguous) $(basename $(dirname $lg)): End=${ends} frames=${frames}" ;;
    esac
  done

  # A filter never shown a real crash is not a crash detector, whatever it
  # returns on healthy logs -- and one never shown a healthy log is not a filter,
  # it is an alarm.  BOTH halves must be exercised or this refuses to arm.
  [ "${seen_bad}"  -eq 1 ] || { echo "SELFTEST: no known-BAD control exercised -- REFUSING"; fail=1; }
  [ "${seen_good}" -eq 1 ] || { echo "SELFTEST: no known-GOOD control exercised -- REFUSING"; fail=1; }
  return $fail
}

case " $* " in *" --selftest "*) SELFTEST_ONLY=1 ;; *) SELFTEST_ONLY=0 ;; esac
if [ "${SELFTEST_ONLY}" = "1" ]; then
  echo "== JF1 WATCHER FILTER SELFTEST =="
  if selftest; then echo "== SELFTEST PASS =="; exit 0; else echo "== SELFTEST FAIL =="; exit 2; fi
fi

# ---- rc captured INSIDE, never inferred from the setsid line ----
WATCH_RC=99
finish() {
  WATCH_RC=$?
  log "WATCHER EXIT rc=${WATCH_RC} pid=$$"
  exit "${WATCH_RC}"
}
trap finish EXIT

# Arm only behind a passing selftest.
if ! selftest >> "${OUT}" 2>&1; then
  log "WATCHER REFUSED TO ARM -- filter selftest failed; no watching is claimed"
  exit 2
fi

log "WATCHER ARMED pid=$$ (OS daemon; survives every agent) tracking ${NTRACK}: ${TRACK}  chainlog ${CHAINLOG}"

declare -A SEEN
CHAINSEEN=""
for i in $(seq 1 480); do        # 480 x 30 s = 4 h ceiling
  nterm=0
  for c in ${TRACK}; do
    d="${R}/${c}"; f="${d}/RUN_STATUS.${c}.txt"; lg="${d}/log.simpleFoam"

    # (1) TERMINAL VIA STATUS FILE -- every rc, not just 0
    if [ -f "$f" ]; then
      rc=$(grep -E "^rc " "$f" 2>/dev/null | awk '{print $2}')
      stg=$(grep -E "^stage_at_exit" "$f" 2>/dev/null | awk '{print $2}')
      if [ -n "${rc:-}" ] && [ "${rc}" != "99" ] && [ -n "${stg:-}" ]; then
        nterm=$((nterm+1))
        if [ -z "${SEEN[$c]:-}" ]; then
          cm=$(grep -E "^core_min_MEASURED" "$f" | awk '{print $2}')
          cap=$(grep -E "^cap_core_min" "$f" | awk '{print $2}')
          note=""
          [ "${rc}" = "6" ] && note=" CAP-STRUCK (rule 12: an overrun STOPS the run)"
          [ "${rc}" != "0" ] && [ "${rc}" != "6" ] && note=" NONZERO RC -- TRIAGE BEFORE ANY READING"
          log "TERMINAL ${c} rc=${rc} stage=${stg} core_min=${cm} cap=${cap}${note}"
          SEEN[$c]=1
        fi
        continue
      fi
    fi

    # (2) VALIDATED CRASH SIGNATURE
    if [ -f "$lg" ] && [ -z "${SEEN[crash_$c]:-}" ]; then
      n=$(grep -acE "${STRICT}" "$lg" 2>/dev/null || true)
      if [ "${n:-0}" -gt 0 ]; then
        log "CRASH ${c} ${n} validated crash-signature lines: $(grep -aoE "${STRICT}" "$lg" | sort -u | head -3 | tr '\n' ' ')"
        SEEN[crash_$c]=1
      fi
    fi

    # (3) VANISHED -- process gone, no status file.  The silent case that is
    #     indistinguishable from "still running" unless somebody looks.
    if [ -d "$d" ] && [ ! -f "$f" ] && [ -z "${SEEN[gone_$c]:-}" ]; then
      if ! pgrep -f "simpleFoam -case .*/${c}\$" > /dev/null 2>&1; then
        age=$(( $(date +%s) - $(stat -c %Y "$lg" 2>/dev/null || date +%s) ))
        if [ "${age}" -gt 180 ]; then
          log "VANISHED ${c} no solver process, no status file, log idle ${age}s -- INVESTIGATE"
          SEEN[gone_$c]=1
        fi
      fi
    fi
  done

  # (4) THE CHAIN DRIVER'S OWN TERMINAL STATES
  cl="${R}/${CHAINLOG}"
  if [ -f "$cl" ]; then
    ev=$(grep -aE "LINK FAILED|CHAIN STOPPED|CHAIN COMPLETE" "$cl" 2>/dev/null | tr '\n' ';')
    if [ -n "${ev}" ] && [ "${ev}" != "${CHAINSEEN}" ]; then
      log "CHAIN ${ev}"
      CHAINSEEN="${ev}"
    fi
  fi

  if [ "${nterm}" -ge "${NTRACK}" ]; then
    log "ALL ${NTRACK} TRACKED RUNS TERMINAL -- watcher standing down"
    exit 0
  fi
  sleep 30
done

log "WATCHER CEILING REACHED (4 h) with ${nterm}/${NTRACK} terminal -- standing down, runs NOT abandoned"
exit 0
