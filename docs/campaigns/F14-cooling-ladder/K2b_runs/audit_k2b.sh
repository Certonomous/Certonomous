#!/bin/bash
# audit_k2b.sh -- run scripts/heat_balance.py over a K2b case at named times.
#
#   bash audit_k2b.sh K2bP_coarse 500 2500 5000
#   bash audit_k2b.sh K2bP_under            # latestTime only
#
# Writes HEATBALANCE_<time>.{json,txt} into the case directory, which is tracked;
# `postProcessing/` is not, and `heat_balance.py` deletes and rebuilds it, so do
# not run this against a case whose solver is still running.
#
# THE TWO FLAGS, AND WHY BOTH ARE REQUIRED HERE.
#
#   --allow-advective   The module is an OPEN case with four non-wall patches.
#                       The advective enthalpy flux is validated at KV1 (a
#                       planted 5.000e-03 W recovered at +2.40e-08 % error).
#
#   --allow-turbulent   k-omega SST makes alphat non-zero, so alphaEff varies
#                       over a patch and the auditor REFUSES (exit 2) without
#                       this flag.  The flag's own path is UNCALIBRATED and the
#                       report is stamped UNVALIDATED.  K2a section 8 named KV1
#                       as the instrument prerequisite for quoting a closure
#                       number and KV1 is a LAMINAR rung, so this requirement
#                       was not met by anything the spec named.
#
#                       WHAT BOUNDS THE DAMAGE, AND IT IS MEASURED PER RUN
#                       RATHER THAN ARGUED: the uncalibrated path affects only
#                       the CONDUCTIVE rows.  Every wall in this module is
#                       adiabatic, so those rows are identically zero, and the
#                       report's own `conduction` line against its `advection`
#                       line is the bound.  Read it in the output below before
#                       quoting any closure figure; if conduction ever becomes
#                       a material fraction of the ledger on some later variant
#                       of this module, the UNVALIDATED stamp starts to bite
#                       and the number stops being quotable.
#
# `--length 2.7` is the room height, so the report can state Ra.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../../../.." && pwd)
CASE=$1; shift
TIMES=("$@")
if [ ${#TIMES[@]} -eq 0 ]; then TIMES=(latestTime); fi
for t in "${TIMES[@]}"; do
  # Read the AUDITOR'S OWN exit status.  Piping this into `head` reports head's
  # status, and that mistake has cost this lab a false pass before (KV1 section 9).
  set +e
  python3 "$REPO/scripts/heat_balance.py" "$HERE/$CASE" \
      --time "$t" --length 2.7 --allow-advective --allow-turbulent \
      --json "$HERE/$CASE/HEATBALANCE_${t}.json" \
      > "$HERE/$CASE/HEATBALANCE_${t}.txt" 2>&1
  rc=$?
  set -e
  echo "$CASE @ $t : heat_balance.py exit $rc"
  command grep -E "IMBALANCE|conduction  =|advection   =|mass imbalance|BOUSSINESQ|fvOptions in the SOLVER LOG|IDENTITY CLASS" \
      "$HERE/$CASE/HEATBALANCE_${t}.txt" || true
done
