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
