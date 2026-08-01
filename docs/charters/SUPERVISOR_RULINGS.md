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
