# .gitignore Rebuild Proposal (H3b)

**Status:** DEFERRED from H3a due to multi-agent flight. Execution must occur in a quiet window when no sweeping is active (all agents idle).

---

## Overview

This proposal documents the entries proposed for `.gitignore` addition and the atomic operation required to execute them safely. **The moves described below CANNOT occur without simultaneously modifying `.gitignore`, because `grep` in this lab honours `.gitignore` via `ugrep --ignore-files`. Any `git rm --cached` move executed *before* the rule is added will be visible to ongoing sweeps, potentially blinding them.**

---

## Proposed Rules and Affected Files

### 1. Build Retry Logs (10 files, 2.2 KB total) — NEW RULE

**Proposed rule:**
```
# Build retry logs (added 2026-08-12) — transient output from failed builds
mbc_retry.err
mbc_retry.log
mbc_retry2.err
mbc_retry2.log
mbc_retry3.err
mbc_retry3.log
mbc_retry4.err
mbc_retry4.log
mbc_retry6.err
mbc_retry6.log
```

**Rationale:** These files are build-time transient artifacts, not evidence or configuration. They are currently TRACKED in git at HEAD but completely unreferenced throughout the codebase (verified by sweep: `grep -r "mbc_retry"` returns only `.gitignore` line 45). They total 2.2 KB and serve no function; they appear to be stray outputs from interrupted build attempts during early development.

**Files affected (currently visible):**
- `/mbc_retry.err` (0 bytes)
- `/mbc_retry.log` (663 bytes)
- `/mbc_retry2.err` (0 bytes)
- `/mbc_retry2.log` (615 bytes)
- `/mbc_retry3.err` (235 bytes)
- `/mbc_retry3.log` (0 bytes)
- `/mbc_retry4.err` (0 bytes)
- `/mbc_retry4.log` (440 bytes)
- `/mbc_retry6.err` (0 bytes)
- `/mbc_retry6.log` (258 bytes)

**Execution (atomic, single commit):**
```bash
# Step 1: Add rule to .gitignore
git add .gitignore
git commit -m "Add .gitignore rule for build retry logs" -- .gitignore

# Step 2: Untrack and move (atomic with .gitignore rule now in place)
git rm --cached mbc_retry.err mbc_retry.log mbc_retry2.err mbc_retry2.log \
  mbc_retry3.err mbc_retry3.log mbc_retry4.err mbc_retry4.log \
  mbc_retry6.err mbc_retry6.log
mv mbc_retry*.err mbc_retry*.log evidence/
git add -A evidence/
git commit -m "Move build retry logs to evidence/" -- mbc_retry*.err mbc_retry*.log evidence/
```

---

### 2. badFaces File (7 bytes) — CLEANUP NOTE

**Status:** Already ignored (present in `.gitignore` at line 45 as `badFaces`), untracked on disk, no action required.

**Rationale:** This file exists on disk but is already ignored by `.gitignore:45`. It is untracked and invisible to `git status`. It is not referenced anywhere in the codebase. The file harms nothing and requires no action. If an agent encounters it, the presence is benign.

---

## Critical: Wheels Tracked at HEAD (numpy, h5py)

**Files in question:**
- `numpy-2.5.1-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl` (15.9 MB, tracked at HEAD)
- `h5py-3.16.0-cp312-cp312-manylinux_2_28_x86_64.whl` (5.2 MB, tracked at HEAD)

**Status:** DO NOT SWEEP THESE FROM HISTORY without simultaneously untracking them at HEAD.

**The trap:** Both wheels are flagged in `/docs/MOVE_MAP_HISTORY_PURGE.md` as the largest safe reclaim from git history (21.1 MB total). A history-purge operation (e.g., `git filter-branch` or BFG) can remove them from all past commits, reducing `.git` size. **However, if they are NOT simultaneously untracked at HEAD (via `git rm --cached`), the next commit to the working tree will reintroduce both wheels back into git history.** This creates a classic history-purge false success: the `.git` folder shrinks, but the next mutation re-expands it to nearly the original size.

**Required coordination:** Whoever executes the history purge MUST:
1. Run the purge tool (BFG, filter-branch, etc.) to remove wheels from history
2. IN THE SAME SESSION, untrack the wheels at HEAD: `git rm --cached numpy-*.whl h5py-*.whl`
3. Add a rule to `.gitignore` if not already present (verify first)
4. Commit the untracking

Alternatively, if the intent is to KEEP the wheels (for reproducibility or caching), add them to `.gitignore` without purging history; they then stay in git but are invisible to new commits.

---

## Referenced Files — DO NOT SWEEP

**These files are referenced by `/docs/HANDOFF-UQ.md` and are evidence. They must NOT be moved, deleted, or ignored:**
- `uq_batch.err` (0 bytes, tracked)
- `uq_batch.log` (31 KB, tracked)

**Citation:** `/docs/HANDOFF-UQ.md` line: "`uq_batch.log` in the worktree root; relaunch with..."

These are handoff evidence and part of the durable record. They remain at the repo root with full tracking.

---

## Atomic Execution Requirement

**This proposal CANNOT be executed piecemeal.** The circular dependency arises from the fact that:
- `grep` (via `ugrep --ignore-files`) honours `.gitignore` dynamically
- If `.gitignore` is not yet updated, `git rm --cached mbc_retry*` removes the files from the index, but downstream `grep` sweeps may still see them as untracked, leading to false negatives in searches
- If an agent is sweeping during a partial execution, it may become blind to one of the rule's states

**Execution window:** This rebuild must occur when ALL agents are idle (verified via DOCKET as clear or manually confirmed). A single commit that bundles:
1. `.gitignore` update (the rule)
2. `git rm --cached` for mbc_retry files
3. Move to `evidence/`
4. Any other synchronized cleanup (e.g., wheel untracking if pursued separately)

into one or two tightly-sequenced commits, back-to-back in the same window, ensures no intermediate state blinds a sweep.

---

## Summary Table

| Item | Category | Size | Status | Action | Notes |
|------|----------|------|--------|--------|-------|
| mbc_retry*.err/log (10 files) | Build logs | 2.2 KB | TRACKED, unreferenced | Untrack + move to evidence/ | Atomic with .gitignore rule |
| badFaces | Generated | 7 bytes | Untracked, ignored | None | Already safe; note for record |
| numpy-*.whl | Dependency | 15.9 MB | TRACKED at HEAD | Evaluate: untrack OR purge history + untrack | **Trap:** History purge alone reintroduces on next commit |
| h5py-*.whl | Dependency | 5.2 MB | TRACKED at HEAD | Evaluate: untrack OR purge history + untrack | **Trap:** History purge alone reintroduces on next commit |
| uq_batch.err/log | Evidence | 31 KB | TRACKED, referenced | KEEP — do not sweep | Referenced in /docs/HANDOFF-UQ.md |

---

## Related Documents

- `/docs/MOVE_MAP_HISTORY_PURGE.md` — history-purge safety audit; wheels listed as reclaim targets
- `/docs/HANDOFF-UQ.md` — cites `uq_batch.log` as durable evidence
- `/LESSONS.md` — research log; kept at root, fully tracked

