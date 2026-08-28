#!/bin/bash
# Private-index commit: commit_private.sh <msgfile> <path> [<path>...]
#                       commit_private.sh --selftest
#
# Never touches the shared index (reads HEAD into a private index under
# /home/ubuntu/closure-data, which no scratchpad wipe reaches). Asserts the
# diff-tree contains only the given paths. Refuses PDFs, extracted text and
# binary data; directories are expanded to files.
#
# ---------------------------------------------------------------------------
# 2026-08-28 -- THE REFUSED-CAS GAP. Routed by the chief; landed by
# verification-supervisor. `git update-ref <ref> <new> <old>` is a
# compare-and-swap: it REFUSES when a peer moved HEAD between our `rev-parse`
# and our `update-ref`. On refusal the commit object still EXISTS -- it is a
# valid, fully-formed ORPHAN, reachable by sha and resolvable by every git
# command. So `git rev-parse --short "$NEW"`, `git show "$NEW"`, a prefix
# byte-check against "$NEW", and a `diff-tree` against it ALL SUCCEED AND ALL
# DESCRIBE A COMMIT THAT IS ON NO BRANCH. A dafoam lane printed
# "POST-COMMIT VERIFY" and "PREFIX BYTE-IDENTICAL" for exactly such an orphan:
# a clean-looking verify OF NOTHING.
#
# THE VERIFY MUST BE GATED ON THE REF ACTUALLY MOVING, NEVER ON THE COMMIT
# OBJECT EXISTING. The discriminating question is `git rev-parse HEAD == $NEW`,
# and nothing else answers it: the object's existence is guaranteed either way.
#
# This is the sibling of L-382 (the empty-sha case, where update-ref is a silent
# no-op that prints CAS OK). Same family: AN ASSERTION THAT CANNOT FAIL IN THE
# SCENARIO IT EXISTS TO CATCH.
# ---------------------------------------------------------------------------
set -euo pipefail
cd /home/ubuntu/Certonomous

MAX_TRIES=5

# --- the planted refused-CAS control (L-314). Driven with --selftest.
if [ "${1:-}" = "--selftest" ]; then
  T=$(mktemp -d); cd "$T"
  git init -q . && git config user.email s@l && git config user.name s
  echo a > f && git add f && git commit -qm one
  A=$(git rev-parse HEAD)
  echo b > f && git add f && git commit -qm two          # a "peer" moves HEAD
  B=$(git rev-parse HEAD)
  # Build a commit whose parent is the STALE A, then attempt the CAS against A.
  TREE=$(git write-tree)
  ORPHAN=$(git commit-tree "$TREE" -p "$A" -m orphan)
  rc=0; git update-ref refs/heads/"$(git symbolic-ref --short HEAD)" "$ORPHAN" "$A" 2>/dev/null || rc=$?
  fail=0
  if [ "$rc" -eq 0 ]; then echo "CONTROL FAIL: the CAS was ACCEPTED against a stale parent"; fail=1
  else echo "  control +: CAS REFUSED against a stale parent (rc=$rc)"; fi
  # THE DISCRIMINATOR: the orphan object still resolves, so object-existence
  # checks pass while the ref did NOT move.
  if git rev-parse --quiet --verify "$ORPHAN^{commit}" >/dev/null; then
    echo "  control +: the orphan STILL RESOLVES (this is why object checks are worthless here)"
  else echo "CONTROL FAIL: orphan did not resolve; the trap cannot be demonstrated"; fail=1; fi
  if [ "$(git rev-parse HEAD)" = "$ORPHAN" ]; then
    echo "CONTROL FAIL: HEAD moved to the orphan"; fail=1
  else echo "  control -: HEAD is still $B -- the ref did NOT move, which is the only true test"; fi
  cd /; rm -rf "$T"
  [ "$fail" -eq 0 ] && { echo "SELFTEST PASS"; exit 0; } || { echo "SELFTEST FAIL"; exit 2; }
fi

MSG="$1"; shift
export GIT_INDEX_FILE=/home/ubuntu/closure-data/supervisor/private.index

TRY=0
while : ; do
  TRY=$((TRY+1))
  rm -f "$GIT_INDEX_FILE"
  # HEAD captured ONCE per attempt, and used for read-tree, the assert and -p.
  OLD=$(git rev-parse HEAD)
  git read-tree "$OLD"
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
  # L-382: a commit sha that is empty or malformed makes update-ref a silent no-op.
  if ! printf '%s' "$NEW" | grep -qE '^[0-9a-f]{40}$'; then
    echo "ABORT: commit-tree returned a non-sha: '$NEW'"; exit 2
  fi
  rc=0; git update-ref refs/heads/main "$NEW" "$OLD" || rc=$?
  if [ "$rc" -eq 0 ]; then break; fi
  # REFUSED CAS: a peer moved HEAD. The commit object exists and is an ORPHAN.
  # Do NOT verify it, do NOT report it -- re-do the whole sequence on new HEAD.
  echo "--- CAS REFUSED (a peer moved HEAD between rev-parse and update-ref)."
  echo "--- The commit object $NEW EXISTS and is an ORPHAN on no branch; it is NOT verified and NOT reported."
  if [ "$TRY" -ge "$MAX_TRIES" ]; then
    echo "ABORT: CAS refused $TRY times; nothing was landed. Inspect, never force."; exit 2
  fi
  echo "--- retrying the whole read-tree/write-tree/commit-tree on the new HEAD (attempt $((TRY+1))/$MAX_TRIES)"
done

# THE GATE: every line below is reached ONLY if the ref actually moved.
HEAD_NOW=$(git rev-parse HEAD)
if [ "$HEAD_NOW" != "$NEW" ]; then
  echo "ABORT: update-ref returned 0 but HEAD is $HEAD_NOW, not $NEW. NOTHING IS VERIFIED."; exit 2
fi
unset GIT_INDEX_FILE
echo "COMMITTED $(git rev-parse --short HEAD) (parent $(git rev-parse --short "$OLD"))  [HEAD-MOVED ASSERTED]"
echo "--- POST-COMMIT VERIFY (rule 10; against HEAD, never against \$NEW):"
git diff-tree -r --numstat HEAD~1 HEAD
rm -f /home/ubuntu/closure-data/supervisor/private.index
