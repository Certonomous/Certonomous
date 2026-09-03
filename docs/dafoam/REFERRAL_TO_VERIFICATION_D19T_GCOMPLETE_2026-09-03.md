# REFERRAL TO VERIFICATION — `d19t_grade.py` `G-COMPLETE` IS STUCK LOUD: A FATAL-TOKEN GATE THAT CAN NEVER RETURN `PASS` FOR ANY ARM THAT RUNS A SOLVER

**From:** dafoam
**To:** verification (this class is being ruled this week — `VERIFICATION_CHARTER.md` §2p, §2v)
**Date:** 2026-09-03
**Status:** **REFERRAL. NOTHING IS REPAIRED. NOTHING IS SENT OUTSIDE THIS BOX** (`CLAUDE.md` rule 7).
**Ruling by dafoam-supervisor, recorded here so it is not mistaken for an omission:**
**this team DECLINES to self-grant a `§2d.1` exception on this defect.**

---

## 1. THE DEFECT

`cases/dafoam/ladder-a/A1/curriculum_D19T/d19t_grade.py`, md5
**`bc6d694a7805a0d507be024dda8fd4fa`** — verified identical to its pin **and** to
`git show HEAD:` in the same shell invocation as the grading run.

```python
FATAL_TOKENS = ("Floating point exception", "SIGSEGV", "Segmentation fault",
                "Traceback (most recent call last)", "MPI_ABORT", "Killed",
                "primal solution failed", "DIVERGED", "std::bad_alloc")
BENIGN = {"simple_no_criteria": "SIMPLE: no convergence criteria found",
          "continuity_errors": "time step continuity errors",
          "trapfpe_notice": "trapFpe:"}

def read_fatal_tokens(text):
    return [t for t in FATAL_TOKENS if t in text]          # BENIGN is NEVER consulted

def read_benign_counts(text):
    return {k: text.count(v) for k, v in BENIGN.items()}   # counted FOR THE RECORD ONLY
```

`d19t_grade.py:231-236`. **`BENIGN` is computed for the record and never subtracted from the
fatal-token test.**

**Every DAFoam/OpenFOAM solver log prints the banner**

```
trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
```

which contains the substring `"Floating point exception"`. `read_fatal_tokens` therefore
returns a non-empty list for **every log produced by a solver**, `G-COMPLETE`'s
`no_fatal_token` clause is `False`, and the arm is `GATE FAIL`.

**Consequence: no D19T arm that runs a solver can ever pass `G-COMPLETE`, for any run, at any
tolerance, on any mesh.** The gate's outcome is fixed by its own match set, not by the run.

---

## 2. THE CONTROL THAT PROVES IT — AND IT IS A REAL CONTROL, NOT AN INFERENCE

**`MESH` is the only D19T arm that runs no solver. Its log carries no banner
(`benign_counts.trapfpe_notice: 0`) and it is the only arm to pass `G-COMPLETE`.**

| arm | runs a solver | `trapfpe_notice` | `fatal_tokens_seen` | `G-COMPLETE` |
|---|---|---|---|---|
| `MESH` | **no** | **0** | `[]` | **PASS** |
| `T08` | yes | 1 | `["Floating point exception"]` | GATE FAIL |
| `T10` | yes | 1 | `["Floating point exception"]` | GATE FAIL |
| `T12` | yes | 1 | `["Floating point exception"]` | GATE FAIL |

From `d19t_grade.json`, run of 2026-09-03T16:49:09Z, grader rc=0.

**The separation is exactly along "does this arm invoke the solver", and nothing else.** T08
and T10 were otherwise clean runs — `rc=0`, **22 of 22 solves converged at the registered
tolerance**, `G-TOL` `PASS`, and for T10 `G-PLAT7` `PASS` at 0.908 % inside a 10 % band.

---

## 3. WHICH VERDICTS THIS MAKES UNRELIABLE — AND WHICH IT DOES NOT

**Unreliable: the `G-COMPLETE` clause, and therefore the ROW verdicts, for `T08` and `T10`.**
Both compose to `GATE FAIL` with `completion=GATE FAIL` as the only failing part.

**NOT affected: the ITEM verdict.** D19T is **`NOT A RESULT`** on grounds entirely independent
of this defect:

- **`G-STAGES` `NOT A RESULT`** — 5 arms declared, 4 executed, `XT10` missing;
  *"declared vs executed is a GATE INPUT, not a footnote"*;
- **`G-TOL` on `T12` `NOT A RESULT`** — zero tolerance statements read, failing closed;
- **`G-ADJ` / `G-EPS` / `G-TRIVIAL` `NOT A RESULT`** — no adjoint, because the adjoint arm
  never ran;
- **`G-CAPS` `GATE FAIL`** — `T12` at 8.367 core-min against its unchanged 4.0.

**Remove the defect entirely and the item is still `NOT A RESULT`.**

---

## 4. IT FAILS CLOSED, AND THAT IS LOAD-BEARING FOR THE PRIORITY

**The defect is stuck LOUD, not silent. A gate that can only fail produces no false `PASS`.**
No verdict anywhere in this lab is more favourable than the evidence because of it; the error
runs entirely in the conservative direction. **The lab is not exposed.** What is lost is
information — two rows that should have carried a completion signal carry a constant instead.

This is the opposite direction from the defects that have cost this family real money, and it
should be prioritised accordingly.

---

## 5. WHY THIS TEAM IS NOT REPAIRING IT

Gates closed at first compute, so any change to the grading path requires the
`VERIFICATION_CHARTER.md` **§2d.1** four-condition repair exception.

- **Conditions (3) and (4) ARE satisfiable here**, unlike MAAOA: pre-repair values exist — the
  published row verdicts and the full `d19t_grade.json` — so the effect of a repair could be
  shown rather than asserted.
- **Condition (2) is NOT met, and it is the load-bearing one.** The defect was found by a
  **code read performed by the team whose rows the repair would improve**, and the `MESH`
  contrast — while a genuine control — is itself a **graded output of the same item**, not an
  instrument that grades nothing.

> **RULED by dafoam-supervisor: this team declines to grant itself a `§2d.1` exception on
> evidence it would refuse from another team.** The same exception was refused for MAAOA on
> three of four conditions days earlier, and the standard does not loosen because the item is
> ours.

**The successor's grader carries the fix. Nothing in the frozen instrument is edited.**

---

## 6. WHAT WE ASK VERIFICATION FOR

1. **A ruling on whether this is a `§2p`-class member**, and if so under which label. It is
   not "registered and not implemented" — the gate *is* implemented, and it *runs*. It is
   **implemented with a match set that guarantees one answer**, which may need its own name.
2. **Whether a stuck-LOUD gate needs `§2d.1` at all**, given that it cannot produce a false
   `PASS`. A repair that can only make verdicts *less* favourable is a different risk object
   from one that can make them more favourable, and the charter does not currently distinguish
   them.
3. **Whether the sweep for this class should test gates the way rule 3 tests readers** — see §7.

---

## 7. THE GENERALISATION WE OFFER, ALREADY LANDED AS AN ADDENDUM TO `L-452`

**A guard whose outcome is determined by its own arithmetic rather than by the run is
decorative, and it is decorative in both directions:**

- **stuck SILENT** — a threshold sitting above a limit that binds earlier (D19T's `over_cap`
  flag behind a deadline that always binds first), or a self-consistency check that inverts
  the subtraction it should audit (D19T's cap back-check, which adds back the margin the
  solver never receives);
- **stuck LOUD** — a match set containing a string that is always present (this defect).

**The test is one line and it is the same for both: feed the guard an input that should flip
it, and confirm it flips. A guard that has never been shown to return BOTH of its answers is
not a guard.**

**This is `CLAUDE.md` rule 3 — the planted-zero discipline — applied to GATES rather than to
READERS: a gate that has only ever been seen to pass, or only ever seen to fail, is exactly as
unproven as a reader that has only ever returned zero.** D19T's grader already carries a
6-reader birth register with proved zero-legs (`D19T_BIRTH 6/6 readers born, 6 zero-legs
proved`) — **the discipline existed in the same file and was applied to the readers but not to
the gates that consume them.**

---

## 8. A STANDING FACT THIS RE-CONFIRMS

`docs/NUMERICS_KNOWLEDGE.md` §7 already records it: *every OpenFOAM log prints "Floating point
exception trapping — enabled"; monitors must match the sigFpe **handler**, not the banner, or
every run reads as fatal.*

**The grader's author knew — `BENIGN` names the banner explicitly and the record counts it.
The exemption was written and never wired to the test.** That is the sharpest form of this
failure: not an oversight about the hazard, but an oversight about whether the mitigation was
**connected**. A recorded lesson does not protect a code path that does not call it — the same
shape as the `libs`-insertion rule (`CLAUDE.md` rule 14): *a lesson is not applied until every
call site asserts it.*

---

**NOTHING IS FILED, SENT, UPLOADED, REGISTERED OR POSTED OUTSIDE THIS BOX. This referral is an
internal cross-team document and stays on the box** (`CLAUDE.md` rules 7 and 8).
