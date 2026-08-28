# Commit helper — RENAME MODE

**Status: SPEC, FROZEN AT ITS COMMIT. No code exists yet.** This document is written
**before** the implementation precisely so the implementation cannot be shaped to pass its
own test (`CLAUDE.md` rule 2's discipline applied to tooling). The commit that lands this
file is the freeze; the code that follows cites that sha, and any departure from what is
written here is a dated amendment at the foot, never an edit above it (rule 6).

**Owner:** cfd-supervisor. **Provenance:** the fossil mechanism was put to cfd by the chief
on 2026-08-28 from the board's fossil count, with the rename precedent `ee4c331c` cited
beside it; cfd accepted building a rename mode **spec first**, on the
`QUEUE_ENTRY_TEAM_BINDING.md` pattern. Every git behaviour asserted below was **measured in
throwaway repositories by cfd lane SPEC** on 2026-08-28, using **real blobs from this
repository's own history**, not recalled; the measurements are printed inline beside the
claims they support. Two statements in the framing were falsified on that check and are
corrected in §2a.

**This document adds no gate, no threshold, no cap and no label.** It specifies a **new
mode of a commit helper**. It changes no verdict, re-opens no run and back-fills nothing
(§8).

> **REFERRAL 1, NOT A DECISION — for the verification team, via the cfd-supervisor.**
> `docs/standards/COMMIT_INTEGRITY_STANDARD.md` **Clause 2** requires a numeric assertion
> that **`deletions == 0`** before `commit-tree` and again after `update-ref`. **A rename
> is a deletion.** Measured on the real production pair (§4.2): without `-M` the diff reads
> **`2 files changed, 46 insertions(+), 37 deletions(-)`**; with `-M` it still reads
> **`1 file changed, 10 insertions(+), 1 deletion(-)`**. **Clause 2, read literally,
> refuses every rename this mode exists to make.** §4.4 proposes the narrow reading that
> reconciles them — deletions counted at **PATH level**, not line level, with the deleted
> path set required to equal the declared old paths exactly. That standard is **owned by
> the verification team**, and its own scope paragraph says a clause-level conflict is *"a
> referral to the verification team and not a judgement call inside the tooling."*
> **This is written; the code does not land until that is ruled.**

> **REFERRAL 2, NOT A DECISION — for the chief.** The existing helper lives in the
> **closure team's** tree (`cases/RANS_LES_closure_models/_common/commit_private.sh`) while
> the fossils are lab-wide. §6 recommends a **new, separate, cfd-owned script** rather than
> a flag on closure's file, and §7 states that **any relocation or consolidation of
> closure's helper is a CROSS-TEAM decision for the supervisor to escalate, not something a
> lane does.** No line of closure's file is edited by this spec.

---

## 1. What `commit_private.sh` does TODAY, by line

Read in full, 29 lines, `cases/RANS_LES_closure_models/_common/commit_private.sh`:

| lines | what it does |
|---|---|
| `:6` | `set -euo pipefail` |
| `:7` | `cd /home/ubuntu/Certonomous` |
| `:8` | `MSG="$1"; shift` — the message is a **file path** |
| `:9-10` | exports `GIT_INDEX_FILE=/home/ubuntu/closure-data/supervisor/private.index` and `rm -f`s it |
| `:11` | `OLD=$(git rev-parse HEAD)` — the HEAD capture |
| `:12` | `git read-tree HEAD` — **re-resolves HEAD; does not use `$OLD`** (see D1) |
| `:13-18` | builds `FILES[]` from the arguments; a **directory** argument is expanded by `find … ! -name '*.pdf' ! -name '*.txt' ! -name '*.npy' ! -name '*.npz' ! -name '*.h5' ! -name '*.pt' ! -name '*.pkl' ! -path '*/__pycache__/*' | sort` |
| `:19` | refuses, exit 2, if a **directly named** file is `*.pdf` or `docs/papers/*.txt` |
| `:20` | `git update-index --add -- "${FILES[@]}"` — **the only index operation in the file** |
| `:21` | `TREE=$(git write-tree)` |
| `:22-23` | **prints** `git diff-tree -r --name-status "$OLD^{tree}" "$TREE"` |
| `:24-25` | computes `N=$(git diff-tree -r --name-only … | wc -l)` and **prints** `"$N paths changed; ${#FILES[@]} requested"` |
| `:26` | `NEW=$(git commit-tree "$TREE" -p "$OLD" -F "$MSG")` |
| `:27` | `git update-ref refs/heads/main "$NEW" "$OLD"` — **both arguments quoted** |
| `:28` | prints `COMMITTED <short new> (parent <short old>)` |
| `:29` | `rm -f "$GIT_INDEX_FILE"` |

### 1a. What reading it found — six defects, reported, NOT repaired by this spec

These are recorded because the new mode must not inherit them and because closure is
entitled to know. **This spec repairs none of them: the file is another team's, and cfd
does not edit it.** They are relayed to the cfd-supervisor for onward relay.

- **D1 — HEAD IS CAPTURED TWICE.** `:11` captures `$OLD`; `:12` then runs `git read-tree
  HEAD`, which **re-resolves HEAD independently**. `CLAUDE.md` rule 10 requires HEAD
  captured **once** for `read-tree`, the assertion and `-p`. A peer landing a commit between
  the two resolutions yields a tree read from one commit and a `-p` parent naming another —
  L-223's exact failure. The **one-shell-invocation** half of L-223 is satisfied; the
  **single-capture** half is not. Repair is one character class: `git read-tree "$OLD"`.
- **D2 — THE ASSERTION IS PRINTED, NOT ENFORCED, AND THE FILE SAYS OTHERWISE.** `:4`
  states *"Asserts the diff-tree contains only the given paths."* `:22-25` **display** a
  name-status listing and a count. **`$N` is never compared to `${#FILES[@]}`. There is no
  `if`, no `test`, no exit.** A foreign path in the tree is printed and committed. This is
  the instrument's own headline claim, and it is a display. *(Same family as the
  "evidence annotated as non-binding" class: a printed discrepancy that gates nothing.)*
- **D3 — THERE IS NO POST-COMMIT VERIFY.** `CLAUDE.md` rule 10 calls `git diff HEAD~1 HEAD
  --stat` after the commit **"not optional"** (`c46309f5` lost nine files). `:28` prints two
  shas and stops. *(And the rule's literal form is itself superseded for tooling by
  `COMMIT_INTEGRITY_STANDARD.md` **G2**, which refuses `HEAD~1` outright and requires
  anchoring on `git rev-parse "$C^"` — see §4.5.)*
- **D4 — L-382 IS HALF-COVERED, BY LUCK OF QUOTING.** `COMMIT_INTEGRITY_STANDARD.md`
  Clause 4 requires **both** a `^[0-9a-f]{40}$` assertion on the new sha **and** quoted
  `update-ref` arguments, noting either alone suffices. `:27` **has the quoting**; there is
  **no sha assertion**. So the specific L-382 collapse (an empty `$C` making `update-ref` a
  silent two-argument no-op that prints `CAS OK`) is blocked here — by the quoting, not by
  a check. Under `set -e` a failing `commit-tree` in `NEW=$(…)` also aborts the script.
  The residual is that **nothing in the file says why it is safe**, so a future edit that
  drops the quotes reintroduces L-382 silently.
- **D5 — THE PRIVATE INDEX IS ONE FIXED PATH SHARED BY EVERY CALLER.** `:9` hardcodes
  `/home/ubuntu/closure-data/supervisor/private.index`. Two concurrent invocations `rm -f`
  and `read-tree` the same file; the fleet runs many lanes at once and nothing in the file
  is closure-only at the shell level. *(Same shape as the shared-scratchpad collision: one
  fixed path, many writers, generic name.)*
- **D6 — DIRECTORY EXPANSION SILENTLY DROPS FILE TYPES THAT A DIRECT NAME REFUSES
  LOUDLY.** `:19` **refuses with exit 2** for a directly named `*.pdf`. `:16` **silently
  omits** every `*.pdf`, `*.txt`, `*.npy`, `*.npz`, `*.h5`, `*.pt`, `*.pkl` found under a
  directory argument — so a `RECORD.txt` or `NOT_FILED.txt` inside a named directory is
  never committed and **nothing is printed about it**. The same file is a loud refusal or a
  quiet omission depending on how it was named.
- **D7 — the helper can only ADD.** `:20` is the only index operation. **There is no
  `--remove` and no `--force-remove` anywhere in the file.** A deletion or a move cannot be
  expressed. This is not a defect of implementation; it is the whole subject of §2.

## 2. The defect — a MOVE committed as an ADD strands the old path

`scripts/queue_runner.py` moves a launched entry out of the drop path. **The move is not in
a function called `move_launched`** (§2a): it is inline in `launch()`, at

- `:515` `launched_dir = path.parent / "launched"`
- `:517` `dst = launched_dir / path.name`
- `:520` `shutil.move(str(path), str(dst))`
- `:536` `dst.write_text(json.dumps(meta, indent=2) + "\n")` — **the moved file is then
  OVERWRITTEN** with `meta = dict(entry)` plus `_launch` (`:522`) and `_field_classes`
  (`:526-535`).

The runner is a daemon and commits nothing. The commit is made **later, by an agent**, from
a worktree in which the old file is already gone and the new file already exists. With
`git update-index --add -- <newpath>` and nothing else, git records an **addition** at the
new path and **leaves the old path tracked at HEAD**. The old path becomes a **fossil**: a
blob the tree still claims to have, at a location nothing on disk occupies.

### 2a. TWO STATEMENTS IN THE FRAMING THAT WERE FALSIFIED ON CHECK

1. **There is no `move_launched` function** in `scripts/queue_runner.py`. `grep -n "def
   move_" ` on that one file returns `move_refused` (`:444`) and nothing else. The launched
   move is the four inline lines above. A spec that told an implementer to "see
   `move_launched`" would send them looking for code that does not exist.

2. **`ee4c331c`'s `R100` DOES NOT GENERALISE TO THE QUEUE→LAUNCHED MOVE, and this is the
   single most important measurement in this document.** `ee4c331c` is verified `R100`,
   `0/0`:

   ```
   R100  verification/queue/heat-transfer/held/W1c_c.json  verification/queue/heat-transfer/W1c_c.json
   ```

   — but that is a **`held/` → drop-path** move, in which **the content does not change**.
   The **drop-path → `launched/`** move **does** change content, because `queue_runner.py:536`
   rewrites the file with `_launch` and `_field_classes`. Measured on the real pair
   `verification/queue/closure/G1_grid_triple.json` → `…/launched/G1_grid_triple.json`,
   reconstructed from this repository's own HEAD blobs (2557 B → 2883 B):

   | detection setting | result |
   |---|---|
   | `-M` (git's default, 50 %) | **`R088`** — detected |
   | `-M50%` | **`R088`** — detected |
   | **`-M90%`** | **`D` + `A`** — **NOT detected** |
   | **`-M100%`** | **`D` + `A`** — **NOT detected** |

   **A rename mode that required `R100`, or any floor above 88 %, would be unable to commit
   the very move it was built for.** §4.3 fixes the default floor at git's own 50 % for
   this reason, and §9 control R1 drives the 88 % case so the floor is exercised by
   production's shape rather than by a synthetic identical-content pair — G1 of
   `COMMIT_INTEGRITY_STANDARD.md`.

### 2b. The fossil count — MEASURED HERE, and it does not equal the board's 19

Measured 2026-08-28 by cfd lane SPEC from `git ls-files 'verification/queue/*'` at HEAD,
cross-checked against the disk. Stated with its definition, because the framing's figure
of **19** carries a definition this lane does not have and **is not contradicted here**:

| reading | value |
|---|---|
| files tracked at HEAD under `verification/queue/` | **65** |
| tracked drop-path `<team>/<case>.json` | **34** |
| of those, **absent from disk** | **34 of 34** |
| tracked `<team>/launched/*.json` | **18** |
| pairs where the **same name** is tracked at HEAD under **both** the drop path and `launched/` | **1** — `closure/G1_grid_triple.json` |
| `<team>/refused/` files tracked | **0** |

**Every one of the 34 tracked drop-path entries is a fossil in the sense that matters**: the
tree claims a file the disk does not have. Whether the board's 19 counts a narrower set —
committed launched records whose drop-path sibling is also committed, or the fossils
attributable to a particular window — cannot be determined from here. **The mechanism is
identical either way and the spec does not depend on the count.** The count is reported so
the supervisor can reconcile the two definitions; **RE-MEASUREMENT IS MANDATORY** at
implementation time, in the same shell invocation that lands the code.

## 3. How a rename is expressed in a private index

**A rename is not a git operation.** Git stores trees of paths and blobs; it has no rename
record. `git mv` is a worktree move plus an index update. What `--find-renames` does is
**detect, at diff time, that a deletion and an addition are probably the same file** and
render them as one `R` entry. Nothing about a rename is stored; it is inferred every time
it is displayed.

So the mechanism is exactly two index operations, **in one private index, in one shell
invocation, under one HEAD capture**:

```bash
export GIT_INDEX_FILE="$IDX" && rm -f "$GIT_INDEX_FILE"
H=$(git rev-parse HEAD)
git read-tree "$H"                                  # "$H", never bare HEAD -- D1
git update-index --add          -- "$NEWPATH"       # the addition
git update-index --force-remove -- "$OLDPATH"       # the deletion
T=$(git write-tree)
```

**`--force-remove`, never `--remove`, and the reason is measured, not stylistic.**
In a throwaway repository, with one tracked file `f.txt`:

| worktree state | flag | entry after `write-tree` |
|---|---|---|
| file **present** | `--remove` | **`f.txt` SURVIVES** — the command exits **0** and does nothing |
| file **present** | `--force-remove` | removed |
| file **absent** | `--remove` | removed |

`--remove` is a **conditional** removal whose condition is worktree state, and **it succeeds
silently when it does nothing** — the L-382 shape, a success signal on a no-op. In the queue
case the old file is genuinely absent, so `--remove` would happen to work; it would break
the moment the mode were used for a copy-then-delete, a re-armed entry, or any caller who
had restored the old file. **`--force-remove` is unconditional and therefore deterministic
regardless of worktree state**, and determinism is the property being bought.

**Order within the index does not matter** (the index is a map, not a log), but the two
calls must be in the **same** `GIT_INDEX_FILE` and the **same shell invocation** — shell
environment does not persist between an agent's Bash calls, and a protocol split across two
calls runs its second half against the **shared** index (`COMMIT_INTEGRITY_STANDARD.md`
Clause 1).

**How the resulting tree is asserted: §4.** The tree is asserted **before** `commit-tree`,
from `"$H^{tree}"` against `"$T"` — tree-to-tree, the form the existing helper already uses
at `:23`, and the form every measurement in §4 was taken in.

## 4. THE ASSERTION — this is the whole point of the mode

Today's helper asserts (or rather, displays — D2) that the diff touches only the caller's
paths. **That test cannot distinguish a rename from a bare addition, which is precisely the
defect.** Rename mode adds three assertions and one refusal, all measured.

### 4.1 A1 — THE DIFF IS A RENAME, NOT AN ADDITION

**Literal command, tree-to-tree, exactly as measured:**

```bash
git diff-tree -M50% -r --name-status "$H^{tree}" "$T"
```

**Required output shape: one line per declared pair, and no other line**, each of the form

```
R<score>\t<oldpath>\t<newpath>
```

where `<score>` is **three digits**, zero-padded — `R088` and `R100` were both observed —
and `<oldpath>`, `<newpath>` are **byte-equal to the pair the caller declared**. The
declared-pair equality is not decoration: `-M` pairs a deletion with whichever addition it
finds most similar, and queue entries are structurally near-identical JSON. **An `R` line
alone proves a rename happened; it does not prove it is YOUR rename.**

*Measured, one sample, and reported as one sample:* deleting the real
`verification/queue/cfd/F25_DUCT3D.json` (6535 B) while adding the real
`verification/queue/cfd/launched/F24_PRANDTL_MEYER.json` (5685 B) — two unrelated entries of
the same schema — produced **`D` + `A` and no `R` line at 50 %**. So false pairing is not
routine at this floor. **That measurement is why the exact-pair assertion is required
anyway**: one negative sample is not a proof about all pairs, and the assertion makes the
guard independent of the question.

**`--stat` MUST NOT be used for this assertion.** With `-M`, `git diff-tree -M -r --stat`
renders the rename as

```
 q/closure/{ => launched}/G1_grid_triple.json | 11 ++++++++++-
```

— a **brace-elided** path in which **neither the literal old path nor the literal new path
appears as a contiguous string**. Any check that greps a `--stat` line for a declared path
fails on every rename it is shown. Recorded because `--stat` is what rule 10's own example
line uses.

### 4.2 A2 — THE ZERO-DELETION ASSERTION, AT PATH LEVEL

**The rename must delete the old path and nothing else.** Literal command:

```bash
git diff-tree -M50% -r --name-only --diff-filter=D "$H^{tree}" "$T"
```

**Required output: EMPTY.** Not "one line"; **empty**. Under `-M` a detected rename's source
half is consumed into the `R` entry and is **not** reported as `D` — measured: the command
prints nothing for the real G1 pair, and prints `q/closure/G1_grid_triple.json` when `-M` is
omitted. **So a surviving `D` line means exactly one thing: a path left the tree that is not
the source half of a declared rename.** That is the condition to refuse on, and it is
detected by the same mechanism that detects the rename, which is what makes the pair of
assertions cheap and hard to fool.

A second, independent limb, because A1 and A2 both read the same `diff-tree` and a broken
`-M` would satisfy both vacuously — **the path-set assertion, computed from `ls-tree`, not
from any diff:**

```bash
git ls-tree -r "$H"  --name-only | sort > before.txt
git ls-tree -r "$T"  --name-only | sort > after.txt
comm -3 before.txt after.txt          # symmetric difference
```

**Required: the symmetric difference is exactly `{<oldpath>, <newpath>}`** — the old path
present only in `before`, the new path present only in `after`, and **nothing else on either
side**. This is the **zero-net-file-loss** statement in its strongest form: `|after| ==
|before|` and the two differ by one swap. It is computed from the trees themselves and does
not depend on rename detection at all.

### 4.3 A3 — THE SIMILARITY FLOOR: a rewrite is DECLARED, never disguised

Detection is **always run at `-M50%`** — git's own default floor — and the score is
**parsed out of the `R<score>` field** and compared **in the script** against the caller's
floor. It is *not* enforced by passing a higher `-M` to git, and this matters: at `-M90%`
the real pair degrades to `D` + `A`, which A2 would refuse with the message *"a path left
the tree"* — **true, and completely misleading about the cause.** Parsing the score lets the
refusal say what actually happened and print the number.

- **Default floor: 50** — git's own, and the value under which the production move
  measures **88**. A floor above 88 cannot commit the move the mode exists for (§2a item 2).
- **`--min-similarity <N>`**, 1–100, raises it. The value in force is **printed on every
  run**, passing or failing, so a reader never has to infer which floor applied.
- **Below the floor → REFUSE (exit 4), printing the measured index**, e.g.
  `RENAME-SIMILARITY: <old> -> <new> scored 41 %, below the floor of 50 %. This is a
  REWRITE, not a rename. Commit it as a deletion and an addition, and say so in the
  message.` **A rewrite disguised as a rename is worse than a rewrite**: the reader of
  `git log --follow` is told the content is continuous when it is not.
- **`R100` is NEVER required and never assumed.** `ee4c331c` is `R100` because a `held/` →
  drop-path move changes no bytes; the launched move changes bytes at
  `queue_runner.py:536`. Two different moves, two different scores, one mode.

### 4.4 THE CLAUSE-2 RECONCILIATION — proposed, REFERRED, not taken

`COMMIT_INTEGRITY_STANDARD.md` Clause 2 requires **`deletions == 0`** asserted numerically
before `commit-tree` and again after `update-ref`. Measured on the production pair, the
figures that clause would read are:

| what is counted | without `-M` | with `-M` |
|---|---|---|
| files changed | 2 | 1 |
| insertions | 46 | 10 |
| **deletions** | **37** | **1** |

**Both are non-zero. Clause 2 read literally refuses every rename.** The proposed
reconciliation, which is a **referral and not a ruling**:

> **Clause 2's `deletions == 0` is a statement about PATHS LEAVING THE TREE, not about
> lines. For rename mode it is satisfied by A2: the set of paths deleted from the tree
> equals exactly the set of declared old paths, and the `--diff-filter=D` listing under
> `-M50%` is EMPTY.** Line-level deletions inside a detected rename are content churn
> already bounded by the similarity floor of A3, and are reported (the score is printed)
> rather than gated.

The reasoning is that Clause 2's stated hazard is **plausibility** — *"`+3/−2` and `+1/−1`
read as an ordinary edit, and a human reviewing a stat line passes them"* — and a numeric
assertion is what cannot be persuaded. **A2 keeps that property exactly**: it is a numeric
(empty-set) assertion, computed twice, that a human cannot argue with. What changes is the
**unit of the count**, from lines to paths, in the one mode where a path deletion is the
declared purpose. **The verification team owns that standard and this is theirs to rule.**

### 4.5 A4 — THE POST-COMMIT VERIFY, ANCHORED ON THE PARENT

`CLAUDE.md` rule 10 requires the post-commit verify and calls it not optional.
`COMMIT_INTEGRITY_STANDARD.md` **G2 refuses `HEAD~1` outright** — five peer commits landed
underneath a lane and `HEAD~1` was already the amended blob, so the lane *"compared a file
with itself and got a confident, meaningless match"* — and requires anchoring on the
commit's **true parent**. Rename mode therefore verifies:

```bash
git rev-parse "$C^"                    # must equal "$H"
git diff-tree -M50% -r --name-status "$C^" "$C"     # must reproduce A1's lines exactly
git diff-tree -M50% -r --name-only --diff-filter=D "$C^" "$C"   # must be EMPTY
```

and, per L-382 / Clause 4, **before** `update-ref`:

```bash
[[ "$C" =~ ^[0-9a-f]{40}$ ]] || { echo "COMMIT-SHA: refused"; exit 10; }
git update-ref refs/heads/main "$C" "$H"            # BOTH arguments quoted
[[ "$(git rev-parse HEAD)" != "$H" ]] || { echo "HEAD-DID-NOT-MOVE: refused"; exit 10; }
```

**`$C` is quoted at `update-ref` AND regex-asserted before it.** Clause 4 says either fix
alone suffices; this mode takes both, because the quoting is free and the assertion is what
says why. The message is passed by **STDIN**, not `-F <path>` (Clause 4), which removes the
missing-message-file path that produced the empty sha in the first place.

**The CAS proves the PARENT is current and NOTHING about the tree.** A stale `read-tree`
passes CAS and loses files (`c46309f5`). A4's re-run of A1 and A2 **against the landed
commit** is what catches it, and it is not optional.

## 5. THE REFUSAL CONDITIONS — each with its exit code

Every one is a `test`/`[[ ]]` followed by `exit`, never an `echo`. **D2 is the defect this
list exists not to repeat: a printed discrepancy is not a refusal.** Exit codes are distinct
so a caller can branch on the cause.

| exit | condition | probe | message must name |
|---|---|---|---|
| **1** | usage error — no pair given, odd argument count, `--min-similarity` out of 1–100 | argument parse | the usage line |
| **2** | **the old path is NOT tracked at HEAD** | `git cat-file -e "$H:$OLDPATH"` returns non-zero | the old path and `$H`. *There is nothing to rename; this is an addition wearing a rename's name* |
| **3** | **the new path IS ALREADY tracked at HEAD** | `git cat-file -e "$H:$NEWPATH"` returns **zero** | both paths. *The destination is occupied; a "rename" onto it silently replaces a tracked blob* |
| **4** | **similarity below the floor** | `R<score>` parsed from A1, `score < floor`; **or no `R` line at all while both A1's paths appear as `D` and `A`** | the measured score, the floor, and the words `REWRITE, not a rename` |
| **5** | **more than one pair without explicit opt-in** | `pairs > 1 && ! --multi` | the count and the flag. *A multi-pair rename is legitimate — `ee4c331c` moved three — but it must be asked for, because a script that silently accepts N pairs accepts a typo'd N+1th* |
| **6** | **a path lies outside the caller's team directory** | each of `$OLDPATH`, `$NEWPATH` must be prefixed by the `--team-dir` the caller declares, which must itself be one of the team territories | the offending path and the declared team directory. `--team-dir` is **REQUIRED and never defaulted** — the `QUEUE_ENTRY_TEAM_BINDING.md` §5 P2 discipline: a caller that cannot say whose tree this is fails loudly, not silently |
| **7** | **a path in the diff was not declared** | A1's line set contains any path outside the declared pairs | the foreign path. *This is D2 made binding* |
| **8** | **a bare `D` line survives `-M50%`** | A2's `--diff-filter=D` listing is non-empty | every surviving deleted path |
| **9** | **the `R` line's fields do not equal the declared pair** | byte comparison of both fields | what was declared and what git paired |
| **10** | **sha regex fails, or HEAD did not move after `update-ref`** | §4.5 | the sha as captured (or its emptiness) |
| **11** | **the path-set symmetric difference is not exactly `{old, new}`** | A2's `comm -3` limb | every extra path on either side |
| **12** | **`GIT_INDEX_FILE` is unset, or resolves to the repository's `.git/index`** | checked **first**, before any git call | the resolved path. *Rule 10: never touch the shared index — and a guard that runs after the first `update-index` is a post-mortem* |
| **0** | committed, all of A1–A4 satisfied | — | the new sha, the parent, the pair, and the **measured similarity score** |

**No refusal creates a commit.** Every probe above runs **before** `commit-tree` except
those in §4.5, which run before or after `update-ref` and whose failure leaves the branch
unmoved (exit 10) or reports a landed commit that must be inspected, never reverted
(`CLAUDE.md` rule 10: *an unexpected change is inspected, never reverted*).

## 6. A NEW FLAG, OR A SEPARATE SCRIPT? — RECOMMENDED: a separate, cfd-owned script

**Recommendation: a new script, `scripts/commit_rename_private.sh`** — `lower_snake.sh`
under `scripts/`, per `FILING_CHARTER.md` R3. **Not a flag on
`cases/RANS_LES_closure_models/_common/commit_private.sh`.**

**The case FOR a flag on the existing helper**, stated fairly because it is the more
obvious answer: one implementation of the private-index protocol means one place to fix D1
through D5, no divergence between two copies, and callers already know the file.

**The case for a separate script, which prevails, in four parts.**

1. **The existing helper is in ANOTHER TEAM'S TREE.** `cases/RANS_LES_closure_models/` is
   closure's territory. Adding a mode to it is a cfd lane editing closure's file — the thing
   the territory rules exist to prevent. §7.
2. **It is closure-specific in its body, not merely its location.** `:9` hardcodes
   `/home/ubuntu/closure-data/supervisor/private.index`; `:16` and `:19` encode closure's
   paper workflow (`*.pdf`, `docs/papers/*.txt`) and a research-data exclusion list
   (`*.npy`, `*.h5`, `*.pt`). A lab-wide queue-move tool inherits none of that and would
   have to carry it dead.
3. **The two modes have INCOMPATIBLE assertion regimes.** Add mode's correct assertion is
   *zero deletions*; rename mode's is *exactly these deletions*. Bolting the second onto a
   script whose first is **not implemented at all** (D2) risks the new flag inheriting the
   broken path — and worse, a `--rename` flag on a script that never enforced its
   single-path claim would be the **first** enforcing mode in the file, which reads as
   though the others enforce too.
4. **Blast radius.** A new file cannot regress any existing caller. A new flag on a helper
   whose `set -e` behaviour, argument parsing and array expansion are load-bearing for
   closure's commits can.

**The real cost of the recommendation, named rather than waved past: two implementations of
one protocol diverge.** The mitigation is stated as a follow-up and not taken here:
**closure's helper should eventually delegate its protocol core to the shared one** — which
is the consolidation question of §7, and is not a lane's to decide.

## 7. RELOCATION IS A CROSS-TEAM DECISION — FLAGGED, NOT TAKEN

The helper sits at `cases/RANS_LES_closure_models/_common/commit_private.sh` — closure's
tree — and is cited by `CLAUDE.md` rule 10's provenance line as the lab's reference
implementation of the private-index protocol. **The fossils are lab-wide.**

**This spec does NOT require relocating it, and deliberately so**: §6's recommendation makes
relocation unnecessary for the rename mode to exist. But the underlying question — *should
the lab's reference private-index implementation live in one team's case tree?* — is real,
is raised here, and is **explicitly escalated**:

> **CROSS-TEAM DECISION, for the cfd-supervisor to escalate, not for this lane.** Moving or
> consolidating `commit_private.sh` touches closure's tree, changes a path cited in
> `CLAUDE.md`, and affects every team that uses the protocol. `ESCALATION_CHARTER.md` §9.6
> governs; `FILING_CHARTER.md` §4 requires **coupling measured before anything moves** (a
> webroot move once broke 178 code files and git rename detection was useless at that
> coupling). **A lane does not move another team's file, and does not measure its coupling
> on the way past.**

The six defects in §1a are likewise **relayed, not repaired**. They are closure's file.

## 8. OUT OF SCOPE — the existing fossils are NOT back-filled

**Stated explicitly, at the supervisor's instruction and on the chief's board's own rule:
launched records are never back-filled.** This spec governs **FUTURE moves only.**

- The **34** tracked-but-absent drop-path entries measured in §2b are **left exactly as they
  are.** Nothing here retro-commits a deletion, rewrites a history, or re-renders a past
  addition as a rename.
- No `git filter-branch`, no rebase, no history rewrite of any kind is proposed, permitted
  or implied. The branch is append-only.
- Retiring a fossil would mean committing a deletion of a path whose launched sibling was
  landed by another team under another pre-registration. **That is not a tooling change and
  it is not cfd's to make.**
- The correct reading of the existing fossils is **a record of how moves were committed
  before this mode existed** — which is exactly what a fossil is for.

## 9. Controls — planted, with mutations that must flip

Per `CLAUDE.md` rule 3 and `COMMIT_INTEGRITY_STANDARD.md` **G1** (*make the test exercise
what production does*), **R1 uses the real production pair's shape — content that changes
across the move, scoring 88 % — never an identical-content pair.** An identical-content
control would pass at `R100` and prove nothing about the case the mode exists for. Every
control runs in a **throwaway repository created by `mktemp -d`**; nothing real is touched,
and `.git/index` of this repository is asserted unchanged (R12).

| # | control | plant | required outcome — the exact assertion |
|---|---|---|---|
| **R1** | **THE POSITIVE: a rename lands, with `R` status and zero net file loss** | old = the HEAD blob of `verification/queue/closure/G1_grid_triple.json` (2557 B); new = the HEAD blob of `…/launched/G1_grid_triple.json` (2883 B), at the launched path | exit **0**; A1 prints **exactly one** line matching `^R0?[5-9][0-9]\t<old>\t<new>$` with score **88**; A2's `--diff-filter=D` listing is **EMPTY**; `comm -3 before after` yields **exactly** `<old>` on the left and `<new>` on the right and nothing else; `wc -l < after == wc -l < before`; and A4 reproduces all three against `"$C^"`/`"$C"` |
| **R2** | **THE NEGATIVE: a same-content ADDITION where the old path was never tracked is REFUSED** | new path added with content byte-identical to a file that exists **only in the worktree**, never committed; old path declared but absent from `$H` | exit **2**; message contains the old path and the words `not tracked at HEAD`; **and `git rev-parse HEAD` is BYTE-EQUAL before and after the run** — no commit object is created, no ref moves |
| **R3** | **MUTATION OF R2** | the `git cat-file -e "$H:$OLDPATH"` probe replaced by `true` | **R2 FLIPS** — the bogus rename commits. Proves R2's refusal comes from the probe and not from some other guard incidentally in the way |
| **R4** | **MUTATION OF R1 — the fossil, reproduced** | the `git update-index --force-remove -- "$OLDPATH"` line **deleted**, everything else unchanged | **R1 FLIPS**: A1 shows `A\t<new>` and **no `R` line** (exit 7 or 9), the old path is **still present in `after.txt`**, and the symmetric difference is `{<new>}` alone. **This is the control that reproduces the exact defect the mode exists to fix** — the fossil is created inside the test, seen, and refused |
| **R5** | **destination already tracked** | both paths committed at `$H`, rename declared | exit **3**, both paths named, HEAD unchanged |
| **R6** | **a REWRITE is refused and DECLARED** | old = `verification/queue/cfd/F25_DUCT3D.json` HEAD blob (6535 B); new = `verification/queue/cfd/launched/F24_PRANDTL_MEYER.json` HEAD blob (5685 B) — two unrelated real entries, **measured to produce `D` + `A` and no `R` at 50 %** | exit **4**; message contains the words `REWRITE, not a rename` and either the measured score or the literal `no rename detected at 50%` |
| **R7** | **the floor is the thing being tested** | R1's pair with `--min-similarity 90` | exit **4** naming **88** and **90** — **not** exit 8. Proves A3 parses the score rather than delegating the floor to `-M`, and that the refusal names the real cause |
| **R8** | **multi-pair without opt-in** | two valid pairs, no `--multi` | exit **5** naming the count |
| **R9** | **multi-pair WITH opt-in** | the three-pair shape of `ee4c331c` (`held/` → drop path, content unchanged) | exit **0**; **three** `R100` lines; `--diff-filter=D` empty; symmetric difference exactly the six paths. Proves the mode handles the `R100` case too, and that R1's 88 % is not the only shape it accepts |
| **R10** | **a path outside the declared team directory** | a valid pair plus `--team-dir verification/queue/cfd` while the pair is under `verification/queue/closure` | exit **6** naming the path and the declared directory |
| **R11** | **the L-382 control, DRIVEN THE WAY PRODUCTION REACHES IT** | the commit message made unavailable **by removing it**, per `COMMIT_INTEGRITY_STANDARD.md`'s controls table — **never** by assigning `C=""` | exit **10**; `refs/heads/main` **unchanged**; and the run does **not** print any success line. Companion positive limb: a real 40-hex sha passes and HEAD is asserted **moved** |
| **R12** | **THE SHARED INDEX IS NEVER TOUCHED** | a full successful run (R1) | `.git/index` of the operating repository has the **same mtime and the same `git hash-object`** before and after; and the run with `GIT_INDEX_FILE` **unset** exits **12** before issuing any `update-index` |
| **R13** | **HEAD IS CAPTURED ONCE — static, and honest about being static** | the script's own source | `grep -c 'rev-parse HEAD'` **== 1**; `grep -c 'read-tree HEAD'` (bare, unquoted) **== 0**; `grep -c 'HEAD~'` **== 0** (G2). *A dynamic control for D1 would require racing a peer commit and is not reliably reproducible; the static check is what can actually be asserted, and it is labelled static rather than dressed as behavioural* |
| **R14** | **the private index cannot collide** | two runs launched concurrently | each resolves `GIT_INDEX_FILE` to a **distinct** path incorporating the caller's pid; both complete; the second's CAS either succeeds against the first's commit or **fails loudly and retries**, never silently overwrites (D5's repair, in the new script only) |
| **R15** | **no `assert`-equivalent silent guard** | the script's own source | every refusal in §5 is a `test`/`[[ ]]` followed by `exit`; `grep -c 'echo.*REFUS' ` lines are each **immediately** followed by an `exit` line. *D2 is a printed refusal that never exits; this control is what makes that impossible to reintroduce* |

**R1 without R4 is not evidence.** R1 alone passes if `-M` happens to pair the files for
some other reason; R4 is what shows the `--force-remove` line is what produced the `R`.
**R2 without R3 is not evidence** for the same reason, in the other direction.

## 10. What this spec does NOT do

- It changes **no gate, no threshold, no cap and no label.** No pre-registration is
  amended, no verdict is re-graded, no verdict-vocabulary word is added or retired.
- It does **not edit** `cases/RANS_LES_closure_models/_common/commit_private.sh`. The six
  defects in §1a are **reported to the cfd-supervisor for relay to closure**, not repaired
  here.
- It does **not** relocate that helper, and §7 escalates the relocation question rather
  than answering it.
- It does **not** back-fill, retire, delete or rewrite any existing fossil (§8), and it
  proposes **no history rewrite of any kind**.
- It does **not** change `scripts/queue_runner.py`. The runner is where the move happens;
  this spec is about how an agent **commits** a move that already happened.
- It does **not** make any commit automatically. The mode is a helper a human or an agent
  invokes with an explicit pair; nothing in it watches, polls or fires on its own.
- It does **not** amend `COMMIT_INTEGRITY_STANDARD.md`. §4.4 is a **referral** to that
  standard's owner, and rename mode does not land until it is ruled.
- It sends nothing anywhere (`CLAUDE.md` rule 7).
