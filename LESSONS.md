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

## L-5. A dispatched agent will orphan its own long job — the supervisor must arm the collector

**The rule.** When dispatching an agent that launches a long-running solve, do
not tell it to "run detached and collect once" and leave it there. Either
instruct it explicitly to **block until its job finishes** (foreground run, or
`wait` on the PID) so it is still alive to collect, **or** arm your own
collector at the supervisor level. Never rely on a monitor the agent sets up
for itself.

**Why.** On 2026-07-28 this happened **three times in a row**, with three
different agents on three different tasks. Each launched its solve, set up a
background monitor, reported something like "waiting for the monitor to notify
me", and ended its turn — which killed the monitor. In every case the job was
still running correctly; the *result collection* was what died. Had the
supervisor not checked, three completed solves would have been silently lost.

It was caused by my own briefing line, "run detached and collect once; do not
sit in a tight polling loop" — written to avoid wasteful polling, and reasonably
read as "launch it and exit."

**How to apply.**
1. Prefer: tell the agent to run the job in the **foreground** with a generous
   timeout. Simple, and it cannot orphan.
2. Always: arm a supervisor-side watcher keyed on the **process name or an
   output artifact**, not on a PID captured at launch — see L-6.
3. When an agent reports "waiting" or "standing by", treat that as a **handoff
   to you**, not as work in progress. Verify what is actually running before
   believing either "done" or "in flight".

## L-6. Capture a PID from the thing you launched, not from the shell that launched it

**The rule.** `$!` and `pgrep -f <script> | head -1` both routinely return the
wrapper shell or a transient, not the long-lived worker. Key waits on a stable
identifier — the process *name*, a lock file the job itself writes, or an output
artifact appearing.

**Why.** Twice on 2026-07-28 a watcher fired within seconds and reported a job
"finished" that was in fact still running: once `$!` captured a wrapper `bash`
(so `runner.pid` held the wrong PID for the mega-batch), and once
`pgrep | head -1` grabbed a transient during process startup, making a 36-minute
mesh look like a 19-second crash. Both were caught only by checking `ps` before
believing the result.

**How to apply.** `while pgrep -f "<distinctive script name>" >/dev/null; do
sleep 20; done` is more robust than any captured PID. Then confirm the expected
output artifact exists before declaring success — a process exiting is not the
same as a job succeeding.

## L-7. "Converge harder" is not the default fix for gradient disagreement — first ask whether the plateau is a genuine fixed point

**The rule.** When a finite-difference check disagrees with an adjoint on a case
whose primal sits at a residual plateau, do **not** assume tightening the solve
will fix it. Check cheaply first — re-run the primal at 5x or 10x the iteration
count and compare residuals. If they are unchanged, the plateau is a genuine
fixed point of the discrete iteration, more iterations and tighter tolerances
cannot help, and the next lever is **mesh resolution or geometry smoothness**,
not solver settings.

**Why.** I formed this hypothesis as supervisor from two rungs: A1's primal
converged to 9.6e-9 and its shape derivatives verified at 11.43% with no sign
flips, while A5's primal plateaued at 2.3e-4 and its check gave 46.6% with 2
sign flips. Five orders of magnitude apart in convergence, four times the error.
I proposed that the adjoint, being exact only for the discrete converged state,
was being linearised about a non-solution.

**It was tested and refuted.** Adding `residualControl` at A1's 1e-8 bar,
tightening solver tolerances by one to two orders of magnitude, and extending
`endTime` from 1000 to 5000 to 10000 produced:

| metric | before | after |
| --- | --- | --- |
| p initRes | 2.2576e-04 | 2.0568e-04 (9% better, still nowhere near 1e-8) |
| total residual norm2 | 55.776 | 59.324 — **worse** |
| FD aggregate error | 46.64% | **46.21% — no material change** |
| components within 12% | 5 of 27 | 4 of 27 — slightly worse |
| sign flips | 2 | 3 — slightly worse |

Iterations 1000 through 10000 produced **bit-identical residuals**. This was
never under-iteration; it is a true fixed point, plausibly the curved duct's
secondary-flow structure, which a coarse steady solve cannot resolve away.

**I also asserted a mechanism that was wrong.** I argued that temperature, at
residual 41.16 of the 55.776 total, was polluting the state the adjoint
linearises about. For this case `transportProperties` carries a constant
viscosity with no temperature dependence and no buoyancy, and the objective is a
pure function of pressure and velocity — so temperature's adjoint row is
**analytically decoupled** from the rows the gradient depends on. It had no
channel into the result, in exact arithmetic, and tightening its solve
predictably did nothing.

**How to apply.** Two supervisory habits, not one:
1. Before prescribing "converge it properly", spend one cheap run establishing
   whether convergence is even *available*. A plateau that survives a 10x
   iteration increase is telling you something about the physics or the mesh.
2. **A correlation across two rungs is a hypothesis, not a finding.** I stated
   n=2 with more confidence than it earned, and attached a mechanism I had not
   checked against the case's own transport properties. The correct framing
   would have been "here is a candidate and here is the one-variable test",
   which is what the test itself ended up being — the framing around it was
   overconfident. Compare the discipline applied elsewhere the same night, where
   an n=5 correlation of −0.94 and an n=4 AUC of 1.0 were both explicitly
   labelled suggestive rather than established.

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

---

# PROCESS DOCTRINE (P1-P5) — how to act, not just what to know

These are standing rules for how work is conducted. Unlike L-1..L-7, which
record what went wrong, these govern the method itself.

## P1. Control before doubt

Before publishing a hypothesis that contradicts a report, run the cheapest
control experiment.

Earned three times in one session. The worst instance: C4 reported the TMR
medium rung unaffordable, citing a max aspect ratio of 26.4 million and a failed
checkMesh. I published the doubt that degenerate cells were holding the timestep
hostage — then ran `checkMesh` on the COARSE grid, which works fine and cheaply,
and found **20.6 million aspect ratio and the same failed check**. The control
took one command and refuted my objection outright. **A mechanism claimed from
one suggestive number is a draft, not a finding.**

## P2. Prediction-first runs

Any comparative study writes its prediction down before executing. Confirmations
and refutations count only if the prediction predates the data.

The RANS model sweep did this correctly: it stated that linear Boussinesq models
cannot produce secondary flow of the second kind at any coefficient setting, then
measured five of them at 5.5e-16 to 9.2e-16 — machine zero — against a nonlinear
model at 0.174. A prediction written afterwards would have been worth nothing.

## P3. Zero-compute checks first

Read the dictionaries, configs and git log before burning cores.

The F7a diagnosis cost **zero core-minutes**: `constant/turbulenceProperties`
said `simulationType laminar`, so no turbulence model had ever been active and
the entire model-comparison question was inapplicable. Reading one file
prevented a whole false investigation.

## P4. No orphaned runs

Every launched solve gets a collector armed **at launch**, and an agent may not
report "finished" while its PID list is alive.

This pattern recurred **three times before the rule was written and three more
after** — the ladder agent twice, the DPW agent once. Discipline demonstrably
does not fix it; see D12, which moves the responsibility into the launcher.

## P5. One change per rung

In any debugging ladder, exactly one variable moves per attempt, logged.
Compound fixes that work teach nothing, because the cause stays unattributed.

---

## L-8. The sign-flip diagnostic protocol

**The rule.** When mesh refinement **flips the sign** of an error rather than
reducing it, under-resolution is DISQUALIFIED as the sole cause. Refinement that
merely shrinks an error is consistent with convergence; refinement that reverses
it is not. The diagnosis must then walk this order, cheapest-and-most-often-
guilty first:

1. **The comparison itself.** Verify the reference definition before touching
   the solver: what exactly was measured, the initial geometry, the time origin
   and non-dimensionalisation, and how the experiment differs from the idealised
   setup (e.g. instantaneous versus finite gate release).
2. **Boundary and initial conditions.** Wall treatment, outlet, initialisation.
3. **Scheme sensitivity.** Interface-capturing controls, compression settings,
   discretisation variants.
4. **Time-step and mesh convergence, SEPARATED.** Refine each independently so
   their effects cannot alias into one another.

**Why.** F7a dam break deviated +13.6% mean on the surge front, and the coarse
mesh **undershot by −13.2%** while the medium overshot — a sign flip across
refinement. Turbulence was ruled out at zero cost (the case is laminar). The
remaining suspects are ordered above by cost and by how often each is actually
the culprit.

**The gate stays FAIL until the sign flip is EXPLAINED, not merely reduced.**
A number that moves closer to the reference for unknown reasons is not a fix.

**Resolution (D1, 2026-07-29).** Walked all four stages on F7a. Stages (a)/(b)
(comparison definition, wall treatment) were checked and ruled out. The actual
cause surfaced at stage (c)/(d): "front position" was defined as an alpha=0.5
crossing at an ABSOLUTE probe height tied to mesh resolution ("half the first
cell above the floor"), and the surge's leading toe is thin and height-sensitive
enough that swapping to the adjacent row of the SAME mesh's SAME solve swings the
answer by >40 percentage points and flips its sign — larger than the entire
cross-mesh deviation being investigated. Confirmed independent of timestep by
running mesh-only and timestep-only rungs at FIXED dt (separated per item 4): the
sign flip persisted unchanged with dt held fixed, refuting "adaptive timestepping
aliased into mesh refinement" as the cause; a 2.4x dt refinement at fixed mesh
moved the result by <1 percentage point. **Lesson generalises beyond F7a:** a
sign flip under mesh refinement is not automatically evidence of an unconverged
PDE solution — check whether the DIAGNOSTIC EXTRACTION itself (not the solve) is
mesh-resolution-dependent before concluding anything about physical/numerical
convergence. Full record: `demo-output/website/campaign/F7_runs/F7a_diagnosis.json`.

---

## D12 — collectors are structural now, not disciplinary

**The rule is no longer a rule.** `scripts/launch_solve.sh` is the only sanctioned
way to start a long solve, and it does four things the caller cannot forget:

1. Runs `case_preflight.sh` and **refuses to launch** if it fails.
2. Launches detached, capturing the real PID (not a wrapper shell — see L-6).
3. **Arms the collector at launch**, `setsid`'d so it outlives the caller's turn
   and writes a completion record itself.
4. Registers the job, so `launch_solve.sh --check` can test whether an agent's
   "finished" claim is actually true.

**Why this stopped being a discipline problem.** The
agent-exits-while-solver-runs pattern recurred **three times before L-5 was
written and three more times after** — the ladder agent twice, the DPW agent
once, the F4 agent once. Writing the rule down did not reduce the rate. The
responsibility therefore moves out of the agent's head and into the harness: an
agent may still forget, the launcher cannot.

Verified on three tests: the collector fires and records after the caller has
gone; a job that exits **without producing its expected artifact** is explicitly
flagged `MISSING ... process exited without producing it`, which is the case that
previously looked identical to success; and a case with a malformed field header
is **refused at the gate** rather than launched.

One of those three tests initially passed for the wrong reason — it tripped on a
bad argument rather than the preflight gate. A test that passes for the wrong
reason is not a test, so it was corrected and re-run.
