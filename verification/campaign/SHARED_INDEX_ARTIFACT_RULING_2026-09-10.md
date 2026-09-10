# RULING — the "SHARED INDEX HAZARD" is **NOT A HAZARD AND NOT CLEARABLE**: it is a permanent, expected REPORTING ARTIFACT of the private-index protocol, it regenerates once per commit, and the remedy closure named first is **REFUSED**

**Ruled by:** verification-supervisor. Routed by the chief from closure, bearing on the ansys-verification escalation already with this team.
**Date:** 2026-09-10. **HEAD at ruling:** `acbea6e2`. **Cost: 0 solver core-min, $0.00.** `[lab-attributed]`.
**Standing:** this closes a defect escalated independently by **three teams** — ansys-verification, closure, and this team's own 2026-08-27 desk item.

---

## 1. CLOSURE'S MECHANISM CLAIM IS **VERIFIED**, AND I VERIFIED IT ON PATHS I LANDED MYSELF

Closure's claim, treated as a claim and not a fact: *every private-index commit makes the shared index stale in the reverting direction for exactly the paths it just landed, so the hazard regenerates once per commit and cannot be cleared by discipline.*

**Tested on this supervisor's own commits from this session, which is the right sample because their provenance is not in question:**

| path | added at | `git status` | at HEAD | on disk | in shared index |
|---|---|---|---|---|---|
| `verification/campaign/K0H_AGE_GUARD_RESTART_RULING_2026-09-10.md` | `d102afa2` | **`D`** | **YES** | **YES** | **NO** |
| `scripts/lab_state_split.py` | `3c859b37` | **`D`** | **YES** | **YES** | **NO** |
| `verification/campaign/K0H_FREEZE_COVERAGE_RULING_2026-09-10.md` | `e1971288`, amended twice | **`MM`** | YES | YES | YES, at an **older blob** |
| `verification/campaign/A2_GC_P_GATE_R_LEVEL_RULING_2026-09-10.md` | `c41672a8` | *(clean)* | YES | YES | YES, current |

**Two files I committed hours ago are reported as STAGED DELETIONS while present at HEAD and present on disk.** The fourth row is the tell that the index was refreshed by somebody between `c41672a8` and `d102afa2` — consistent with closure's 16:19:31Z observation and with this team's earlier finding of an index byte-identical to HEAD at ~15:45Z.

**The mechanism, stated so it need not be re-derived:** the protocol writes `GIT_INDEX_FILE=<scratch>/idx` and **never `.git/index`**, then moves HEAD. For a path it just landed the shared index therefore holds **either no entry at all** — which reads as a **staged deletion** against the new HEAD — **or an older blob**, which reads as a **staged modification in the reverting direction.** Both are correct renderings of a stale index; neither describes anybody's intent.

**Current reading: 12 `D` + 10 `M` staged, 3,949 deletions.** That the set differs from the one ansys escalated, and from closure's 16:19:31Z and 16:37:47Z sets, **is the claim's own signature**: the set is simply *whatever landed since the index was last written*.

---

## 2. THEREFORE THE ESCALATION IS **DOWNGRADED** — and this is the substance of the ruling

**It is not a defect. It is not a race. It is not clearable by discipline, and no team should try again.** It is the price the private-index protocol pays to keep six teams from clobbering each other, and it is the correct price. **A refresh buys minutes**, as this lab has already recorded; three teams have now spent effort clearing a condition that regenerates on the next commit by design.

---

## 3. THE REMEDY CLOSURE NAMED FIRST — A POST-COMMIT INDEX REFRESH IN `commit_private.sh` — IS **REFUSED**, FOR TWO REASONS, AND THE SECOND SURVIVES PERMISSION

**(a) Rule 10 reserves it.** *"Never touch the shared index … the index is chief's call."* Putting a `read-tree` into the shared commit helper makes **every commit by every team touch the shared index**. That is not a tooling tweak; it amends a standing rule, and standing rules are Sanaa's.

**(b) THE REASON THAT SURVIVES EVEN IF PERMISSION WERE GIVEN: a post-commit refresh silently discards whatever anyone HAS staged.** `git read-tree HEAD` over the shared index drops staged content not in HEAD, and it cannot distinguish a stale phantom from a peer's deliberate staging.

**Measured, because the objection is worth testing rather than asserting: 0 of 11 index-modified paths currently hold worktree content.** Every one is a stale older blob, so a refresh today would destroy nothing. **That is exactly the reasoning that makes a destructive default acceptable until the day it isn't** — and this helper would run on every commit, by six teams, indefinitely. **It converts a REPORTING nuisance into a DATA-LOSS mechanism in order to quiet a cosmetic complaint.** Refused.

*(The same measurement carries a second finding: **nobody in this lab stages into the shared index at all**, because the protocol means nobody ever needs to. An index with no writer of genuine intent carries no information — which is the whole argument for §4.)*

---

## 4. THE RULING: **THE SHARED INDEX IS NOT A REFERENT. NOTHING READS IT AND NOTHING REFRESHES IT. HEAD IS THE REFERENT.**

**This is not new law. It is already implemented in a lab instrument and stated in that instrument's own docstring** — `scripts/check_filing.py:87-92`, verbatim:

> *"Paths in HEAD. HEAD is the referent, never the index. Files landed by the private-index commit protocol have no shared-index entry, so `git ls-files` and `git diff --cached` misreport them. This lab has been bitten by that repeatedly; ask the commit graph, not the staging area."*

**The doctrine existed in code and was never stated as a standing rule — which is precisely why three teams escalated the same artifact as a hazard.** Operationally: any check, census or status reading that must know what is in the repository asks `git ls-tree -r HEAD` or `git show HEAD:<path>`, never `git status`, `git ls-files` or `git diff --cached`. A report of "N files staged for deletion" is a report about the index's age, not about the repository.

**No executable check is added and nothing is made to refuse — `D539`.** This is a reading discipline, and a reading discipline needs no gate.

---

## 5. WHAT REMAINS GENUINELY DANGEROUS — AND IT IS **ALREADY FORBIDDEN**

The danger was never the reporting; it is the commands that **act on** the index:

- **`git commit -a` / a bare `git commit`** — measured earlier today at **245 files, 8,966 deletions across six teams.**
- **`git checkout --` / `git restore` / `git reset --hard`** — and note the direction has **inverted** since the last refresh: these are no longer a deletion risk but a **RESURRECTION** risk, restoring **162 consumed queue entries** into live queue directories whose twins already sit in `launched/` — **a duplicate-launch surface, i.e. unbudgeted compute.**

**Every one of these is already banned by rule 10.** So the hazard is fully mitigated by rules that exist. What was missing was the statement that the *reporting* is expected — which §4 now supplies.

---

## 6. ONE THING CHECKED BECAUSE IT WOULD HAVE BEEN THIS TEAM'S TO CORRECT

A path present at HEAD but absent from the shared index could plausibly be double-counted — once as a staged deletion, once as untracked — which would have contaminated **this team's own `D593`**, whose population figure rests on `git ls-files --others --exclude-standard`.

**Measured: it does not. Of the untracked enumeration, `0` paths are present at HEAD.** The enumerator is clean and **`D593` needs no correction.** Recorded because the check was owed, and a negative result that was actually run is worth more than one assumed.

*(Noted in passing: the untracked population reads **79,188** now against `D593`'s **68,051** earlier today. `D593`'s figure is a clock-stamped measurement of a volatile population, not a constant, and is correct as recorded.)*

---

## 7. TWO ITEMS ROUTED ONWARD, NOT DECIDED HERE

**(a) closure's repair of a peer's board line (`5f86dce4`) is ALREADY ADJUDICATED** — by this team, at `D595` / `COMMIT_INTEGRITY_STANDARD` §A8.7, and **the certification they asked for is negative**: the line they restored had been **superseded in place**, not lost. Their conduct is not criticised; §A5.3 **part 6** was added because their five controls all asked *faithfulness to the blob* and none asked *currency of the blob*.

**(b) `L-525`, `L-529`, `L-530` owe executable checks — NOTED, NOT TAKEN.** Whether a lesson owes a check is the lesson-owner's call, and **any such check lands ADVISORY**: making one refuse is `D539`, which is this team's own ruling and binds this team first.

---

## 8. DATED SECTION — cfd's BOARD-CLOBBER GUARD CLAIM IS **VERIFIED**, THE GUARD **CANNOT** BE FIXED WITHOUT MAKING IT A PERMANENT RED, AND IT IS BLIND TO PRECISELY THE **UNRECOVERABLE** CLASS

**Routed by the chief from cfd, who lost their board block 129 this way and wrongly implicated heat-transfer's `a0d5a4d7`.**

### 8.1 BOTH HALVES VERIFIED AT SOURCE

**(a) `a0d5a4d7` IS INNOCENT, confirmed independently by this team:** `git show --numstat` on the board gives **`48  0  docs/LAB_STATE.md`** — **48 insertions, 0 deletions, a clean pure append.** cfd withdrew the implication themselves; it is confirmed here so the record does not carry a live accusation against another team.

**(b) THE GUARD IS PARENT-BASED, and its own comment says so** — `cases/RANS_LES_closure_models/_common/commit_private.sh:217-222`, verbatim:

> *"if this commit touched the shared board, refuse to LAND it when it would DROP a section or block **vs the parent** … Counts equal (edit) or grown (append / **swept-in peer block, content survives**) pass; only a DECREASE aborts."*

**That last clause is sharper than cfd's claim and it is the whole finding.** A block that exists in the **worktree** and not in the **parent** — i.e. any peer's block written but not yet committed — **cannot make the count DECREASE against the parent, because it was never counted there.** A commit that drops it produces counts *equal or grown*, and **passes.**

### 8.2 IT IS BLIND TO EXACTLY THE CLASS THAT CANNOT BE RECOVERED

This is `§A8`'s window seen from the guard's end, and the asymmetry is the point:

| the two exits from the §A6 window | recoverable? | guard sees it? |
|---|---|---|
| peer **stages the worktree copy** → the uncommitted block **survives under their sha** | yes — it is in history, merely mis-attributed | **passes, correctly** (the comment names this: *"swept-in peer block, content survives"*) |
| peer **rebuilds from the HEAD blob** → the uncommitted block is **destroyed at no sha** | **NO — it exists at no sha, ever** | **BLIND** |

**The guard protects the recoverable case and is structurally incapable of protecting the unrecoverable one.** heat-transfer's measured **13,512-byte** loss (`D583`) is in the blind column.

### 8.3 IT CANNOT BE FIXED UNDER L-221/L-222 WITHOUT READING THE SHARED WORKTREE — AND READING IT MAKES THE GUARD A PERMANENT RED

To see an uncommitted block's loss the guard needs a referent that **contains** it, and the only such referent is the **shared worktree**. That fails on two independent grounds:

1. **It would fire on essentially every commit.** The shared worktree *always* holds other teams' uncommitted board edits that this commit **correctly does not carry** — a per-item commit is supposed to leave foreign rows alone (rule 10). So `NEW` vs `WORKTREE` shows a "loss" every time, and the guard becomes **a permanent red** — the exact failure mode this team spent `V-151` removing from `check_harness.py`, where *"a red that no action can clear has only one exit, which is switching the clause off."*
2. **Reading the shared worktree to decide a commit is `L-223`'s own hazard**, and this guard exists to defend the commit path, not to add a second stale read to it.

**RULED: the guard is CORRECT AS BUILT FOR WHAT IT CAN SEE, and its blind spot is NOT a defect to repair but a limit to state.** `L-221`/`L-222`'s insert-with-assert discipline does not reach it, because there is no assertion to insert — the information is not available at the choke point. **Recorded as a limit rather than left as an open repair, so nobody re-opens it and no one reads a green guard as proof no block was lost.**

*(One bounded observation, not a repair: the guard's basis is a **count** of `##`…`#####` headings, so a commit that preserved the count while replacing content would also pass. Outside cfd's referral and named only so it is not discovered later as new.)*

### 8.4 THE REAL FIX IS STRUCTURAL, AND IT IS ALREADY BUILT

**Per-team / per-case state files plus a generated rollup — CASE PROTOCOL §6 and `V-119` — remove this class entirely, because two writers never touch one path**, so there is no uncommitted peer block in your referent to lose. **The tooling landed today at `D599`** with its byte-identity abort proven both ways (`8,133,073 B` identical; a planted length-preserving byte flip aborts rc 3, nothing written). **This is a third independent argument for the cutover**, after the clobber class and the false attribution of `§A8.3`, and it is the one that retires a guard rather than patching it.
