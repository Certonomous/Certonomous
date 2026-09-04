#!/bin/sh
# FIXTURE g_unbound_positive.sh -- STATIC COMMITTED BYTES, A1WRT2 control.
# KNOWN-POSITIVE DIRECTION: G-UNBOUND must FLAG this file.
# `MISSING_PIN` is expanded at line 9 under an active `set -u` and is never
# assigned anywhere in the file, so the shell aborts at 127-class before the
# container starts.  Committed WITH the instrument so the known-positive is
# guaranteed to be inside the searched population -- unlike the historical
# `rc 127` bytes, which were repaired on disk and never landed in git.
set -u
STAGED_ROOT=/mnt/case
echo "staging into $STAGED_ROOT"
echo "pinning $MISSING_PIN"
echo "done"
