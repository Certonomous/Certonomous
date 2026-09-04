#!/bin/sh
# FIXTURE g_unbound_fence_unclosed.sh -- STATIC COMMITTED BYTES, A1WRT2 control.
# KNOWN-POSITIVE DIRECTION: G-UNBOUND must FLAG this file.
#
# The failure mode the fence itself introduces: `set +u` is opened to cross a
# foreign init script and is NEVER closed, so every expansion after it -- for
# the whole remaining launcher, including the container invocation -- runs with
# the guard disabled.  A gate that only checks for unassigned expansions would
# read this file as clean, which is exactly why the unclosed fence is its own
# flagged condition rather than an absence.
set -u
LOADER=/opt/openfoam/openfoam2506/etc/bashrc
set +u
# shellcheck disable=SC1090
. "$LOADER"
echo "foam dir is $WM_PROJECT_DIR"
docker run --rm -v "$STAGED_ROOT":/mnt "$IMG" bash -lc "$CMD"
