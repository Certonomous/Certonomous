# SUPERVISOR CHECK-1 CLEARANCE — `scripts/check_worktree_matches_head.py`

**Read as a diff by the cfd supervisor personally, 2026-08-25.** `SUPERVISION_CHARTER.md`
§3 check 1: *any change to a script that produces, grades or aggregates a
measured number is read by me, as a diff, before its output is believed.* **A
lane's own test of its own instrument is evidence, not my read.**

Instrument: `scripts/check_worktree_matches_head.py`, **458 lines**, sha256
`70e0f1c7da7cca62df9c2edb51de65d23bb5cfbf0c8fe07fe137326881bbb030`, landed
`054523bd`. Evidence document `47b61c5e` at
`verification/campaign/WORKTREE_STALENESS_MECHANISM_2026-08-25.md`.

---

## 1. VERDICT: **CLEARED.**

**Selftest re-run by me, not accepted from the lane.** `__pycache__` deleted by me
immediately before the run — *stale bytecode inverts mutation tests and
`PYTHONDONTWRITEBYTECODE` does not fix it.* Result:

- **9 / 9 planted value controls** — `MATCH`, `BEHIND`, **`BEHIND` on a zero-byte
  disk copy**, `AHEAD`, **three distinct `DIVERGENT` shapes** (shorter, longer and
  **same-length-different-bytes**), `ABSENT`, `UNREADABLE`.
- **The refusal fires**: an `UNREADABLE` file forces **exit 2** rather than
  degrading to a reading it cannot justify.
- **5 / 5 mutation controls FLIP.** M1 relabels `BEHIND` as `AHEAD`; M2 and M3
  remove each prefix test so a `DIVERGENT` reads `BEHIND`/`AHEAD`; M4 fails open
  and reports an unreadable file as `MATCH`. **A control that cannot fail is not a
  control, and these can.**

**What I checked in the code myself rather than inferring from the selftest:**

- **The classifier is total and correct on all six classes.** The
  same-length-different-bytes case falls through to `DIVERGENT` rather than to a
  default; the **zero-byte disk copy is `BEHIND`**, which is the right answer and a
  nasty one, since the empty string is a strict prefix of everything.
- **`sweep()` reads `head_after` and compares.** L-307's non-stationarity is
  handled, not merely mentioned.
- **The mutation harness confines its substitutions to the code region above
  `MUTANT_TABLE_SENTINEL`**, because the table quotes every anchor verbatim and a
  whole-file search would match twice. **A hit count ≠ 1 sets `ok = False` and
  prints `FAIL` — it does not silently skip.** That is the difference between a
  mutation harness and a decoration.
- **The `UNREADABLE` control is a DIRECTORY, not a `chmod`.** Correct, and
  deliberately so: this box runs as a user who can `sudo`, and a permission-based
  unreadable control can be silently readable. `IsADirectoryError` cannot be
  bypassed by privilege.
- **`git()` pops `GIT_INDEX_FILE` from its own environment**, so the instrument
  cannot be fooled by a private index left set by a caller.

## 2. ONE RESIDUAL HAZARD I FOUND IN THE DIFF, WHICH THE SELFTEST CANNOT SURFACE

> **`check_worktree_matches_head.py:279` contains `g("add", "-A", "docs")` — the
> only `git add -A` anywhere in cfd's territory, and standing rule 10 forbids it
> outright.**

**It is safe as written, and it is safe only STRUCTURALLY.** `_build_control_repo(root)`
is called from exactly one place, `selftest()`, with
`repo = os.path.join(tmp, "repo")` where `tmp = tempfile.mkdtemp(...)` two lines
above; the helper's environment has `GIT_INDEX_FILE` popped. So it cannot reach the
shared index today.

**But nothing ASSERTS that.** A future caller passing the real repository root —
or a refactor that hoists the helper — turns line 279 into a **1,187-file directory
sweep of the shared tree**, which is L-12, twice. The selftest cannot catch it,
because the selftest is the only thing that calls it correctly.

**REQUIRED, and it is one line:** `_build_control_repo` must **assert its `root` is
inside a temp directory and is not the Certonomous root** before it runs `add -A`.
**Not a blocker on the clearance** — the instrument's output is believable now —
but it is owed, and it is logged here rather than left in a message. *(A lane slot
is at the cap; this is queued, not forgotten.)*

## 3. THREE CORRECTIONS THE LANE MADE TO MY OWN BRIEF. ALL THREE ACCEPTED.

**This is the fourth lane to refuse a premise I wrote, and the fourth to be right.**
Recorded together so the pattern is visible rather than buried.

**3.1 I TOLD IT TO USE `git ls-files` AND THAT WOULD HAVE CRIPPLED THE INSTRUMENT.**
My brief said *"use `git ls-files` for the tracked walk"*. It refused and measured
the cost: at HEAD `57de4025`, `git ls-tree -r HEAD -- verification docs` lists
**565** tracked `.md`; `git ls-files` lists **464**. **The shared index hid 101
tracked files — 18 % of the population — from any sweep that asked it.**

**An instrument for worktree staleness built on the index would have been blind to
exactly the files most likely to be stale.** The lane's own first measurement was
wrong for this reason and it retook it and said so. **My error, and it is the same
error my own board warns about in bold three paragraphs up: the shared index lies,
and I wrote a brief that trusted it anyway.**

**3.2 The population is 569 and moving, not 557; `docs/LAB_STATE.md` was already
repaired** by the time the sweep ran, and `RUN_STATUS_EVIDENCE` is a `.md`. My
figures came from `1251a015` and had already decayed. **L-307's point exactly: the
gap is non-stationary in size AND direction.**

**3.3 D480 IS ALREADY ON SANAA'S DESK FOR THIS EXACT CLASS, AND I VERIFIED IT
MYSELF RATHER THAN RELAY IT.** `docs/DOCKET.md:845` at HEAD reads, in terms:
*"wiring into `check_harness` or any gate is **NOT authorized** ahead of the
ruling. Owner: **Sanaa**."* **The lane therefore did NOT file a rival proposal** —
it made its document evidence FOR D480 and wrote the script to default to exit 0
with `--strict` opt-in. **That is the correct reading of rule 9 and I am endorsing
it explicitly**, because the tempting move was to file a second instrument and let
two proposals compete for one ruling.

## 4. A CORRECTION TO MY OWN FRAMING, AND THE LANE'S VERSION IS SHARPER

I briefed this as *"a staleness defect class has reached a CHARTER"* — implying a
discovery. **It is not one.** The mechanism is **`L-253` (2026-08-23, verification)**
with **`L-307`** on non-stationarity, and `check_docket_reconciliation.py` already
names it for docket rows.

**The lane's replacement finding is better than mine and I am adopting it:**

> **L-253 is still producing fresh instances. Five of the six files still `BEHIND`
> were put there by commits made AFTER L-253 landed.**

**A lesson that keeps producing new instances two days after it was learned is a
lesson that was never mechanised.** What this item genuinely adds is **scope** —
the mechanism reaches a **charter** and a **frozen pre-registration**, single-owner
documents where L-253's concurrent-writers framing does not apply — and
**mechanisation**, a repeatable graded sweep with planted and mutation controls.

## 5. WHAT THE LANE COULD NOT VERIFY, CARRIED FORWARD RATHER THAN DROPPED

1. **The route is INFERRED, not observed.** No command transcript of the eleven
   commits survives on this box. Three converging lines make
   `git show HEAD:<path>` → append → `hash-object -w` → `update-index --cacheinfo`
   the only consistent reading — every `BEHIND` copy is byte-identical to an
   **ancestor commit's blob**, `ctime == mtime` on all seven (**no inode replaced,
   which is what refutes the concurrent-overwrite race, since an overwrite sets a
   new mtime AFTER the commit it lost**), and 11 of 11 unlanded commits are pure
   appends. **But nobody was watched doing it, and the record says so.**
2. **`cases/` — 225 tracked `.md` — was not swept at all**, nor anything untracked
   or non-`.md`. **A clean report is not a clean repository.**

## 6. THE REPAIR, AND WHY IT IS A RESTORE AND NOT A REVERT

Only cfd's own file was touched: `verification/campaign/F11_CONVERSION_PREREGISTRATION.md`,
disk blob `00d62c82` at 60,016 B against HEAD blob `fd34c3b0` at 65,909 B, with
`cmp -n 60016` identical — **so HEAD adds 5,893 B that have no counterpart on
disk.** The proof was re-taken **in the same shell invocation as the write**, and
`hash-object` afterwards equals the HEAD blob.

**A strict prefix carries no information that is not already in HEAD**, so writing
the HEAD blob over it destroys nothing. That proof is what satisfies rule 10's
*"inspected, never reverted"* rather than bending it. Done with
`git cat-file blob > file` — **no `checkout --`, no `reset --hard`, no `stash`, no
`clean`** — and **not re-committed**, per
`check_docket_reconciliation.py`'s own guidance. **AMENDMENT 2 — the amendment that
WITHDRAWS a "Sanaa's directive, verbatim" attribution — is now readable on disk.**

**Nine files were left untouched and none is cfd's**: six `BEHIND` (five
ansys-verification, including their own charter stopped at v1.2 with 24,508 B
missing; one verification), one `DIVERGENT` (ansys-verification `CASE_MAP.md`) and
two `AHEAD` (heat-transfer). **The `AHEAD` and `DIVERGENT` files carry bytes that
exist in no commit — the strict-prefix proof does not apply and they must NOT be
restored.** **Routing is the chief's, not cfd's.**

## 7. ONE OPEN DOCKET CONDITION THAT MAY ALREADY BE SATISFIED — **VERIFY**

`docs/DOCKET.md:845` records that `check_board_reconciliation.py` *"exits 4 on the
live tree until cfd repairs the doubled `## cfd` heading from `fe065ca6`."*

**Measured by me at HEAD just now: `docs/LAB_STATE.md` carries exactly ONE `## cfd`
heading**, at line 4559, and seven top-level headings in total. **So either the
doubling was already repaired or that clause is stale.** I did not re-run
`check_board_reconciliation.py` and I am not claiming the exit code moved — marked
**VERIFY** and left for whoever owns D480's disposal. **Flagged because a docket
row that names cfd as the blocker should not sit open if cfd is no longer blocking
it.**

## 8. COST

**ZERO COMPUTE**, for the instrument, the sweep and this clearance alike. **No
`docs/COST_CALIBRATION.md` row is owed for a records-and-instrument item, and an
empty row would be noise.**
