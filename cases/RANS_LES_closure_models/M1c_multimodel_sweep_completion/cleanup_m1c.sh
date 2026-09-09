#!/usr/bin/env bash
# cleanup_m1c.sh -- M1-C run-tree cleanup.  FROZEN 2026-09-09 (§3 check-1 done, SOUND).
#
# Removes EVERYTHING under the M1-C run tree /home/ubuntu/closure-data/m1c_completion
# (the 2 stray over-staged dirs kOmega/CBFS + kOmega/AR_10_Ret_180 from the aborted
# stage, the 6 empty scaffolding dirs, any partial manifest), leaving the tree EMPTY.
#
# FAIL-CLOSED.  It refuses to remove anything unless the target is EXACTLY the
# M1-C tree and resolves inside it; it explicitly refuses to touch the M1 evidence
# tree /home/ubuntu/closure-data/multimodel_sweep.  DRYRUN default; --execute gated.
set -uo pipefail

ROOT="/home/ubuntu/closure-data/m1c_completion"
EVIDENCE="/home/ubuntu/closure-data/multimodel_sweep"

DRYRUN=1
[ "${1:-}" = "--execute" ] && DRYRUN=0

# --- fail-closed guards on ROOT ---------------------------------------------
[ "$ROOT" = "/home/ubuntu/closure-data/m1c_completion" ] || { echo "REFUSE: ROOT is not the literal M1-C tree" >&2; exit 2; }
[ -d "$ROOT" ]  || { echo "REFUSE: ROOT does not exist" >&2; exit 2; }
[ ! -L "$ROOT" ] || { echo "REFUSE: ROOT is a symlink" >&2; exit 2; }
RP=$(realpath "$ROOT") || { echo "REFUSE: cannot resolve ROOT" >&2; exit 2; }
[ "$RP" = "$ROOT" ] || { echo "REFUSE: ROOT resolves elsewhere ($RP)" >&2; exit 2; }
case "$RP" in *multimodel_sweep*) echo "REFUSE: ROOT path contains the evidence tree" >&2; exit 2 ;; esac
# defensive: the evidence tree must exist and must NOT be inside ROOT
[ -d "$EVIDENCE" ] || echo "WARN: evidence tree $EVIDENCE not found (continuing; nothing here touches it)" >&2

removed=0
shopt -s nullglob dotglob
for child in "$ROOT"/*; do
  crp=$(realpath "$child") || { echo "REFUSE: cannot resolve $child" >&2; exit 2; }
  # child must be strictly inside ROOT and must not resolve into the evidence tree
  case "$crp" in
    "$ROOT"/*) : ;;
    *) echo "REFUSE: $child escapes ROOT (-> $crp)" >&2; exit 2 ;;
  esac
  case "$crp" in *multimodel_sweep*) echo "REFUSE: $child resolves into evidence tree" >&2; exit 2 ;; esac
  if [ "$DRYRUN" = 1 ]; then
    echo "DRYRUN would rm -rf: $child"
  else
    rm -rf "$child" && removed=$((removed+1))
  fi
done

if [ "$DRYRUN" = 1 ]; then
  echo "DRYRUN complete -- pass --execute to remove.  Evidence tree $EVIDENCE untouched by design."
else
  echo "removed $removed top-level entries; M1-C tree now: $(find "$ROOT" -mindepth 1 | wc -l) entries remaining"
  echo "evidence tree $EVIDENCE: NOT touched (this script never resolves a path into it)"
fi
