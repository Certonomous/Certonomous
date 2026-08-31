#!/bin/bash
# Sanaa's PLUMBING FREEZE directive, 2026-08-31 (etc/sessions/*_sanaa_plumbing_freeze.md):
# the shared index is never used by anyone under rule 10, so clearing it to HEAD
# can clobber nothing. Runs under flock; read-tree only — the worktree is never touched.
set -u
cd /home/ubuntu/Certonomous || exit 1
exec 9>/tmp/certonomous_index_autoclear.lock
flock -n 9 || exit 0
git read-tree HEAD 2>>/home/ubuntu/harness-state/index_autoclear.log
# planted check: a tracked file's staged blob must equal its HEAD blob after the clear
P=docs/LAB_STATE.md
S=$(git rev-parse ":$P" 2>/dev/null); H=$(git rev-parse "HEAD:$P" 2>/dev/null)
if [ "$S" = "$H" ] && [ -n "$S" ]; then R=OK; else R=FAIL; fi
echo "$(date -u +%FT%TZ) read-tree HEAD done planted_check=$R" >> /home/ubuntu/harness-state/index_autoclear.log
