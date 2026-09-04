#!/bin/sh
# FIXTURE g_unbound_negative.sh -- STATIC COMMITTED BYTES, A1WRT2 control.
# KNOWN-NEGATIVE DIRECTION: G-UNBOUND must NOT flag this file.
# Byte-for-byte the positive fixture with the one assignment restored, so the
# pair differs in exactly the variable under test and in nothing else.
set -u
STAGED_ROOT=/mnt/case
MISSING_PIN=sha256:2927768a16ac
echo "staging into $STAGED_ROOT"
echo "pinning $MISSING_PIN"
echo "done"
