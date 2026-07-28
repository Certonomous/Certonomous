# Lessons

Process rules earned from real incidents on this project. Each entry states the
rule, the incident that produced it, and how to apply it. Rules are added only
after something actually went wrong or was actually caught — not from theory.

---

## L-1. Verify docket entries against `git log` before investigating

**The rule.** Before starting any docket or queue item, check the repository
history for work already done on it. Treat the brief as a description of intent,
not a description of current state. If `git log` contradicts the docket, the
commit wins — then correct the docket.

**Why.** On the night of 2026-07-27 the instance died at ~05:12:56. A large
amount of work had landed in the preceding ~90 minutes and never made it into
the operator's notes. **Three of five docket items were materially stale:**

| Item | Docket said | Repository said |
| --- | --- | --- |
| TMR NACA 0012 drag | "suspected missing viscous term" — open | Already **refuted and fixed** in `6606434` at 03:38, 94 min before the crash |
| DAFoam shape gradients | "3 of 8 components disagree at 11.9 and 11.6 percent, one sign-reversed at index 6" | Superseded by `b4662e1`: **no sign flips**, spread 0.7–8.2% (dCD), 4.52% in norm |
| Pressure slices | "regenerate every image" | Already regenerated at 03:50; **exactly one** image was genuinely stale |

Acting on any of those at face value would have burned hours re-deriving settled
results, and — worse — a blind "regenerate everything" pass on the pressure
slices would have **buried** the single genuinely stale image in a wave of
no-op rewrites, making the real defect undetectable.

**How to apply.**
1. `git log --oneline --grep=<topic> -i` and read the commit *bodies*, which on
   this project carry the measured numbers.
2. Check artifact mtimes against the commit that supposedly produced them.
3. Where the docket and the repository disagree, **report both** and say which
   artifact each figure came from. Do not silently pick one.
4. An item that turns out to be already done is a completed item. Say so and
   pull the next one; do not manufacture work to justify the entry.

**Corollary — the same applies to numbers quoted in a brief.** The operator
quoted a motorBike peak Cp of 0.8897; the published record said 0.8892. Both
were right: identical raw peak `p_max = 100.08748`, the 0.0524% gap being
exactly the `p_inf` normalisation. Reconciling and naming both sources took
minutes; picking one silently would have been a fabricated reconciliation.

---

## L-2. Never trust a verifier's own success report

**The rule.** When a tool reports that it verified something, re-derive the
result independently before relying on it. A verifier's self-assessment is a
claim, not evidence.

**Why.** The ledger backup script reported `✓ Backup complete ... verified` on
every run while silently discarding 122,800 of 184,237 rows — 67% of the ledger
— because it truncated at the first unparseable line (line 61438, a third of
the way in). All three rotated snapshots held the same truncated file
(`a04f924`).

Applying this rule on 2026-07-27 immediately paid: re-auditing the ledger by
hand after a "successful" backup surfaced **55 previously unknown duplicate
indices** at 186,838–186,893, caused by a second runner launched on top of a
live one at 05:11 (`f198cf4`).

**How to apply.** Recompute the headline figure from the raw artifact — row
counts from the file, checksums independently, force splits from the solver's
own log rather than a parsed summary. If a fix is claimed, construct the failure
case and confirm it now behaves.

---

## L-3. A negative result is a result; an untested hypothesis is not a refuted one

**The rule.** Report failed experiments with their measured numbers. But
distinguish carefully between *tested and refuted* and *the experiment did not
run properly*. Only the first is a finding.

**Why.** The NACA 4412 finer-rung re-mesh was meant to test whether the ladder's
non-monotonicity was a meshing defect. The attempt drove layer coverage from
58.3% to 4.36% — the opposite of intended. That does **not** refute the
hypothesis; it means the hypothesis is still **untested**, because the
better-resolved mesh the test required was never produced. Claiming refutation
would have been claiming a result that does not exist.

The run was not wasted: it produced a real incidental finding — **Cd is
essentially invariant to boundary-layer coverage on this rung**, moving 0.02%
(0.0183291 to 0.0183329) across a 13-fold collapse in resolved boundary layer.
That result partly undercut the original hypothesis and was worth more than the
test itself.

**How to apply.** State what was measured, what it does and does not establish,
and which of the three outcomes a follow-up experiment can distinguish. Design
the follow-up to change one variable so the result is decisive either way.

---

## L-4. Absence of an error message is not absence of the error

**The rule.** When diagnosing a failure, establish whether the failure mode
would have been *capable* of logging itself before treating silence as evidence.

**Why.** The 2026-07-27 outage left no OOM kill, no panic, and no lockup message
anywhere in the previous boot — which initially argued against memory
exhaustion. It was memory exhaustion. With zero swap the box livelocked in
direct reclaim before the OOM killer completed, and `journald` could not
allocate the memory needed to record the event. The last `sar` sample (05:10:03)
showed 460 MB free with **112.90% of RAM committed** and reclaim scanning at
~10x the daily average.

A second instance of the same trap in the same incident: logging stopped at
05:11:42, which looked like the moment of death. The filesystem showed 126 files
written *after* that, the last at 05:12:56 — the machine ran 74 more seconds.
The log gap was simply a quiet window with no scheduled logger due, not a
failure.

**How to apply.** Cross-check against a channel with a different failure mode —
filesystem mtimes, `sar`/`sysstat` samples, artifact contents. Ask "if this had
happened, what would have recorded it, and was that recorder alive?"
