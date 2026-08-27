# PROPOSAL to the verification team — re-measure before you amend

**STATUS: PROPOSAL. NOT ADOPTED. NOT A STANDARD. NOT SENT.**

This file sits in `docs/standards/` beside real standards and is **not one**. Nothing in it
binds anybody. It is a draft for the verification team's consideration, and **routing it to
verification is the chief's relay — not this lane's and not the cfd Owner's.** `CLAUDE.md`
rule 7: submissions are parked; nothing is sent, filed, posted or registered outside this
box, and readiness never slides into sending. Adopting a lab-wide clause is verification's
call, and retiring or creating a standard is reserved to Sanaa.

- **Proposed by:** cfd-supervisor (Owner of `docs/standards/COMMIT_SIZE_GUARD.md`), drafted
  by cfd lane G3, 2026-08-27.
- **Scope of the ask:** one clause, applied lab-wide.
- **Precedent in force today:** `COMMIT_SIZE_GUARD.md` AMENDMENT 5 (v1.5), which binds
  amenders of that one guard. This proposal asks whether it should bind everywhere.
- **Revised 2026-08-27 to the stronger two-limb form** after AMENDMENT 4 was found to
  violate itself (see "The near-miss" below). Verification should rule on the version the
  Owner actually wants, not on the weaker one it superseded.

---

## The defect

A guard or comparator earns trust by carrying a **measured false-positive rate**. Once it
has one, every later reader treats its refusals as calibrated. But the measurement decays
silently: an amendment changes what the instrument catches, and unless somebody re-runs the
measurement, the document still displays measured rows while its newest clause has never
been measured at all.

**That state is worse than an openly unmeasured guard**, because it is indistinguishable
from a measured one. Nothing in the artifact tells a reader which clauses were measured and
which merely inherited the credibility of the ones that were.

## The evidence, from one guard's three amendments

- **AMENDMENT 2** went looking for its own clause's error rate and found `LOGS` at
  **0 true / 14 false** on 200 real commits. It did not have to look. Nothing asked it to.
- **AMENDMENT 3** exists *only* because AMENDMENT 2 looked. Sanaa's ruling exempting
  `verification/runs/**/log.*` rests entirely on that 0/14 split.
- **AMENDMENT 1's before and after rows were identical** — a zero delta on the sample —
  while its real effect (forward exposure falling from 64 tracked paths to 14) was invisible
  to the sweep. So the measurement matters even when it moves nothing, and a zero delta is a
  result rather than evidence that the work was unnecessary.
- **The instrument that produced all of it was never filed.** It lived in the scratchpad,
  which is temp-only and is wiped (rule 13, L-186). AMENDMENT 3's author had to reconstruct
  it from one line of prose and then prove the reconstruction by reproducing a recorded row
  before being allowed to report a new one. That is the cost of an unfiled instrument, paid
  once and avoidable forever after.

Three amendments, three measurements, **zero rules requiring any of them.**

## The near-miss, which is the sharpest evidence of all

`COMMIT_SIZE_GUARD.md` AMENDMENT 4 made the sweep a binding precondition on every amendment
to that guard — **and then shipped without running it.** Its commit touched two documents and
no guard code, recorded no rows, and so violated its own clause on the day it landed. The gap
was found by a reader who was not its author.

The obvious repair was to narrow the clause to *"any amendment that changes guard behaviour"*.
**That was rejected**, because it makes the precondition fire only when the amender
**classifies their own change** as behaviour-changing. *"My change is text-only"* is precisely
the self-assessment this lab refuses everywhere else, and an amender who miscategorised a real
behaviour change would be exempted by the very clause meant to catch them.

**The rule was strengthened instead of narrowed**, and AMENDMENT 4's gap was then closed **by
running the instrument**: the guard blobs before and after were shown byte-identical and the
sweep rows identical across all 200 commits in every recorded field. AMENDMENT 4 satisfies the
rule **because it was measured to have changed nothing, not because it was excused.** That
distinction is what this proposal is really asking verification to adopt.

## The proposed clause

> Any guard or comparator that carries a **measured false-positive rate** must have that rate
> **re-measured under the amended code before an amendment ships**, with the rows recorded in
> the amendment. Both rows must be produced from **committed blobs**, over the **same** frozen
> sample, in one process — never from a worktree — and the instrument must be **filed in the
> repository**, not in scratch.
>
> **The precondition applies to EVERY amendment, without exception. What varies is not whether
> the sweep runs, but what it must show:**
>
> 1. **An amendment that changes behaviour** records the before/after rows with the per-clause
>    split and an explicit statement of which outcomes moved and which did not.
> 2. **An amendment that claims to change no behaviour records the rows too, and they MUST BE
>    IDENTICAL — commit-for-commit, clause-for-clause. That identity IS the evidence for the
>    "text-only" claim.** A differing row means the amendment changed behaviour its author did
>    not know it was changing, which is precisely the event worth catching.

**There is no self-classification exemption, and that is deliberate.** A clause that exempts
whatever the amender calls text-only delegates the gate to the person it is gating.

Three riders the cfd precedent found necessary, offered with it:

- **The precondition is about the DELTA, not about hitting a rate.** No threshold is
  implied. A future amendment may legitimately raise a refusal rate; what it may not do is
  ship without knowing what it did.
- **The sweep is a floor, not a ceiling.** A fixed sample cannot see forward exposure, which
  is where AMENDMENT 1 actually acted. Running it is the minimum, not the whole job.
- **An identical row is a result, not a formality.** Under limb 2 the expected outcome is
  "nothing moved", and recording it is what makes the claim checkable by someone who was not
  there. An amender who skips it because the answer is obvious has skipped the only evidence
  that the answer was obvious.

## What it would cost an amender

With the instrument filed, **two commands and two rows in the amendment section.** On this
guard the whole re-measurement is `--guard-blob <sha>^` and `--guard-blob <sha>`, seconds of
single-core Python over 200 commits, well under one core-minute. **Limb 2 costs exactly the
same as limb 1** — that is the point: making the no-behaviour-change case cheap is what makes
"apply it to every amendment" a reasonable ask rather than a tax on documentation edits.

Without the instrument filed, it costs what AMENDMENT 3 paid: reconstructing a harness from
prose and proving the reconstruction before being allowed to use it. **That asymmetry is the
real argument for the clause** — the filing requirement is what makes the measuring
requirement cheap, and either alone is much weaker than both.

## Known objections, stated rather than answered

1. **It binds work that may not need binding.** Some comparators carry no published rate and
   would be untouched; whether that exemption is clean, or an invitation to publish no rate,
   is verification's to judge.
2. **A frozen sample ages.** Every fixed window drifts out of relevance under live traffic,
   and a clause that mandates one is mandating a decaying instrument. The cfd precedent
   handles this by making the harness **refuse** when its window stops resolving rather than
   silently sweeping a different sample — but refusing is not the same as staying relevant.
3. **This is a rule proposed by the team it would most constrain.** cfd wrote the guard,
   measured it, and is asking for the obligation to be made general. That is offered as
   evidence of good faith, not as a reason to skip scrutiny.
