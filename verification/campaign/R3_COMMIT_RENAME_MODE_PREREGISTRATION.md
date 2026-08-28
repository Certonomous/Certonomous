# R3 — PRE-REGISTRATION: THE COMMIT-HELPER RENAME MODE — frozen, capped, schedulable, and **BLOCKED**

**Team:** cfd. **Owner:** cfd-supervisor. **Registering lane:** cfd lane **REPAIRQ**, 2026-08-28.
**Status at writing: FROZEN ON COMMIT. No code exists. Zero compute has been spent.**

## VERDICT AT REGISTRATION: **BLOCKED**

Stated in the fixed vocabulary of standing rule 1, at the top of the document, and **not softened
into prose anywhere below.** This item is fully specified, fully costed, fully capped and fully
schedulable. **It may not run**, and the reason is a clause this team does not own:

> `docs/standards/COMMIT_INTEGRITY_STANDARD.md` **Clause 2** requires a **numeric** assertion that
> **`deletions == 0`** before `commit-tree` and again after `update-ref`. **A rename is a
> deletion.** **Clause 2, read literally, refuses every rename this mode exists to make.**

`COMMIT_INTEGRITY_STANDARD.md` is the **verification team's** standard, and its own scope paragraph
says a clause-level conflict is *"a referral to the verification team and not a judgement call
inside the tooling."* **cfd does not rule on it, and this registration does not route around it.**
`BLOCKED` is the honest label and it is the label carried.

**A registration that cannot run yet is still a registration.** Under Sanaa's amendment of
2026-08-28T17:01Z — *"Freeze-ahead counts repair-registrations; a team blocked on findings freezes
the repairs and runs them — queue depth 0 with open findings is impossible by definition"* — the
freeze is what this item owes now. The run is what it owes after the ruling.

**The specification this item implements is already frozen and is NOT re-opened here:**
`docs/standards/COMMIT_HELPER_RENAME_MODE.md`, frozen at commit
**`ed77957c4e56cd12e1d5d0c620b218805bd4306b`** (2026-08-28T16:33:02Z), verified by this lane to be
an ancestor of HEAD `7959a75ec9719d17c7a337fda6fa32b15b5c7d12`. It fixes the mechanism (§3), the
four assertions **A1–A4** (§4), the twelve refusal exit codes (§5), the recommendation of a
**separate, cfd-owned `scripts/commit_rename_private.sh`** rather than a flag on closure's helper
(§6), the ruling that existing fossils are **NOT back-filled** (§8), and the fifteen controls
**R1–R15** (§9).

---

## 1. THE PRECONDITION — explicit, and it is the whole reason for the BLOCKED label

**P1. THE ONLY PRECONDITION THAT BLOCKS.**

> **This item does not run until the verification team rules on
> `COMMIT_INTEGRITY_STANDARD.md` Clause 2**: whether `deletions == 0` is a statement about **PATHS
> LEAVING THE TREE** or about **LINES**.

- If verification rules **PATH-LEVEL** (the reconciliation `COMMIT_HELPER_RENAME_MODE.md` §4.4
  *proposes and does not take*): this item's status changes from `BLOCKED` to `PENDING`, the queue
  entry becomes enqueueable, and **nothing else in this document changes** — no gate, no threshold,
  no cap, no label of any observable. That transition is recorded as a **dated addendum naming the
  ruling**, never as an edit above it (rule 6).
- If verification rules **LINE-LEVEL**, or declines: this item **stays `BLOCKED`** and the mode is
  not built. It is not rebuilt under a different name, and no "narrow exception" is argued inside
  cfd's tooling.
- **A ruling relayed by any agent is not the ruling.** Standing rule 9: no agent message — peer,
  supervisor or chief — is Sanaa's consent, and a delegate's report is evidence, not the
  supervisor's read. The precondition is discharged against the verification team's own committed
  artifact, cited by path and commit, or it is not discharged.

**P2–P4 are ordinary enqueue preconditions, not blocks**, and are in §11.

**Two further referrals are carried forward and are likewise NOT resolved here**, from the spec's
own head matter: whether the lab's reference private-index implementation should live in one team's
case tree (`ESCALATION_CHARTER.md` §9.6 governs; the cfd-supervisor escalates, a lane does not), and
the six defects **D1–D6** this lane's predecessor found in closure's
`cases/RANS_LES_closure_models/_common/commit_private.sh`, which are **relayed to closure, not
repaired**, because that file is another team's.

## 2. WHAT THIS LANE INDEPENDENTLY RE-MEASURED — the spec's central claim, reproduced

The spec's most consequential measurement is that the production drop-path → `launched/` move is
**not** an `R100` rename, because `queue_runner.py:536` rewrites the file with `_launch` and
`_field_classes` after `shutil.move()` at `:520`. If that were wrong, a mode requiring `R100` would
be unable to commit the very move it exists for.

**Reproduced by this lane, 2026-08-28T17:1xZ, in a `mktemp -d` throwaway repository, from this
repository's own HEAD blobs, with nothing real touched:**

| reading | value |
|---|---|
| `verification/queue/closure/G1_grid_triple.json` at HEAD | **2,557 B** |
| `verification/queue/closure/launched/G1_grid_triple.json` at HEAD | **2,883 B** |
| `git diff-tree -M50% -r --name-status "$H^{tree}" "$T"` | **exactly one line**: `R088` + the two declared paths, and no other line |
| `git diff-tree -M50% -r --name-only --diff-filter=D "$H^{tree}" "$T"` | **EMPTY** |
| one full cycle (init, base commit, private index, `--add` + `--force-remove`, `write-tree`, both diff-trees) | **0.08 wall s** |

**The spec's 88 % is CONFIRMED independently**, and with it §4.3's ruling that the default
similarity floor is git's own **50** and that a floor above 88 could not commit the production move.
The **A2 empty `D`-listing is confirmed**, which is the exact reading §4.4's Clause-2
reconciliation rests on — measured here rather than taken on report.

## 3. THE OBSERVABLE — AND IT IS NOT A RICHARDSON QUANTITY

**The observable is the CONTROL OUTCOME VECTOR** `(R1 … R15)`, each element `FIRED` / `HELD` /
`FLIPPED` / `NOT RUN`, as enumerated in `COMMIT_HELPER_RENAME_MODE.md` §9 at its freeze commit,
together with the **exit code** each control's run returned, compared against §5's table.

**Stated explicitly, so it cannot later be asked for:**

- There is **no grid triple**, no mesh, no field, no refinement ratio.
- **NO OBSERVED ORDER OF ACCURACY IS COMPUTED** and none will be reported.
- **NO GCI IS COMPUTED OR QUOTED.**
- `scripts/roache_triple.py` is **not called**. Standing rule 5 is **inapplicable** — not waived,
  not satisfied — because it grades a row with a grid triple and this row has none. Precedent for an
  ordinal/structural observable: `cases/F26_RINGLEB/PREREGISTRATION_F26D_2026-08-27.md` §4.
- The similarity **score** (`088`) is a git rename-detection index, **not** a physical quantity and
  **not** an error norm. No uncertainty interval is attached to it and none is meaningful.

## 4. THE REGISTERED GATES — fixed before the work runs

| gate | statement | verdict if met | verdict if not |
|---|---|---|---|
| **G-R3-1 — THE POSITIVE CONTROL FIRES ON THE UNREPAIRED SHAPE (R4)** | With the `git update-index --force-remove -- "$OLDPATH"` line **deleted** and everything else unchanged: A1 shows `A` + the new path and **no `R` line**; the run refuses (exit **7** or **9**); the old path is **still present** in `after.txt`; the symmetric difference is `{<new>}` alone. **The fossil is created inside the test, seen, and refused.** | required for **PASS** | **GATE FAIL** — the defect was never demonstrated |
| **G-R3-2 — THE DEFECT STOPS FIRING ON THE REPAIRED CODE (R1)** | On the real production pair: exit **0**; A1 prints **exactly one** line matching `^R0?[5-9][0-9]\t<old>\t<new>$` with score **88**; A2's `--diff-filter=D` listing **EMPTY**; `comm -3 before after` yields **exactly** `<old>` left and `<new>` right and nothing else; `wc -l < after == wc -l < before`; and A4 reproduces all three against `"$C^"`/`"$C"` | required for **PASS** | **GATE FAIL** |
| **G-R3-3 — THE NEGATIVE CONTROLS (§6)** | R2, R5, R6, R7, R8 and R10 each refuse with **their own registered exit code** — 2, 3, 4, 4, 5, 6 — and **`git rev-parse HEAD` is BYTE-EQUAL before and after** every one of them | required for **PASS** | **GATE FAIL** |
| **G-R3-4 — THE MUTATION FLIPS (R3)** | With the `git cat-file -e "$H:$OLDPATH"` probe replaced by `true`, **R2 FLIPS** and the bogus rename commits | required for **PASS** | **GATE FAIL** — R2's refusal was not coming from the probe |
| **G-R3-5 — A REWRITE IS DECLARED, NOT DISGUISED (R6 + R7)** | R6: two unrelated real entries produce exit **4** with the words `REWRITE, not a rename`. R7: R1's pair with `--min-similarity 90` produces exit **4** naming **88** and **90** — **not** exit 8, proving A3 parses the score rather than delegating the floor to `-M` | required for **PASS** | **GATE FAIL** |
| **G-R3-6 — THE L-382 CONTROL, DRIVEN THE WAY PRODUCTION REACHES IT (R11)** | The message made unavailable **by removing the file**, never by assigning `C=""`: exit **10**, `refs/heads/main` **unchanged**, and **no success line printed**. Companion positive limb: a real 40-hex sha passes and HEAD is asserted **moved** | required for **PASS** | **GATE FAIL** |
| **G-R3-7 — THE SHARED INDEX IS NEVER TOUCHED (R12)** | The operating repository's `.git/index` has the **same mtime and the same `git hash-object`** before and after a full successful run; and a run with `GIT_INDEX_FILE` unset exits **12 before issuing any `update-index`** | required for **PASS** | **GATE FAIL** |
| **G-R3-8 — NO PRINTED REFUSAL (R13 + R15)** | R13: `grep -c 'rev-parse HEAD'` **== 1**, bare `read-tree HEAD` **== 0**, `HEAD~` **== 0** — declared **STATIC**, not dressed as behavioural. R15: every `echo`-ing refusal line is **immediately** followed by an `exit` | required for **PASS** | **GATE FAIL** — D2 reintroduced |
| **G-R3-9 — INVARIANCE** | §7's named set is **bit-identical** | required for **PASS** | **GATE FAIL** |

**PASS iff all nine hold.** §8's conditions take precedence — and clause 1 of §8 is the one that
applies **today**.

## 5. THE BIRTH REQUIREMENT — Sanaa directive 1, AS A REFUSAL CONDITION ON THIS INSTRUMENT

Sanaa's directive of 2026-08-28T17:01Z: *"A planted control must travel the real production path —
written by the real producer's code, read through the real reader … no instrument grades anything
until that answer is yes, demonstrated."*

**THE REAL PRODUCER, NAMED.** `scripts/queue_runner.py::launch()` — the inline four lines that make
the move this mode exists to commit: `:515` `launched_dir = path.parent / "launched"`, `:517`
`dst = launched_dir / path.name`, `:520` `shutil.move(str(path), str(dst))`, `:536`
`dst.write_text(json.dumps(meta, indent=2) + "\n")` with `_launch` (`:522`) and `_field_classes`
(`:526-535`) added. **It is `:536` that makes the move an 88 % rename rather than a 100 % one, and
that is the entire difficulty.** *(There is no `move_launched` function; a spec that sent an
implementer to one would send them to code that does not exist.)*

**THE REAL READER, NAMED.** `git diff-tree -M50% -r --name-status` and
`git diff-tree -M50% -r --name-only --diff-filter=D`, **run by the shipped
`scripts/commit_rename_private.sh` itself**, against `"$H^{tree}"`/`"$T"` before `commit-tree` and
against `"$C^"`/`"$C"` after `update-ref`. **Not a re-implementation, not a helper's copy of the
command, and never `--stat`** — with `-M`, `--stat` renders the rename as a **brace-elided** path
in which neither literal path appears as a contiguous string, so any check that greps a `--stat`
line for a declared path fails on every rename it is shown.

**BR-1 — THE DEMONSTRATION, MANDATORY, AND THE INSTRUMENT REFUSES WITHOUT IT.**

> **R1's fixture is built from bytes the real producer wrote.** The old side is the **HEAD blob** of
> `verification/queue/closure/G1_grid_triple.json` (2,557 B) and the new side the **HEAD blob** of
> `verification/queue/closure/launched/G1_grid_triple.json` (2,883 B) — a pair this lane confirmed
> at those exact sizes and whose difference is `queue_runner.py:536`'s own rewrite. **Never an
> identical-content pair**, which would score `R100` and prove nothing about the case the mode
> exists for.
>
> **THE REFUSAL.** Before it grades anything, the driver asserts, in the same invocation:
> (i) both blobs are fetched with `git cat-file` from **this repository's HEAD**, and their byte
> sizes are asserted **2557** and **2883** — a synthesised or hand-edited pair is refused;
> (ii) the new-side blob **contains the keys `_launch` and `_field_classes`** that only
> `queue_runner.py:522`/`:526-535` write, so the new side is provably the producer's output and not
> a copy of the old side with a field appended;
> (iii) **R4 fires first**: with `--force-remove` deleted, the run must be observed producing the
> **fossil** — `A` and no `R` line, the old path surviving in `after.txt` — before the repaired run
> is allowed to report that it does not.
> **If any of (i)–(iii) fails the driver exits 2 and grades NOTHING.**

**WHY AN IDENTICAL-CONTENT PAIR IS REFUSED, in this document's own words.** An `R100` fixture is a
control defined in terms of the thing it controls: it passes at every similarity floor including
ones that cannot commit the production move, so it certifies the mode against a case that never
occurs. `ee4c331c`'s real `R100` is a **`held/` → drop-path** move, where content does not change;
the launched move changes bytes. **Two different moves, two different scores, one mode** — and R9
exercises the `R100` shape separately so that R1's 88 % is not mistaken for the only accepted shape.

## 6. THE NEGATIVE CONTROLS — the repair did not disable the thing it repaired

A mode whose whole purpose is to permit deletions is one wrong line away from permitting all of
them. Six fixtures, all mandatory, each with its own registered exit code, **each additionally
asserting `git rev-parse HEAD` byte-equal before and after** — no refusal may create a commit:

| id | fixture | required |
|---|---|---|
| **R2** | old path **never tracked** at `$H`; new path added with content identical to a worktree-only file | exit **2**, message names the old path and the words `not tracked at HEAD` |
| **R5** | **both** paths already tracked at `$H` | exit **3**, both paths named |
| **R6** | two **unrelated** real entries (`verification/queue/cfd/F25_DUCT3D.json` 6,535 B HEAD blob → `.../launched/F24_PRANDTL_MEYER.json` 5,685 B HEAD blob), measured to produce `D` + `A` and **no `R`** at 50 % | exit **4**, `REWRITE, not a rename` |
| **R7** | R1's pair with `--min-similarity 90` | exit **4** naming **88** and **90**, **not** exit 8 |
| **R8** | two valid pairs, **no** `--multi` | exit **5** naming the count |
| **R10** | a valid `closure/` pair with `--team-dir verification/queue/cfd` | exit **6** naming the path and the declared directory |

**R2 without R3 is not evidence**, and **R1 without R4 is not evidence** — the two mutation
controls are what show the refusals come from the probes named and not from something incidentally
in the way. **R14** additionally requires that two concurrent runs resolve `GIT_INDEX_FILE` to
**distinct** pid-bearing paths and that the second's CAS either succeeds against the first's commit
or **fails loudly and retries** — never silently overwrites (D5's repair, **in the new script
only**).

## 7. THE INVARIANCE SET — BIT-IDENTICAL, checked by hash

Hashed (`sha256`) before and after; any difference is `GATE FAIL` under G-R3-9, with the path
printed.

1. **`cases/RANS_LES_closure_models/_common/commit_private.sh`** — closure's file, 29 lines. **Not
   one byte is edited by this item**, and D1–D6 are **relayed, not repaired** (§1). This hash is
   that promise made mechanical.
2. **`.git/index` of this repository** — mtime **and** `git hash-object`, per R12. The shared index
   is never touched (rule 10).
3. **`refs/heads/main`** — the branch is **not moved** by any control. Every control commits inside
   its own `mktemp -d` throwaway repository. **A control run that moves this repository's `main` is
   an incident, not a control result.**
4. **Every file under `verification/queue/`** — nothing real is renamed, moved, deleted or committed
   (§12: the 34 fossils are left exactly as they are).
5. `docs/standards/COMMIT_HELPER_RENAME_MODE.md`, `docs/standards/COMMIT_INTEGRITY_STANDARD.md` —
   frozen standards; rule 6. **The second is the verification team's and this item may not edit it
   under any ruling.**
6. This document.

## 8. CRITERIA — how the verdict is reached, in order

1. **BLOCKED** — **the state today** — while §1's P1 precondition is undischarged, or if any of
   §11's P2–P4 is unmet at launch. **Nothing is graded and no control is run.** BLOCKED is not a
   softened GATE FAIL and is not a PENDING: `PENDING` is a queue state meaning *not yet run*, and
   this item is *not yet permitted to run*.
2. **NOT A RESULT** if BR-1 refuses (exit 2) — the instrument was never shown able to see the fossil
   through the real code path.
3. **NOT A RESULT** if the driver's completion clause fails: rc != 0, no terminal record line, or
   any of R1–R15 reported `NOT RUN`.
4. **GATE FAIL** if any of G-R3-1 … G-R3-9 is not met, naming which.
5. **PASS** iff all nine are met and none of 1–3 applies.

**No partial credit, no degraded reading** (rule 4).

## 9. COST, CAP AND CALIBRATION — rule 12

**A blocked item is still costed.** Rule 12 disqualifies a proposal with no cost, and a cost that
appears only once the block lifts is a cost chosen after the answer was known.

### 9.1 The basis, term by term, each labelled MEASURED or ALLOWANCE

`ranks = 1`. Core-minutes = wall s × ranks ÷ 60.

| term | wall s | basis |
|---|---|---|
| a) 15 controls, each a throwaway `mktemp -d` repository cycle, at ~2 cycles per control (R3, R4, R7, R9, R11, R12, R14 each run two) | 2.4 | **MEASURED.** One full production-shape cycle — `git init`, base commit, private index, `--add` + `--force-remove`, `write-tree`, both `diff-tree`s — ran in **0.08 wall s** in this invocation. 15 × 2 × 0.08 = 2.4 s. |
| b) R9's three-pair `ee4c331c` shape and R14's two concurrent runs | 1.0 | **ALLOWANCE**, on the same measured cycle rate. |
| c) `COMMIT_HELPER_RENAME_MODE.md` §2b's **mandatory** fossil re-measurement: `git ls-files 'verification/queue/*'` at HEAD, cross-checked against the disk | 2.0 | **ALLOWANCE.** |
| d) R13/R15 static source checks and R12's `.git/index` hash before/after | 1.0 | **ALLOWANCE.** |
| **TOTAL** | **6.4** | |

### 9.2 THE ESTIMATE, THE CAP AND THE RATIO

| | value |
|---|---|
| **cost_core_min_estimate** | **0.1067** core-min (6.4 wall s × 1 rank ÷ 60) |
| **cap_core_min_registered** | **0.1600** core-min |
| **cap / estimate** | **1.4995** |
| dollars at the estimate | **$0.0000912** — **DERIVED, NOT MEASURED** |
| dollars at the cap | **$0.0001368** — **DERIVED, NOT MEASURED** |

Rate **$0.0513 per core-hour**, c7a.4xlarge, **owner-stated and reported-by-owner, never measured**
(`COMPUTE_BUDGET_CHARTER.md` §5).

**HOW THE CAP IS ENFORCED, and it is never raised.** The cap converts to a wall allowance of **9.6
s** at 1 rank, handed to `timeout` around the whole control run. An overrun **kills the run and
STOPS the item**, leaving controls incomplete, which §8 clause 3 grades **NOT A RESULT**. It does
not get a second budget.

**MANDATORY RE-MEASUREMENT AT IMPLEMENTATION.** The fossil counts in `COMMIT_HELPER_RENAME_MODE.md`
§2b — **65** files tracked at HEAD under `verification/queue/`, **34** tracked drop-path entries of
which **34 are absent from disk**, **18** tracked `launched/`, **1** same-name pair, **0** tracked
`refused/` — are re-derived **in the same shell invocation that lands the code**, and the record
carries the fresh figures. The spec also records that the board's **19** carries a definition this
lane does not have and **is not contradicted**; **the mechanism does not depend on the count**, and
reconciling the two definitions is the supervisor's, not this item's.

### 9.3 CALIBRATION AT COMPLETION (rule 12's calibration clause)

At completion: actual core-minutes from the driver's own log, gross and cleaned separately; waste
named separately and never absorbed into the ratio; the ratio actual/predicted against **0.1067**;
the gap attributed to contention, waste or misprediction; dollars **derived, not measured**. A row
lands in **`docs/COST_CALIBRATION.md`**. **A completion report without this comparison is
incomplete.** **If this item is retired as `BLOCKED` without ever running, the calibration row
records zero actual against 0.1067 predicted and says why** — a blocked item that never ran is not
a free item, it is an item whose prediction was never tested.

## 10. RULE-2 ABSENCE CONDITION, CHECKED IN THIS WRITING INVOCATION

**All four of the following DO NOT EXIST at 2026-08-28T17:12:20Z**, each checked **four ways** in
that invocation — `os.path.exists` **False**, `os.path.lexists` **False** (so not a dangling
symlink), `os.path.isdir` **False**, `glob` on the literal path **[]**:

- `/home/ubuntu/Certonomous/verification/runs/TOOLING_REPAIRS`
- `/home/ubuntu/Certonomous/verification/runs/TOOLING_REPAIRS/R3_RENAME_MODE_2026-08-28`
- `/home/ubuntu/Certonomous/scripts/commit_rename_private.sh`
- `/home/ubuntu/Certonomous/scripts/run_r3_rename_mode_repair.sh`

A fifth, wider check: `glob('verification/runs/TOOLING*')` → **[]**.

**0.000 core-min have been spent under this registration**, and **no commit has been made by it** —
`refs/heads/main` is untouched by this lane, which has committed nothing and staged nothing.

Amendments **before** first compute remain legal under rule 2 and must state this condition and how
it was checked, naming the directory that does not exist. **The P1 transition of §1 — BLOCKED to
PENDING on verification's ruling — is exactly such an amendment**, lands as a **dated addendum**
citing the ruling by path and commit, and **may not alter a gate, threshold, cap or label.**

## 11. LAUNCH SHAPE — for the supervisor's check 4; **NOT an authorisation**, and today not even a
possibility

    bash /home/ubuntu/Certonomous/scripts/run_r3_rename_mode_repair.sh \
         --prereg-commit=<the sha of THIS document's adding commit>

The driver **fires nothing without `--prereg-commit`**, verifies the sha is a commit in this
repository, and verifies `docs/standards/COMMIT_HELPER_RENAME_MODE.md` at
`ed77957c4e56cd12e1d5d0c620b218805bd4306b` hashes to the blob it was frozen as.

**ENQUEUE PRECONDITIONS.**

- **P1 — THE BLOCK.** Verification has ruled on `COMMIT_INTEGRITY_STANDARD.md` Clause 2, and the
  ruling is cited **by path and commit** in the addendum that lifts this item's `BLOCKED` label. §1
  governs. **Until then the entry is not enqueueable and the supervisor does not drop it.**
- **P2.** `scripts/run_r3_rename_mode_repair.sh` and `scripts/commit_rename_private.sh` **exist** at
  the absolute paths above. The queue validator does **not** check `launch_cmd[1]`; an entry naming
  an absent script validates cleanly and then dies at launch behind a LAUNCHED record.
- **P3.** `bash scripts/run_r3_rename_mode_repair.sh --selftest` returns **rc 0**.
- **P4.** The `prereg_commit` placeholder in the held queue entry has been replaced with the real
  sha of this document's adding commit.

A queue entry is drafted at `verification/campaign/queue_entry_R3_COMMIT_RENAME_MODE.json` and is
**HELD beside this registration. THIS LANE DOES NOT ENQUEUE IT and has committed nothing.**
**Enqueueing is not authorisation**, and enqueueing a `BLOCKED` item would be worse than that — it
would arm a launch the lab has said may not happen.

## 12. WHAT IS **NOT** CLAIMED, REGISTERED OR AUTHORISED HERE

- **No verdict of any existing rung is re-graded**, in any team.
- **No frozen comparator is edited**, and **`COMMIT_INTEGRITY_STANDARD.md` is not amended.** §4.4 of
  the spec is a **referral** to that standard's owner and this registration adopts it as a referral,
  not as a reading it may act on. **cfd does not rule on verification's clause under any
  circumstances**, including a favourable one.
- **`cases/RANS_LES_closure_models/_common/commit_private.sh` is not edited, moved, wrapped or
  consolidated.** D1–D6 are relayed to closure. The relocation question is escalated by the
  supervisor under `ESCALATION_CHARTER.md` §9.6, with coupling measured before anything moves — a
  lane does not move another team's file and does not measure its coupling on the way past.
- **NO FOSSIL IS BACK-FILLED, RETIRED, DELETED OR REWRITTEN.** The 34 tracked-but-absent drop-path
  entries are left exactly as they are. **No `git filter-branch`, no rebase, no history rewrite of
  any kind** is proposed, permitted or implied. The branch is append-only. Retiring a fossil would
  mean committing a deletion of a path whose launched sibling was landed by another team under
  another pre-registration — not a tooling change, and not cfd's to make.
- **`scripts/queue_runner.py` is not changed.** The runner is where the move happens; this item is
  about how an agent **commits** a move that already happened.
- **Nothing commits automatically.** The mode is a helper invoked with an explicit pair; nothing in
  it watches, polls or fires on its own.
- **No observed order and no GCI is produced** (§3); `roache_triple.py` is not called.
- **Nothing is sent, filed, uploaded, registered, posted or submitted** (rule 7). Submissions are
  PARKED.

---

*Registration ends. Written before implementation; the commit that lands it is the freeze.*
*Verdict at registration: **BLOCKED**.*

---

## DRAFTING NOTE — 2026-08-28T17:1xZ, BEFORE THE FREEZE, BEFORE ANY COMPUTE

**HEAD MOVED WHILE THIS DOCUMENT WAS BEING WRITTEN.** At this lane's first read HEAD was
`7959a75ec9719d17c7a337fda6fa32b15b5c7d12`; on completion it was
`83cb13dabdba2a053ccd2e3d0a1af226ccb151a9`. Peers commit constantly, and a HEAD sha quoted in a
document has a shelf life. **Re-verified in the closing invocation: all three of
`ae2c8c49366259fe2c5bb8ece09d32bc8017c3f6`, `ed77957c4e56cd12e1d5d0c620b218805bd4306b` and
`7959a75ec9719d17c7a337fda6fa32b15b5c7d12` are ancestors of the new HEAD.** Every ancestry claim
above therefore still holds; only the reference point moved. **The supervisor re-derives the freeze
sha at the freeze, from `git log --diff-filter=A -- <this path>`, never from a subject line.**

**This lane committed nothing and staged nothing.** All six artifacts of this item — three
registrations and three held queue entries — stand as **untracked** working-tree files. The shared
git index was not touched, no `git add` of any form was issued, and `refs/heads/main` was not moved.

**Filing, measured before and after in this invocation:** `python3 scripts/check_filing.py` returned
**37 violations across 8 rules (rc 1)** before these files were written and **35 violations across 8
rules (rc 1)** after. **These six files contributed ZERO violations**; the decrease of two is a
peer's removal of `cases/F17c_kovasznay_floor/STATUS.F17c_KV40_FLOOR` and
`cases/F17c_kovasznay_floor/launcher.queue.out` under `R6-RUNARTIFACT` and is **not** this lane's
doing. Stated with its attribution because an improvement claimed by the wrong agent is a false
record in the cheap direction.
