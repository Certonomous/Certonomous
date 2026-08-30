#!/usr/bin/env bash
# R3 -- THE COMMIT-HELPER RENAME MODE.  THE ITEM IS BLOCKED.
# The launch_cmd of verification/campaign/queue_entry_R3_COMMIT_RENAME_MODE.json.
#
#   bash scripts/run_r3_rename_mode_repair.sh --prereg-commit=<sha>   -> BLOCKED, rc 2
#   bash scripts/run_r3_rename_mode_repair.sh --selftest              -> rc 0
#   bash scripts/run_r3_rename_mode_repair.sh --preconditions
#
# This wrapper issues NO git command of any kind and returns the python exit code
# unchanged.  The shared index is never touched.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRIVER="${HERE}/r3_rename_mode_driver.py"
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
