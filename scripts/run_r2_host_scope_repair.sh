#!/usr/bin/env bash
# R2 -- THE QUEUE-VALIDATOR HOST-SCOPE REPAIR.  The launch_cmd of
# verification/campaign/queue_entry_R2_QUEUE_HOST_SCOPE_REPAIR.json.
#
#   bash scripts/run_r2_host_scope_repair.sh --prereg-commit=<sha>
#   bash scripts/run_r2_host_scope_repair.sh --selftest
#   bash scripts/run_r2_host_scope_repair.sh --preconditions
#
# This wrapper adds NOTHING to the decision and returns the python exit code unchanged.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRIVER="${HERE}/r2_host_scope_driver.py"
if [ ! -f "${DRIVER}" ]; then
    echo "REFUSED: ${DRIVER} does not exist. scripts/queue_entry_check.py does NOT" >&2
    echo "         check that launch_cmd[1] resolves; this line is that check." >&2
    exit 2
fi
if [ "$#" -eq 0 ]; then
    echo "REFUSED: no arguments. This driver fires nothing without --prereg-commit," >&2
    echo "         --selftest or --preconditions." >&2
    exit 2
fi
python3 "${DRIVER}" "$@"
exit $?
