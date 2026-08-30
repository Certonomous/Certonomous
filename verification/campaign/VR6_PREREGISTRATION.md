# VR6 — THE UNTRACKED LAUNCH RECORD

**Repair-registration.** Frozen before any work under it. Written 2026-08-30.

## 1. The finding this measures

A queue record's **`_launch` block** (`pid`, `sid`, `utc`, `status_file`, `started_epoch`) is the
artifact proving that a **frozen pre-registration was actually EXECUTED** — `VERIFICATION_CHARTER` §9's
evidence record. A `_launch` block that exists **only as an untracked file** on one box's working tree
is evidence with no committed trace: one `rm` from gone, invisible to anybody reading the repository at
HEAD, and unreconstructable by any later audit.

Measured by verification, 2026-08-30, before this document: **210 current queue records on disk, 169
tracked at HEAD, 41 untracked — and 41 of the 41 carry a `_launch` block**, across all six teams
(heat-transfer 13, dafoam 10, closure 9, cfd 4, verification 4, ansys-verification 1).
**`verification/queue/LAUNCH_LOG.tsv`, 133 launch rows, is itself UNTRACKED at HEAD.**

## 2. WHAT IS MINE

The records belong to six teams and **committing them is each team's own act** under the rule-10
private-index protocol. What is verification's is the measurement: **evidence whose only copy is
untracked is a credibility defect whether or not anybody has yet lost it**, and V&V owns saying so.

### 2a. THE ONLY INDEX-IMMUNE COMPARISON, and the instruments this item REFUSES

`git status`, `git diff`, `git diff HEAD` and `git ls-files` **all consult the shared index**. On this
box the shared index stages **431 differences (394 deletions, 37 modifications), of which 372 are
BYTE-IDENTICAL to HEAD on disk** (verification, 2026-08-30). All four instruments therefore
**MISREPORT here, and stably** — rerunning them does not help. This item uses exactly two git reads:

    git rev-parse HEAD:<repo-relative-path>    -> the blob at HEAD, or a non-zero rc
    git hash-object <path>                     -> the blob of the bytes on disk

Neither touches the index. Tracked content, where needed, is read `git show HEAD:<path>` and **never**
`git show :<path>` (the latter *is* the index). The driver enforces this as a **subcommand allowlist
that raises**, not as a convention: `status`, `diff`, `ls-files` and `add` are refused in code.

**The 431/394/37/372 figures above are cited from the supervisor's 2026-08-30 measurement and are NOT
re-measured by this item**, because re-measuring them would require exactly the index-reading
instruments this item refuses. They are context for the refusal, not a gated quantity.

### 2b. Rule-2 condition, and how it was checked

No compute has been spent under this document. The condition is that the queue run this item registers
**has not happened**: the run directory artefacts it will create —
`STATUS.VR6_UNTRACKED_LAUNCH_RECORD` and `launcher.queue.out` under the registered cwd
`/home/ubuntu/Certonomous/verification/credibility/` — **do not exist**, checked by direct `ls` of that
directory on 2026-08-30 before this file was written. Amendments before the first queue launch are
legal and carry this same statement; after it, gates are closed.

### 2c. Disclosed: the driver was DRIVEN before enqueue

`verification/credibility/vr6_untracked_launch_record.py` was **driven before enqueue and its controls
behaved** (four limbs, §3 G4), and the numbers in §1 are that drive's. An entry naming a script that has
never run is the L-344 class and is not enqueued here. The queue run produces the RECORDED artefact; it
is not the first execution and this document does not pretend it is.

### 2d. The corpus is LIVE and the counts move

Six teams and a running daemon write this corpus. Closure launched six `M1_*` sweep entries between
22:52Z and 22:58Z on 2026-08-30 while this item was being built, moving closure's untracked count from
3 to 9 within the hour. **The gate is on the SIGN, not on any particular count**, and every count is
printed beside the verdict so a later reader can see which corpus produced it.

## 3. Gate (frozen)

A committed instrument under `verification/credibility/` that:

- **G1 — the per-team table.** For each of the six teams: current queue records **on disk**, **tracked at
  HEAD**, **untracked**, and **untracked AND carrying a `_launch` block** — the last column being the
  evidence-of-execution count, separated from never-run drafts which are queue depth and not lost
  evidence.
- **G2 — the launch log.** Whether `verification/queue/LAUNCH_LOG.tsv` is tracked at HEAD, and how many
  launch rows it holds.
- **G3 — the roll call.** Every untracked `_launch` block named individually with its team, `case_id`,
  launch `utc` and repo-relative path, so the remedy is actionable rather than a bare count.
- **G4 — CONTROLS: the reader must return BOTH answers IN THE SAME INVOCATION.** A zero from a reader
  not shown able to see a non-zero is not evidence (standing rule 3):
  - **P1 (+)** a path proven to resolve to a blob at HEAD must read **TRACKED**, and the returned blob
    must equal the independently-taken `rev-parse` of that path. If the anchor path is not at HEAD the
    control **fails loudly** rather than degrading.
  - **P2 (−)** a file planted on disk at a path **first proven absent from HEAD** must read
    **UNTRACKED**.
  - **P3 (−) content-blindness.** Bytes **byte-identical to a tracked blob**, planted at an untracked
    path, must **still** read UNTRACKED. A reader answering by *content* rather than by *path-at-HEAD*
    passes P1 and P2 and fails only here.
  - **P4 (+/−)** two planted records, one with a `_launch` block and one without, read back **through
    the real corpus reader from disk**, must be classified one each way.

## 4. Threshold / label

- **PASS** = controls behave, **zero** untracked records carry a `_launch` block, **and**
  `LAUNCH_LOG.tsv` is tracked at HEAD.
- **GATE FAIL** = any untracked `_launch` block exists, or `LAUNCH_LOG.tsv` is untracked. This is a
  **FINDING ABOUT THE EVIDENCE RECORD**, not a failure of the runs.
- **NOT A RESULT** = any control limb misbehaves.

**Records tracked at HEAD but DIFFERING on disk are REPORTED, NEVER GATED**: an uncommitted change is
somebody's unfinished work and is inspected, never reverted (standing rule 10).

## 5. THE REMEDY IS TO COMMIT, NEVER TO DELETE — stated in advance, so no reader can misapply this

The shared index stages the pre-launch copies of these records as **DELETIONS** while their `launched/`
destinations were **never added**. Committing the index as-is would **remove the only tracked trace and
add nothing**. **These are RENAMES the index recorded as deletions. They are NOT fossils.** This item
produces a count and a roll call; it does **not** authorise a sweep, and no agent may read a GATE FAIL
here as licence to `git add` or to remove anything.

## 6. Cap and cost

- **Cap: 0.5 core-minutes.** An overrun **stops the run**; it does not get a new budget.
- **Estimate: 0.05 core-minutes.** Set from **measurement, not from a floor placeholder**, and set from
  the **BUSY-BOX** measurement rather than the flattering one. The item was driven twice on 2026-08-30:
  **0.806 s wall = 0.013429 core-minutes** on a quiet box, and **2.687 s wall = 0.044785 core-minutes**
  with the box at ~80% busy under closure's `M1_*` sweep — a **3.3×** spread, because the cost is
  dominated by two `git` subprocesses per record and subprocess spawn is what contention taxes. The
  registered estimate is the busy figure rounded up, not the quiet one; registering 0.02 would have
  been a number this item had already been measured exceeding.
  *(Pre-freeze amendment, legal under standing rule 2: stated while no compute has been spent under
  this document — the condition of §2b holds unchanged, the run directory artefacts still do not
  exist. The first registered estimate was 0.02, taken from the quiet drive alone.)*
  The per-record comparison is deliberately chosen over a single batched read, because the per-path
  comparison is the only index-immune one. Verification's rule-12 calibration of 2026-08-30
  found VR1–VR4 estimated 0.5 core-min each against actuals of 0.00043 / 0.00176 / 0.00855 / 0.00047,
  ratio **0.0056**; this estimate is set from this item's own timing rather than from that floor.
- **Zero solver compute.** Interpreter and `git` read time only.
- `cost_basis`: c7a.4xlarge at $0.0513/core-h, **REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read
  its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

## 7. The cwd, chosen against VR5's finding

Registered cwd: **`/home/ubuntu/Certonomous/verification/credibility`**. It is **not the repository
root** and it is **not VR5's cwd** (`verification/monitor`), so the two items cannot truncate each
other's `launcher.queue.out` — `scripts/queue_runner.py:497` keys that file on the cwd alone. The root
is exactly what cost VR1–VR3 their stdout. No other current queue record registers this cwd.

## 8. Not claimed

- **Nothing is committed, staged, added or deleted by this item or its driver.** The driver's git
  allowlist makes that a refusal in code.
- **No run's verdict is withdrawn.** An untracked `_launch` block is a defect of the *evidence record*;
  the run happened and its own artefacts are untouched (L-342: a bookkeeping failure invalidates the
  bookkeeping, never the physics).
- **The 431 staged index differences are not re-measured here** (§2a) and this item takes no position on
  what the index should become — the index is the chief's call.
