# Supervisor rulings, 2026-08-01

Katie delegated these while filming: "I'll let you decide. You are the global
supervisor." Each had been queued for her and each was blocking work. They are
recorded here so a ruling can be argued with later rather than inferred from
what changed.

Anything outward-facing is NOT ruled on here. Sending an entry, filing an
upstream report, or contacting a steward carries the company's name and stays
hers.

---

## R1. Monitor rule S7 is withdrawn

Ungated it fires on **68 of 106 archived steady logs and calls 65 fatal** —
runs whose results are on the record. It cannot separate the two logs of the
case it was written for (22 firings on the sick one, 20 on the healthy one).
Four tightenings were measured and none rescued it.

It currently survives on a gate the archive cannot replay, so its false-positive
rate is unmeasured and unmeasurable with the data held.

**A detection rule nobody can validate is worse than no rule, because it is
trusted.** Withdrawn, with the measurements kept beside it. S10, which names
exactly one log out of 383, stands.

## R2. The hump does not display a fleet it did not use

On the warm path the mesh and the solve are both restored and the elapsed time
computes to zero, so the act declares workers for work that never runs. Moving
the declaration earlier to fix the timing would invent a fleet.

The act shows no fleet on that path. This follows the standing rule against
implying anything was prepared in advance: a worker count is a claim about the
run, and a claim about a run that did not happen is the same defect as a band
that was never adjudicated.

## R3. Hardness is a property of the regime, not the shape

The camera rule bans toy geometries by naming shapes: sphere, cube, plate,
cylinder. The rehearsed sequence contains two cylinder acts, both passing
against published references at 0.77% and 0.70%.

A cylinder at Re 100 shedding a von Karman street, and a cylinder at Mach 8
carrying a bow shock, are not toy problems. The intent of the rule was to keep
trivial cases off camera, and both of these are graded against external
references the lab did not choose.

**Ruling: read hardness as the regime.** A bare cylinder in creeping flow stays
banned; an unsteady wake and a hypersonic standoff do not. The shape list stays
as guidance for what usually indicates a toy case, not as the test.

## R4. The credentials wall is regenerated, and loses its only VALIDATED row

The evidence is one-sided. 0.3041 is converged on 79,439 cells; the wall's
0.3219 is the coarser rung of the same ladder, superseded when the three-mesh
study landed. The refinement study is genuinely inconclusive, which blocks
VALIDATED by the rule working as intended. A frozen snapshot computed a day
before the study was last touched already reads SOLVER-BACKED 0.3041.

Every other surface in the lab already says 0.3041 and SOLVER-BACKED. The wall
is the sole holdout and the most public of the seven.

**A wall that contradicts its own generator is worse than a wall with no
VALIDATED row.** Regenerate.

## R5. The bump comparison carries its status or comes off the wall

It sits beside the verified flat-plate result with nothing saying its ladder is
non-conclusive, which makes the pairing read as two results of equal standing.
Two sessions flagged it and neither would edit a published claim.

Same principle as R4: disclose it where it is shown, or withdraw it from that
surface. Not both, and not neither.

## R6. Stage 1 is restated as a production-term inversion

The roadmap names beta on the omega-destruction term. DAFoam exposes a field
multiplier on the **production** term; the destruction term's coefficient is
the blended constant with no field hook. These are not equivalent.

**The goal is restated to what can actually be built**, and the destruction-term
variant is filed as its own item requiring a model patch. Building the
production-term version and calling it the roadmap item would be the quieter
and worse choice.

## R7. Settling scatter belongs to the numerical channel

Two filmed acts put settled-state scatter into the combined band while
reporting the input channel as unquantified. Settling spread is iterative
convergence noise, not input uncertainty.

**Move it to the numerical channel.** The alternative, showing it as an input
channel, would claim an input spread nobody assumed.

## R8. The high-lift entry is deferred, on submission not on cost

It can be prepared and cannot be sent: submission needs an account, a
participant identifier and a merge request, and all three sit on that item's own
forbidden list. Its rendered deliverable is priced at zero on top of a corrected
6,390 core-minutes.

**Deferred.** The grid importer the probe produced is kept and is the durable
value: every workshop grid this lab intends to read arrives in that format, and
it could read none of them before.

## R9. Not ruled on, because it is not mine

- **Filing the DAFoam report upstream.** Outward-facing under the company name.
  Prepared, reproducible from a fresh clone, waiting.
- **Submitting the closure entry.** Same. The draft, the disclosures and the
  eight prediction files exist.
- **The result-priority ordering.** Drafted to v1.0 for her to react to, with
  the open questions named. A declared priority over which numbers matter most
  is a statement about what the company is for.

---

## R10. A warm path spends nothing to the solver ledger

Added 2026-08-01, after R2 turned out to have a false premise on two of the
six sites it touched.

R2 assumed every warm branch clamps a zero-length interval to 1.0 s. On the
hump, the CRM and the M6 that is exactly what happens. On the Ahmed body and
the geometry study it is not: `elapsed` there is a genuine measured interval of
about 14 seconds. But that interval is the cost of **pacing a trace for the
viewer**, and it is spent to the ledger as `simpleFoam (14s)`.

A sixth site, never previously named, does the same thing one second at a time:
the refinement-ladder rung loop spends `max(1.0, ...)` across a zero-length
interval as `simpleFoam rung <tag>` for every warm rung.

So the defect is not six defects. It is one question asked six times, and it
wants one ruling.

**The ledger records compute this lab performed. Pacing a display is not
compute.** A warm path spends nothing to it, whether the interval it would
have spent is clamped, zero, or honestly measured at fourteen seconds. A
measured interval is not the test; what the interval paid for is.

This matters beyond tidiness. That ledger produces the core-hours figure on the
credentials wall, and a number that counts display pacing as solver time is
overstating the lab's own work in the one place it is most public. The
evaluation count survived its audit yesterday on exactly this principle: it
counts what ran.

The fleet numeral on those paths goes for the same reason R2 gave. A worker
count is a claim about the run, and a claim about work that did not happen is
the defect, not the clock that measured it.

### R10 correction, same day: the stake I gave it was false

R10 argued the fix mattered because "that ledger produces the core-hours figure
on the credentials wall." **It does not, and I should have checked before
writing it.**

There are two ledgers. `ComputeLedger` in `lab.py` is per-mission and in
memory, and is what these six sites spend to. The wall's core-hours come only
from `mega-batch/ledger.jsonl`, written in exactly one place, and **no workflow
act writes to it.** The wall's 239.259 core-hours never contained a second of
display pacing, and no published number needed restating.

Measured, the whole effect was **33 to 35 core-seconds per fully warm sweep**,
0.0093 core-hours, and **zero across the record, because no record accumulates
it.** The narration that printed the spend rounded both one second and fourteen
to `0` regardless.

So the ruling stands on its own principle and only that: a warm path spends
nothing to a solver ledger because pacing a display is not compute. It was
tidiness, not an overstatement anyone could have read, and the agent was right
to refuse to imply otherwise.

**Recorded because a ruling argued from a false stake is worth more as a
correction than as a quiet edit.** The reasoning was sound and the fact under
it was not checked, which is the same failure this lab keeps finding in its own
records.

### The opposite defect, found while applying it

`onera_m6.py:504`, the primal-plateau path. A genuine 498-second four-rank cold
solve raises before spending, so the transcript reads `solve stage 498 seconds`
and then `Spend 0 core-minutes`. The ledger **understates** roughly 33
core-minutes that actually ran.

R10 covers warm paths and deliberately leaves this alone. It is the more
serious direction of the two and it is now filed rather than fixed in passing.

## R11. The grading policy the regrades already follow becomes law, minus the clause that is not mine

Ruled 2026-08-04. The four-point shipped-vs-patched grading policy proposed in
`demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` under
`w4-carry-the-warp-patch-to-the-blocked-rungs` is **adopted** as stated: verdicts
grade against the shipped toolchain; patched numbers sit beside them as
diagnosis-confirmed-by-repair; a clearly-labeled patched grade is permitted only
with the paired-run controls on the record (bit-identical FD column, invariant
primal, `IDWARP_IMPORTED_FROM:` stamps); and point 4's replacement clause is
adopted exactly as written — a patched grade replaces a shipped grade only on an
upstream fix or on Katie's adoption of a fork, which is her decision and stays
on the decision-requests list.

The reason to adopt rather than wait: every regrade since 2026-08-01 already
follows this convention implicitly, and two supervisor sweeps (rotation patch,
A4 decomposition) verified regrades produced under it. A convention that is
already load-bearing and already audited is worse unstated than stated.

### R7 correction, 2026-08-05: the fold never considered the pending case

R7 folded settled-window scatter into the numerical channel. For a pending
study with no measured discretization band, that fold promoted the settle
scatter alone to the channel value, and `quantified: True` was stamped on a
channel whose dominant contribution was unmeasured — exactly the invention of
certainty the verification charter forbids. Found by a failing test the ruling
never ran; fixed in `4925fafb` by keeping the measured figure on the page as a
note while the channel stays unquantified. The ruling's principle stands for
completed studies; its blind spot is recorded here because a ruling that
creates a truthfulness defect owes the record the correction in its own file.

## R12. A canonical reference grid may carry a model-form band above the mesh gate, in writing

Ruled 2026-08-07, on the Cases family supervisor's escalation (C2): every family-N
cell fails the 70-degree non-orthogonality gate at 85.70 degrees, because the grid
is NASA's own TMR C-grid, whose far-wake skew is characteristic of the topology
the whole verification community standardises on.

The ruling: for MODEL-FORM BANDING ONLY, a grid that is the reference community's
own canonical verification grid is exempt from the lab's mesh-quality gate,
because the band measures inter-model spread on a fixed grid — it needs the same
grid, not a compliant one, and swapping in a home-built compliant grid would
break the family's comparability with the reference it exists to be compared to.
Three conditions, all mandatory: (1) the exemption is stated on the band artifact
itself with the failing number beside it; (2) physics gates and credential
verdicts still require compliant meshes — this exemption never travels to them;
(3) the exemption names its grid provenance (who published it, where). A quiet
exemption would have been L-30's defect wearing new clothes; this one is loud.

Consequence: the family-N regrade under the design gate is approved (~18
core-min, the supervisor's own filed estimate), with the exemption implemented
in the runner as a per-family flag that requires all three conditions.
