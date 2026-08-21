#!/bin/bash
# Private-index commit for the closure team: commit_private.sh <msgfile> <path> [<path>...]
# Never touches the shared index (reads HEAD into a private index under /home/ubuntu/closure-data,
# which no scratchpad wipe reaches). Asserts the diff-tree contains only the given paths.
# Refuses PDFs, extracted text, and binary data; directories are expanded to files.
set -euo pipefail
cd /home/ubuntu/Certonomous
MSG="$1"; shift
export GIT_INDEX_FILE=/home/ubuntu/closure-data/supervisor/private.index
rm -f "$GIT_INDEX_FILE"
OLD=$(git rev-parse HEAD)
git read-tree HEAD
FILES=()
for p in "$@"; do
  if [ -d "$p" ]; then
    while IFS= read -r f; do FILES+=("$f"); done < <(find "$p" -type f ! -name '*.pdf' ! -name '*.txt' ! -name '*.npy' ! -name '*.npz' ! -name '*.h5' ! -name '*.pt' ! -name '*.pkl' ! -path '*/__pycache__/*' | sort)
  else FILES+=("$p"); fi
done
for f in "${FILES[@]}"; do case "$f" in *.pdf|docs/papers/*.txt) echo "REFUSE $f"; exit 2;; esac; done
git update-index --add -- "${FILES[@]}"
TREE=$(git write-tree)
echo "--- diff-tree HEAD..new (must list only our files):"
git diff-tree -r --name-status "$OLD^{tree}" "$TREE"
N=$(git diff-tree -r --name-only "$OLD^{tree}" "$TREE" | wc -l)
echo "--- $N paths changed; ${#FILES[@]} requested"
NEW=$(git commit-tree "$TREE" -p "$OLD" -F "$MSG")
git update-ref refs/heads/main "$NEW" "$OLD"
echo "COMMITTED $(git rev-parse --short "$NEW") (parent $(git rev-parse --short "$OLD"))"
rm -f "$GIT_INDEX_FILE"
