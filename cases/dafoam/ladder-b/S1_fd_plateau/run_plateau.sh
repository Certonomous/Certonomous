#!/usr/bin/env bash
# S1 FD PLATEAU -- Arm F (the registered falsifier) then Arm P (the plateau step).
# Frozen registration: cases/dafoam/ladder-b/S1_FD_PLATEAU_PREREGISTRATION.md
# frozen at commit a1727bd01c4012e1350cd7138460606a3d103338 (blob md5 4c40181966d39acc39489b094e4b824a).
#
# PROVENANCE: this file is /home/ubuntu/certonomous-runs/S1-cbfs-reinversion/run_fd8.sh
# with the STEP and the CELL LIST changed, as briefed. What is added is not an
# instrument: it is (a) the rule-12 hard-cap STOP, which the registration demands
# ("an overrun STOPS the item"), and (b) preservation of each primal's decomposed
# fields, which is what makes rule 4's AGE GUARD checkable PER PRIMAL instead of only
# for whichever primal happened to run last. run_fd8.sh deleted the processor dirs
# before every run; deleting the physics artefact would make the registered completion
# rule ungradeable, so they are MOVED aside rather than removed.
#
# WHAT IS NOT RE-BOUGHT: the unperturbed baseline. `fd8_base` = 6.1509017109920479e-04
# is STEP-INDEPENDENT -- a central difference (J+ - J-)/(2h) does not use it at all --
# and the registration budgets no new baseline primal (prereg 2.8). It is reused from
# /home/ubuntu/certonomous-runs/S1-cbfs-reinversion/log.fd8_base and this is said out
# loud rather than left to be noticed.
#
# ARM ORDER: F BEFORE P, deliberately. Arm F is the DAFOAM_CHARTER section 4 trivial
# baseline, and prereg 2.5 registers that if the deliberately-wrong step PASSES, P1's
# verdict is WITHDRAWN for every component. The falsifier is therefore a PRECONDITION
# for being entitled to read P1 at all, so a budget stop must never be able to leave
# this item holding a P1 reading it may not use. Buying F first also smoke-tests the
# whole chain (staged case, container, objective extraction) for 15 core-min instead
# of 45.
set -uo pipefail
BASE=/home/ubuntu/certonomous-runs/S1-fd-plateau
cd "$BASE"

CAP=75.0        # REGISTERED HARD CAP in core-min (prereg 2.8). NOT a target, a stop.
RANKS=2         # --cpus=2 -- the measured cost basis, and what run_one.sh bills at
NEED=8.35       # 7.5889 measured core-min/primal x 1.10. Do not START what cannot finish.
NCELLS=21000

spent() { awk -F, '$2=="END"{split($7,a,"=");s+=a[2]}END{printf "%.4f", s+0}' "$BASE/ledger.csv" 2>/dev/null; }

# One perturbed primal: write beta, clear the decomposition, run, preserve the fields.
one() {
  local tag="$1" cell="$2" step="$3" sgn="$4"
  local sp rem tmo
  sp=$(spent); [ -z "$sp" ] && sp=0
  rem=$(awk "BEGIN{printf \"%.4f\", $CAP-$sp}")
  if awk "BEGIN{exit !($rem < $NEED)}"; then
    echo "RULE-12 STOP before $tag: spent=$sp core-min of CAP=$CAP, remaining=$rem < $NEED needed for one primal. THE ITEM STOPS; IT DOES NOT GET A NEW BUDGET." | tee -a "$BASE/RULE12_STOP.txt"
    return 9
  fi
  # The remaining budget IS the timeout. Cumulative spend therefore cannot exceed CAP.
  tmo=$(awk "BEGIN{printf \"%d\", $rem*60/$RANKS}")
  python3 -c "
import numpy as np
b = np.ones($NCELLS); b[$cell] += ($step if '$sgn'=='plus' else -$step)
assert 0.2 <= b[$cell] <= 4.0, 'beta outside the registered [0.2,4.0] bounds'
np.save('$BASE/cbfs_inv/beta_fd.npy', b)" || return 8
  rm -rf "$BASE"/cbfs_inv/processor{0,1,2,3}
  "$BASE/run_one.sh" "$tag" "$RANKS" "$tmo" -task run_model -betafile beta_fd.npy -primalTol 1e-8
  local rc=$?
  # PRESERVE the decomposed fields for this tag: rule 4's age guard is read off them.
  mkdir -p "$BASE/fields_${tag}"
  for p in 0 1 2 3; do
    [ -d "$BASE/cbfs_inv/processor$p" ] && mv "$BASE/cbfs_inv/processor$p" "$BASE/fields_${tag}/"
  done
  return $rc
}

echo "S1-FD-PLATEAU START $(date -u +%FT%TZ)  CAP=${CAP} core-min"

# ---- ARM F : the registered falsifier. cell 5363 at h = 0.5, central pair. 2 primals.
# Registered prediction: rel. err against the anchor8 gradient > 2 %.
for sgn in plus minus; do
  one "f500_5363_${sgn}" 5363 0.5 "$sgn" || echo "ARM F $sgn returned non-zero"
done

# ---- ARM P : the plateau step. cells 5363 / 5428 / 5491 at h = 0.025, central pairs.
# 6 primals. s_lo = 0.025 is fixed by N-D21's pair constraint s_hi >= 2*s_lo with
# s_hi at the already-graded 0.05; it is not this lane's taste.
for cell in 5363 5428 5491; do
  for sgn in plus minus; do
    one "p025_${cell}_${sgn}" "$cell" 0.025 "$sgn" || echo "ARM P $cell $sgn returned non-zero"
  done
done

echo "S1-FD-PLATEAU DONE $(date -u +%FT%TZ)  spent=$(spent) core-min of CAP=${CAP}"
