#!/bin/bash
# T25R4 LADDER ENTRY -- THE GATE IS THE FIRST ACTION AND IT IS DEFAULT-DENY.
# Queued as this command; the queue runner never sees the solver directly.
RUN="$1"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$HERE/ladder_gate_t25R4.py" --run "$RUN"
G=$?
if [ "$G" -ne 0 ]; then
  echo "LADDER ENTRY $RUN NOT LAUNCHED: the G-P gate refused (exit $G)."
  echo "This is default-deny and it is correct. Nothing is run."
  exit "$G"
fi
exec bash "$HERE/run_one_t25R4.sh" "$RUN"
