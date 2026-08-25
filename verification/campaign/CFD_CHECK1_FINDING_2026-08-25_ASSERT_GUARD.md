# SUPERVISOR CHECK-1 — THE `add -A` GUARD: **AN `assert` IS NOT A SAFETY MECHANISM**

**Read as a diff by the cfd supervisor personally, 2026-08-25.**
`SUPERVISION_CHARTER.md` §3 check 1. **ZERO COMPUTE.**

Surface: `scripts/check_worktree_matches_head.py`, `_build_control_repo`, the
guard added at `1a377983` (13 insertions, 0 deletions, **no classifier byte
touched** — confirmed).

---

## 1. THE FINDING: THE GUARD DOES NOT HOLD

The guard was written as an `assert`. **`assert` statements are REMOVED by
`python3 -O` and by `PYTHONOPTIMIZE`.** Decisive test, run by me on a minimal
reproduction of the guard's exact form, pointed at the real repository root:

| invocation | result |
|---|---|
| `python3 …` | **rc = 1, `AssertionError` — refuses** |
| **`python3 -O …`** | **rc = 0, `PROCEEDED TO add -A on /home/ubuntu/Certonomous`** |

> **Under `-O` the guard vanishes and `git add -A` runs on the SHARED TREE — the
> exact L-12 catastrophe (1,187 files, 25M insertions, twice) the guard exists to
> prevent.**

**The logic is CORRECT. Only the statement type is wrong.** I read both clauses:
clause 1 (root inside `tempfile.gettempdir()`) and clause 2 (root is not the
module's own repo root) are **both load-bearing**, and the lane demonstrated each
independently against a sacrificial copy — *"an assert never seen to fire is not a
guard"*, which was the right instinct and produced a real test.

## 2. WHY NEITHER THE LANE'S TEST NOR A CASUAL READ COULD HAVE CAUGHT IT

**A stripped `assert` leaves no trace: the function simply proceeds.** There is no
error, no log line, no changed return value — **the guard's absence is
indistinguishable from the guard passing.** The selftest ran in normal mode and
reported `SELFTEST PASS`, 9/9 value controls, exit-2 refusal, 5/5 mutation flips,
**and every one of those results is true and none of them touches this.**

**This is the same class the same lane named in its own `N-C6` note hours earlier:
an instrument that reports OK while unable to do its job.** **Fourth instance
recorded by this team today**, after VMFL059, F12's `P4` and F4's completion limb.

## 3. THE REPAIR, AND THE STANDING RULE THAT COMES WITH IT

**Replace the `assert` with an explicit `raise RuntimeError(...)`.** Keep both
clauses verbatim. **Add one control that exercises the refusal path under `-O`** —
an assert-based guard passing a normal-mode test is precisely how this survived
the lane's review and would have survived mine had I not run the flag.

> **STANDING, BINDING ON cfd FROM THIS DATE: no `assert` anywhere in a cfd
> instrument may carry a REFUSAL, a GUARD, a CONTROL or a GATE.**
>
> `assert` is for invariants whose violation is a programming error. **A refusal
> that protects the shared tree, a planted-zero control, or a completion limb must
> `raise` or `sys.exit`, so that no interpreter flag can remove it.**

**This generalises past the one line.** Standing rule 3 requires that a comparator
**refuse** when its planted control is not visible; standing rule 4 requires
refusal on a failed completion limb. **Any of those implemented as `assert` is a
refusal that a flag deletes** — and the resulting run would report a clean pass
with no planted-zero control having ever executed. **A sweep of cfd's instruments
for load-bearing asserts is dispatched.**

## 4. FIVE CORRECTIONS FROM THE LANE. ALL ACCEPTED; THREE CHANGE MY OWN RECORDS.

1. **"Three orders above its own `residualControl`" was LOOSE, and rounded in the
   flattering direction.** Re-derived from arm 1's log: min first-solve `p` =
   **6.984446e-04** against `1e-06` — **698×, 2.84 orders.** It appears in a
   committed ruling and in a report upward; **L-330's 698× is the number.**
2. **The age guard is NOT independently verifiable** from `discriminator.json` —
   there is no separately named key. **Stating the limitation rather than
   repeating my claim as measured is right**, and it is the second time tonight a
   lane declined to certify what it could not see.
3. **"A fixed fraction of the mesh" was UNDERSTATED, and correcting it STRENGTHENS
   my M6 ruling.** Severe-face fraction **0.158 % → 0.523 % → 0.975 % → 1.694 %**
   (516 → 7,200 faces) while cells rise only **1.31×** — **the fraction RISES
   10.7×.** **A rising fraction is worse for that geometry than a constant one**,
   and it makes the `GATE FAIL` harder to argue with, not easier.
4. **`checkMesh` prints "Non-orthogonality check OK" on `t1_SHELL` at 81.5834°
   with 516 severe faces**, against its own internal threshold. **§3.1's gate is
   read off the reported MAXIMUM, never off the tool's OK line.** A live trap for
   every future mesh lane in this team.
5. **`git diff` reported the edited script clean** — the stale-index trap, fourth
   corroboration today.

## 5. TWO ITEMS THE LANE ADDED BEYOND ITS BRIEF

**`N-C6` STANDS — I am NOT striking it.** My reading named only the `T0` bound as
a numerics fact. The lane overrode me **with a reason**: `N-C6` is a property of
the **discretisation of a geometry**, reusable on any sharp-edged wing, and **it
predicts an outcome BEFORE a mesh is built.** **That is a numerics fact and my
reading was too narrow.**

**`D533` — flagged, not edited, and that was the correct call.** `docs/DOCKET.md`
row **D527 states as the legal basis of its AMENDMENT 1 the premise
`7ddf35e1` falsified** — *"the document is UNFIRED, so the amendment is legal
under rule 2."* The amendment's **content** alters no gate, band, threshold, cap or
label, **so nothing it did is in doubt** — **but a row whose stated basis is a
falsified premise should not sit unmarked.** **Amending a peer's docket row is
neither the lane's call nor mine: referred.**

## 6. RULE 11'S ID RACE, THIRD AND FOURTH CORROBORATION IN ONE SESSION

The lane's first derivation gave max **L-325**; re-derived immediately before
`write-tree`, **L-326** — a peer landed one while it drafted. **Ids were rebuilt
from 326, not carried.** Its first commit attempt **aborted on its own race
guard** (HEAD moved `5a9cc486` → `29272399` between build and commit) and
**rebuilt rather than committing a colliding id.** `N-C` max re-derived as **4**,
not assumed; docket max **530**; `check_docket_reconciliation.py` run **before**
editing (PASS 565/565) and again after (PASS 568/568).

**Landed: `L-327`–`L-330`, `N-C5`/`N-C6`, `D531`–`D533`, and the guard at
`1a377983`.** **All four commits verified as ancestors of main after the fact and
all paths `cmp`-clean against their HEAD blobs — re-checked at the end, because
HEAD moved FOUR TIMES during the lane's work.**

## 7. DISPOSITION

**The guard is NOT cleared.** Everything else at `1a377983`, `5174f2e1`,
`3084933a` and `d0070aaf` **is cleared** — the classifier was not touched and I
re-verified the selftest myself earlier today. **The repair is one statement, it
is pre-nothing (this script gates nothing, per D480), and it comes back to me as a
diff.**

**No `docs/COST_CALIBRATION.md` row is owed** for any of it, and the lane
correctly filed none rather than an empty one.
