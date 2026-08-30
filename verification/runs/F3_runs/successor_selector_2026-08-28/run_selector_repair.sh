#!/usr/bin/env bash
# R1 -- THE F3S UNIQUE-SELECTOR REPAIR.  The launch_cmd of
# verification/campaign/queue_entry_R1_F3S_SELECTOR_REPAIR.json.
#
#   bash run_selector_repair.sh --prereg-commit=<sha>   the graded path
#   bash run_selector_repair.sh --selftest              the driver's own controls
#   bash run_selector_repair.sh --birth-control         drive BR-1 alone
#
# This wrapper adds NOTHING to the decision.  It resolves its own directory, refuses
# an empty argument list, and hands everything to the python entry point, whose exit
# code it returns unchanged -- so a refusal is rc 2 here exactly as it is there.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRIVER="${HERE}/selector_repair_driver.py"

if [ ! -f "${DRIVER}" ]; then
    echo "REFUSED: ${DRIVER} does not exist. The queue validator does not check that" >&2
    echo "         launch_cmd[1] resolves to anything; this line is that check." >&2
    exit 2
fi
if [ "$#" -eq 0 ]; then
    echo "REFUSED: no arguments. This driver fires nothing without --prereg-commit," >&2
    echo "         --selftest or --birth-control." >&2
    exit 2
fi
cd "${HERE}" || exit 2
python3 "${DRIVER}" "$@"
exit $?
