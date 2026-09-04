#!/bin/sh
# FIXTURE g_unbound_fenced_ok.sh -- STATIC COMMITTED BYTES, A1WRT2 control.
# KNOWN-NEGATIVE DIRECTION: G-UNBOUND must NOT flag this file.
#
# This reproduces the SHAPE `SO3aF2` ADDENDUM 4 measured -- OpenFOAM's own
# `etc/bashrc` referencing `WM_PROJECT_DIR` before setting it, aborting a
# `source` under an active `set -u` -- together with §A4.3's repair:
#   set +u ; source "$LOADER" ; SRC_RC=$? ; set -u
# It is registered as a BEHAVIOUR the gate must exhibit on a fixture, NOT as a
# citation of a blob: this lane has NOT verified that either the defective or
# the repaired OpenFOAM bytes are committed anywhere in this repository, and
# does not claim they are.
#
# If G-UNBOUND flagged this file it would forbid the one construction that
# makes sourcing a foreign init script legal, so the negative direction here is
# load-bearing and not decorative.
set -u
LOADER=/opt/openfoam/openfoam2506/etc/bashrc
set +u
# shellcheck disable=SC1090
. "$LOADER"
echo "foam dir is $WM_PROJECT_DIR"
SRC_RC=$?
set -u
echo "source rc $SRC_RC"
