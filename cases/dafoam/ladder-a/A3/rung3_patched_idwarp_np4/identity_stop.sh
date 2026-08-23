#!/usr/bin/env bash
# identity_stop.sh -- the WIRED early stop for the A3 rung-3 patched-IDWarp arm (np=4).
#
# WHAT IT DECIDES. The shipped rung-3 CD adjoint stagnates: 4000 iterations, PetscConvergedReason
# -3, 1.31x total residual reduction. The rotation patch touches only vectorUtils_{b,d}.f90 -- the
# mesh-warp derivative, which enters the chain AFTER A^T psi = -dF/dW is solved -- so the patched
# arm's Krylov solve cannot see it and must reproduce that stagnation digit for digit. Rung 2
# measured exactly that identity, 11 of 11 printed pairs bit-identical.
#
# Once the patched arm has reproduced the shipped path through iteration 1000, the remaining 3000
# iterations buy nothing but a repeat of a known stagnation, at roughly 70% of the arm's cost. This
# script stops it there. THE STOP IS DELIBERATE AND IS NOT A MEASUREMENT FAILURE: per
# DAFOAM_CHARTER.md section 7 a stop is not a measurement, and no conditioning, memory or gradient
# claim is drawn from the stop itself. The identity finding rests on the 11 matched checkpoints,
# which are complete before the stop fires.
#
# THREE BRANCHES, all registered in PREREGISTRATION.md section 6 before the arm runs:
#   MATCH through the final checkpoint            -> exit 5, kill, identity CONFIRMED
#   DIFFER while still stagnating (R >= CONV)     -> exit 6, kill, STOP AND ESCALATE -- the
#                                                    "patch is downstream of the Krylov solve"
#                                                    claim is falsified and rung 2's comparability
#                                                    argument is in question
#   DIFFER in the CONVERGING direction (R < CONV) -> DO NOT KILL. A patched adjoint that actually
#                                                    converges at rung 3 is the largest result this
#                                                    item could produce and must not be killed by
#                                                    its own guard.
# CONV is passed in; the pre-registration fixes it at 1.0e-03, three decades below the shipped
# plateau of 1.6152e-02 and far above the 1e-4 relative target of ~2.12e-06, so no stagnating path
# can reach it and no converging path can miss it.
#
# Usage: identity_stop.sh <container> <logpath> <checkpoints-file> <conv-threshold> <root> <arm> [--no-kill]
# Exit:  5 = identity confirmed through the final checkpoint, container killed (deliberate stop)
#        6 = path DIVERGED while stagnating, container killed, ESCALATE
#        0 = container finished on its own, or a converging-direction difference was seen and the
#            guard stood down
#        7 = single-pass selftest reached no decision
#        2 = usage / preconditions wrong
set -u

if [ "$#" -lt 6 ]; then
  echo "usage: identity_stop.sh <container> <log> <checkpoints> <conv> <root> <arm> [--no-kill]" >&2
  exit 2
fi
NAME="$1"; LOG="$2"; CKPT="$3"; CONV="$4"; ROOT="$5"; ARM="$6"; NOKILL="${7:-}"
SINGLE=0; [ "$NOKILL" = "--no-kill" ] && SINGLE=1
OUT="$ROOT/identity_stop_${ARM}.log"

[ -f "$CKPT" ] || { echo "identity_stop: checkpoints file $CKPT missing -- refusing to run blind" >&2; exit 2; }
FINAL=$(grep -vE '^\s*#' "$CKPT" | awk 'NF==2{n=$1} END{print n}')
[ -n "${FINAL:-}" ] || { echo "identity_stop: no checkpoints parsed from $CKPT" >&2; exit 2; }

kill_arm() {
  if [ "$SINGLE" = "1" ]; then
    echo "$(date -u +%FT%TZ) NO_KILL (selftest) -- would have killed $NAME" >> "$OUT"
  else
    sudo -n docker kill "$NAME" >/dev/null 2>&1
  fi
}
lt() { awk -v a="$1" -v b="$2" 'BEGIN{ exit !(a+0 < b+0) }'; }

echo "# identity_stop armed $(date -u +%FT%TZ) container=$NAME final_checkpoint=$FINAL conv=$CONV single_pass=$SINGLE" >> "$OUT"
seen_container=0

for _ in $(seq 1 20000); do
  if [ -f "$LOG" ]; then
    DECISION=""
    matched=0
    while read -r N REF; do
      case "$N" in ''|\#*) continue;; esac
      # The solver's own line, e.g. "Main iteration 700 KSP Residual norm 1.615266448650e-02 348.44 s."
      GOT=$(grep -m1 -E "^Main iteration ${N} KSP Residual norm " "$LOG" 2>/dev/null | awk '{print $7}')
      [ -z "${GOT:-}" ] && break          # this checkpoint has not been printed yet; wait
      if [ "$GOT" = "$REF" ]; then
        matched=$((matched + 1))
        continue
      fi
      # A difference. Which kind?
      if lt "$GOT" "$CONV"; then
        DECISION="CONVERGING"
        echo "$(date -u +%FT%TZ) iteration $N: $GOT != shipped $REF, and $GOT < conv threshold $CONV." >> "$OUT"
        echo "  The patched adjoint is on a CONVERGING trajectory the shipped one never reached." >> "$OUT"
        echo "  THE GUARD STANDS DOWN. This is the largest result this arm could produce; it is not killed." >> "$OUT"
        touch "$ROOT/PATH_CONVERGING.${ARM}"
      else
        DECISION="DIVERGED"
        {
          echo "$(date -u +%FT%TZ) IDENTITY STOP FIRED -- PATH DIVERGED on arm $ARM (container $NAME)"
          echo "iteration $N: patched printed $GOT, shipped printed $REF, and $GOT >= conv threshold $CONV"
          echo "matched checkpoints before the divergence: $matched"
          echo "DISPOSITION: the claim that the IDWarp patch enters strictly AFTER the Krylov solve"
          echo "is FALSIFIED at rung 3. Rung 2's two-image comparability argument is in question."
          echo "STOP AND ESCALATE. No conditioning or gradient claim is drawn in either direction."
        } | tee -a "$ROOT/PATH_DIVERGED.${ARM}" >> "$OUT"
      fi
      break
    done < "$CKPT"

    if [ "$DECISION" = "DIVERGED" ]; then kill_arm; exit 6; fi
    if [ "$DECISION" = "CONVERGING" ]; then
      [ "$SINGLE" = "1" ] && exit 7
      exit 0
    fi

    # All checkpoints present and matching?
    LASTGOT=$(grep -m1 -E "^Main iteration ${FINAL} KSP Residual norm " "$LOG" 2>/dev/null | awk '{print $7}')
    if [ -n "${LASTGOT:-}" ] && [ "$DECISION" = "" ]; then
      {
        echo "$(date -u +%FT%TZ) IDENTITY CONFIRMED on arm $ARM: $matched of $matched checkpoints"
        echo "bit-identical to the shipped rung-3 CD adjoint through iteration $FINAL."
        echo "DELIBERATE STOP: the remaining iterations repeat a known stagnation. Per"
        echo "DAFOAM_CHARTER.md section 7 a stop is not a measurement -- the identity finding rests"
        echo "on the matched checkpoints, which are complete, and NOT on the stop."
      } | tee -a "$ROOT/IDENTITY_CONFIRMED.${ARM}" >> "$OUT"
      kill_arm
      exit 5
    fi

    # A terminal reason printed before the final checkpoint: let the container finish on its own.
    if grep -qE '^\*\*Completed\*\*! Total iterations: [0-9]+\. PetscConvergedReason: 2\.' "$LOG" 2>/dev/null; then
      echo "$(date -u +%FT%TZ) reason 2 printed: the patched adjoint CONVERGED. Guard stands down." >> "$OUT"
      touch "$ROOT/PATH_CONVERGING.${ARM}"
      exit 0
    fi
  fi

  if [ "$SINGLE" = "1" ]; then
    echo "$(date -u +%FT%TZ) single pass: no decision reached on $LOG" >> "$OUT"
    exit 7
  fi

  if sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$NAME"; then
    seen_container=1
  elif [ "$seen_container" = "1" ]; then
    echo "$(date -u +%FT%TZ) container gone before a decision was reached." >> "$OUT"
    exit 0
  fi
  sleep 5
done
exit 0
