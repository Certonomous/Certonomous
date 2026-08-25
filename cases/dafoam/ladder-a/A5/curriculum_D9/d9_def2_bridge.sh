#!/usr/bin/env bash
# D9-DEF-2 BRIDGE.  NOT a frozen instrument -- written AFTER first compute and disclosed
# as such.  It edits NEITHER frozen file.
#
# THE DEFECT.  The frozen launcher and the frozen grader disagree on the endpoint stage
# DIRECTORY NAME:
#     launcher  `sed 's/\./p/; s/-/m/'` on "1.0e-5"      -> fd_1p0em5
#     grader    fmt_tag == "%.1e" then the same replaces -> fd_1p0em05
# Left alone the frozen grader finds ZERO endpoint tables and returns a FALSE
# "NOT A RESULT" from G9-4 -- an antecedent firing for a reason the mapping never
# contemplated.
#
# THE BRIDGE.  A SYMLINK per step, inside the RUN TREE (artifacts), from the name the
# grader looks for to the directory the launcher wrote.  NOTHING is copied, edited,
# regenerated or recomputed: the bytes the grader reads through the alias are the same
# inode the launcher produced, and that is asserted below by comparing md5 through both
# paths.  No frozen file is touched and no gate, threshold, cap or label moves.
set -uo pipefail
BASE="${1:?usage: d9_def2_bridge.sh <run-dir>}"
for h in 1p0em5:1p0em05 1p0em4:1p0em04 1p0em3:1p0em03 1p0em2:1p0em02; do
  src="fd_${h%%:*}"; dst="fd_${h##*:}"
  [ -d "$BASE/$src" ] || { echo "SKIP $dst: $src absent"; continue; }
  [ -e "$BASE/$dst" ] && { echo "SKIP $dst: already present"; continue; }
  ln -s "$src" "$BASE/$dst" || { echo "ABORT: cannot link $dst"; exit 1; }
  a=$(md5sum "$BASE/$src/d9_out.json" | cut -d' ' -f1)
  b=$(md5sum "$BASE/$dst/d9_out.json" | cut -d' ' -f1)
  [ "$a" = "$b" ] || { echo "ABORT: content differs through the alias $dst ($a vs $b)"; exit 1; }
  echo "BRIDGED $dst -> $src  content md5 $a IDENTICAL THROUGH BOTH PATHS"
done
