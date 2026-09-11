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

# ---------------------------------------------------------------------------
# 2026-09-07 -- THE BOARD-CLOBBER GUARD (L-499 / L-499-CORRECTION). The enforcing
# instrument the lesson was owed and never got. docs/LAB_STATE.md is the shared
# handoff board; a commit must NEVER reduce its top-level section count or its
# block (## .. #####) count versus the parent -- that is a clobber / sweep-delete
# (the L-499 cascade silently dropped 17,944 lines and 8 blocks). Counts may stay
# EQUAL (a content edit) or GROW (an append, or a swept-in peer block whose content
# SURVIVES -- the survivable direction). A DECREASE aborts and RESTORES the ref to
# the parent (CAS rollback; the working tree is untouched). Intentional block
# removal (a coordinated de-dup/de-bloat) is done OUTSIDE this guarded path.
# ---------------------------------------------------------------------------
BOARD_PATH="docs/LAB_STATE.md"
_board_counts() {  # $1 = <rev>  ; prints "<sections> <blocks>" for that rev's board (0 0 if absent)
  local content secs blocks
  content=$(git show "$1:$BOARD_PATH" 2>/dev/null || true)
  secs=$(printf '%s\n' "$content" | grep -cE '^## ' || true)
  blocks=$(printf '%s\n' "$content" | grep -cE '^#{2,5} ' || true)
  echo "${secs:-0} ${blocks:-0}"
}
# returns 0 if NEW did not drop sections/blocks vs OLD; 1 (clobber) if either dropped.
assert_board_not_clobbered() {  # $1 OLD rev  $2 NEW rev
  local os ob ns nb
  read -r os ob < <(_board_counts "$1")
  read -r ns nb < <(_board_counts "$2")
  echo "--- BOARD GUARD: parent(sections=$os blocks=$ob) -> new(sections=$ns blocks=$nb)" >&2
  if [ "$ns" -lt "$os" ] || [ "$nb" -lt "$ob" ]; then return 1; fi
  return 0
}

# ---------------------------------------------------------------------------
# 2026-09-07 -- THE CALIBRATION-ID GUARD (L-500 enforced as a commit-time invariant).
# A hand-rolled / non-canonical tool id (e.g. %N nanoseconds, or a malformed body)
# that bypasses --allocate-id is the S-119 recurrence that TWICE blocked the whole
# fleet's COST_CALIBRATION appends at append_record.py's D549 clause-1b. This refuses
# such a row AT THE OFFENDING COMMIT -- turning the write-time lesson into a
# choke-point guard, parallel to the board-clobber guard. It inspects ONLY the
# commit's ADDED rows (git diff OLD NEW), so pre-existing rows never retrigger;
# numeric C-NNN rows are not timestamp-shaped so are not flagged; canonical
# --allocate-id rows (incl. a CORRECTION row re-issued for a poison row) pass; only a
# NEWLY-ADDED non-canonical timestamp id aborts. Intentional exact-exclusion of an
# already-landed poison row lives in append_record.py's KNOWN_EXCLUDED, not here.
# ---------------------------------------------------------------------------
CAL_PATH="docs/COST_CALIBRATION.md"
# returns 0 if NEW adds no non-canonical timestamp C-id row vs OLD; 1 if it does.
assert_no_new_noncanonical_cal_id() {  # $1 OLD rev  $2 NEW rev
  local added bad
  # ADDED timestamp-shaped C-id rows only (git diff '+' lines; a numeric C-NNN row
  # has no 8-digit date+T so never matches, and the +++ header cannot match \+\|).
  added=$(git diff "$1" "$2" -- "$CAL_PATH" | grep -E '^\+\|[ \t]*C-[0-9]{8}T' || true)
  [ -z "$added" ] && return 0
  # ...of those, the ones whose FIRST CELL is NOT the canonical --allocate-id form
  # (%f = 6 micro-digit fractional seconds + an 8-hex body). The canonical match is
  # ANCHORED to the id column (^\+\| .. canonical .. \|), mirroring the `added`
  # anchor -- an UNANCHORED match would let a canonical id string ANYWHERE ELSE in
  # the row (e.g. a citation in the description column) mask a non-canonical id in
  # the first cell (the bypass §3 caught). A 9-digit nano id or a non-hex body in the
  # id column fails this and is flagged.
  bad=$(printf '%s\n' "$added" | grep -vE '^\+\|[ \t]*C-[0-9]{8}T[0-9]{6}\.[0-9]{6}Z-[0-9a-f]{8}[ \t]*\|' || true)
  echo "--- CAL-ID GUARD: checked added timestamp C-id rows vs canonical C-\d{8}T\d{6}.\d{6}Z-[0-9a-f]{8}" >&2
  [ -n "$bad" ] && { printf 'NON-CANONICAL added calibration id row(s):\n%s\n' "$bad" >&2; return 1; }
  return 0
}

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
  # --- board-clobber guard arm (L-499 enforcing instrument): a dropped block MUST be
  #     caught (RED); an append MUST pass (GREEN).  §28: the guard is shown able to fire.
  mkdir -p docs
  printf '## verification\n##### UPDATE V-1 — a\n##### UPDATE V-2 — b\n' > docs/LAB_STATE.md
  git add docs/LAB_STATE.md && git commit -qm board_v1
  P=$(git rev-parse HEAD)
  printf '## verification\n##### UPDATE V-1 — a\n##### UPDATE V-2 — b\n##### UPDATE V-3 — c\n' > docs/LAB_STATE.md
  git add docs/LAB_STATE.md && git commit -qm board_v2_append
  G=$(git rev-parse HEAD)
  printf '## verification\n##### UPDATE V-1 — a\n' > docs/LAB_STATE.md
  git add docs/LAB_STATE.md && git commit -qm board_v3_clobber
  R=$(git rev-parse HEAD)
  if assert_board_not_clobbered "$P" "$G" 2>/dev/null; then
    echo "  board +: GREEN append PASSES the guard (blocks grew)"
  else echo "CONTROL FAIL: the guard rejected a legitimate append"; fail=1; fi
  if assert_board_not_clobbered "$G" "$R" 2>/dev/null; then
    echo "CONTROL FAIL: the guard MISSED a dropped block (clobber went undetected)"; fail=1
  else echo "  board -: RED clobber CAUGHT (a dropped block would abort+restore)"; fi
  # --- calibration-id guard arm (L-500 enforcing instrument): a NEWLY-ADDED
  #     non-canonical tool-id row MUST be caught (RED, both a nano id and a bad body);
  #     a canonical --allocate-id row, a numeric C-NNN row and a prose-only edit MUST
  #     pass (GREEN). §28: the guard is shown able to fire AND to stay silent.
  printf '| id | date | team | process |\n|---|---|---|---|\n| C-20260901T120000.000000Z-00000000 | 2026-09-01 | seed | base |\n' > docs/COST_CALIBRATION.md
  git add docs/COST_CALIBRATION.md && git commit -qm cal_base
  CB=$(git rev-parse HEAD)
  printf '| C-20260907T195722.461339Z-abcd1234 | 2026-09-07 | verification | canonical 6-digit |\n' >> docs/COST_CALIBRATION.md
  git add docs/COST_CALIBRATION.md && git commit -qm cal_green_canonical
  CG=$(git rev-parse HEAD)
  printf '| C-20260907T195722.461339981Z-b826b62e | 2026-09-07 | dafoam | NANO hand-roll |\n' >> docs/COST_CALIBRATION.md
  git add docs/COST_CALIBRATION.md && git commit -qm cal_red_nano
  CR=$(git rev-parse HEAD)
  printf '| C-20260906T232437.922647Z-w4reanc | 2026-09-06 | dafoam | bad body |\n' >> docs/COST_CALIBRATION.md
  git add docs/COST_CALIBRATION.md && git commit -qm cal_red_badbody
  CR2=$(git rev-parse HEAD)
  # EVASION arm (§3-found bypass, §28 load-bearing): first cell is a NON-canonical
  # nano id, but the description column CITES a canonical id string. WITHOUT the
  # id-column anchor on the `bad` grep this row wrongly PASSES; WITH it, CAUGHT.
  printf '| C-20260907T195722.461339981Z-b826b62e | 2026-09-07 | dafoam | evasion: cites C-20260101T000000.000000Z-deadbeef |\n' >> docs/COST_CALIBRATION.md
  git add docs/COST_CALIBRATION.md && git commit -qm cal_red_evasion
  CE=$(git rev-parse HEAD)
  printf '| C-104 | 2026-09-07 | closure | numeric legacy id |\n' >> docs/COST_CALIBRATION.md
  git add docs/COST_CALIBRATION.md && git commit -qm cal_green_numeric
  CN=$(git rev-parse HEAD)
  printf 'A prose line naming no new id row.\n' >> docs/COST_CALIBRATION.md
  git add docs/COST_CALIBRATION.md && git commit -qm cal_green_prose
  CP=$(git rev-parse HEAD)
  if assert_no_new_noncanonical_cal_id "$CB" "$CG" 2>/dev/null; then
    echo "  cal +: GREEN canonical --allocate-id row PASSES the guard"
  else echo "CONTROL FAIL: the guard rejected a canonical calibration id row"; fail=1; fi
  if assert_no_new_noncanonical_cal_id "$CG" "$CR" 2>/dev/null; then
    echo "CONTROL FAIL: the guard MISSED a NEW nanosecond (hand-rolled) id row"; fail=1
  else echo "  cal -: RED nanosecond id CAUGHT (would abort+orphan; the S-119 recurrence)"; fi
  if assert_no_new_noncanonical_cal_id "$CR" "$CR2" 2>/dev/null; then
    echo "CONTROL FAIL: the guard MISSED a NEW malformed-body id row"; fail=1
  else echo "  cal -: RED malformed-body id CAUGHT"; fi
  if assert_no_new_noncanonical_cal_id "$CR2" "$CE" 2>/dev/null; then
    echo "CONTROL FAIL: the guard MISSED an evasion row (canonical id cited in the description masking a non-canonical id column) -- the id-column anchor is NOT load-bearing"; fail=1
  else echo "  cal -: RED evasion CAUGHT (id-column anchor is load-bearing; unanchored, this row would wrongly PASS)"; fi
  if assert_no_new_noncanonical_cal_id "$CE" "$CN" 2>/dev/null; then
    echo "  cal +: GREEN numeric C-NNN row PASSES (not timestamp-shaped)"
  else echo "CONTROL FAIL: the guard flagged a numeric C-NNN row"; fail=1; fi
  if assert_no_new_noncanonical_cal_id "$CN" "$CP" 2>/dev/null; then
    echo "  cal +: GREEN prose-only edit PASSES (no new id row)"
  else echo "CONTROL FAIL: the guard flagged a prose-only edit"; fail=1; fi
  # --- the planted EMPTY-TREE control (2026-09-11, verification).
  # Demonstrates BOTH halves: that the unguarded path commits an empty tree and
  # reports success, and that the guard refuses it. A guard never shown firing
  # is not a guard.
  ET=$(mktemp -d); (
    cd "$ET"
    git init -q . && git config user.email s@l && git config user.name s
    echo x > g && git add g && git commit -qm base
  ) >/dev/null 2>&1
  EOLD=$(git -C "$ET" rev-parse HEAD)
  # stage the file UNCHANGED -- exactly the scenario that bit heat-transfer
  ETREE=$(cd "$ET" && GIT_INDEX_FILE=$ET/.idx sh -c 'rm -f $GIT_INDEX_FILE; git read-tree HEAD; git update-index --add -- g; git write-tree')
  EN=$(git -C "$ET" diff-tree -r --name-only "$EOLD^{tree}" "$ETREE" | wc -l)
  if [ "$EN" -eq 0 ]; then
    echo "  empty +: an UNCHANGED file yields a tree identical to the parent's (N=0)"
  else echo "CONTROL FAIL: the empty-tree scenario could not be built (N=$EN)"; fail=1; fi
  # the PRE-FIX behaviour, driven: every downstream check passes over nothing
  ENEW=$(git -C "$ET" commit-tree "$ETREE" -p "$EOLD" -m "empty as the unguarded path would commit it")
  if printf '%s' "$ENEW" | grep -qE '^[0-9a-f]{40}$'; then
    echo "  empty +: UNGUARDED, commit-tree returns a REAL 40-hex sha over the empty tree"
  else echo "CONTROL FAIL: commit-tree did not return a sha"; fail=1; fi
  git -C "$ET" update-ref refs/heads/"$(git -C "$ET" symbolic-ref --short HEAD)" "$ENEW" "$EOLD" 2>/dev/null
  if [ "$(git -C "$ET" rev-parse HEAD)" = "$ENEW" ]; then
    echo "  empty +: UNGUARDED, the CAS SUCCEEDS and HEAD genuinely MOVES -- the"
    echo "           HEAD-MOVED gate is SATISFIED and would print [HEAD-MOVED ASSERTED]"
  else echo "CONTROL FAIL: HEAD did not move; the trap cannot be demonstrated"; fail=1; fi
  if [ -z "$(git -C "$ET" diff-tree -r --numstat HEAD~1 HEAD)" ]; then
    echo "  empty -: and the rule-10 POST-COMMIT VERIFY prints NOTHING -- a clean-looking"
    echo "           verify OF NOTHING, which is the defect this guard exists to catch"
  else echo "CONTROL FAIL: the post-commit verify was not empty"; fail=1; fi
  # THE GUARD ITSELF, on the same N
  if [ "$EN" -eq 0 ]; then
    echo "  empty +: GUARDED, 'N -eq 0' REFUSES this commit BEFORE commit-tree runs"
  else echo "CONTROL FAIL: the guard would not fire on N=0"; fail=1; fi
  # and the guard must NOT fire on a real change (it must be capable of passing)
  (cd "$ET" && echo y > g && git add g && git commit -qm real) >/dev/null 2>&1
  RN=$(git -C "$ET" diff-tree -r --name-only 'HEAD~1^{tree}' 'HEAD^{tree}' | wc -l)
  if [ "$RN" -eq 1 ]; then
    echo "  empty -: a REAL one-path change gives N=1 and PASSES the guard (not a blanket refusal)"
  else echo "CONTROL FAIL: a real change did not give N=1 (N=$RN)"; fail=1; fi
  rm -rf "$ET"
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
  # EMPTY-TREE GUARD (2026-09-11, verification; raised by heat-transfer after this
  # wrapper committed an EMPTY TREE for them tonight and reported success).
  #
  # $N was COMPUTED, PRINTED, AND NEVER TESTED. With a tree identical to the
  # parent's, every downstream check still passes -- commit-tree returns a real
  # 40-hex sha, the CAS succeeds, HEAD genuinely moves to $NEW, the HEAD-MOVED
  # gate at the foot is SATISFIED, and the rule-10 post-commit verify prints
  # NOTHING because there is nothing to print. The operator is told
  # "COMMITTED ... [HEAD-MOVED ASSERTED]" over an empty verify.
  #
  # That is precisely the failure this file's own header (lines 20-28) lectures
  # about -- "a clean-looking verify OF NOTHING" and "AN ASSERTION THAT CANNOT
  # FAIL IN THE SCENARIO IT EXISTS TO CATCH" -- committed by the file that
  # carries the lecture. The header was right and nothing enforced it.
  #
  # Refused BEFORE commit-tree, so no object is created at all: an empty commit
  # is not an orphan to inspect, it is a lie to avoid telling.
  if [ "$N" -eq 0 ]; then
    echo "ABORT: the tree is IDENTICAL to the parent's -- 0 paths changed, ${#FILES[@]} requested."
    echo "--- NOTHING WOULD HAVE BEEN COMMITTED. No commit object was created."
    echo "--- Every downstream check would have PASSED: commit-tree returns a real sha,"
    echo "    the CAS succeeds, HEAD moves, and the post-commit verify prints an EMPTY diff."
    echo "--- Inspect why your files are unchanged versus HEAD \$OLD=$OLD. Do NOT force."
    exit 2
  fi
  # $N < requested is LEGITIMATE and is reported rather than refused: a directory
  # argument expands to every file under it and some are routinely unchanged.
  # $N > requested cannot occur -- only "${FILES[@]}" were staged into an index
  # read from $OLD -- so it is asserted rather than assumed.
  if [ "$N" -gt "${#FILES[@]}" ]; then
    echo "ABORT: $N paths changed but only ${#FILES[@]} were requested -- a path this"
    echo "--- invocation did not stage is in the tree. That is the sweep class; never force."
    exit 2
  fi
  if [ "$N" -lt "${#FILES[@]}" ]; then
    echo "--- NOTE: $N of ${#FILES[@]} requested paths differ from \$OLD; the rest are unchanged"
    echo "    and contribute nothing to this commit. Expected for a directory argument."
  fi
  NEW=$(git commit-tree "$TREE" -p "$OLD" -F "$MSG")
  # L-382: a commit sha that is empty or malformed makes update-ref a silent no-op.
  if ! printf '%s' "$NEW" | grep -qE '^[0-9a-f]{40}$'; then
    echo "ABORT: commit-tree returned a non-sha: '$NEW'"; exit 2
  fi
  # BOARD-CLOBBER GUARD (L-499 enforcing instrument): if this commit touched the shared
  # board, refuse to LAND it when it would DROP a section or block vs the parent (a
  # clobber / sweep-delete -- the L-499 cascade). Checked on the commit object $NEW
  # BEFORE update-ref, so a clobber never reaches the branch; $NEW is left an
  # unreferenced orphan. Counts equal (edit) or grown (append / swept-in peer block,
  # content survives) pass; only a DECREASE aborts.
  for _bf in "${FILES[@]}"; do
    if [ "$_bf" = "$BOARD_PATH" ]; then
      if ! assert_board_not_clobbered "$OLD" "$NEW"; then
        echo "ABORT: BOARD CLOBBER -- $BOARD_PATH would DROP a section/block vs parent $OLD (L-499 guard)."
        echo "--- commit $NEW is an unreferenced ORPHAN; NOTHING landed. Inspect what dropped a block; never force."
        exit 2
      fi
      break
    fi
  done
  # CALIBRATION-ID GUARD (L-500 enforcing instrument): if this commit touched the
  # calibration ledger, refuse to LAND a NEWLY-ADDED non-canonical tool-id row (one
  # not minted by --allocate-id). Checked on $NEW BEFORE update-ref, so it never
  # reaches the branch; $NEW is left an orphan. Pre-existing rows and numeric C-NNN
  # rows are not flagged; only a new non-canonical timestamp id aborts.
  for _cf in "${FILES[@]}"; do
    if [ "$_cf" = "$CAL_PATH" ]; then
      if ! assert_no_new_noncanonical_cal_id "$OLD" "$NEW"; then
        echo "ABORT: CALIBRATION ID GUARD -- a NEW non-canonical tool-id row (not --allocate-id-minted) would land in $CAL_PATH; mint via --allocate-id (canonical %f=6)."
        echo "--- $NEW is an unreferenced ORPHAN; nothing landed (L-500 enforced)."
        exit 2
      fi
      break
    fi
  done
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
