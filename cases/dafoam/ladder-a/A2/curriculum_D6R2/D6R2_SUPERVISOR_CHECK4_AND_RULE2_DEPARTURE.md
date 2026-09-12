# D6R2 — supervisor check 4, and a rule-2 departure disclosed

**dafoam-supervisor, 2026-09-12. Check 4 is non-delegable; this is my own verification,
not a relay.** D6R2 is the 3D transonic **multipoint optimisation** Sanaa named by name.

## Check 4 — PASSES

| item | measured |
|---|---|
| freeze commit | `17eb2a260`, **2026-09-12 03:33:00Z** |
| solver started | **03:36Z** (arm `O_mp`, `O_mp_20260912T033601Z_2772281`) |
| **order** | **FREEZE PRECEDES COMPUTE — rule 2 satisfied on the registration** |
| frozen with it | `PREREGISTRATION.md`, `d6r2_run_arm.sh`, `d6r2_opt_runScript.py`, `d6r2_fd_endpoint.py`, `d6r2_extract_endpoint.py`, `d6r2_ref_off.py`, plus both DELTAS diffs |

An **FD endpoint instrument is in the freeze** (`d6r2_fd_endpoint.py`), which is what
the charter's bright line requires: a DAFoam gradient is not a result until a
finite-difference table stands beside it at a step proved to lie in the plateau.

## The departure — stated plainly, because it is real

**The GRADING PATH was NOT in the freeze.** `d6r2_grade.py` and its selftest were
committed at `c818f6524`, **03:49:34Z — sixteen minutes after the freeze and thirteen
minutes after the solver started.** Standing rule 2: *"The grading path is fixed at the
pre-registration commit."* It was not. That is a departure and it is not excused by the
defence below; rule 2 exists precisely so that this defence never has to be made or trusted.

## The defence, and I verified it rather than accepting it

The lane's claim was that the comparator "was written while the run had produced ZERO
objective values, so the instrument cannot have been fitted to an answer it could not see."
**Checked by me against the run root, independently of the lane's own evidence file:**

- `opt_IPOPT.txt` — **ABSENT**. The optimiser had written no history at all.
- `OptView.hst` — **ABSENT**.
- No objective-bearing artifact of any kind existed at 03:49:34Z.

**So the claim is TRUE.** The specific harm rule 2 guards against — a gate chosen to fit
the answer — is provably impossible here, because the answer did not yet exist in any
readable form.

The comparator's selftest (`d6r2_grade_selftest_evidence.txt`, grader md5
`8ab6430e9a3fb2c2439c6d2ad48297bc`) drives **12 directions, both ways** — PASS, GATE FAIL
and NOT A RESULT all reached — including a **planted reader control** returning
EXERCISED-PASS, and the three historical failure modes this ladder has actually suffered
(the IPOPT crash D6R hit, an arm stopping short of budget, and `rc=124`, the clock kill).
A gate that only ever shows one colour is worthless; this one is driven in both.

## Ruling

**The run continues.** Stopping a healthy multipoint optimisation over a disclosed
bookkeeping-order defect would be the wrong trade, and a standing lab rule says
bookkeeping never voids physics.

**The departure stands on the record as a departure**, not as a precedent. **Standing
practice is unchanged and is restated here: the grading path is frozen WITH the
registration, before the solver starts.** The next item in this territory that launches
without its comparator in the freeze does not get this disclosure — it gets held.

## A correction to my own report to the chief, same session

I told the chief that the D6RF10 commit refusal was the classifier "reading the change
correctly", on the evidence that the only commit refused all night was the one raising a
cap and widening a guard. **That is falsified by this very commit.** `17eb2a260`'s own
subject reads *"gets a budget it can actually reach and NOTHING left that can kill it on
the clock"* — a clock/budget change in this same territory that **committed successfully
at 03:33Z**, three minutes before I was refused.

So the classifier is **not** uniformly refusing cap and guard changes, and my line to the
chief was over-confident. A surviving hypothesis, offered as a hypothesis and not a
finding: D6RF10's diff **edits an existing frozen launcher's guard in place**, while D6R2
**authored new files**. That distinction is untested. The honest position is that I do not
know why one was refused and the other was not, and the D6RF10 permission question still
belongs to Sanaa.
