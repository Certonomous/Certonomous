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
- **Precedent in force today:** `COMMIT_SIZE_GUARD.md` AMENDMENT 4 (v1.4), which binds
  amenders of that one guard. This proposal asks whether it should bind everywhere.

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

## The proposed clause

> Any guard or comparator that carries a **measured false-positive rate** must have that
> rate **re-measured under the amended code before an amendment ships**, with the
> before/after rows recorded in the amendment, including the per-clause split and an
> explicit statement of which outcomes moved and which did not. Both rows must be produced
> from **committed blobs**, over the **same** frozen sample, in one process — never from a
> worktree. The instrument must be **filed in the repository**, not in scratch.

Two riders the cfd precedent found necessary, offered with it:

- **The precondition is about the DELTA, not about hitting a rate.** No threshold is
  implied. A future amendment may legitimately raise a refusal rate; what it may not do is
  ship without knowing what it did.
- **The sweep is a floor, not a ceiling.** A fixed sample cannot see forward exposure, which
  is where AMENDMENT 1 actually acted. Running it is the minimum, not the whole job.

## What it would cost an amender

With the instrument filed, **two commands and two rows in the amendment section.** On this
guard the whole re-measurement is `--guard-blob <sha>^` and `--guard-blob <sha>`, seconds of
single-core Python over 200 commits, well under one core-minute.

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
