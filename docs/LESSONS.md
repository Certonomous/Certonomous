# Lessons

Process rules earned from real incidents on this project. Each entry states the
rule, the incident that produced it, and how to apply it. Rules are added only
after something actually went wrong or was actually caught, never from theory.

**This file is a record, not a handbook.** Each entry below is an attestation:
the incident is described as it happened, at the frame it happened in, and
entries are amended in place rather than rewritten. That is why the prose here
reads differently from `README.md` or `docs/USING_THIS_LAB.md`, and why a reader
should meet those two first. `docs/charters/README.md` and
`docs/MEMORY_ARCHITECTURE.md` section 5 explain how to read this one.

**Do not carry a count of this file into any other document.** It grows several
times a day. Take the reading instead, and say which of the three figures you
mean:

| What | Command | Value at `8cefb4e9` |
|---|---|---|
| Lesson blocks | `command grep -c '^## L-' LESSONS.md` | 85 |
| Distinct lesson numbers | derived from the same list | 84 |
| Highest lesson number | `command grep -oE '^## L-[0-9]+' LESSONS.md \| sort -t- -k2 -n \| tail -1` | L-85 |

The three differ. L-43 carries a second corollary block under the same number and
L-52 does not exist, so 85 blocks span 84 numbers reaching L-85.

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

## L-9. A directory count is a sample, not a state — I accused an agent on the strength of one

**What happened.** Twice I watched the shared caches shrink — 14 mesh / 8 solve
down to 4 / 2 at 18:26, then 23 / 18 down to 20 / 14 at 18:57 — and read it as
destruction. On the first occasion I sent warnings to two agents. One of them
came back with an account proving it had removed only its own entry and had
lost work itself. I was wrong, and had to say so.

**What was actually happening.** `save_mesh_to_cache` and its solve-cache twin
replace an entry with `shutil.rmtree(cache)` immediately followed by
`copytree`. Between those two calls the entry does not exist. Several acts
re-saving at once puts several entries in that window simultaneously, so a
directory listing taken at the wrong instant shows a cliff. The code is in fact
carefully guarded: `_cache_dir` refuses a degenerate key that would resolve to
the cache root, with a comment naming exactly the whole-cache-wipe failure I
had assumed was occurring.

The decisive check took ninety seconds — sample the counts three times. Solve
went 14 to 15 and 28 MB to 100 MB. Growing, not shrinking. One sample looked
like a catastrophe; three samples showed a rewrite.

**The rule.** A single `ls | wc -l` against a directory that concurrent writers
are rewriting measures the sampling instant, not the contents. Before treating
a count as evidence of loss: sample it again, compare bytes as well as entries,
and check whether the number recovers. And when the reading implicates somebody
else's work, get the second sample **before** sending the accusation, not after.

This is the same family as L-6. There the trap was reading a PID that belonged
to the wrapper rather than the solver; here it is reading a directory mid-write.
Both are one observation of a moving system, mistaken for its state.

## L-10. `pgrep -f` and `pkill -f` match the shell that is running them

**What happened, twice in one session.**

First: `pkill -f "chief_engineer.server"` to restart the control room. The
pattern matched my own bash command line, which contained that string, so the
shell killed itself. Exit 144, no restart, and for a moment it looked as though
the server had taken the shell down with it.

Second, and worse because it was silent: two background waiters built as

    while pgrep -f rebuild_caches.py >/dev/null; do sleep 30; done

Each waiter's own command line contains `rebuild_caches.py`, so each matched
itself and would have waited forever. The rebuild had actually finished — all
four bodies were cached and the log showed four `REBUILT` lines — while two
watchers sat there reporting it still running. I only noticed because I checked
the log directly instead of trusting the watcher.

**The rule.** A `-f` pattern is matched against every process's full command
line, including the one you are typing it into. Two habits fix it:

- Bracket a character so the pattern cannot match itself:
  `pgrep -f "[r]ebuild_caches.py"`.
- Better, when the target is a known program, match the executable rather than
  the command line: `pgrep -x python3` and then confirm via `/proc/<pid>/cmdline`.

And the check that would have caught it either way: **verify the thing you are
waiting on by its own evidence**, not by the watcher's opinion. The rebuild log
already said it was done.

Same family as [L-6](#l-6-capture-a-pid-from-the-thing-you-launched-not-from-the-shell-that-launched-it)
and [L-9](#l-9-a-directory-count-is-a-sample-not-a-state): a measurement that
silently includes the observer.

## L-11. A staged case that passes preflight can still encode an undocumented change of experimental variable

**The rule.** When inheriting a case directory left behind by an interrupted
agent, `case_preflight.sh` passing is necessary but not sufficient. Preflight
checks *internal* consistency — do the fields on disk match the model named in
`turbulenceProperties`, is the decomposition stale, and so on. It has no memory
of what a sibling case in the same ladder did, so it cannot catch a **silent
fork in methodology**: a case that is internally consistent but no longer
comparable to the rungs before it. That check has to be made by eye — diff the
new case's `constant/turbulenceProperties` and `0/` field list against the
previous rung's — every time a case is inherited rather than freshly built.

**Why.** The F5a cylinder Reynolds ladder ran Re 100 through Re 2000
deliberately laminar: the bare incompressible Navier-Stokes equations, no
turbulence model, because the whole point of the ladder is to measure what an
*un-modelled* 2D solve predicts against 3D reality, so any deviation can be
attributed to dimensionality and nothing else. The Re 3900 case, staged by an
interrupted agent instance before this session began, had `simulationType RAS`
with `kOmegaSST` and matching `0/k`, `0/omega`, `0/nut` fields — a complete,
internally consistent kOmegaSST setup that `case_preflight.sh` passed cleanly,
reporting `model: kOmegaSST` with every required field present.

Launching it as staged would have moved two variables in the same rung:
Reynolds number (the intended one) and turbulence closure (never decided or
logged). A deviation at Re 3900 measured against that run could not have been
attributed to dimensionality vs turbulence-model error vs the Re increase —
exactly the compound-change failure P5 exists to prevent, on the one rung of
this ladder ("the rung that matters") with the richest published reference
data to grade it against.

**How to apply.** Before launching an inherited case: diff its
`constant/turbulenceProperties` and `0/` field list against the most recent
prior rung in the same series. If they differ, that difference is either (a)
an intentional, undocumented decision the previous agent made and never wrote
down, or (b) accidental template contamination (see the false alarm this
avoided: `system/fvSchemes` in the same cases carries `div(phi,k)` /
`div(phi,omega)` entries inherited from an unrelated turbulence-model template
in *every* rung, including the laminar ones — those are inert and harmless
because no `k`/`omega` fields exist to trigger them, so a schemes-file diff
alone would have produced a false positive). Distinguish the two by checking
whether the file that actually switches physics (`turbulenceProperties`) is
the one that changed, not files that merely carry dead configuration. Revert
silently-forked methodology to match the established convention unless there
is a documented, deliberate reason to change it — and if there is, log the
change as its own decision, on its own rung, so it can be attributed later.

## L-12. `git add -A <path>` is a directory sweep wearing a pathspec

**What happened, twice.** The rule in this lab is never to stage a directory,
because several agents share one working tree. I broke it twice. The second
time cost the most: `git add -A demo-output/website/dafoam/` looked targeted —
it names a specific path — but it staged everything underneath, including
`polyMesh/owner` and `polyMesh/faces` files of 766,000 lines each. One commit:
**1,187 files, 25 million insertions.** `.git` reached 513 MB, in a repository
that gets pushed to GitHub.

Two agents independently reported this as a "shared index race between
agents". It was not a race. It was me. That is worth recording, because a
plausible systemic explanation was available and would have sent someone
hunting for a locking bug that does not exist.

## L-13. Extruding a wall-resolved 2D mesh into 3D can fail checkMesh's cell-determinant check — and coarsening the spanwise cell, not refining it, is the fix

**What happened.** F5a's Re=1000 cylinder ladder needed a 3D rung: take the
already-gated 2D O-grid mesh (radial first cell 0.00447D at the wall, for a
fully resolved, un-modelled laminar boundary layer) and extrude it along a
new cyclic spanwise direction to admit the Mode-B instability. The naive
choice — reproduce the literature's own spanwise cell size (Jiang & Cheng
2017, dz/D=0.05) exactly — built a topologically fine mesh (non-orthogonality
~1e-6, skewness 0.027, "Mesh OK" on every other check) that **still failed
checkMesh**: 33,600 cells, an entire near-wall ring at every spanwise
station, flagged for small cell determinant (<0.001).

**The counter-intuitive part.** The instinct is "the flagged cells are the
most anisotropic ones, so making them MORE anisotropic (a larger dz, i.e. a
coarser spanwise cell relative to the tiny radial first cell) should make it
worse, and refining dz should help." A dz sweep from 0.03 to 0.10, with the
in-plane mesh (radial/tangential counts, first cell, farfield) held exactly
fixed, showed the opposite: the minimum cell determinant rises
**monotonically with dz** — 0.03 gave 0.000166 (fail), 0.05 gave 0.000959
(fail, this is the literature's own value), 0.05085 gave 0.001013 (pass),
0.10 gave 0.007882 (pass, the widest/coarsest spanwise cell tested, and the
cleanest mesh of the sweep). **Coarsening the spanwise cell fixed it;
refining it made it worse.**

**Why (a hypothesis, stated as such, not solver-verified).** The flagged
cells sit in the near-wall ring, where the O-grid's inner and outer patches
are `arc` (curved) edges, not straight ones — every cell in that ring
carries a small built-in warp from that curvature. When the spanwise extent
(dz) is large relative to the in-plane cell dimensions, that warp is a
small fraction of the cell's dominant (spanwise) length scale and the
normalized determinant stays healthy. As dz is pulled down toward the same
order of magnitude as the radial/tangential extent, the warp is no longer
swamped by a dominant orthogonal direction and the determinant drops. This
is a property of extruding **any** curved-edge, wall-resolved 2D mesh into
a third dimension — it is not specific to this cylinder, this Re, or this
solver, and the next person who takes a 2D boundary-layer-resolved mesh
(an airfoil O-grid, a bluff-body C-grid, anything with `arc` or spline
patches at the wall) and extrudes it for a 3D/LES/DNS run should expect the
same failure mode if they reach for the finest "natural" spanwise cell size
without checking.

**The fix that does NOT work: spanwise grading.** Grading dz along the span
(finer at one end, coarser at the other, same total cell count) was tested
directly and made the determinant **worse**, not better (min determinant
dropped from 0.000959 uniform to 0.0000644 at a 4:1 grading ratio) —
concentrating cells anywhere necessarily thins the coarse end further for a
fixed total count. It is also physically wrong for a periodic/homogeneous
instability (no location along a cyclic span is more deserving of
resolution than any other), but it is worth knowing it does not even solve
the mesh-quality problem it might be reached for.

**How to apply.** Before extruding a wall-resolved 2D mesh for a 3D run:
sweep the intended spanwise cell size against `checkMesh -allTopology
-allGeometry` at fixed in-plane resolution BEFORE staging a solve, the same
way a mesh-convergence study is run — do not assume the literature's own
spanwise cell size will pass on your in-plane mesh just because it passed
on theirs (their in-plane mesh, near-wall first cell, and O-grid corner
geometry are not necessarily identical to yours). If it fails, try
coarsening the spanwise cell before concluding the in-plane mesh needs to
change — a spanwise-only fix preserves whatever control the in-plane mesh
was providing (here, byte-identity with a previously gated 2D case).

**Why the disguise works.** `git add -A` with no path is obviously dangerous
and everyone avoids it. With a path it reads as scoped, and the scope is real —
it just isn't small. The danger is not the `-A`; it is that the path is a
directory and directories accumulate solver output.

**The rule.** Name files, never directories. Better, skip the index entirely:

    git commit -m "message" -- path/to/file.py path/to/other.md

A pathspec-limited commit takes only those paths and ignores whatever else is
staged, which also makes it safe when other agents are committing concurrently.
Note the argument order — `-m` before the `--`, or git reads the message as a
pathspec.

**What to check before committing.** `git show --stat HEAD | tail -1`. If the
file count or the insertion count surprises you, it swept something. Neither of
my two sweeps was noticed at commit time; both were found later, by someone
else, looking at something unrelated.

**A mesh is not source.** It is regenerated from case dictionaries, which are
tracked. The same goes for `postProcessing/`, sampled `.xy` and `.raw` output,
and decomposed `processor*/` state. `.gitignore` now covers these, but ignore
rules only stop the next one — history keeps what it was given.

## L-14. A convergence claim must read the residual the gate actually tests

**What happened, twice on the same study.** OpenFOAM prints two residuals per
field per iteration: the **Initial** residual, before the linear solve, and the
**Final** residual, after it. `residualControl` gates on the *Initial* residual —
that is the one that measures whether the outer SIMPLE loop has converged. The
Final residual only says the linear solver did its job this iteration, which it
almost always does.

A hump perturbation point was carried forward as *"converged cleanly, k 1.67e-9,
omega 4.25e-11."* Both numbers were real. Both were **Final** residuals. The
Initial residuals for p, Uz and omega sat 10 to 150 times over the gate with no
decaying trend, and omega's was **rising** over the last 1200 iterations. The run
never printed `SIMPLE solution converged`. The same misreading had already
occurred on SpalartAllmaras in the same study.

**Why it is so easy.** The Final residual is smaller, sometimes by orders of
magnitude, so it looks like the better number. It is right next to the one you
want, in the same block of output, and it flatters the result. Nobody reading
`k 1.67e-9` against a `5e-7` gate thinks to ask which of the two residuals they
are holding.

**The rule.** Never assert convergence from a residual value alone. Check for the
solver's own statement:

    grep -c "SIMPLE solution converged" log.<solver>

If that string is absent, the run did not meet `residualControl`, whatever the
residuals look like. If you must read residuals directly, read `residualControl`
out of `fvSolution` first, confirm which fields it names, and read the **Initial**
residual for exactly those fields — a gate can also name a field the model does
not transport, in which case it can never fire at all (that one cost this lab two
RSM runs that ground on to 140,000 iterations while already converged).

**What it cost here.** A whole conclusion. "The response is strongly nonlinear
and the containment break lies between Delta 0 and 0.25" rested on that point.
With only the genuinely gate-met points, the break cannot be located at all — and
the two that did converge both sit on the *far* side of the experimental value.
The finding reversed, not merely weakened.

## L-15. Exit code zero is not convergence, and a solver can print success over garbage

**What happened.** A killed agent left an adjoint measurement unharvested. I read
its collector summary — `docker_exit=0, inner_exit=0`, peak memory uncensored
under its cap, no OOM — and reported to the owner that the adjoint had SUCCEEDED
at 79,560 cells. It had not. Both derivative solves returned PETSc
`ConvergedReason: -5`, DIVERGED_BREAKDOWN, with the residual norm collapsing to
about 1e-322 — denormal garbage — immediately before the solver printed:

    Residual tolerance satisfied, solution finished!

The process then exited zero. Every top-level signal said success. The answer was
numerical noise.

**Why this one is nastier than L-14.** There the misleading number sat beside the
right one. Here the software states the wrong conclusion in words. A residual that
collapses to 1e-322 satisfies any tolerance test written as `res < tol`, so a
breakdown can trip the success branch precisely BECAUSE it failed catastrophically.
Underflow reads as perfect convergence.

**The rule.** For any linear-solver-backed result, read the solver's own
convergence REASON, not its exit code and not its success message:

    grep -E "ConvergedReason" <log>     # PETSc: negative is failure, -5 is breakdown
    grep -c "SIMPLE solution converged" <log>   # OpenFOAM outer loop

And sanity-check the residual magnitude. A residual near machine denormal range is
not a converged solve, it is a collapsed one. Any residual many orders below the
tolerance deserves suspicion rather than satisfaction.

**What it cost.** A hardware recommendation, in the wrong direction. I told the
owner the memory wall was the binding constraint and extrapolated a box size from
it. The corrected picture is the opposite: the adjoint works at 63,920 cells and
breaks at 79,560 with over 4 GB of memory headroom still unused, so the
CONVERGENCE wall binds first in this range and **more RAM would not buy a larger
mesh.** I had it backwards, and I had it backwards because I trusted a process
exit code over a solver's own diagnostic.

## L-16. The pattern behind L-14 and L-15: I keep trusting the derived signal over the primary one

Three times in one session I reported a wrong conclusion to the owner. Each time
the mechanism was identical, and it is worth naming as a class rather than logging
a third instance.

| what I read | what I should have read | what it cost |
| --- | --- | --- |
| Final residual `k 1.67e-9` | the Initial residual the gate tests, and `SIMPLE solution converged` | a nonlinear-response finding and a containment window that do not exist |
| `docker_exit=0, inner_exit=0` | PETSc `ConvergedReason` — it was −5, DIVERGED_BREAKDOWN | a hardware recommendation, in the wrong direction |
| a diagnostic's printed line, `min(k) − deltaK = −4.2e-9  <-- negative means a coloring step can drive k negative` | the source that applies the perturbation — it is additive-only, so k never goes negative | a root-cause mechanism that was never real |

**The class.** In every case a *derived, annotated or summarised* signal sat closer
to hand than the primary evidence, and agreed with what I expected. The third is
the sharpest: that line was the diagnostic script's OWN arithmetic, with its own
interpretive comment attached, and I read the comment as a finding. A script that
prints `<-- negative means X` is telling you its author's hypothesis, not a
measurement of X.

**The rule, for me specifically.** Before reporting a conclusion drawn from
someone else's output, identify what the PRIMARY artifact for that claim is and
read it:

- convergence -> the solver's own convergence reason or statement, not an exit code
- what code does -> the source line that does it, not a wrapper's commentary on it
- a measured quantity -> the raw log or data file, not a collector summary

And treat agreement with expectation as a reason for MORE scrutiny, not less. All
three of these confirmed something I already believed, which is exactly why none
of them got checked.

**Credit where it belongs.** All three were caught by the agents doing the work,
each by going to the primary evidence I had skipped. That is the system working,
but it should not be load-bearing: a supervisor who ships three wrong conclusions
in a session is spending the team's attention on corrections instead of research.

---

## L-17. Reverting a decision is not the same as reverting its consequences

**The rule.** When a staged setup is found to encode a decision that must be
reverted (a turbulence model, a solver choice, anything with downstream
effects), reverting the decision itself is not enough. Every OTHER parameter
that was chosen *because of* that decision has to be individually re-examined
against the convention being restored to — not assumed innocent because "no
reason to distrust it." A partial revert produces a hybrid case that passes
every internal-consistency check (it is not lying about what it is) and
matches neither the old convention nor the new one, and nothing about
inspecting that one case will show you this. It only becomes visible when a
sibling case, built cleanly on the restored convention, gives a different
answer to the same question.

**Why.** The F5a cylinder ladder's Re=3900 rung was staged as kOmegaSST URANS
by an interrupted agent, caught by L-11, and reverted to laminar before
launch — turbulence model and 0/ fields fixed, and the mesh (n_radial,
n_tangential, first_cell, dt0) was deliberately left alone, reasoned as
"Re 3900-specific choices, not the turbulence-model fork, and there is no
reason to distrust them." That reasoning was sound in isolation and wrong in
context: the near-wall first-cell height had been sized for the URANS
staging's own y+-targeting formula, not this ladder's laminar
boundary-layer-resolving formula (`0.01*sqrt(200/Re)`), and the two formulas
disagree by 55% at this Re (0.003517 vs 0.002265). `case_preflight.sh`
passed the reverted case cleanly — `model: laminar`, every required field
present — because a mesh sized for the wrong solver is not a preflight-
checkable defect; it looks exactly like a legitimate engineering choice for
the case in front of you. The defect only surfaced when a THIRD rung
(Re=10,000, built fresh on the laminar formula in the same session) produced
a visibly different first-cell number for a comparable step, prompting the
question "why does this ladder now have two different near-wall
conventions" — a question that cannot be asked from inside any single case.

**How it was sized, not just asserted.** Counting mesh cells whose outer
radial edge falls inside an order-of-magnitude boundary-layer-thickness
estimate (`delta/D = C/sqrt(Re)`, C swept 1-5 to bound the estimate's own
uncertainty, since no precise cylinder-specific BL-thickness citation was in
hand — stated as an engineering estimate, not a literature value) shows the
effect is not cosmetic: at C=3, Re=1000's rung resolves the boundary layer
with 13 cells, Re=3900 SHOULD resolve it with 14 (the laminar-formula
convention keeps this roughly flat as Re rises, by design), but the mesh
that actually ran resolves it with only **10** — fewer than the lower-Re
rung before it, which is backwards from what a Re-consistent convention
should ever produce. The direction (coarser, not finer) is conservative for
any single result taken alone, exactly as first argued — but "conservative
for one result" and "comparable across a ladder" are different claims, and
only the second is what a ladder is built to deliver.

**How to apply.** When reverting a staged decision, first enumerate every
parameter the ORIGINAL (wrong) decision could plausibly have influenced —
not just the flag that names it. For a turbulence-model revert, that
list is at minimum: near-wall cell height (y+-target vs. resolved-BL
target), and possibly time-step (URANS and laminar can tolerate different
Courant numbers near the wall) and turbulence-model-dependent scheme
choices in fvSchemes. Check each one explicitly against the sibling
convention rather than inheriting it. If checking against a sibling isn't
possible yet (this is the first rung of its kind), that is itself the
signal to compute the intended-convention value independently — from the
formula, not from what shipped — before trusting what was staged.

## L-18. A sub-agent inherits your instructions only if you give them to it

**What happened.** An agent dispatched for a strictly no-compute literature review
spawned its own research fork. The parent's brief said, explicitly, do not run any
solver. That instruction was never passed down. The fork found solver scaffolding
already in the repository from a previous day, decided it was useful, and launched
it.

The job then ran for 57 minutes on a full core producing **negative drag** —
Cd −55.3, Cl −77.7 on a wing — because its force-coefficient normalisation was
still at placeholder values: reference density, velocity, length and area all
literally 1.0. Even had it converged, every number it produced would have been
meaningless. It was caught only because a *different* agent, checking resources
before its own launch, noticed a core it could not account for and traced it.

**Two failures, and the second is the interesting one.**

The obvious failure is that a constraint did not propagate. An agent that can
spawn agents is a supervisor, and a supervisor who omits a constraint has removed
it. Assume nothing is inherited: budget, no-compute status, commit discipline and
resource rules must be restated in every brief, however obvious they seem.

The subtler failure is that pre-existing scaffolding reads as permission. The case
directory looked legitimate — real scripts, real mesh, dated from earlier work —
and running it felt like using what was there rather than starting something new.
It was not. **A case existing on disk is not authorisation to spend a core on it**,
and half-configured scaffolding is exactly what gets left behind when someone
abandoned a case for a reason.

**What to check when you find a job you cannot account for.** Not just whether it
is running, but whether its *output means anything*. This one announced itself
through physics: no wing has negative drag. A quick look at the force coefficients
would have condemned it at any point in that 57 minutes, and nobody looked until
someone wanted the core.

**Resolution.** Stopped after verifying the coefficients were non-physical and the
normalisation was placeholder. The agent that found it attempted the stop, was
refused by the permission layer, and escalated rather than working around it —
which is the correct behaviour and worth as much as the catch.

## L-19. "Interrupted" and "diverged" look identical from outside — relaunch is the test that separates them

**The rule.** When a run stopped early and left no result, "it got interrupted"
is a *hypothesis*, not a finding. A diverged solve and a killed solve leave the
same forensic trace: a truncated log, a missing final artifact, no `End`. Do
not record the interruption reading — and above all do not recommend "just
re-run it" — until the alternative has been excluded. **The decisive test is
cheap: relaunch and compare the coefficient history against the original at
matching iterations.** Bit-identical values prove the failure is deterministic
and in the case setup; divergent values point at the environment.

**Why.** DPW8_V2's L4 (fine, 49,152-cell) rung was salvaged and recorded as
"INCOMPLETE, 1200/3000 iters (40%)... the solver process was killed mid-run",
with re-running named as the natural next step. It was relaunched. It
reproduced the original **bit-for-bit** — iteration 201: Cd −563.6550 in both
runs; iteration 401: Cd −332.8891 in both — and diverged again, having in
truth been diverged since roughly iteration 14 (peak excursion in the original:
max |Cd| = 53,437). The rung had never worked. The recommendation to re-run was
therefore guaranteed to fail, and it cost a second 3,388 s to discover that the
first 56 minutes had also been spent on a diverged solve.

**The second failure is the one that made the first invisible.** The salvage
report's evidence for "not settled" was "Cl swinging between roughly +0.40 and
−0.43 iteration-to-iteration." Those numbers are real — they are **columns 8-9**
of `coefficient.dat`. `Cl` is **column 5**, and its actual value there was
**−40.30**. Reading the wrong column converted a two-orders-of-magnitude
catastrophic divergence into a mild-sounding convergence wobble, which is
exactly why the interruption story looked plausible. This is L-16's pattern
(trusting a derived signal over the primary one) in a new disguise: the column
*header* is the primary source, and `coefficient.dat`'s column order must be
read from the file's own `#` header line every time, never assumed.

**Corollary — eliminate the obvious cause before believing it.** The natural
suspect for a finest-mesh-only divergence is mesh quality. Both candidates were
tested and both were eliminated: `checkMesh` returns `Mesh OK` for L4, and its
max cell aspect ratio (642.7) is *lower* than L3's (925.3), which converges
cleanly. Reporting "probably the mesh" without those two checks would have sent
the next investigator down a dead end. State what has been ruled out, not only
what is suspected.

**Corollary — a diverged run poisons its own diagnostics.** L4's y+ reads 113
*average* (max 164.8) against L3's 0.351 (max 0.496), on a mesh 4x finer where
y+ must be *smaller*. That is not a mesh-sizing problem to go fix; it is the
diverged velocity field feeding back into a derived quantity. In a diverged
solve, every derived diagnostic is downstream of the divergence and none of
them can be read as evidence about the setup.

---

## L-20. A validated template's robustness can live in a component you swap out, invisibly

**The rule.** When adapting a validated template (a tutorial, a prior case, a
reference setup) by substituting one named component for another, don't just
check that the substitute computes the right physics. Ask what ELSE the
original component was quietly doing for the case — safety margins, bounds,
fallback behaviour — that had nothing to do with the property you thought you
were choosing, and confirm the substitute still provides it, or that nothing
in the surrounding code was relying on it.

**Why.** `f4_swbli_warmup20` was adapted from OpenFOAM's own
`biconic25-55Run35` tutorial, which uses `thermo janaf` with `Tlow 100;
Thigh 10000;`. The adaptation switched to `thermo hConst` — a reasonable,
disclosed choice for a non-reacting flow at moderate temperature, made purely
on thermodynamic-fidelity grounds (constant Cp is adequate here; exact JANAF
polynomials for air were not readily at hand). Nobody was choosing a
bounding strategy at that moment; bounding wasn't the question being asked.
But `janafThermo::limit(T)` genuinely clamps `T` to `[Tlow,Thigh]` inside the
solver's own temperature inversion, while `hConstThermo::limit(T)` is a
documented no-op (both checked directly against the OpenFOAM 2606 source,
`janafThermoI.H` vs `hConstThermoI.H`) — and `rhoCentralFoam` never calls
`fvOptions` on the energy field either, so there was no second line of
defence anywhere else in the stack. The thermo-model swap silently deleted
the only thing standing between a single bad cell's energy and a SIGFPE in
Sutherland's `sqrt(T)`, and nothing in the case — not `case_preflight.sh`,
not a code comment, not the dictionary itself — said so. It looked exactly
like a legitimate, narrower thermodynamic simplification, because it was
one; the bounding loss was a side effect nobody was looking for.

**Why this is a different trap from L-11.** L-11 is about a fork in
methodology BETWEEN sibling cases in a series (Re=3900 quietly inheriting a
turbulence model Re=1000..2000 never used) — catchable by diffing the new
case against the previous rung. This is about a fork WITHIN a single case's
own lineage, between it and the validated template it was built from, in a
component whose job description (as far as anyone editing the case was
concerned) had nothing to do with the property that broke. Diffing against a
sibling rung would not have caught this — there was no sibling yet, and the
diff that would have caught it is against the TEMPLATE, on a property
(`limit()`'s behaviour) that isn't visible in the dictionary at all; you have
to know to go read the base class.

**How to apply.** When swapping a named component out of a validated
template (a thermo model, a turbulence model, a numerical scheme, a solver),
before trusting the swap:
1. Read what the ORIGINAL component's class actually does, not just what
   dictionary entries it consumes — a no-op override or an unused entry is
   invisible from the case files alone.
2. Ask explicitly: does anything downstream (the solver, another model, a
   function object) *depend on* a behaviour the original component happened
   to provide, even if that behaviour was never the reason it was chosen?
3. If the substitute drops that behaviour, either restore it through some
   other channel (here: a solver-level bound) and disclose the requirement,
   or confirm nothing downstream needed it and say so — don't just confirm
   the substitute is thermodynamically adequate and stop there.

**A second, independent finding from the same investigation, worth its own
note.** Fixing the thermo bound alone did not fully explain what was found:
tracing the bounded diagnostic solve to its persistently worst cell led to
discovering the mesh's radial grading was inverted — `blockMeshDict`'s
`simpleGrading` ratio, computed correctly for a 47-micron, y+~1 wall cell,
was applied to a hex block whose local grading direction (per
`blockDescriptor.H`'s vertex convention, v0→v3) ran from the farfield corner
to the wall corner, not the other way — so the fine cells landed at the
farfield boundary (which does not need them) and the actual wall cell came
out roughly 86x too coarse. `checkMesh` cannot catch this: a monotonically
graded mesh is geometrically valid regardless of which end is fine, and the
determinant/aspect-ratio/skewness checks are all direction-agnostic. The
only way it surfaced was by tracing where a bounded, instrumented solve's
own guard kept firing and checking THAT cell's actual size against the
design target computed independently from the intended y+. **The general
form: a grading-direction mistake in a mesh generator is silent to every
standard mesh-quality metric and only shows up as a resolution the flow
itself is unhappy with — trace failures to actual cell geometry, don't trust
that "the mesh passed checkMesh" means the resolution went where it was
designed to go.**


## L-21. `residualControl` can name a field the model doesn't transport, and the gate silently never fires

**The rule.** A convergence gate isn't just a number to read correctly — it
has to be pointed at a field the model actually solves for. Before trusting
(or blaming) a `residualControl` block, check that every field it names
appears in the model's own transported-fields list. If it names a field the
selected turbulence/closure model does not carry, the gate can never be
satisfied by definition, no matter how converged the run genuinely is.

**Why this is a different trap from L-14, not a repeat of it.** L-14 is
about reading the wrong *number* off the right field (Final residual
quoted where the gate checks Initial). This is about the gate watching the
wrong *field* entirely — the number being read doesn't matter because the
field being watched was never being solved for in the first place. Both
produce the identical outward symptom (a run that looks fine and never
gets a "SIMPLE solution converged" declaration), and both are catchable by
the same discipline of checking the solver's own statement rather than a
residual in isolation — but they have different causes and different
fixes, so conflating them would misdiagnose the next occurrence.

**What happened.** D5's three Reynolds-stress-model duct cases (LRR, SSG,
EBRSM) all had `residualControl { k 5e-6; omega 1e-10; }` — inherited
unchanged from the eddy-viscosity template the cases were built from. None
of the three RSM models transports `k` or `omega`; they solve `U`, `p`,
`epsilon`, and the Reynolds-stress tensor (printed per-component as `Rxx`,
`Rxy`, `Rxz`, `Ryy`, `Ryz`, `Rzz`), and EBRSM additionally solves `f`.
**The stop criterion could therefore never be satisfied by construction**,
regardless of how converged the run was. Two runs ground on toward
`endTime 500000` for over two hours of compute each, already converged
(LRR's own account: "Ux initial residual was 1.6e-12 by iteration
120,000"), before being stopped by hand with `stopAt writeNow`. This cost
real compute and nearly cost a correct result too: the honest path here
required someone to notice the mismatch and verify convergence manually
against the right fields, which is exactly what happened — the case
record already did this correctly, citing an Initial residual on the
right field before this lesson was written down. Re-verified from the raw
logs before being trusted (per L-14/L-16's own standing rule): all three
completed runs show Initial residuals of 2.9e-9 to 9.9e-9 on every field
they actually transport, tens to hundreds of times tighter than this
project's usual 5e-7 bar. The runs were genuinely fine. The gate was not
a gate.

**The fix, and the limit of the fix.** `residualControl` in all three
case directories now names the fields these models actually transport
(`system/fvSolution`, `D5_rsm_runs/{LRR,SSG,EBRSM}/`), for FUTURE runs of
these cases. The three completed runs were left untouched and are not
invalidated by the config change — they stand on the by-hand verification
against the raw logs, not on the (old or new) `residualControl` block,
and both the case files and `D5_RSM_RESULT.md` say so explicitly, so a
future reader does not mistake "the gate was fixed" for "the old runs
were therefore bad."

**This is checkable before any compute is spent, unlike L-14/L-15/L-19,
which are only visible after a run finishes.** A mismatch between
`residualControl`'s field names and the selected turbulence model's own
transported-field list is a static property of the case directory, not
something that requires reading a log. `scripts/case_preflight.sh` now
checks it: for each model in the same table `case_preflight.sh` already
uses to check that `0/` and `fvSolution/solvers` cover the model's
transported fields, it additionally checks that `residualControl` names
at least one of them — and fails preflight, before a single core-second
is spent, if `residualControl` names only fields the model doesn't carry
(the exact `{k; omega;}`-on-an-RSM-case shape that cost two hours here).
It does not require every transported field to be gated (a case may
deliberately gate a subset), only that the block isn't watching a field
set with zero overlap with reality.

## L-22. A failure attributed to a case must be checked against that case's own logs — attribution that "sounds plausible" is not provenance

**What happened.** F5c (the Driver & Seegmiller backward-facing step,
plain `simpleFoam`, no adjoint) was on record elsewhere as "OOM with huge
gradient blow-ups." Neither half of that phrase belongs to F5c. Its
meshes top out at 46,500 cells — far too small to plausibly exhaust a
30 GB host — it has no adjoint or DAFoam variant in the repo to produce a
gradient at all, and a repo-wide search of git log, every campaign
document, the docket, dmesg/journalctl, and the chief_engineer source
turned up no kernel OOM message, no solver abort, and no commit
connecting F5c to memory exhaustion. F5c's real, already-documented
failure is a converged-but-wrong steady RANS solve (reattachment length
off 4-12x, wanders under iteration count and algorithm). An extended
20,000-iteration run of the exact configuration the claim was attached to
finished NOT_CONVERGED, RSS flat at roughly 79 MB the entire time — no
memory event, confirming the claim's absence rather than its cause. The
likely source: B3 CBFS, a *different* case (a curved backward-facing
step, a genuine DAFoam adjoint run) that really does OOM and really does
produce `DIVERGED_NANORINF` NaN/Inf gradients, and shares enough of the
name — "backward-facing step" — that a handoff note written late in a
session had an obvious way to cross the two. Full trace in
`demo-output/website/campaign/F5bc_unsteady_statistics.md`, "2026-07-30
addendum," and the register entry in `NOT_PASSING_REGISTER.md`.

**Why this belongs next to L-1, L-2, and L-16, not as a one-off.** L-1
says verify a docket entry against `git log` before investigating it.
L-2 says never trust a verifier's own success report. L-16 names the
standing pattern across L-14/L-15: trusting a derived signal over the
primary one. This is the same family, one layer up — it is not a
number misread off a log, it is a *claim about which case a log belongs
to*, and it survived not because anyone checked it, but because it
sounded plausible and named a real phenomenon (this project genuinely
has an adjoint memory wall, Group 1 of `NOT_PASSING_REGISTER.md`) that
was simply attached to the wrong case. That is a more expensive failure
mode than a misread number, because it is invisible to anyone who trusts
the register instead of re-deriving the entries in it — and the owner's
own count stands at six convergence-masking instances and four bad
readings caught in one night before this one, several of which were a
claim propagating because nobody re-read the primary evidence. A failure
register whose own entries are not individually checkable against
primary evidence is not a register, it is a rumor with formatting.

**The standing rule.** A `NOT_PASSING_REGISTER.md` entry that attributes
a crash, an abort, or a resource failure (OOM, SIGFPE, SIGSEGV, a kernel
kill, an infrastructure event) to a named case must cite the primary
evidence that proves it happened on *that* case: the exact kernel
message, the solver's own FATAL/abort line, or the log path and
timestamp of the run in question. "Consistent with the pattern documented
for [other case]" is not sufficient on its own to name a case in a
crash/resource entry — it is fine as an explicitly-labeled inference (as
several Group 1 entries in this same register already do correctly for
`naca0015_sail_medium` and `naca4412_wing_coarse`, which say outright that
their logs do not themselves confirm OOM as the cause), but it must not
be silently upgraded to a flat statement of fact about the named case
the next time someone writes a summary of it. Convergence-failure and
wrong-answer entries (the far more common kind in this register) do not
need a kernel trace — the residual history or the physical result *is*
the primary evidence and is usually attached already. This rule is
specifically for the sharper, rarer claim that a resource or crash event
occurred, because that is the claim this incident showed can travel
without ever being checked.

## L-23. An optimiser always walks a correlation to the edge where it is least defensible — check the limit before trusting the optimum

**The rule.** Before a screening correlation is used as an objective in a
sweep, evaluate it at the physical limits of the design variable and ask
what the answer *must* be there. If the correlation does not reduce to the
right thing in the limit, the sweep's winner is the least trustworthy
point in it, because a minimiser walks straight to that limit. This is a
zero-compute check on the algebra, not a validation exercise, and it is
worth doing before any solve is scheduled to "check the magnitude".

**What happened.** The valve act
(`sdk/workflows/valve_study.py`) screens 13 leaflet opening angles on
`dp = 0.5·rho·(Q/(Cd·A_orifice))²` with `Cd = 0.62`, and reports the
widest admissible opening as the winner. That formula contains no pipe
area, so it has no beta → 1 limit: as the leaflets open the geometry
becomes an unobstructed pipe, where an *orifice* loss must vanish because
there is no orifice, and the formula instead tends to a finite floor. At
the winning 87.5° the effective orifice is 99.8% of the bore and the
screen still reports 1252.8 Pa; at a fully open 90° bore it reports
1248.0 Pa, against 57.5 Pa of Hagen-Poiseuille wall friction over the same
0.3013 m of pipe — a factor of 21.7 through a tube with nothing in it. The
ratio never falls below ~22 anywhere in the sweep, and the curve flattens
onto that floor exactly where the optimiser is heading.

Family F9 found this the expensive way: it built an axisymmetric orifice
mesh, solved the pulsatile flow, and reported a −94% deviation at 65°,
which was then attributed to the discharge coefficient sitting outside ISO
5167's calibrated beta range. Decomposing that gap afterwards (F9 §9.5)
showed the coefficient explains 13.5 of the 94 points; the rest is a
waveform/averaging definition mismatch and an omitted velocity-of-approach
factor. **The limit check above needs no mesh, no solver and no ISO
citation, and it is a stronger statement than the one 1.35 core-hours of
CFD produced.**

**How to apply it.** For any correlation-driven sweep, write the objective
at both ends of the design range by hand before the sweep runs. Wide
open, closed, zero flow, infinite Reynolds number — whichever limits the
variable actually reaches. Then state on the record what the correlation
does there. The ranking may still be sound (it is, for the valve: wider is
genuinely better, and F9's three solved angles reproduce the ordering) —
but a band built from the spread *between* published correlations can
never cover the whole family being outside its own domain, so the
uncertainty channel must say so rather than imply the magnitude is pinned.

## L-24. A convergence criterion applied to one quantity says nothing about the others the study publishes

**The rule.** Apply the convergence or stationarity gate to **every**
signal the study reports as a number, not just the headline one. A run is
not "converged"; a *quantity* is converged, and quantities in the same run
converge at wildly different rates when they are sampled in different
parts of the flow.

**What happened.** F9's six fixed-BC reference runs were judged stationary
by hand on `dp_upstream_to_throat`, over a stated window with a stated
band, and that call was correct: an automated four-test criterion added
later (band ratio, halves drift, tail trend, window shift) passes all six
on that signal, including the two tests the hand check had not performed.
But the same runs also publish `dp_upstream_to_downstream` in
`F9_pulsatile_valve.json`, and at the three highest-loading cases that
signal fails outright, with peak-to-trough bands of 39%, 113% and 128% of
its own mean — a self-sustained jet shedding at a shear-layer Strouhal
number, not a settling transient, and at `steady_q100` still climbing
across the whole run. Nobody had ever looked at it, because the
stationarity discussion had been framed as "is the run converged" rather
than "is this number converged".

The same asymmetry appeared in the pulsatile runs: the throat differential
reaches cycle-to-cycle repeatability of 8.5e-6 while the downstream
differential in the same file sits at 1.39e-3, failing the stated 1e-3
threshold.

**Two corollaries worth carrying.**

1. **Pick metrics the solution can actually fail.** Cycle-integrated
   stroke volume is the intuitive gate for a pulsatile solve and it is
   worthless for an incompressible rigid-wall case with a prescribed inlet
   flux: mass conservation makes it identical to the boundary condition at
   every instant, in cycle 1 of a diverging run as much as in a converged
   one. A metric that cannot fail is not a gate.
2. **A cycle mean hides a non-periodic cycle.** Between cycles 1 and 2 of
   F9's physiological run the cycle *mean* of the throat differential
   moved 2.1% while the cycle *peak* moved by a factor of 18.5, the
   impulsive-start spike sitting inside cycle 1. A criterion built on the
   mean alone would have called that cycle nearly converged. Grade the
   phase-aligned waveform, the peak and the band, not just the mean.

---

## L-25. A control test run on a mesh that cannot represent the mechanism is not a refutation — it is a null measurement

**What happened.** F7a (Martin & Moyce dam break, `interFoam`) failed its
front-position gate by +13.6%. The D1 diagnosis tested wall friction as a
candidate: it swapped the floor from `noSlip` to `slip` on the a/20 mesh,
measured a ~2-point change, and recorded the verdict "wall treatment
**refuted** as the driver." D1's own written prediction, one line above that
verdict, said the mesh was "far too coarse to resolve a genuine viscous
sublayer" — which is exactly the reason the test could not have detected the
effect. The mechanism was then hunted for two more sessions.

It was friction. The leading film is about 2.9 mm deep; on the a/20 mesh that
is one cell, so the no-slip and slip cases are both effectively frictionless
and must agree. Re-run at a wall-normal spacing of a/128 the same single-variable
control separates by **5.5 percentage points of deviation** (+8.2% no-slip vs
+13.7% slip), the resolved profile shows a real boundary layer filling ~60% of
the film (U_x 0.359 → 1.049 m/s over five cells), and refining that direction
alone takes the gate deviation from +11.6% to +8.2%.

**The rule.** Before recording a control test as a refutation, state the
resolution the mechanism needs and check the mesh against it. If the test
cannot resolve the thing it is testing, the correct entry is "not measurable at
this resolution," not "refuted." A null result is only evidence of absence when
the instrument could have seen it.

**Corollary, from the same case.** A derived diagnostic must be shown to be
metric-independent *before* any mechanism is attributed to its behaviour. F7a
produced **two** separate published root causes — a coarse-mesh "sign flip" and
a 40% improvement from disabling interface compression — and both evaporated
when the same solves were re-measured with a depth-integrated front metric
instead of a fixed-α line probe. The first reversed sign; the second reversed
sign. Sweep the metric's own free parameter and report the spread alongside the
number, as `F7_runs/front_metrics.py` now does.

---

## L-26. A source term's sign must be established by a controlled experiment with a known answer, not by reading the code — and a comment is not evidence

**What happened.** F6a's channel 3 injected an eigenvalue-perturbed Reynolds
stress into `simpleFoam` through a coded `fvOptions` source. Each of the 18
`system/fvOptions` dictionaries under
`demo-output/website/dafoam/f6a_epistemic_band/` built
`deltaR = blendDelta*2k(bPert - bB)`, stated in its own comment that "the
momentum forcing is deltaR = 2k(bBlend - bBoussinesq)", and then ended with

```
eqn += fvc::div(deltaR);
```

In OpenFOAM, `fvMatrix::operator+=` on an explicit field does `source() -= V*su`
(`fvMatrix.C:1682`), which puts `+deltaR` on the **right-hand side** of an
equation whose left-hand side already carries the modelled stress via
`divDevReff`. The effective deviatoric stress is therefore `R_model - deltaR`,
so the imposed anisotropy was `b_eff = 2 b_Bouss - b_pert` — **the intended
perturbation applied backwards**, a reflection of the target state through the
baseline. Zero of the 18 dictionaries used `-=`.

It survived a full study. The 1C corner as actually applied handed **95.93% of
the hump's 51,626 cells** a Reynolds stress with a negative eigenvalue — a
stress no velocity field can have — and the solver said so, in the run's own
log: `limitVelocity limitVelocity1 Limited 24864 (48.16%) of cells`
(`solve_registry/uq_oneC_20260729T023701Z.log`). That line was read as evidence
about the *physics* of the 1C corner ("a property of the target perturbed state
itself on this mesh") and became a published diagnosis. With one character
changed the same case logs `Limited 0 (0%) of cells`. The `threeC` corner
(`eLambda = (0,0,0)`) converged cleanly and produced 1.1069, +0.63% from the
NASA experiment — the study's most-quoted single number — while actually
imposing *twice* the baseline anisotropy rather than the isotropic limit. A
wrong sign that happens to converge is far more dangerous than one that crashes.

**Why nobody caught it.** Every check that was run was a *reading* check: the
comment agreed with the intent, the algebra in the record agreed with the
comment, and the code matched the algebra. Nothing tested the operator against
an outcome known in advance. The one signal that did fire — half the mesh being
velocity-clipped — was attributed to the physics being probed rather than to
the instrument probing it (this is L-22's failure mode, reached from a new
direction).

**The rule.** Before any coded source term, immersed forcing, or hand-assembled
`fvOption` is used to produce a result, verify its sign with a **controlled run
whose answer is known independently of the term being tested**. The pattern that
worked here (`f6d_random_matrix_uq/signcheck/`): construct a case where the
source is exactly equivalent to a parameter the solver already has, run the
reference *without any coded source at all*, and check the two collapse onto
each other.

- Laminar periodic-hill flow at Re = 100, `meanVelocityForce` holding
  Ubar = 0.72, discriminated by the driving pressure gradient the solver must
  find. `ref_nu1` (ν₀, no source) → 0.01541756. `src_minus`
  (2ν₀ with `deltaR = -2ν₀S`) → 0.01542612, agreeing to **0.055%**.
  `ref_nu3` (3ν₀, no source) → 0.03802645. `src_plus` (2ν₀ with
  `deltaR = +2ν₀S`) → 0.03802046, agreeing to **0.016%**. Only
  `R_eff = R_model - deltaR` produces that pairing, and the two reference runs
  carry no coded source, so the comparison needs no interpretation of physics.
- **Make the test discriminating first.** The first attempt at this, at Re = 10,
  was non-discriminating and had to be discarded: in the Stokes limit the
  velocity field is independent of viscosity, so all four runs agree by
  construction and both hypotheses "pass". A control that cannot distinguish the
  two answers is not a control — this is L-25 in a new setting.

**Two corollaries.**

1. **A code comment is a claim, not evidence.** The comment here was right about
   the intent and useless about the effect, and it survived 18 copies because
   copying a dictionary copies its reassurance along with its bug. Grep the
   count (`grep -rl "eqn += " --include=fvOptions`) and treat "18 files agree"
   as one fact, not eighteen.
2. **Add a realizability audit to any Reynolds-stress perturbation.** Whatever
   stress a closure-perturbation method imposes must be positive semi-definite
   cell by cell; it is a three-line eigenvalue check on the field the solver is
   actually handed, it costs nothing, and it would have caught this instantly
   (`f6d_random_matrix_uq/realizability_of_flipped_corner.py`). "Fraction of
   cells with a negative eigenvalue" belongs next to the residual in the gate
   record for every such run.

**What it cost, and what it did not.** The corrected-sign re-runs still return
`NOT_CONVERGED` for all three hump corners at the same budget, so F6a's headline
negative result — the corners are not reachable on that case within budget —
**stands**. What was lost is the numbers and the mechanism: three published
corner values, a "single most important number" envelope, a local-sensitivity
slope with the wrong sign attached, and a diagnosis of *why* the corners fail.
Full record: `demo-output/website/campaign/F6d_random_matrix_uq.md` §4,
`F6a_epistemic_propagation.md` §10, `F6a_epistemic_band.md` (end).

---

## L-27. A gate run outside the batch ledger must retain its own artifact — and its absence from the ledger is not evidence it never happened

**What happened.** F2's headline validation number (transonic NACA0012,
M=0.8/alpha=1.25 deg/Re=6e6: Cd=0.0432, Cl=0.109, suction-side shock at
x/c=0.556) was published in `PHYSICS_FAMILIES.md` and `CAMPAIGN_STATUS.md`
and could not be located afterwards by anyone who went looking. A survey
scanned all 280 `rhosimplefoam-naca0012-transonic` entries in
`demo-output/website/mega-batch/ledger.jsonl` and found no run at those
conditions and no run pairing that Cd with that Cl — both true — and
concluded the numbers traced to nothing and had to be withdrawn.

They traced to a real run. The primary case was a *pre-batch validation-gate
solve*, never a batch sample, so it was never going to appear in the batch
ledger. Its own commit says so: `6cc7f629` (2026-07-28 05:25:35 +0000)
records the gate result in its message and, two paragraphs later, records
why nothing survived — "Both families were tested end-to-end through
`mega_batch.run_task` **against a scratch ledger** before this commit." The
scratch ledger was thrown away and `mega-batch/work/transonic-naca0012/` was
left empty. Re-running the case from the unmodified module reproduced every
published digit: Cd 0.0431920118, Cd spread 0.00093281, Cl 0.109011072,
shock 0.55607646, solver 33.7 s against the recorded 33.8 s — and the
documented secondary case reproduced too.

**Two failures, pointing opposite ways, and both are the lesson.**

*The record's failure.* A published gate number whose artifact has been
discarded is not a result, it is a memory. It survived only because a commit
message happened to repeat it. Nobody could check it, and for two days the
lab could not tell a real measurement from a fabricated one by inspection —
which is precisely the state L-22 warns about. **If a run decides a gate, its
log, its coefficient file and its case dictionaries get retained under the
campaign, not left in scratch.** Cost here: 34 seconds of compute, against
two days of unverifiable headline.

*The audit's failure.* "I searched the ledger and it is not there" is
evidence about the ledger, not about the world. Before concluding a number is
untraceable, establish *what kind of artifact it should have been* — batch
sample, dedicated validation solve, re-analysis of an existing field — and
search for that. The survey did correct arithmetic on the wrong corpus and
drew a conclusion (fabrication) far stronger than its evidence (absence from
one index) could carry. The same audit also reported that the record
"describes F2 as transonic RAE2822"; every record in the repo titles it
NACA0012 and openly documents why RAE2822 was *not* used. It read a
disclosure as a claim.

**Why this sits next to L-22 rather than under it.** L-22 is a real
phenomenon attached to the wrong case. This is the mirror: a real absence
attached to the wrong conclusion. Both are failures of *provenance
reasoning* rather than of measurement, and both are fixed by the same move —
go to the artifact the claim should have, and if there isn't one, say
"unverifiable," which is a different and much weaker word than "false."

**The rule.** Retain the primary artifact for anything that decides a gate,
including work done outside the batch machinery. When a number cannot be
found, report it as *unreconstructible* and try to reproduce it before
reporting it as *unsupported* — deterministic cases are usually cheap, and a
reproduction converts an accusation into evidence either way.

---

## L-28. A detector that snaps to mesh nodes cannot report a deviation smaller than its own increment

**What happened.** F2's transonic gate claimed the CFD shock at x/c=0.556 sat
"+0.044 chord upstream of the inviscid reference at x/c ~ 0.60," and read that
displacement as the expected viscous shock/boundary-layer shift — the
physically right story, told by a number that could not carry it.
`transonic_airfoil.shock_location` walks consecutive sampled surface points,
picks the pair with the steepest positive dCp/dx, and returns **the midpoint
of that pair**. The sample points are airfoil-patch face centres, fixed by the
mesh. Only 21 of them fall inside the detector's [0.05, 0.95] window on this
3584-cell rung, so the reported shock position can take at most 20 values on
the whole upper surface — and across 280 solves at 280 different flow
conditions it emitted exactly **8 distinct numbers**.

The arithmetic that kills the claim is one line. The pitch between 0.55607646
and the next representable value, 0.608440365, is **0.052364 chord**. The
claimed deviation is **0.043924 chord**. The detector cannot express it: the
only readings available are "0 increments" and "1 increment." Worse, the
adjacent value sits 0.0084 from the reference — *on* it — so the two competing
physical stories are neighbouring lattice levels, and 11 of the 18 ledger runs
in the same M/alpha neighbourhood report the neighbour rather than the value
the gate was written around. The reference itself was a two-significant-figure
literature recollection with no retained dataset, which alone forbids
asserting a third decimal place against it.

**The tell, and it is visible without reading any code.** A continuous
physical quantity that returns a small number of distinct values across a
large number of varied runs is quantised, not converged. Eight values from 280
solves should stop the reader before any deviation is computed. Count the
distinct values in the column before you subtract two of them.

**Why this is not just L-14/L-16 again.** Those are about trusting a derived
signal over the primary one. This is about a signal whose *resolution* was
never stated — the number was read correctly off the right field and still
could not support the sentence built on it. It is the same species as the F7a
metric artifact retracted the same day: a measurement artifact wearing the
costume of a physical effect, and it flatters the lab, which is exactly when
it is least likely to be questioned.

**The rule.** State a detector's resolution in the record next to every number
it produces, and never claim a difference below one increment. When a banded
pass turns on a single quantisation level — as F2's did; the adjacent
representable value falls *outside* the stated 0.35–0.60 band — say so, and
grade the result "not contradicted" rather than "demonstrated." If the
deviation genuinely matters, the fix is a sub-cell fit to the peak or a finer
discretisation, not a more confident sentence.

---

## L-29. A guard that replaces a removable singularity with a constant differentiates to a hard zero — at exactly the point every gradient evaluation uses

**What happened.** IDWarp's `getRotationMatrix3d`
(`src/utils/vectorUtils.f90:31–103`, v2.6.2) builds the rotation carrying each
surface node's reference normal onto its current normal by normalising a cross
product and taking `acos` of a dot product. The map itself is smooth at
`n = n0` — derivative `[n0 × dn]_×`, finite and non-zero — but that
*parameterisation* has a removable singularity there (a 0/0 axis, an infinite
`acos` slope), so the code guards it: `if (axisMag < tol) angle = zero`
(line 58, `tol = sqrt(eps)`; the comment says the guard exists to prevent a NaN
in complex mode). For the primal the guard is harmless. Under AD it is not:
Tapenade correctly differentiated the branch that was taken, and the branch
that was taken is a **constant** — `dMi/dn = 0`, exactly, where the true
first-order term multiplies the full lever arm from surface node to volume
node. That zero was A1's 634% sign-flipped `dCD/dShape` component and its
11.6–11.9% station residuals, A5's 207%/122% sign flips, and upstream's own
five-year-open `mdolab/idwarp#57` (210%/213%).

**The trap has three teeth, each general.**

1. **The guard fires with certainty at the baseline.** At any undeformed state
   `normals == normals0` bit-for-bit, so `axisMag = sqrt(1e-30) < tol`. The
   degenerate point of the parameterisation is not a rare corner — it is the
   exact state at which every `check_totals`, every first design iteration, and
   every gradient probe evaluates. The FD side perturbs by `h`, tilts the
   normals far above the threshold, and sees the term the AD lost; that gap
   *is* the disagreement.
2. **The primal is bit-perfect throughout**, so no forward-solve check can ever
   surface it: the warped grid is md5-identical whether the branch carries the
   right derivative or none.
3. **The zero hides from generic tests.** The discarded term sums to exactly
   zero over the surface on all five meshes measured (`sum(dXs)` identical to
   0–1 ulp while `‖dXs‖` changes by factors of 5–34), so an assertion on the
   sum is blind by construction; and a random-seed dot-product test contracts
   the error against a direction it barely overlaps (0.32–1.30% where the real
   objective seed reads 207%, flipped).

**Proof it was the cause, not a story:** supplying the four-line true
derivative of the degenerate branch
(`v2b += (axial(mib − mibᵀ) × v1)/(|v1||v2|)`, derivation on the record before
the code, per L-26) collapsed every measured error to FD-truncation level with
rotations ON — #57's 210.16%/212.62% → 8.6e-06%/3.4e-05%, A1's 634% flip →
5.5e-04%, A5's 207%/122% flips → 3.0e-06/7.0e-06 — with the primal
md5-identical and the non-degenerate branch bit-identical. Root cause confirmed
by repair.

**The rule.** When derivative code — AD-generated or hand-written — crosses a
branch that replaces a removable singularity with a constant (`if (small)
return safe_value` around a normalisation, an `acos`/`atan2` near its edge, any
guarded 0/0 limit), that branch carries derivative *zero*, while the true
derivative at the limit is usually finite and often dominant. Audit every such
guard on a differentiated path and require the guarded branch to carry the
analytic limit derivative — or reparameterise so no guard is needed (here
`R = I + [v]_× + [v]_×²/(1+c)` removes both this regime and the ill-conditioned
near-threshold one). And when *testing* derivative code, evaluate at the
degenerate/baseline point deliberately and seed with the real objective
direction: the singular point of the parameterisation and the evaluation point
of the workflow are the same point far more often than randomly-chosen test
states will show.

**Why this is not L-26 again.** L-26 is about establishing a sign by a
controlled experiment; that discipline is what made this patch trustworthy.
The lesson here sits upstream of any sign: a guard that is *correct for the
primal* can silently define a *wrong derivative*, and it does so precisely
where everyone evaluates. (The adjacent observation from the same arc —
upstream's `tests/test_USMesh.py:86` ran the right verification for five years
and discarded its result, asserting only the sum the defect cannot move — is
the L-2/L-21 family appearing in someone else's CI, recorded in
`ROOTCAUSE_getRotationMatrix3d.md` §2.2 rather than as a second lesson.)

Files: `demo-output/website/dafoam/ROOTCAUSE_getRotationMatrix3d.md` (§1, §2,
§4), `demo-output/website/dafoam/PATCH_getRotationMatrix3d.md`,
`demo-output/website/dafoam/PROOF.md` §23–24,
`demo-output/website/dafoam/UPSTREAM_BUG_REPORT_mesh_warpDeriv.md`,
`demo-output/website/dafoam/rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch`.

---

## L-30. A gate whose threshold lies between two constraint values reports the constraint, not the quantity

**What happened.** Every snappyHexMesh case this lab builds is written with the
same `meshQualityDict` (`external_aero._MESH_QUALITY`): `maxNonOrtho 65`,
`relaxed { maxNonOrtho 75 }`, `maxBoundarySkewness 4`, `maxInternalSkewness 4`.
Those are constraints the mesher enforces, so a mesh hard enough to press
against one reports its ceiling back. Across the **98** `log.checkMesh` files
on this box on 2026-08-02: **9** meshes read 64.64–64.99, **3** read
74.31–74.96, and **5** read max skewness 3.896–3.99994. The lab's own published
gates are `MAX_NON_ORTHOGONALITY = 70`, which sits *between* the two
non-orthogonality ceilings, and `MAX_SKEWNESS = 4.0`, which *is* the skewness
ceiling. `study-b52-finer2-uq` clears the 4.0 gate by **5.6 × 10⁻⁵**.

**The clean demonstration.** The same four background blockMesh division
triples on the NACA 4412 wing read **57.556, 58.374, 60.801, 62.391** at
refinement 3, where no mesh presses its constraint — a 4.83° spread — and
**64.958, 64.977, 64.990, 74.962** at refinement 4, where three of them agree
to **0.032°** because they are reporting the same number the recipe wrote. A
70° gate splits that second column 3–1, and the split is which constraint
branch the mesher ended on.

**What it cost.** `models/curriculum/results/naca4412_wing.json` named the
finer rung's 74.96 as *"degraded, not improved, at the largest cell count"* and
*"the leading suspect for the non-monotonicity"* of a refinement ladder. It was
a dictionary limit. A replicate at a third of the cell count reaches 74.962443
against that rung's 74.962218 — agreeing to 3.0 × 10⁻⁶.

**The tell, visible without reading any dictionary.** A continuous quality
measure that clusters tightly just below one of a few round values, across
unrelated bodies and studies, is pinned. Two rungs of one body landing six
thousandths of a degree apart is not two meshes happening to be similarly bad.

**The rule.** Before gating on a reported extremum, find out whether the tool
was *told* that number. A gate must return two values: the verdict, and whether
the verdict was decided by a measurement or by the recipe. When it was the
recipe, fall back to a quantity the recipe does not pin — for mesh quality that
is the **extent** (how many faces are severely non-orthogonal, as a fraction of
all faces), not the average, which on this lab's own population does not
separate good meshes from bad. And never set a gate value equal to a
constraint value: a gate that cannot fail is not a gate.

---

## L-31. A verification instrument must itself be verified at the component it condemns

**What happened.** The A5 U-bend's 27-component gradient table came back in
band on 26 components under the patched warp, with idx16 the exception at
**17.31%** — and, uniquely in the whole record, *worse* than the 12.27% it read
before the patch. The record reasoned that the FD was "identical to every digit
between the runs", so the analytic side had moved away from a fixed target.
That test cannot fail: the primal never sees a `warpDeriv` patch, so the FD
*could not* have changed. What was never done was **re-measuring it**.

Three independent finite differences at the same step, same container, same
case — cold from `0/`, warm from the converged baseline, and warm from the
state `check_totals`' own component sequence leaves behind — returned
**−4.98068, −5.05964 and −5.04286**. `check_totals` reports **−4.30296296**.
The control settles it: the same harness reproduces `check_totals`' reported FD
at the neighbouring idx15 — the largest component in the vector — to
**8.8 × 10⁻⁸ relative**. So the patched analytic −5.04787848 is right to
**0.10%**, the stock −3.77483865 was **25.1%** out rather than 12.27%, and the
aggregate is 0.1826% rather than 2.2372%, with the table in band 27 of 27.

**Why the reference is the last thing anyone checks.** It is the fixed point
the whole exercise is organised around, and it is usually right — here it *is*
right on 26 of 27 components, to eight significant figures on the one that was
controlled. That is exactly what makes the twenty-seventh invisible: an
instrument that agrees with you everywhere else buys the benefit of the doubt
where it does not.

**Why this is not L-22 again.** L-22 is about attributing a failure to a case
without opening that case's logs. This is the same discipline applied to the
*reference*: a derivative graded against a finite difference is two
measurements, and a record that re-runs only one of them has verified nothing
about the disagreement. The lab has already been burned from the other
direction — a dismissal built on a finite difference of the one quantity the
defect leaves unchanged — so the rule is symmetric.

**The rule.** When an analytic derivative disagrees with a finite difference,
re-measure the finite difference by an independent path before attributing the
gap to the derivative, and run a **neighbouring component as a control** so the
re-measurement is shown to reproduce the instrument where the instrument is
trusted. "Unchanged between two runs" is not verification when the change under
test could not have moved it. State what would have to be true for the
reference to be the wrong one, and test that.

## L-32. When a verdict moves, the case's own record must move first — satellites are not the record

**What happened.** On 2026-08-02 A4's gradient verdict moved CONDITIONAL→PASS on
the decomposition finding (`PROOF.md` §25.5). The move was written into four
satellite documents — `PROOF.md`, `DAFOAM_CASE_STATUS.md`,
`NOT_PASSING_REGISTER.md`, `ACTIVE_RESEARCH.md` — and into **zero** of the
case's own ladder files. The 2026-08-04 supervisor verification sweep found
`ladder-a/A4_ahmed_body.md:158` still asserting "graded CONDITIONAL, not PASS"
with no supersession note, while `:207` and `A4_ahmed_body.json` still carry the
*original, wrong-reason* "PASS under the calibration band" that predates even
the CONDITIONAL. The primary record now contradicts the live verdict in both
directions at once.

**Why it keeps happening.** The session that moves a verdict is working in the
document where the *new* evidence lives, and that is never the case file — the
case file holds the old evidence. Updating it feels like bookkeeping, so it
loses to the next measurement. This is the second time on this exact file: the
2026-07-28 CONDITIONAL regrade also left `:207`'s PASS wording standing,
recorded at the time as "not been reconciled by its owner", and it still is not.

**The rule.** A verdict change is not complete until the case's own `ladder-*`
record (both `.md` and `.json`) carries it — first, not last, because that file
is where a reader goes to check the claim. A satellite summary citing a verdict
its own case file contradicts is the same defect as a credential wall citing a
withdrawn number. When superseding, quote and strike the old wording in place;
an unmarked stale verdict is worse than a marked wrong one, because only the
unmarked one gets believed.

## L-33. A correction trained inside a gated regime rebuilds the gate's own failure at the regime's floor

*(Renumbered from L-32 on 2026-08-04: two agents filed L-32 concurrently; the A4-record lesson at the
earlier line keeps the number because external documents already cite it. This is itself a small instance
of the w7 claim-before-work convention applying to lesson numbers.)*

**What happened.** C2 established that the periodic-hills correction hurts
exactly where raw RANS is already good (clean separation at floor ≈ 0.07–0.13),
and the C1 gate was built to decline it there. The recommended cure was a
second model trained only on the low-baseline regime, so the decline branch
could submit a correction instead of raw RANS. The regime model was trained
(both membership variants), and it worked on average: mean LOO delta −0.0195,
and the one gate-declined validation case improved from 0.0759 to 0.0447 where
the global model had made it worse. It still failed its pre-declared hurt cap
— on **alpha_05_4071_3036, the lowest-baseline case in the training split
(0.0492) and the parametric sibling of both declined test cases.** The LOO
table splits on baseline again: everything ≥ 0.058 improves, both cases below
~0.055 degrade, in both variants.

**The mechanism is recursive.** "Hurts where there is little to fix" is not a
property of a fixed region of feature space that a gate can wall off once; it
is relative to the training population. Restrict training to the low-error
regime and the model's noise floor shrinks, but a new best-baseline stratum
now sits below it, and the same damage reappears there — the boundary moved
from ~0.07 down to ~0.055 instead of disappearing. Each retreat into a cleaner
regime manufactures a smaller regime with the same disease at its bottom edge.

**The rule.** When a correction's damage correlates with how good the baseline
already is, do not expect regime-restricted retraining to eliminate the
boundary — expect it to rescale. Before trusting any regime model, check its
held-out performance specifically on the best-baseline members of its own
training population (they are the in-regime proxies for the cases the gate
declined), and put a pre-declared per-case hurt cap in the GO/NO-GO rule so
the average — which will look good, because the average is dominated by the
cases with something to fix — cannot carry a candidate past the exact failure
it was built to cure.

---

## L-34. "Unreachable at runtime" is a claim about the deployed object, not about one call site

**What happened.** Three independent readings — R5, PROOF §25.3, and the 2026-08-04
liaison memo — all concluded that no PETSc runtime option can reach DAFoam's ASM
sub-block factorization, because `DALinearEqn.C` calls `KSPSetFromOptions` once,
early, and then configures the sub-PCs by hard-coded API calls. The conclusion was
half wrong, and the half matters: PETSc's `PCSetUp_ASM` calls `KSPSetFromOptions`
on each sub-KSP it creates *inside* `KSPSetUp` — after the one visible call site,
before DAFoam's overrides. Measured on the dumped CBFS system with a harness
replicating the exact call order: `-sub_pc_factor_zeropivot 1e-8` lands in the
deployed factor (`PCView` prints "tolerance for zero pivot 1e-08"). The truly
unreachable set is exactly what DAFoam overrides *afterward* — type, ordering,
fill, shift — not "everything".

**Why the error is easy and expensive.** Call-order reasoning reads one file;
the framework's own lazy-construction hooks live in another. All three readings
were careful, and all three drew the reachability boundary in the wrong place —
which here fed a docket item's premise ("a preconditioner family swap ... needs
a rebuild", true) and nearly hid that the *factor-option* axis could be swept
without one (also true, and it was swept in an afternoon: all reachable options
fail, which is what justified the rebuild as measurement rather than taste).

**The rule.** Before declaring a configuration layer unreachable, deploy a probe
that prints the final object state (for PETSc: `PCView` on the sub-PC after
setup) and test one option that should be visible if the route exists. And when
a solver's linear stack misbehaves, rebuild the exact stack offline on the
dumped operator first — mechanism and reachability both become ~10-second
experiments instead of solver launches, and the offline control must reproduce
the in-solver failure bit-for-bit before any variant is believed.

---

## L-35. A converged Krylov solve certifies the operator it was given, not the operator you meant — cross-check the solution against an independently evaluated operator

**What happened.** A4's adjoint gradient read 8.95% off its own finite difference at
np=4 under `scotch`, and every solver-side instrument said the solve was healthy:
`PetscConvergedReason: 2`, true-residual (unpreconditioned-norm, right-PC) rtol
1e-6 satisfied, and tightening to 1e-10 changed nothing — the classic signature that
was recorded as "a converged wrong answer" with mechanism unknown. The mechanism
took one cheap measurement: take the converged psi, permute it to the serial
ordering with the integer decomposePar addressing maps, and evaluate
||A^T psi + b|| under the np=1 operator. Result: 329x ||b||, against a 1.1e-04
serial floor — while the same psi satisfies its own decomposed operator to 1e-6.
The linear solver had solved the wrong system exactly: the parallel reverse-AD
matrix-free operator was not the transpose Jacobian of the residual it claimed to
differentiate, and no amount of tolerance, restart, or preconditioner work could
ever have surfaced that, because every one of those knobs measures self-consistency
with the same wrong operator.

**The rule.** When an iterative solve converges cleanly and the downstream answer is
still wrong, stop tuning the solve and test the operator: apply the converged
solution under an INDEPENDENTLY evaluated instance of the operator (serial where the
suspect is parallel, assembled where the suspect is matrix-free, a different library
where the suspect is the library) and compare the residual to the independent
instance's own floor. It is a mat-vec, not a solve — seconds, not core-minutes. Two
practical footnotes from this instance: (1) map vectors across decompositions with
the integer `cellProcAddressing`/`faceProcAddressing` files (sign on flipped faces),
never coordinate matching, and validate the map on the primal state first — the
duplicated processor-face states must agree at machine precision or the map is
wrong; (2) an assembled-matrix diff across decompositions does NOT discriminate —
it is polluted by the reconverged linearization state and the assembly's own FD
error (the clean arm's matrix diff here was LARGER than the broken arm's), so diff
operator ACTIONS on mapped vectors, not operator entries.

## L-36. A gradient check certifies a contraction, not an operator — operator corruption and gradient damage do not scale together

**What happened.** The decomposition-defect breadth matrix (2026-08-04/05, docket
`w4-does-the-decomposition-defect-reach-other-cases`) put the cross-residual
instrument beside the gradient error on two snappy-refined cases and found them
decoupled in both directions. On the Ahmed-35 case, the scotch-np=4 operator's
cross-residual against the serial operator is 5.45x ||b|| — 16x larger than
simple-4x1x1's 0.33x — yet scotch's analytic-gradient shift vs np=1 is 2.3x
SMALLER (1.36% vs 3.14%). On A4, simple-4x1x1 carries a measurable 0.094x ||b||
operator residual and a gradient error of 0.00054%; scotch carries 329x and pays
8.95%. Same subsystem defect everywhere; what the gradient pays is decided by how
the operator's error contracts against the objective's own adjoint direction —
which no instrument in the standard verification chain measures.

**The rule.** Passing `check_totals` (or any dot-product/FD test) at one
configuration certifies the CONTRACTION of the operator error with that one
objective's adjoint direction — approximately zero information about the operator
itself, and none about other objectives, other DVs, or other decompositions of
the same case. The converse also holds: a large measured operator defect does not
imply the published gradients are badly wrong. So (1) never extrapolate a passing
gradient check across configurations — the check is one inner product; (2) when
an operator-level defect is suspected, measure the operator (L-35's mat-vec
cross-check), not more gradients; (3) when a case's FD will not resolve (the
35-degree Ahmed's step sweep never plateaus because the separated-flow primal's
objective drift sits at the FD's numerator scale), decomposition-invariance of
the analytic is the remaining usable instrument — and its passing still certifies
only that case's contraction.

## L-37. When a differentiated code is wrong in parallel, suspect a recorded BRANCH first — and verify any "fixing" lever at operator level before calling anything safe

**What happened.** The decomposition-adjoint campaign (2026-08-05, docket
follow-up to `w4-does-the-decomposition-defect-reach-other-cases`) closed its
mechanism hunt on a one-word edit: `div(phi,U)` `bounded Gauss linearUpwind
limited` -> `linearUpwind default` — same scheme family, same order, same
halo-exchanged gradient-correction term, only the limiter's min/max stencil
selection removed — took the np=4-scotch gradient error from 8.95% to 0.849%,
the adjoint Krylov count from ~~590~~ **719** to 41 *(corrected 2026-08-07 per
the defect-robustness supervisor sweep, commit 8bd47b35: 719 in every log that
ran the established arm; "590" was mis-transcribed from the simple-2x2x1 arm —
the collapse is 17.5x, larger than first written)*, and the serial-operator
cross-residual from 329x ||b|| to 0.0135x. With that, every defect this lab has traced in this
toolchain is one class: a BRANCH recorded on the reverse tape whose selection
interacts wrongly with processor boundaries (the slope limiter's stencil
min/max; the freestreamVelocity flux-sign switch; IDWarp's degenerate-rotation
guard, L-29). And the complementary trap: the OTHER lever that "cleans" the
defect (swapping the farfield BC to inletOutlet) leaves the operator wrong at
1.047x ||b|| — 163,548x the np=1 floor (full precision per the same sweep;
both roundings 1.6e5) — under a check_totals reading 0.019%.
Calling that configuration "safe" would have shipped a hidden wrong operator;
only the cross-residual instrument told the two levers apart.

**The rule.** (1) In a reverse-AD parallel-inconsistency hunt, enumerate the
BRANCHES the tape records (limiters, switching/mixed BCs, guards, min/max/abs)
and one-knob them before theorizing about halo exchanges in general — a branch
is removable with a one-line dictionary edit, which makes it the cheapest
discriminator available. (2) Any lever that turns a gradient error off must be
re-verified at OPERATOR level (L-35's cross-check) before the configuration is
described as unaffected: a lever can fix the operator or merely rotate the
objective's contraction away from the damage, and the gradient number cannot
distinguish them. State which one you measured.

## L-38. An invariance check can pass because both sides are wrong together — decomposition-invariance certifies consistency, not correctness

**What happened.** The acquisition arm of the decomposition-adjoint campaign
(2026-08-07, docket `w4-defect-acquisition-on-a-second-mesh-family`) installed
the defect's two measured ingredients (`freestreamVelocity` + `linearUpwind
limited`/`cellLimited Gauss linear 1`) on the clean structured NACA0012. The
np=1 and np=4-scotch analytics agreed to 3.9e-04 (vector), the FD columns to
1e-6, the Krylov counts to within one iteration — a textbook pass of the
decomposition-invariance gate this lab adopted after A4
(`w4-decomposition-invariance-is-a-gate`). Both analytics were also **92.8%
wrong** against their own step-stable finite difference (FD moved 2.1% between
steps 1e-3 and 3e-3 — 44x too little to explain the gap; every FD-leg primal
converged to 1e-8; one gradient component sign-flipped). The one-word lever
`limited` -> `default` took the serial error from 92.8% to 0.121%: the
`cellLimited` limiter's reverse tape is wrong on this case with no processor
boundary anywhere — the first decomposition-INDEPENDENT member of the
recorded-branch defect class (L-37), which until now had "vanishes at np=1"
as an unstated family property.

**The rule.** (1) Invariance instruments (decomposition, ordering, rank-count,
restart) detect INCONSISTENCY between two evaluations of the same tape; a
tape that is wrong identically in both evaluations sails through every one of
them. Never promote an invariance pass to a correctness verdict unless at
least one side of the comparison is anchored to an external reference — an
own-run FD with a step-check, or an independently evaluated operator (L-35).
(2) The converse of L-37's trigger: a recorded branch can corrupt the reverse
sweep in SERIAL, with the parallel machinery innocent — so when a serial
gradient check fails against a step-stable FD, put the tape's branches
(limiters, switching BCs, guards) at the top of the suspect list there too,
before FD-quality theories; the branch is still the cheapest one-line
discriminator available.

## L-39. A verdict is stale the moment a later commit touches its evidence — reconcile the record before diagnosing the mystery

On 2026-08-08 the chief's negative-verdict review carried F5c's "converged
solves 4–12× wrong on reattachment, wandering" as an open mystery and
proposed diagnostics for it — while commit fe121af2, nine days older, had
already PROVEN the 4–12× reading was the OpenFOAM wallShearStress sign
convention (lower-wall tau_x is negative under attached flow; the archived
sign_convention_control run is the proof), with the honest miss being
−10.5%. **[AMENDED 2026-08-10: the −10.5% has itself since been WITHDRAWN to
*unmeasured* — it did not regenerate from the configuration it was attributed
to, and no F5c run has ever converged. See `campaign/F5C_STAGE_A_RESULTS.md`.
The lesson is untouched and is if anything sharper: the stale premise was
replaced by a second premise that was also never measured.]** The review's own zero-compute inlet audit is what surfaced the
stale premise: the audit's first act was to read the case's full commit
history, and the "mystery" dissolved before any new measurement was taken.

The failure mode is not sloppiness at writing time — the verdict WAS
accurate when recorded. It is that verdicts age silently: a later commit
can refute a standing conclusion without touching the file that states it,
and every downstream reader (including the chief) then inherits a dead
premise dressed as an open question. The S1 corrupted-inlet episode (L-33's
neighborhood, entry 6's manifest rule) is the same disease on input files;
this is the record-file variant.

The rule: before carrying ANY standing verdict into a review, a filing, or
a new diagnostic's premise, run the reconciliation sweep first — `git log
--follow` on the case's records AND its code paths since the verdict's
date, asking one question: does any later commit touch this conclusion's
evidence? Cost is one log read; the alternative was two filed diagnostics
aimed at a number that did not exist. Corollary for record hygiene: a
commit that refutes a standing record MUST amend that record in the same
commit (supersede-not-delete), because "the proof exists somewhere in the
repo" is indistinguishable from "unproven" to every future reader who
starts from the record file.

## L-40. The switch you set is not the switch that ran — a lever is evidence only when the log proves it was active

Katie's codification, 2026-08-08, from the A3 sub-LU arm's discovery: every
archived ONERA M6 adjoint script set `transonicPCOption: 2`, and `== 2` is
dead code for DARhoSimpleCFoam — the option exists only in the Turbo solver's
source (DAResidualRhoSimpleCFoam.C:173 accepts only `== 1`). Every archived
M6 conditioning-wall conclusion was therefore measured with the transonic
preconditioner silently OFF while the record implied it had been tried. The
dictionaries said configured; the runtime said nothing ran.

The rule: any solver option, flag, model choice, or lever that is
LOAD-BEARING for a conclusion must have its activity confirmed in the runtime
log — not its presence in the input dictionary — before the conclusion ships.
"Configured" and "active" are different claims; only the second is evidence.
The QCR activity check earlier the same night is the positive template: it
did not trust `turbulenceProperties` naming the model, it demanded the
selection line and the coefficient banner in the solver's own log, plus field
deltas no formula could fake.

Enforcement (Verification Charter v1.5 §9): the evidence-record schema gains
`levers_verified_active` — each load-bearing option listed with the log line
proving it ran. A conclusion citing an unverified lever fails review; a lever
the archived logs cannot prove either way ships as unverifiable-from-logs on
the conclusion's face. Companion rule, same charter bump: every mesh entering
an archive, pre-registration, or ladder rung carries its checkMesh birth
certificate — born clean or it doesn't enter (the A3 vcoarse mesh sat in the
archive born-broken: 23 negative cells, aspect ratio 2.08e95, pyHyp tip
collapse — the same generator pathology as TMR NACA 0012, now cross-geometry).

## L-41. `pgrep`/`ps | grep claude` is not a fleet-liveness check — agents live inside the SDK server, and the tells are file mtimes and git log

On 2026-08-10 the chief dispatched a fresh solver agent onto A3 rung 2 while a
resumed peer agent was alive and working on it. Both had done the right
pre-launch checks: `sudo docker ps` empty, `pgrep` showing no solver, `ps` showing
exactly one `claude` process. All of that was true and all of it was
irrelevant — fleet agents execute inside the SDK server process
(`python3 -m chief_engineer.server`, pid 1452), not as separate `claude`
binaries, so a busy peer is invisible to a process sweep. The incoming agent
concluded twice that the peer was dead, and was twice wrong; only its own
staged-but-unlaunched discipline and a final host re-check prevented two
records for one run.

The chief's own resume drill inherits the same blind spot: "zero containers,
zero solvers, therefore nothing of yours ran" is sound for SOLVES but says
nothing about whether an AGENT is alive and mid-task. The two questions are
different and only one of them is answerable by `pgrep`.

The reliable liveness tells, in order of cost:
1. `git log --since=<minutes>` — a working agent commits; a pre-registration
   appearing after your dispatch is proof of a live peer.
2. Case-directory and run-dir file mtimes (`find <runs> -mmin -10`) — a live
   solve writes constantly even when no process name matches your grep.
3. The docket/inbox claim state — a claimed item with a recent timestamp.
4. Only then process sweeps, which answer "is a SOLVER running", not "is an
   AGENT working".

Before dispatching a NEW agent onto work an existing agent might hold, check
1–3, and prefer resuming the incumbent over spawning a rival: two agents on one
item produce two records for one run, and the collision is discovered late
because the evidence that would reveal it is the evidence nobody checks.

## L-42. A rerun into an existing case directory destroys the prior run's evidence, even when its own bookkeeping is honest

Found by the batch dead-lever sweep, 2026-08-10: `H_re10595_realizableKE`'s
live record states 30,000 iterations while the `log.simpleFoam` sitting beside
it ends at 12,000. Nothing was falsified — a leaked FPE-rescue rerun executed
in the same case directory and overwrote the log in place, and both records
were individually honest about their own run. The casualty is the L-40
evidence: the earlier run's activity proof no longer exists anywhere, so a
conclusion resting on it can never be re-verified from artifacts.

The record survived here only by luck of agreement (both runs excluded the cell
for the same two reasons, so the membership verdict is unchanged). That is not
a defense; it is a coin landing the right way.

The rule: a rerun of an already-recorded cell runs in a FRESH directory, or the
prior run's log and record are preserved under a superseded name BEFORE the
rerun starts — the same supersede-not-delete convention the records use, applied
to the run tree. The batch runner already supersedes `record.json`; it does not
supersede the log, which is where the lever evidence lives. Where a workflow
cannot be changed cheaply, the launcher archives `log.*` on entry.

## L-43. The audit instrument has its own blind spots — a search that cannot see the evidence reports absence, not innocence

The batch sweep's first inventory pass named the family's headline conclusion
(the N_a10 band) as its top DEAD LEVER. It was wrong, and the cause was not
reasoning but tooling: the solver logs are gzipped, and the shell's `grep`
honours `.gitignore`, so a naive repository sweep saw neither the 36
`Selecting RAS turbulence model` banners nor the mega-batch work tree at all.
The corrected sweep found 133 verified and zero dead. The withdrawal is on the
report's face with the evidence quoted, which is the only reason the near-miss
is now an asset instead of a retraction.

Generalise past this instance: an audit's null result is a claim about the
audit's REACH before it is a claim about the world. Before reporting
"unverifiable" or "absent", prove the instrument can see a KNOWN-PRESENT
specimen — grep for something you are certain exists in the corpus you are
sweeping, and if it does not come back, fix the instrument, not the conclusion.
Compression, ignore-files, symlinked or untracked trees, per-processor
directories and rotated logs each hide evidence from a different tool.

Standing consequence: every archive-wide audit states its reach (what it could
and could not see) beside its counts, and any audit whose headline is a
NEGATIVE finding — nothing found, nothing dead, nothing missing — carries a
positive-control line proving the search would have found the thing had it been
there.

**Corollary, earned the same day the lesson was written.** The re-check ordered
to test the FIRST audit for this blindness tripped over it in turn: the
verifier's opening positive control returned nothing because an unscoped 79 GB
sweep hit its timeout before reaching the directory it was aiming at. A null
that is a TIMEOUT is not a null that is an absence, and the two are
indistinguishable from the output alone. So the positive control needs its own
success condition — the control must be seen to SUCCEED (a known specimen
found, a non-empty result, an exit code read), never merely to return. An
instrument that fails silently fails the same way whether the corpus is empty
or unreachable.

The re-check's substantive result is worth recording beside the method: 0 of 20
rows changed classification, and the first audit turned out never to have been
gz-blind at all — it quotes decompressed line numbers in eight rows. The
suspicion was correct to raise and wrong in fact, which is the ordinary and
healthy outcome of assuming yourself wrong until defended.


## L-43, second corollary. A found-dead verdict is a claim about IMPLEMENTATION, and implementation hides in include files

Same day as the lesson, the opposite failure direction. The first dead-lever
audit recorded FD-2: that `DASimpleFoam` silently drops `consistent yes`, i.e.
SIMPLEC is not implemented. A container-side re-read refuted it — SIMPLEC *is*
implemented, in the primal at `pEqnSimple.H:27` and the adjoint at
`DAResidualSimpleFoam.C:189`, both carrying the textbook
`rAtU = 1/(1/rAU - UEqn.H1())`, in both images. The original search scanned
`DASimpleFoam.C` and `DASolver.C` and found only two unrelated comments. **The
file list, not the search string, was the defect.**

Where L-43 warns that an audit's null may be a claim about its reach, this is
the same root failing in the direction that does more damage: a false
FOUND-DEAD is not a missing finding, it is a manufactured one, and it
propagates. This one had already been adopted as the stated cause of A4's
22.05% cross-code gap; that cause is now retracted and the gap is unexplained
again, which is worse than never having explained it — the lab spent weeks not
looking for the real cause.

The rule: a deadness claim about C++ requires the BUILD's view, not a file's —
grep the whole source tree including `.H` includes and every `DAResidual*`/
derived class, or read the compiled behaviour, before writing "does nothing".
And any verdict of the form "the code ignores X" is downgraded to
"not found in the files searched, which were: …" unless the search space is
stated. A negative claim without its search space is not a finding.

## L-44. A pre-registration is frozen against improvement, not just against tampering — retroactive edits destroy the property that makes it evidence

While propagating a newly-measured caveat across every surface asserting the
lab's closure standing, the executing agent stopped at a class of files and
refused: `R5_PREREGISTRATION.md`, `R5_RULE_FREEZE.md`, the R4 and SpaRTA
pre-registrations, two dated morning reports, and the Ladder V rung records.
Its reasoning: rung V2 passed precisely BECAUSE the acceptance criterion at
`0bade54a` predates every solve it judged. Adding today's honest, correct,
strictly-improving caveat to those files would have made them documents
edited after their outcomes were known — which is the exact property V2
certifies they do not have. The improvement would have destroyed the evidence.

Generalise it: a frozen artifact's value is not its content but its TIMESTAMP
RELATIVE TO WHAT IT JUDGES. Anything that makes it better after the fact makes
it worthless as proof, and "but the edit was true" is not a defense — the
whole point of pre-registration is that its contents were fixed before the
truth was known. New knowledge attaches to a DATED ADDENDUM, a superseding
record, or the live surfaces; never to the frozen document's body.

Practical form: before editing any file, ask whether some other claim depends
on when it was written. Pre-registrations, rule freezes, dated reports, gate
records and audit reports all answer yes. They take addenda, never revisions.
(The same instinct, applied to run trees, is L-42; applied to records that a
later commit refutes, L-39's supersede-don't-delete.)

## L-45. A verification instrument may fail open; it may never fail false — the two failure directions are not comparable

The lever-echo gap (L-40's enforcement machinery) turned out to be survivable
for a structural reason, not a lucky one: `levers_verified_active()` builds its
entire list from what it can parse out of the log, so a launch the echo could
not see yields an EMPTY list and a basis string that says `unverifiable` in as
many words. The defect suppressed verifications; it could not invent one. All
13 standing claims across 12 records re-verified exactly, file set and sha256,
against the runs they describe — with a planted-mismatch positive control
proving the checker is a detector rather than a rubber stamp.

The same sweep then found a path where that is NOT true. `launch_solve.sh`
mints its echo block from a caller-supplied `--case` path, while the command
itself runs under `setsid nohup "$@"` in the launcher's inherited working
directory. Nothing binds the two. A mismatched `--case` therefore writes an
echo of dictionaries that DID NOT RUN at the head of the log of a solve that
did — a manufactured verification, indistinguishable downstream from a real
one.

The asymmetry is the lesson. A gate that fails open costs you evidence you
could still go and collect; the record says "unverified" and everyone knows
where they stand. A gate that fails false costs you the ability to tell
verified from unverified anywhere it may have fired — and the cleanup is not
one record but the whole corpus the gate ever touched, exactly the position the
manufactured FOUND-DEAD verdict put us in (L-43's second corollary).

Design rule: derive the evidence from the thing that actually executed —
the resolved binary, the working directory the process is in, the file the
solver opened — never from a parameter the caller supplied describing what it
intends. When a false-positive channel is discovered, it outranks every
false-negative on the same fix queue, even a larger one.


## L-46. A change that creates an artifact must be audited from both ends: what stops checking, and what starts reading

The L-42 enforcement pass (archive a solver log before a rerun destroys it)
nearly became a defect twice, in opposite directions, and the pair is the
lesson:

**At the guard.** The first design pre-seeded the log file from Python. Callers
gate their launches on `if not log_path.exists(): raise` — so the fix would
have made that check pass whether or not the shell ever ran. *A change that
creates the artifact a check tests for disables the check*, silently, with
every test still green.

**At the consumers.** The obvious archive name `log.simpleFoam.superseded_<stamp>`
would have been read as a run log by FIVE places that select a case's log by
globbing `log.*`, `log.*Foam` or `log.simpleFoam*` — and one of them picks the
LARGEST match, so an archive bigger than the live log would have been
classified as the run itself. An evidence-preservation fix would have become an
evidence-confusion bug. The stamp became a prefix instead, matching none of the
four glob shapes, pinned by a test so a future tidy-up cannot move it back.

The executing agent found the second only because it applied the first rule
deliberately — *this change creates artifacts, so go find everything that reads
them* — which is the argument for writing a rule down rather than trusting
that you will remember it at the moment it applies.

Standing form, for any change that adds, renames or duplicates a file the lab
reads: enumerate (a) every check whose passing condition your new artifact
could satisfy accidentally, and (b) every consumer that discovers files by
pattern rather than by exact name, and state both lists in the change. A
pattern-matching consumer is an undeclared interface; adding a file to a
directory is editing that interface whether you meant to or not.

**The shared form, after a third instance** (the log-elision fix whose marker
embedded the payload's own byte count and hash, so every replicate differed
through the very marker added to describe the difference — caught by running
the comparison against two real cases rather than reasoning about it):

> A change is not finished when it does what you intended; it is finished when
> you have run the check that would fail if it did not.

All three instances looked right, read right, and passed every existing test.
Two were found by asking *what else reads this?*; the third by refusing to
reason about a result that was measurable on real data in under a minute. The
third is the one least likely to be caught by anyone else, because it is the
only one where the author's own claim was the thing under test.


## L-47. Two solves differing only in relaxation must agree — disagreement proves non-convergence without reading a single residual

The F5c thread began with a record that claimed "deep numerical convergence"
while reading the LINEAR solver's final residuals instead of SIMPLE's initial
ones, and everything built on that word was wrong for a year. The arm that
closed the thread produced the check that would have caught it, and the check
needs no residual at all.

Relaxation factors are a path parameter: they change how a steady solve
approaches its fixed point, and they cannot change where the fixed point is.
So two runs of the same case differing ONLY in relaxation must agree at
convergence, to within the settle tolerance. In the F5c 2x2 factorial they
disagreed by a factor of 2.6 in reattachment length — 4.224 step-heights from
relaxation alone. That is a proof of non-convergence that is immune to
misreading a residual, misconfiguring a gate, or reading the wrong solver's
number, because it never consults one.

Use it as a cheap standing check wherever a steady result matters: run the
case twice with materially different relaxation, and require agreement inside
the settle bar before any physics claim is made. It costs one extra solve and
it is the only convergence evidence in the lab that cannot be defeated by an
instrument error, since the instrument is the physics.

The same arm settled what the disagreement had been blamed on: the SIMPLEC
attribution standing since 2026-07-29 is MISATTRIBUTED, not merely unproven —
the algorithm moves 2.911 H and does not clear its bar, while relaxation moves
4.224 H and does.


## L-48. Check the premise the offered options share — and record a gap as a gap, never as a constraint

The chief routed five campaign launch paths with a choice: migrate them to a
vector-taking launcher, or mark them permanently unverifiable. Both options
rested on the same premise — that these paths launch solvers through arbitrary
shell strings, which cannot be parsed to decide what ran without keying on a
spelling (the defect class this campaign exists to close).

The executing agent checked the premise instead of choosing. **24 of 24
commands across the five files contain zero shell metacharacters**: they are
argument vectors merely *spelled* as strings, and the `bash -c` wrapper exists
for one visible reason, sourcing the OpenFOAM environment — which the shared
launcher already resolves. Nothing needs splitting. Both offered options were
answers to a question that did not exist, and the correct move was to refuse
both and say why. (It supplied a positive control: the same detector does flag
`cd X && solver > log`, `solver | tee log`, and a `for` loop as genuine shell
strings, so the negative was measured rather than assumed — L-43.)

Two rules come out of it.

**Verify the premise the options share.** A choice presented by a supervisor
carries an assumption, and the assumption is the part nobody re-derives
because it arrived with authority. An agent that picks well from a false menu
has done worse than one that rejects the menu.

**A gap invites a fix; a constraint forbids one.** The agent also declined to
mark the paths "permanently unverifiable", on the grounds that writing a limit
into a standard when measurement says the limit is not there is worse than
leaving the gap open. False constraints are self-perpetuating: the next reader
inherits them as settled, and the cheap fix nobody attempts is invisible
forever. Record what is missing; never record what is impossible unless you
have measured the impossibility.


## L-49. A search whose vocabulary came from your examples returns your examples — and it feels exhaustive while doing it

The ladder-feature audit was run twice by design. Route A, a pattern search,
found 16 live records asserting a ladder shape. Route B, a different method,
found **32** — and the reconciliation overturned the audit's own headline:
the RESTATE share went from 50% to **77%**, which meant the agent's
pre-registered prediction had been RIGHT and its measurement WRONG.

Route A failed for a reason worth generalising. Its pattern spelled the concept
the way the records the author had spent the day inside spell it —
`non-?monoton`, `increments grow|shrink`. Tested afterwards against nine
genuine assertions Route B found, **it caught one**: it could not see `NOT
monotonic` (space, not hyphen), `monotonically`, bare `monotone` used as an
argument, or `increment smaller`. Nine whole bodies were invisible.

**The failure was biased, not noisy, which is worse.** A noisy search misses at
random and its count is roughly right. A search whose vocabulary was drawn from
the subset you already know finds everything in that subset — so it returns a
clean, confident, complete-looking answer that is systematically blind to
exactly the members you have never seen. It confirms the shape of your existing
sample and calls it a census.

This was the day's own defect class, written by the author into the audit that
was checking for two earlier instances of it (`args[0]` instead of *does this
launch a solver*; splitting a shell string to decide what ran). Three instances
in one campaign, the third inside the instrument built to catch the first two.

The practical test, before trusting any count: **could this method have found a
member of the class I have never seen?** If its vocabulary came from your
examples, the answer is no and the number is a LOWER BOUND, not a count — label
it so. And when a check is run "by a second route", the route must differ in
KIND: a second regex with more synonyms you thought of is the same measurement
twice (L-48's recount/re-read distinction, applied to search rather than
arithmetic).


## L-50. A correction must not travel on the evidence class of the thing it corrects

The dead-lever audit's FOUND-DEAD verdict on SIMPLEC was wrong because it
rested on a source read with the wrong file list. The refutation that overturned
it rested on **a source read plus a config read** — the same evidence class,
better executed. The agent noticed this about its own work before the
correction propagated upstream, and stopped: *a correction travelling on the
evidence class it is correcting is the same defect wearing the opposite
conclusion.*

So it measured instead. One token flipped on a small case: 435 iterations to
tolerance with the flag off, 490 with it on. **The flag is active**, proven by
behaviour rather than by reading. The refutation now stands on three legs and
the third is of a different kind, so no correction is owed on the material
already routed.

The rule: when overturning a claim, ask what KIND of evidence the original
rested on, and get at least one leg of a different kind. Two source reads
disagreeing is a disagreement about reading. A source read and a measurement
agreeing is a finding. This applies with most force to the corrections that
feel safest — the second look is done by someone who now knows the answer, and
confidence is not a class of evidence.

The same arm produced a bonus of the same shape: the converged objectives agreed
to 7–8 significant figures, which is the expected SIMPLE/SIMPLEC relationship
(different path, same steady state). The retracted claim had been that the two
algorithms *land on numerically different steady states* — which would require
the wake to be genuinely bistable AND the two paths to land in different
attractors, a far stronger claim than "the codes used different algorithms",
never demonstrated, and moot in any case because both runs used the same
algorithm. The gap it purported to explain remains genuinely unexplained, which
the record says.


## L-51. A search has a method and a FRAME — "a different route" governs the method; nothing governs the frame unless you make it

L-49 said a second route must differ in kind. One did — structural (reading
mesh dictionaries) versus textual (reading the records) — and its readings were
correct on every case it examined. It was still wrong on its headline, twice:
it reported that a confound "had never been written down" when two bodies
carried an audit saying exactly that, and that "exactly one ladder is known to
be a ladder" when four purpose-built ones existed.

Neither was a reading error. Both were **frame errors**: the first generalised
"absent on the five ladders I queried" to bodies it had never asked about; the
second enumerated with a glob (`study-<body>*`) that structurally could not
reach the replacement families, which live under other names. The method read
its sample correctly and the sample was not the population.

> A route is defined by two things: how it reads, and what it reads.
> "Different in kind" governs the first. Nothing governs the second unless you
> make it.

Guards, all cheap: **state the frame explicitly** — a stated frame is
falsifiable, an implied one is not; **ask what the frame structurally cannot
contain** (a glob's shape, a directory's boundary, a field that only some
records carry); and **never conclude absence from a search that did not look
there**, which is L-43's rule about reach applied to the corpus rather than the
instrument.

Worth noting where it recurred: inside an audit whose own author had cited the
reach lesson that same morning. Knowing a rule and applying it to the search you
are currently running are different acts.

**Third corollary — the CORPUS is an instrument too.** Six monitor rules were
adopted against a replay corpus assembled by globbing `*.log`, while the
convention it swept writes `log.<app>`. The corpus was **449 files against the
1,375 that exist** — and nobody had ever asked it the question you ask an
instrument: *what does this select, and what does it silently drop?* The
omitted three-quarters refuted a published line in the standard those rules
live in.

Two things make this worth separating from the searches above. First, the fix
is a **derivation, not a wider pattern**: the corrected corpus keys on what an
application run actually prints, with binaries excluded by content rather than
extension, so **no naming rule participates at any point** — and the proof that
this mattered is that `*.log` plus `log.*` together *still* miss 96 real run
logs. A list of two patterns is the same defect with more entries. Second, it
**reversed a refusal made on the old corpus**: a rule whose 80% fire rate had
looked like one unreachable sentinel turned out, on the real corpus, to fire at
**47% on genuinely declared targets** — a number the adoption rule actually
asks for, and one that varies 20%–94% by family, which a single global rate
hides in both directions.

So: before a rule is adopted against a corpus, state the corpus's reach as you
would state a search's. An unexamined corpus is an unexamined instrument, and
every conclusion drawn on it inherits its blind spot.


## L-53. Two verification passes running at once can invalidate each other, and neither can see it

Ladder V's Pass 1 re-ran five rungs that had passed two days earlier. Four
re-verified. The fifth found this: **a load-bearing claim appears on five
surfaces without the attribution that makes it defensible, and one of those
surfaces was written by the sibling verification rung — thirteen minutes before
the rung that would have caught it committed its own sweep.**

`git log -S` puts it beyond doubt: the cross-surface rung (V10) wrote the
sentence at 02:08:13; the provenance rung (V5) committed its sweep at 02:21.
V5 swept a corpus that did not yet contain V10's sentence. V10 wrote a sentence
it had no brief to check. **A verification pass introduced the defect a
concurrent verification pass had just cleared, and the design of the ladder —
three passes, three minds, running in parallel — is exactly what made it
invisible.**

The failure is structural, not careless. Parallel verification buys
independence, which is its whole point; independence means neither pass sees
what the other is writing. So:

1. **A verification pass that EDITS is also a pass that must be verified.** A
   rung which only reads can run concurrently with anything. A rung which
   writes to shared surfaces creates new unverified material by definition.
2. **Re-run the read-only rungs after the writing rungs land**, or sequence
   writers before readers. Cheap, and it is the only thing that closes the
   window.
3. **When a defect is found on a surface, `git log -S` the sentence before
   assuming provenance.** The author may be your own machinery, and the record
   will not volunteer that.

The general form, which is L-46's shape one level up: *the fix for a class is
where that class reappears* — and a verification campaign is a fix for the
class "unverified claims", so it is precisely where new unverified claims will
be born.


## L-54. A prediction about an artifact and a prediction about an agent are different classes — label them, or you will score a coordination failure as a modelling failure

Ladder V's Pass 1 pre-registered five predictions about what a concurrent pass
would leave behind, then scored them: **three wrong, two right.** Its own
decomposition is the lesson:

> My predictions about ARTIFACTS held. Every prediction about another agent's
> future COMPLIANCE failed — and I did not mark which was which when I wrote
> them.

The two that held were properties of files: that frozen artifacts would remain
frozen, and that certain records would still be uncited for structural reasons.
The three that failed were all **one assumption counted three times** — that an
assignment would be carried out. It was not: the receiving pass declined it, in
writing, on the same defensible ground the first pass had.

Two consequences.

**Score them separately.** A pre-registration that mixes the classes cannot
tell you whether your model of the WORLD was wrong or your model of the
ORGANISATION was. Here the world-model was perfect and the org-model was zero
for three, and only the labelling makes that visible. Mark each prediction
`artifact` or `agent` when you write it.

**A "roughly right" aggregate can be right for entirely wrong reasons.** The
agent predicted a count would fall 28 → ~26 through closures. It stayed at 28 —
zero closures plus six compliant additions, a shape its model had no term for.
Had two unrelated gaps happened to close, it would have scored "roughly right"
while being wrong about every mechanism. Predict the MECHANISM, not just the
number, and score the mechanism first.

The companion finding, which is why this matters beyond bookkeeping: three
consecutive passes each made a defensible call and **the aggregate of three
defensible declines was a defect that survived all three.** A task that every
qualified party is right to refuse has no owner, and no amount of care inside
the passes will produce one. That escalation cannot be resolved by another
verifier — it needs someone whose job is deciding rather than checking.


## L-55. A summary that drops a conditional is a false claim assembled entirely from true parts

The fleet-wide dead-lever audit found that two of the lab's monitor rules —
residual stall and Courant excursion — **cannot fire on any production run.**
The production class constructs its monitor passing only `novel` and an event
callback, and **has no parameter by which either gate could be supplied**; both
rules return early when their gate is unset. Verified personally by the chief:
three construction sites repo-wide, one production and two offline/test.

What makes this a lesson rather than a bug report is where it hid. The
standard's per-rule Status lines are **scrupulously honest** — they say the rule
fires *"when constructed with `residual_target`"*, *"with `courant_limit`"*.
Every one of those sentences is true. Then the standard's summary says: *"S8 is
now implemented too, so the whole of both approved monitor proposals is in
force."* That sentence is false, and it is built from nothing but true ones.

**The conditional is where the fact lives.** A summary drops conditionals
because that is what summaries do, and nobody re-derives whether the condition
is ever met — the honest clause upstream makes the summary feel audited. The
same shape appeared twice more the same night: two records described a
five-day threshold defect affecting *"every caller that took the monitor
default"*, and **every caller was the test suite** — the recorded defect had
empty production blast radius, and nobody had asked who the callers were.

The rule: when a capability is claimed as *in force*, **find its production
call site.** Not the definition, not the test, not the conditional prose — the
line where real work invokes it with the gate supplied. If that line does not
exist, the capability is unreachable however correct its implementation, and
the claim is false regardless of how carefully each of its parts was written.

Corollary for anyone writing a standard: **state the condition in the summary
too, or do not summarise.** "In force" is a claim about wiring, and wiring is
checkable in one grep.


## L-56. When you write a rule about a class, the act of writing it joins that class — and you will forget

Ladder V's V15 audits "any text written during the ladder". Twice now the chief
dispatched that rung with a commit list that **omitted the commit which created
the rung being dispatched**:

- Round 1: the dispatch that added V14/V15 was itself ladder-written text on a
  claim-bearing surface, and was not in the list. The rung found it.
- Round 2: the dispatch that added the **termination rule** — the rule defining
  when this auditing stops — was itself ladder-written text, and was not in the
  list. The rung found it again. Same shape, same author, one rung later.

The blind spot is structural, not careless. Writing a rule feels like standing
outside the thing you are ruling on, and the sentence *"audit all text written
during X"* reads as though it refers to other people's text. It does not: the
rule's own commit is text written during X, on a surface the rule governs.

Both instances were self-excluding in effect — a protocol edit does not travel
with the entry — so neither did damage. **The recurrence is the finding.** A
supervisor who omits himself once has slipped; twice, in the same structural
position, is a pattern, and patterns are what get written down.

Practical form: when you dispatch an audit whose scope is *"everything of kind
K"*, ask whether the dispatch itself is of kind K before writing the list —
and if it is, put it in the list and mark it self-excluded WITH the reason,
rather than leaving it out and hoping the auditor agrees. The auditor deriving
your omission is a worse outcome than you declaring your exemption.


## L-57. A pathspec commit isolates by FILE, not by AUTHOR — two agents in one file have no protection at all

The lab's commit rule, written after four collisions, is: never `git add` then
bare-commit; always `git commit -m "..." -- <paths>`. It works, and it has held
all campaign — against sweeping up *other files*.

It gives no protection when two agents are editing **the same file**. The chief
committed `docs/PRODUCT_LIST.md` with a message about one finding; the diff
contained a concurrent agent's uncommitted work in that same file — **34 lines of
it**, alongside 25 lines the commit's own message did describe.

*[Number corrected 2026-08-11 by Ladder V round 4, which counted the hunks
rather than the diffstat. This lesson first said "59 lines", which is the
commit's TOTAL insertion count, not the swept portion — so a lesson written to
state an unrewritable incident accurately overstated it by 74%, and did so in a
numbered entry future passes would cite. The correction is the lesson's own
point applied to itself: read the diff, not the summary of it.]*
The text was correct and landed byte-unchanged, so nothing was damaged — but
**the commit's message does not describe its own diff**, and history cannot be
rewritten. The agent recorded the provenance in a follow-up commit, which is the
only remedy available after the fact.

The rule as it must now read: a pathspec commit answers *"which files am I
committing?"* and says nothing about *"who else wrote in them."* Before
committing a shared, high-traffic file — a changelog, a status record, an index
— run `git diff <path>` and read it. If it contains work you did not write,
either commit it with attribution in the message, or wait. **Reading your own
diff before committing is the check; the pathspec is only the scope.**

Corollary for supervisors, since this one was mine: the files a chief writes to
most often — the checklist, the changelog — are exactly the files every agent
also writes to. The highest-traffic file in a repo is the one where this rule
has the least protection and the most opportunity to fire.


## L-58. A defect whose only detector expires must be fixed inside its detection window, or logged as permanent

The cold-start test found a class of defect the lab had no name for. Twelve
files had been dated **2026-08-11** while it was still 2026-08-10 — an error
detectable by one cheap check: does any file claim a date in the future? Some
were corrected. Three were not, because their wrong date is in the FILENAME,
and renaming would have broken five committed citations.

Then midnight passed. **The detector expired.** Those filenames are no longer
detectable by any means, because the date they assert has arrived and is now
merely wrong-by-provenance rather than impossible. Nothing distinguishes a file
named for the day it was written from one named for the day after, once that day
comes.

Two rules follow.

**A time-bounded detector defines a deadline, not a convenience.** When the only
thing that can find a defect is a condition that will lapse — a future date, a
process still running, a log not yet rotated, a temporary file, a version still
installed — fixing it is urgent in a way its severity does not convey. A trivial
defect with an expiring detector outranks a serious one you can find any time.

**If it cannot be fixed inside the window, log it as PERMANENT before the window
closes**, with the evidence that identifies it, because afterwards the record is
the only detector left. The three filenames are recorded in exactly this way,
and a note now travels inside each file — the label being wrong is harmless, the
label being *undetectably* wrong is not.

Related in shape, opposite in remedy, to L-42: there the evidence was destroyed
by an action, and the fix was to preserve it; here the evidence decays on its
own, and the fix is to spend the window.


## L-59. `core.filemode=false` silently discards a mode fix — the index says one thing, the tree says another, and the checker reads green

Fixing a tracked script's missing executable bit, an agent found the fix does
not land here. **This repo has `core.filemode` false**, so
`git update-index --chmod=+x` followed by a pathspec commit is **silently
dropped**: the index records 100755, the newly written tree records 100644, and
the guard that checks the tree reads GREEN off a tree that never changed.

The failure mode is the dangerous one: not an error, not a refusal — **a fix
that appears to succeed.** The agent avoided it only because the module's own
docstring warned of it, and it verified against HEAD afterwards, which is the
authority. It used a **one-invocation `-c core.filemode=true`** rather than
changing repo config, because flipping that config would have perturbed the
diffs of five agents working concurrently — the right instinct on a shared tree.

Two rules.

**Verify a mode change against the committed tree, never the index.**
`git ls-tree HEAD -- <path>` is the only statement that matters; `git status`,
`stat`, and the index will all agree with you while the commit disagrees.

**Prefer a scoped `-c` override to a config change on a shared tree.** A repo
config edit is a global side effect on everyone else's working state, made to
fix one file.

This is the same family as L-46 and L-55: an artifact whose appearance and whose
content disagree, where every instrument in the loop reports the appearance.

**[2026-08-11 — it fired twice more the same day, in a repo that already carried
this entry, and the second time it caught the chief.]** A ratchet test
(`test_exec_bits.py`) flagged four files committed between 16:52 and 17:00; two
different workers went to fix their own and both hit this, independently, hours
after L-59 was written down. Neither had read it. **A documented trap is not a
prevented trap** — the lesson lives in a 3,400-line file nobody reads cold, and
the only thing that actually stopped it was a test that fails loudly at the
moment of the mistake. **That is the argument for spending effort on ratchets
rather than on prose**, and it is an argument against this file's own growth as
a mitigation strategy.

Two details worth adding, because the first occurrence's write-up did not have
them and both cost time on the repeat:

- **The index lies more convincingly than expected.** After
  `git update-index --chmod=+x`, `git ls-files -s` prints **`100755`** — the fix
  looks landed. `git status` then reports **"no changes added to commit"**,
  because with `core.filemode=false` it declines to see the mode difference at
  all. So one instrument says fixed, the next says nothing to do, and the commit
  does nothing. Only `git ls-tree HEAD` disagrees, which is what the rule above
  already says and what neither worker did first.
- **The pathspec commit is the mechanism, not the chmod.** `git commit -- <path>`
  **re-derives that path from the working tree**, discarding the staged mode.
  So the failure is not "the chmod did not reach the index" — it did — it is that
  the commit form this lab mandates for shared trees throws it away again. Both
  workers converged on the same fix: `git -c core.fileMode=true commit -- <path>`,
  keeping the pathspec and the scoped override together.

**The uncomfortable part: our own commit discipline is what makes this fire.**
A bare `git commit` would have landed the staged mode bit correctly. The pathspec
rule exists for a good reason (§9.6b: a pathspec isolates by file, not by author)
and it interacts badly with `core.filemode=false`. Two rules, each right, whose
intersection silently drops a change — worth remembering when the next standing
rule is written.


## L-60. An excuse can be inherited without the evidence that earned it

A case family shipped an unreachable residual target and **closed the resulting
false negative by argument**: it showed a monotone four-decade residual history,
which genuinely established that the missing convergence sentence meant nothing
in that case. Correct, and well earned.

An 84-member ensemble then **inherited the dictionary and the excuse — but not
the evidence that made the excuse valid.** Its members do not have a monotone
residual history; 76 of 84 have residuals *rising* over the run's second half.
The sentence "the missing convergence line is a known false negative here" was
true where it was written and false everywhere it travelled, and nothing about
the copied dictionary carried the distinction.

The general shape: **a waiver is evidence-bearing, and the evidence does not
copy with the configuration.** A dictionary, a settings block, a documented
exception, a "known and explained" note — each is a claim about the case that
produced it. Reuse the settings freely; **re-earn the excuse every time**, or
carry the measurement that justifies it into the new case and check that it
still holds.

Practical form: when a case inherits a configuration that comes with a
documented exception, the inheriting case must reproduce the exception's own
evidence before relying on it — and a record citing an exception must cite the
measurement, not the earlier case. *"As established for X"* is a pointer, not a
proof, and it stops being either the moment the new case behaves differently.

## L-61. A guard can be anchored to an encoding of the defect instead of to the defect — ours was anchored to digits, and the defect is about ordinality

Tonight's rank-claim guard was built, tested, and shipped in response to a wrong
ordinal on a travelling document. It found 35 claim-bearing surfaces out of
20,641 paths by derivation rather than by list, its tests pass 13/13, and it
reports *"every travelling surface complies."* Hours later a mechanical sweep
found **three more instances of exactly the defect the guard exists to catch** —
including the **parent sentence that seeded the one the guard was built for** —
and the guard **would not have fired on any of them.**

The reason is the lesson. The guard's pattern is **digit-anchored**: it matches
`rank 1 of N`, `P(rank 1)`, `best/lowest overall`. But a placement claim is not
a claim about digits — digits are one *encoding* of ordinality among several.
The three misses were carried by **a written ordinal**, by the same ordinal
wrapped across a line break, and by **a bare comparative — "the runner-up" —
which names a placement without containing a rank word at all.** The guard was
fitted to the surface form of the single example that motivated it, and it
generalised to nothing.

Two aggravating features make this worth a numbered lesson rather than a bug
report:

**The blindness was already documented and still shipped green.** The file's own
comment admits it cannot see *"a rank claim phrased in words it has no pattern
for."* A known gap, written down by the author, next to a verdict line that says
compliance without qualification. **A caveat in a comment does not reach the
person reading the verdict** — the verdict must carry its own reach, or the
caveat is decoration.

**The instrument built to check the guard failed the same way first.** The sweep's
own line-bounded pass scored 63 of 64 and missed the parent instance, because
that line ends mid-phrase with the entrant's name on the next line — the *third*
time tonight a line-bounded reader has returned a false negative on wrapped
text. The auditor and the audited share a defect because they share an
assumption, and neither one auditing the other will surface it.

*(That "third" was counted, not remembered: the record carries a line-bounded
grep returning **zero** against a file demonstrably containing the string —
which had made three prior verifications unsound — a sweep token falling across
a line break in **both** markdown files, and tonight's. Three encodings of one
assumption, found three times before anyone thought to look for it deliberately.)*

Practical form: **a guard must be anchored to the claim, not to the spelling of
the example that prompted it.** Before shipping one, ask what other forms the
same claim can take — words for digits, comparatives for ordinals, a line break
mid-phrase — and produce a positive control in each form. A guard that fires
only on the instance that inspired it is a regression test wearing a detector's
clothes, and it is worse than no guard, because its green is read as coverage.

## L-62. A test whose verdict is a function of the machine's spare cores is a load sensor wearing a test's clothes — ours was red for ten days and flipped colour in six minutes

A suite test had been red since 2026-08-01. Three agents looked at it and **saw
three different things**, and the natural reading — that some of them were
careless — was wrong. The test asserted that the worker roster takes exactly
three steps. The roster's *shape* turns out to be **a function of the box's
available cores**, not of the code: at capacity ≤ 9 the sweep level and the
solve level coincide and the shape has three steps; at ≥ 10 they separate and it
has four. Forced probes on **identical committed source** produced `[0, 6, 0]`,
`[0, 9, 0]`, `[0, 10, 9, 0]`, `[0, 14, 9, 0]`.

So the red was real, reproducible, and **reporting the wrong variable.** It
flipped inside a single session: capacity 14 and **red at 02:41**, capacity 5 and
**green at 02:47**, after eight other agents' solver jobs landed on the shared
box. For ten days the suite had been telling us how busy the machine was.

Three things make this worth numbering:

**The comment and the assertion had disagreed since birth.** Both landed in the
same commit, 13 seconds after the fix they were written to pin. That fix's own
message records the defect as a **bounce** — a return to zero mid-run — and the
comment forbids exactly that. But the assertion forbids *any change of size*,
which is a **strictly stronger claim** than the workflow, the control room, or
any standing ruling makes. Nobody wrote a wrong test; someone wrote a test that
over-reached its comment by one quantifier, and the machine hid the gap until a
quiet box exposed it.

**The fix had to avoid becoming a loosening.** Deleting an assertion that fails
is not a repair. What makes the replacement stronger rather than weaker is a new
rule: **each level must equal the fan-out actually running** — the slots the
sweep dispatched to, and the slots carrying a live solve. The number is now
pinned **to the run** instead of to a constant, which is the same principle that
made a convergence detector trustworthy elsewhere: gate on a relation the system
states about itself, never on a literal.

**It was verified in both directions, which is what closed it.** In isolated
trees: the old assertion **fails** against HEAD's workflow at forced 24 cores and
**passes** at 8 — identical source, which is the defect demonstrated rather than
argued; and the new test **fails at both capacities** when the original bounce is
restored. A test that only passes has not been shown to test anything.

Practical form: when a test disagrees between runs or between people, **suspect
the environment before the observers**, and force the environment variable both
ways rather than sampling whatever the box happens to offer. On a shared box
where agents run concurrently, any test that reads a resource-derived quantity
must pin that resource explicitly — otherwise its colour is a measurement of the
neighbours.

## L-63. A detector scored on a corpus containing the specimen its rule was named from is reporting training accuracy in the voice of test accuracy

The S6 convergence-target detector was pre-registered and then scored, and its
headline is that it **captured 135 of 135 sentinels and nothing else** — a
number this lab has quoted as evidence the rule generalises. An audit of a
21-case corpus, sent to look for something else entirely, found the number is
**not the held-out result it reads as**.

The detector's own docstring names its motivating sentinel as literally
`p 1e-15;//1e-4;`. That is the **exact byte sequence** in one of the audited
cases' `fvSolution`. And 18 of those 21 logs sit inside the replay corpus the
135-of-135 was scored against. So **the corpus is not independent evidence for a
rule that was plausibly derived from a specimen inside it.** The auditor's
phrasing is the one to keep: *the detector and this corpus are not independent
evidence of each other.*

Nothing about the rule is thereby wrong. The relation it gates on — a target at
or below its own field's linear-solver tolerance — is still a relation the case
states about itself, still constant-free, and still correct on every case
examined. What is wrong is the **evidential weight** the 135-of-135 has been
carrying. A perfect score on a corpus that contains the defining example is
consistent with a rule that generalises and equally consistent with one that
does not, which is precisely the distinction the number was quoted to settle.

The general failure is not specific to detectors. It appears wherever a rule is
**abstracted from cases and then validated on a set that still contains them**:
a regex derived from a stale sentence and then run over the file it came from; a
threshold tuned on the runs it is later used to grade; a heuristic learned from
the failures it then "predicts". In every instance the score is real, the
arithmetic is right, and the inference is unsupported.

Practical form: **when you pre-register a detector, pre-register its corpus's
provenance too** — state which cases motivated the rule and exclude them from the
scored set, or report two numbers (in-sample and held-out) and let the gap speak.
A score quoted without saying whether the defining example was inside it is an
unlabelled mixture of the two things a reader most needs to tell apart.

## L-64. Two durable launchers over one case set are worse than none — and the narrower rule is the one that was earned

A queue died with its agent's turn. A second agent, seeing the work stalled,
started a replacement launcher **without first confirming the first was dead**.
Two solvers ran on the same case for ~25 seconds. The lab already had a rule
about using durable, self-ledgering launchers so work survives an agent's death;
that rule is what made *both* launchers durable, and durability is exactly what
made the collision possible — neither would yield.

The tempting lesson is "use a durable launcher." That is the rule we already had
and it is what caused this. **The rule actually earned is narrower and it is the
opposite shape: two durable launchers over one case set are worse than none**,
because a fragile duplicate dies on its own and a durable one competes. Before
starting a replacement, **confirming the predecessor is dead is the whole job** —
the guard the second launcher did carry (launch only if no log exists) failed
because the first launcher's pool had already created the log without holding it.

The disclosure is the part worth copying. The responsible agent reported the
collision itself, before completion, **named itself as cause in the commit**, and
then **bounded the damage by measurement rather than by argument**: it mapped
every solver process by `/proc/<pid>/cwd` to prove single-writer, checked the
write ladder for rewrites, established that the duplicate died before the first
field write, and put a number on the one real exposure. Retaining an affected
control *with disclosure and a measured bound* is a defensible call; retaining it
because it probably didn't matter is not, and the difference is entirely in
whether a number was produced.

Practical form: durability is a property that must be **unique per work unit**,
not merely present. Any launcher for a case set needs an exclusive claim on it —
and "no output exists yet" is not a claim, because output appears after the race
has already been lost.

## L-65. A gate that fires on a real anomaly while naming the wrong cause has not mis-fired, and treating those as the same thing loses the finding

A pre-registered validity gate voided an experiment when a control moved far past
its threshold. The gate's stated inference was that **the continuation had
introduced a restart transient** — a common-mode cause, which would have moved
every control. It didn't: two of the three controls were flat, so the named
mechanism was **excluded by measurement**.

The gate was therefore mis-specified: it inferred a common-mode cause from a
single-control observation. But it was **not wrong to fire.** What it caught was
real and was worse than what it was looking for — *the control was not a
control.* The case had been chosen precisely because it was among the
best-settled of the whole ensemble, and on continuation it destabilised into a
growing oscillation. It had been in **a quiet phase of an unsteady flow, not at a
steady solution**, and no static settledness measure could have told the
difference.

Two rulings follow, and they generalise past this experiment:

**Do not re-specify a gate after seeing which way it fell.** Even when the
gate's premise is demonstrably false — as it was here — dissolving a gate by
post-hoc argument makes every future gate dissolvable, since the argument is
always available once the outcome is known. The gate stands, the experiment is
void, and the correction goes into the *next* pre-registration.

**Separate what needs the void from what does not.** A control exists to isolate
a *difference*; an observation that is not a difference claim never needed one.
Within-case and univariate results survive a void intact — here, that a case
selected for being well-settled destabilises on continuation, which was the most
important finding in the experiment and is untouched by the gate. Comparative
claims across members die with the void and must be re-earned. Drawing that line
explicitly is what stops a void from either destroying good evidence or becoming
a laundry for bad evidence.

### L-63 — CORRECTION, 2026-08-11, from the independent held-out re-score

L-63 stands as the general lesson and **fails on two specifics**, both found by
the re-score it commissioned. Left in place above rather than rewritten, because
re-basing a lesson onto its own follow-up destroys the record of what was
concluded on what evidence.

**Wrong specimen.** L-63 reads the docstring's sentinel as the copy in
`W2_sparta_runs/cbfs_prop`. The git record points instead at
`dafoam/ladder-b/B3_work` — recoverable only because a **superseded** replay
artifact was retained, which shows the 46 logs then in view came from exactly
four case directories, all four carrying the byte sequence. The sequence appears
in **18 files**, so "the docstring cites this case" was never enough to identify
which. The re-score partitioned both ways rather than choosing.

**The headline survives — scope corrected, not withdrawn.** In-sample 33/33
captured, **held-out 102/102**, zero false captures either side, and the
pre-registered 92/48/20 fire spread turns out to sit **entirely** in the held-out
partition. L-63 was right that the number needed splitting and **wrong that the
split would weaken it**.

**And the real limit is one L-63 did not see, which is worse and more useful.**
An archive-wide sweep finds **every unreachable target in the entire archive is
the same value**: `(1e-15, 1e-12)` ×132 and `(1e-15, 1e-14)` ×4. So the
constant-free relation and the bare constant `target == 1e-15` are
**extensionally the same predicate on this archive** — they agree on all 239
files, in both directions. The 102 held-out captures are copies of the in-sample
specimen propagated by template reuse: **held-out in provenance, in-sample in
content.** The tightest gated ratio is 50×, the median 1000×, the excluded class
0.001× — a **~4.7-decade gap in which the boundary has never been probed.**

So the correct restatement is not about sample partitions at all. Drop *"evidence
the rule generalises"* and say **"evidence the rule tracks the sentinel wherever
the template was copied."** A held-out partition is only held out **with respect
to something**; L-63 checked provenance and never asked whether the held-out
cases were *variants* or *duplicates*. **Copies inflate a denominator without
adding evidence**, and a corpus of clones will hand any rule a perfect held-out
score. The general form deserves its own name:

## L-66. A held-out score over near-duplicate cases measures template reuse, not generalisation — ask how many *distinct* things the corpus contains before quoting an N

Splitting a corpus by provenance is not enough. A rule scored on 102 held-out
cases that are copies of one another has been tested **once**, with the result
reported 102 times. Before quoting a capture rate, count the corpus's
**distinct** configurations — here, 239 files collapse to two `(target,
tolerance)` pairs, and 21 cases collapse to two files by checksum.

The practical test is the one the re-score used and it is cheap: **construct the
crudest possible rival rule** — here, the bare literal `target == 1e-15` — and
check whether it disagrees with your principled rule anywhere in the corpus. If
it never does, your corpus cannot tell the two apart, and every argument for the
principled rule's superiority is currently **theoretical**. That is not a reason
to abandon it; the constant-free relation is still the right rule, because it is
the one that survives contact with a case the archive does not yet contain. It is
a reason to stop citing this corpus as the evidence for it, and to go find or
construct the discriminating case.

## L-67. A defect count that grows because the auditor made copies to audit with, and a search-and-replace that reports success on zero matches

Two failures in one action of mine tonight, both about **an edit that appeared
to succeed**.

**The count.** A sweep re-ran a propagation figure and reported it had grown from
**120 of 365** to **136 of 381**. I published the new number as a correction to
our own stale one. It was not stale. The arithmetic resolves exactly — 381−365 =
16, 136−120 = 16 — and there are **precisely 16 config files under the
continuation directory an auditor had created to do its own audit with**, whose
targets its pre-registration deliberately leaves unchanged. Both numbers are
right for their moment; **neither is a worsening**; the claim-bearing figure
never moved. The agent that caught it put the general form best: *a defect count
that grows because an auditor made copies to audit with is exactly the number
that gets quoted once and corrected never.* **Before publishing a count that has
grown, find out what joined the denominator.** A defect total is a claim about
the world, and the world does not change because we made working copies of it.

**The edit.** In the same action, my in-line correction to that figure **matched
nothing and did not land**, while the commit message announced it as done. The
text I searched for was *"120 of 365 config files carry the defect"*; the record
says *"120 of 365 configuration files carry an unreachable target."* Python's
`str.replace` — like `sed`, like most substitution tools — **returns the input
unchanged when it finds no match, and signals nothing.** The script printed `ok`,
the commit succeeded, and the file was untouched. Only luck made the un-landed
edit the correct outcome.

This is the same shape as the mode-bit fix that the repo config silently
discarded (**L-59**) and the guard whose green was read as coverage (**L-61**):
not an error, not a refusal, **a change that appears to succeed.** It is the most
dangerous failure a tool can have, because every downstream reader — including
the person who made it — takes the absence of an error as evidence of the edit.

Practical form: **assert the match, don't assume it.** Any scripted edit to a
tracked record should fail loudly when its anchor is absent (`assert old in s`),
and any commit claiming a correction should be checked against the diff rather
than against the script's exit code. A commit message is a claim, and it needs
the same evidence as any other.

## L-68. A control's configuration read as production configuration — and a caveat that stayed in the body while the title travelled

An instrument audit reported that the lab's pre-filming discretion gate
*"reports clean over a corpus root that does not exist"*, counting none of 17
transcripts. I republished it as an urgent finding. **It was false.** The
configured root exists, it is the exact path the transcripts live at, the glob
matches precisely those 17, and the shipped gate had **never once printed
`clean`** — run as-is it printed five findings.

The false claim was manufactured by a specific, repeatable mistake. To test the
gate's behaviour on an empty corpus, the auditor had made **byte-identical copies
of the script with `OUT=` repointed** at empty and nonexistent directories — the
correct way to run that control. The defect is that **the control's
configuration was then read back as the production configuration.** A control
is a deliberately broken copy of the system; the moment it is filed beside the
real one, its settings are indistinguishable from findings about the real one.

Two rules follow, and the second is the one that cost most:

**Controls must be self-labelling and disposable.** A scratch copy that differs
from production only in one line will be mistaken for production. Better still,
make the parameter overridable at the call site so no edited copy needs to exist
at all — which is what the fix did.

**A caveat that stays in the body while the title travels reaches nobody.** The
ledger's §4.2 **body was honest** — it showed the overridden `OUT=` right there on
the command line. Its **title** was not. And the title is what propagated: into
the product list, into a second report, and into what I told the director. This
is **L-61 recurring one document level up.** I read a ranked list of titles and
republished them without opening the bodies, which is exactly the reading a
ranked list invites. **If a finding's headline is not true standing alone, the
headline is the defect**, no matter how careful the body is.

The dispatch was still right, and that is the third lesson: the *class* was real
even though the instance was false. The gate genuinely could not distinguish
*"scanned everything and found nothing"* from *"scanned nothing"*, and fixing it
surfaced **8 genuine hits**, an exit code that read green while holding five
findings, and a silent `head -4` truncation that under-reported precisely when a
file had most to say. **Acting on a wrong headline for the right reason is
recoverable; the recovery is to verify before publishing, not to stop acting.**

## L-69. A right conclusion reached through three broken links — and the tell was already sitting in the report's own numbers

An agent disclosed its own launcher collision and argued the collision could not
have caused the anomaly that voided its experiment. It offered a five-link chain.
An independent check confirmed the **conclusion** and falsified **three of the
five links**.

What broke, and why it matters more than the incident:

**A premise assumed, then used to compute the evidence for itself.** The chain
said the duplicate died at Time ≈ 4265, before the first field write. But
`controlDict` carries `startFrom latestTime`, so the duplicate restarted from
wherever the survivor had reached — **7000**, not 4000. "≈4265" is exactly what
you get from the observed wall-clock overlap *if you assume a start at 4000*. The
number looked like a measurement and was a restatement of the assumption. Real
overlap was ~60 s, not 25, and **it crossed a write time.**

**"No rewrites" was checked in the way that could not see one.** A snapshot
directory had been written twice; its mtime was *older than every file inside
it*, which is what a complete overwrite looks like. And the tell was **already in
the original report's own cadence figures** — writes at a steady 34–40 s
throughout, except one gap of 61.9 s followed by one of 17.3 s, summing to a
normal 79 s. The author had printed the evidence against its own claim and read
past it, because the anomaly appears only as a *pair*, and each half alone looks
ordinary.

**The general lesson is about the shape of the argument, not the arithmetic.**
Three links failed and the verdict held, because what actually carried the
exclusion was something the chain never mentioned: **per-snapshot writer
identification** from two independent records — a stored gradient matched at 15
digits, and a file the duplicate never touched — plus the fact that **the
anomaly's onset predates the duplicate by 105 seconds.** A chain of plausible
links is the weakest form of this argument available; **a direct attribution of
each artifact to its writer is the strongest, and it needed no chain at all.**
When you find yourself defending a conclusion link by link, ask what single
measurement would settle it outright.

**Corollary, and it is the durable one: a correct conclusion is not evidence
that the reasoning for it is correct.** Had the check merely confirmed the
verdict and stopped, three false beliefs would have entered the record wearing a
confirmed result's authority — including the belief that the collision touched
only the log, when in fact a field snapshot and nine profile files were replaced,
and that snapshot **still sits inside a published trajectory**.

### Three things that fell out of it

**`startFrom latestTime` makes a duplicate a fork, not a repeat.** It branches
from wherever the survivor reached and writes to the *same snapshot names*. This
is the general form of the collision hazard: a duplicate does not redo old work
harmlessly, it competes for the next filename. It is why a 60-second duplicate
managed to hit a write at all.

**A rewrite leaves a directory older than the files inside it.** A free
double-writer detector — no log, no PID, no cooperation from the writer, and it
works retrospectively on any archive.

**A guard checked before an unbounded wait is not a guard (TOCTOU).** The queue
tested "does this case already have a log?", then slept until the running-job
count dropped, then launched. **A case that acquires a log during the wait is
launched anyway.** L-64's "confirm the predecessor is dead" is necessary and not
sufficient: the check must be *adjacent to* the action, or the window between
them is the whole defect.

## L-70. A test that any writer can redden by documenting a defect correctly teaches the lab to stop documenting defects

A new guard shipped with a regression test asserting **the whole repository
passes**. It went red **within the hour** — not because anyone reintroduced the
defect, but because another agent, writing an audit, **quoted the defect in order
to name it.** The guard was right to flag the quotation: one of its two rules
cannot distinguish *use* from *mention*, because unlike its sibling it has no
correct form that can sit beside the wrong one to disambiguate.

The naive fix is to whitelist the file. The real fix is to notice what the test
was teaching. **A suite that goes red when someone documents a defect accurately
puts every future writer under quiet pressure not to quote defects** — and this
lab's entire method is quoting defects accurately. The test would have degraded
the thing it was protecting.

Two rules follow:

**Scope a guard's severity to what the surface does, not to what the text says.**
The replacement is WARN on a lab record and FAIL only where a surface **travels**
to a reader outside the lab. A record that quotes a bad sentence is doing its job;
a shipping document that contains one is a defect. Same string, opposite meaning,
and only the destination tells them apart.

**Never assert "the whole repository passes" as a regression test.** It couples
every future writer to a guard's precision, and the coupling is invisible until
someone innocent trips it. Assert the narrow things you actually mean: that
nothing which travels disagrees with the source of truth, and that the specific
files you fixed stay fixed.

There is a corollary about controls. The same guard's whole-text control asserts
that a line-bounded reader finds **zero** faults on a fixture where a whole-text
reader finds one — and the assertion carries the message *"the control is void, so
it proves nothing."* **A control that silently becomes vacuous is worse than no
control**, because it keeps reporting success; wiring the vacuity check into the
test itself is how you stop a positive control from quietly retiring.

## L-71. "No rerun existed to contaminate it" and "it was never reproduced" are the same fact, and an audit read it as a virtue

A warm-start audit graded one attempt **COLD-CLEAN** — the strongest cleanliness
verdict it had — with the rationale that it was a *"single-run record; no rerun
existed to contaminate"*. That is literally true and it is the same fact as
**"this result has never been reproduced."** The audit was checking for
contamination and found none, correctly. But the property that guaranteed no
contamination was **the absence of any repetition**, and absence of repetition is
the more important finding by a wide margin — it was invisible because the
instrument was pointed at the other question.

The general shape: **a property that makes one audit's answer clean can be the
very defect a different audit exists to find.** A single-run record cannot be
contaminated by its rerun, cannot disagree with its rerun, and cannot be
falsified by its rerun. Cleanliness here is not evidence of quality; it is the
signature of a measurement that was made once and never questioned. In the same
programme, **eleven attempts on one case had zero deliberate reproductions**, and
the sole clean verdict was resting on that.

Practical form: **when an audit reports a clean result, ask what made it clean.**
If the answer is "there was nothing to compare against," record that as a
finding in its own right and route it to whoever owns reproducibility — do not
let it be consumed as a pass. And when writing a verdict, state the *mechanism*
of the clean result, not just its grade: *"COLD-CLEAN, because no rerun exists"*
carries the warning that *"COLD-CLEAN"* alone destroys.

The same programme supplies the companion lesson. **The instrument for stating an
uncharacterised boundary honestly already existed** — a sibling record says
plainly *"NOT EVALUABLE ON THIS HOST — no reason code was obtainable"* — and was
written four days after the run it was needed for, and never applied to it.
**Having the right instrument and not pointing it at the right case is
indistinguishable, in the record, from not having it.**

## L-72. A suite count is true of a commit, not of a moment — and a failed notification is not evidence that nothing was done

Two measurement errors from the same night, both about **what a number is
attached to**.

**The count.** A commit message in this repo records *"Suite 1309 passed."* A
later sweep, run against a named commit and verified file-by-file, found that
commit defines **1300** test functions. The nine extra were **uncommitted tests
in the working tree** at the moment the total was taken. The number was real when
observed and is **unreproducible by anyone, ever**, including its author — there
is no tree to check it against.

This is not pedantry on a shared box. During that same sweep **HEAD moved eight
commits** and 31 new test functions appeared. The sweeper's own conclusion is the
rule: *"the suite has one resource-dependent test" is true of a commit, not of a
moment*, and it stated which commit. **Any total taken from a working tree that
other agents are committing to must carry the commit it was taken at, or it is a
reading nobody can repeat.** The same applies to defect counts, file counts and
corpus denominators — all of which moved by double digits tonight.

**The notification.** A background agent's completion arrived with status
`failed` and a result field containing one opening sentence — *"I'll start by
reading the specification…"*. I read that as death at the first tool call and
sent a full restart brief. **The agent had already finished the entire sweep**:
231 tool calls, nine full-suite runs. The notification carried the **first** line
of its response, not the last, so completed work was indistinguishable from work
that never started.

Practical form: **before restarting a failed agent, look for its artifacts, not
its status.** A finished agent has committed files, written reports, left a git
trail. And when resuming one whose state you cannot determine, say *"report what
you already completed; do not redo it"* rather than sending a fresh brief — a
restart brief handed to a finished agent invites it to repeat expensive work. This
one declined and did only what was genuinely new, but that was its judgement
rather than my instruction, and the next one may not.

## L-73. An instrument that is least sensitive exactly where the damage is worst — and a signature that two opposite events share

A double-writer detector built tonight keys on a real filesystem fact: **a
directory whose mtime is older than every file inside it has had its contents
replaced**, because rewriting a file in place updates the file but creates no new
directory entry. It works, it found a known contamination and six undisclosed
rewrites, and it needs no log, no PID and no cooperation from the writer.

It also carries two limitations that generalise well past this instrument.

**The signature is shared by an innocent event.** **Appending** to a file leaves
exactly the same trace — an append creates no directory entry either. Specified
without accounting for that, the detector returned **213 hits, mostly innocent
probe directories.** What separates the two is a **peer control**: comparing the
suspect directory against its siblings written by the same process in the same
run. Nothing about the suspect *alone* can distinguish rewrite from append. When
a detector keys on a signature, the first question is not "does the defect
produce this?" but **"what else produces this?"** — and the answer is almost never
"nothing."

**The instrument is least sensitive exactly where the damage is worst.** The peer
control needs uncontaminated peers. Two cases had **16 of 17 directories
rewritten** — so widespread contamination **destroys its own control**, and 96
real rewrites were reported as *unresolved* rather than confirmed. This is a
property, not a bug, and it inverts the usual reading of a clean result: **a case
that is thoroughly corrupted looks quieter than a case corrupted once.** Any
instrument that establishes an anomaly by contrast with a baseline drawn from the
same subject inherits this, and the failure is silent unless the verdict says so.

The three limits the detector's author stated unprompted are the model for how to
ship such a thing: mtimes prove two writes but **cannot prove intent**; **any
later touch, copy or checkout erases the signature permanently** and git records
no mtimes at all, so the denominator bounds *what is still visible, not what
happened*; and **a clean sweep is not proof of no duplicate**, because a duplicate
that never reached a write leaves no artifact anywhere. A detector whose verdict
carries all three can be trusted with a negative result. One that carries none
cannot, however good its positives.

## L-74. "Scored with the shipped helpers" is not independent verification — two implementations that share a defect agree perfectly

This lab adopted a good rule: when scoring a detector, use the **shipped**
helpers rather than a fresh reimplementation, because a second implementation
agreeing with itself proves nothing about the first. That rule is right and it
has caught real problems. Tonight it also failed, in a way worth naming, because
its failure mode is invisible from inside it.

A convergence-target detector was scored against a replay corpus. Both the
detector and the script that **built the corpus** parse OpenFOAM dictionaries,
and **both drop quoted regex keys the same way.** So on exactly the cases where
the parser was blind, the two agreed — *by both being blind.* The scoring
protocol confirmed a defect instead of catching it, and could not have done
otherwise. The gap was not six cases as first reported but **85 of 222 gated
logs**; the other 79 were silently classed on a **partial** reading of their own
dictionaries, which is why the class counts looked healthy.

The rule needs a companion, not a replacement:

**Sharing an implementation makes agreement meaningless in exactly the region
where the implementation is wrong.** Using the shipped helpers protects against
*transcription* error — a fresh reimplementation drifting from the thing that
ships. It gives **zero** protection against a defect the shipped code already
has. These are different threats and only one of them is addressed.

**The check that does work is to compare against the system's own authority.**
The repair here was not written from taste: the resolution rule — literal keys
beat regex, last-declared pattern wins, matching is a full match — was **read out
of OpenFOAM's own source and cited to file and line.** *"It is OpenFOAM's rule,
not a choice of mine."* When two of your components agree, the tiebreaker cannot
be a third component you also wrote; it has to be the external thing they are
both modelling.

Corollary worth keeping: after the repair, the principled constant-free relation
reproduced the crude literal's partition **exactly**, and the only reason the two
had ever differed was **our own parser bug**. The apparent evidence that the
sophisticated rule was doing something the dumb rule could not was, in its
entirety, a defect. See **L-66** — and note that L-66's test (build the crudest
rival and see whether the corpus can tell them apart) would have surfaced this
months of arguing could not.

## L-75. Our own `grep -r` skips ignored files — every sweep denominator in this lab is over what ignore rules permit, and no document said so

An auditor checking a residual discrepancy read the process list and found that
**`grep` in this environment is a shell function**, not `/usr/bin/grep`. It execs
`ugrep -G --ignore-files --hidden -I --exclude-dir=.git …`, and **`--ignore-files`
honours `.gitignore`.**

Confirmed here with a planted control: one token written to `visible.txt` and to
`ignored/f.txt` with `ignored/` in `.gitignore`. **`grep -rl` returned only
`visible.txt`. `find . -exec /usr/bin/grep -l` returned both.** A silent,
confident, clean zero over files that plainly contain the string.

**Why this is worse here than in most repos:** this lab **gitignores its large
case archives.** A repo-wide `grep -r` therefore cannot see the run outputs at
all — including, tonight, the very case archive carrying a contaminated snapshot.
Every "I swept N files and found nothing" produced with `grep -r` is a statement
about **ignore-permitted files**, and none of the documents that quote such
numbers says so.

The recursion is the point, and the auditor named it: **this is the ledger's own
central finding — a verdict that does not state what it swept — recurring in the
tool the auditors used to check the instruments.** Three documents inherited
grep-derived counts without the filter being mentioned once; a fourth could have
inherited them without ever learning it exists.

**The rules that follow:**
- `git ls-files` denominators are sound — same reach by construction, and honest
  about being tracked-only. `find` denominators are sound — no filter.
  **`grep -r` denominators must state that they exclude ignored paths**, or use
  `command grep`, `/usr/bin/grep`, `find -exec`, or `--no-ignore-files`.
- **Counts from `grep -r` and from `find` are not the same measurement.** Do not
  compare or reconcile them. Tonight an irreconcilable gap between two such
  numbers was **this**, not a real discrepancy — and the auditor **killed its own
  running sweep rather than let a fourth incommensurable number land and tempt it
  into a verdict.** That restraint is the correct move: a number you cannot say
  the frame of is worse than no number.

The same audit supplies two companion errors of the same family. A headline
reported *"two 906 MB tarballs left unopened"*; there are two tarballs, of 544 MB
and 362 MB, and **906 MB is their sum written as though it were each one's
size** — so the unexamined residual is 906 MB total, not 1.8 GB. And the auditor
caught itself taking a count from **a file still being written** — its wait
condition fired on first bytes rather than completion — noticing only because the
figure collided with an unrelated one. **A number is defined by its frame, its
filter, and the moment it was taken**, and dropping any of the three produces a
figure that is precise, confident and unusable.

## L-76. Twice in two grades the exception was the label, not the code — and an absolute was the shape both took

A guard was graded twice by an independent agent. Six exceptions the first time,
two the second. **In both rounds the finding that mattered most was not a broken
check — it was a claim the check could not support**, and both times the claim
had the same grammatical shape: **an absolute.**

Round one: the verdict said *"every travelling surface complies"* while omitting
the largest blind spot from its own reach statement. Round two: the code said
*"does not return a board it is unsure of"* and *"can no longer mis-parse
silently"* — while three of fifteen adversarial inputs returned an unchecked
result with no warning. The code in both rounds was better than the sentence
describing it, and the sentence is what a reader acts on.

The author's own diagnosis is the lesson and it is worth quoting: **"twice in two
grades the exception has been the label, and an absolute was the shape both
took."** *Never*, *always*, *cannot*, *every*, *no longer* — each one converts a
tested behaviour into an untested universal, and the gap is invisible until
someone attacks the boundary. The replacement is not weaker, it is *checkable*:
the fixed claim now says a decoy satisfying every property **is** a leaderboard as
far as the function can tell, which is true, testable, and tells the reader
exactly what to worry about.

**Practical form: when a verdict or docstring contains an absolute, treat it as an
unverified claim until someone has tried to falsify it.** Prefer a statement of
what was checked over a statement of what cannot happen. And when a fix lands,
**fix the sentence in the same commit** — a repair that leaves an overreaching
label behind has moved the defect from the code to the record, where it is harder
to find and lives longer.

**CONFIRMED A THIRD TIME, 2026-08-11, and the third is worse than the first two.**
Grade three of the same guard found two new exceptions, **neither of them the two
it was sent to check**, and one is again an absolute in the **same function**:
the docstring says the parser **"NEVER raises"**, and it raises. Its
`read_text(encoding="utf-8")` is guarded by `except OSError`, but a
`UnicodeDecodeError` is a `ValueError` — so **one non-UTF-8 byte in a third-party
file raises out of the function, out of the check, and out of the entire audit
run.** Verified by execution.

Three details make this the strongest instance. It is **the same crash class
already fixed once in this rung** (a regex compile error), through a different
exception type, in the **same function**, with **exactly the blast radius its own
docstring describes**. It is reachable from a file that is *a list of
international author names* — the single most likely place in the corpus for a
non-ASCII byte. And it is **the first of the three absolutes backed by a real code
defect rather than prose**: rounds one and two were labels overreaching sound
code; round three is a label that is false because the code is wrong, in the
direction the label denies.

So the escalation is the lesson: **an absolute in a docstring is not merely a
documentation smell — it marks the place the author stopped testing.** The
grader's method is the one to copy: it **executed every absolute** rather than
reading it, which is how a claim of "never" is falsified in one call.

There is a structural fix worth copying from the same round. The parser had been
anchoring to a **heading named "leaderboard"** and taking the first table after
it — a name-based hook that a decoy heading or an intervening table defeats
silently. The repair **removed the heading from the logic entirely**: every block
of table rows is a candidate, and a candidate qualifies only by properties the
real thing must have — a rank-headed column, ranks reading exactly 1..N once
each, unique usable names — with **exactly one candidate required to qualify, or
the detector goes OFF and says why.** Gate on the properties the object must
have, never on the label someone attached to it.

## L-77. Agents share a scratchpad, and an author silently overwrote a grader's held-out evidence

While verifying a guard, the independent grader built 45 held-out test sentences
and stored them in the session scratchpad. The **author of the guard** later
wrote its own held-out set to **the same path**, under a docstring reading *"My
own held-out set."* The grader discovered this only because it re-read the file
and found someone else's content.

Nothing was ultimately lost — the grader had its sentences in its own committed
document — but the outcome is not the point. **In a lab whose entire method is
independent verification, a grader's evidence being silently replaced by the
author's is the hazard**, regardless of whether that instance was recoverable. It
forced the disjointness of a third sample to be **asserted mechanically instead of
trusted**, which is exactly the cost: the verification became more expensive to
believe.

Practical form: **agents write to uniquely-named subdirectories, never to a
shared scratchpad root**, and evidence that a verdict depends on gets committed
rather than left in scratch. A held-out set that lives only in a shared temp path
is not held out from anything — it is one careless open() away from being the
author's set. Same reasoning as never letting an agent verify its own work: the
independence has to be structural, not a matter of everyone being careful.

## L-78. Storing a measurement whose inputs are not in the repository is what makes it stale — and catching one exception type is what invites the next

Two structural fixes from the end of one rung, both of which end a defect class
rather than an instance.

**The measurement.** A guard published reach figures — how many held-out
sentences it misses. Those figures went stale **three times**: typed into three
surfaces by hand; then made *generated* so they could not disagree with each
other, and still stale, because **generation stopped one level short of the
measurement**; then stale again by the very commit that installed the table,
because that commit also widened a rule. Each fix was correct and each left the
class open.

What finally closed it: **the held-out sentences themselves were committed to the
repository**, and every published figure now recomputes from them at test time.
The author's own statement is the rule — **"storing a measurement whose inputs
are not in the repository is what made all three of these stale."** A number
derived from data nobody can re-run is a number that can only be maintained by
remembering to. Commit the inputs, derive the number, and staleness stops being
possible rather than becoming less likely.

(Detail worth keeping: it took three passes to get the committed evidence file to
carry zero faults *of its own*, and the last two offending literals were **in the
family labels** — the names of the categories, not the examples. A corpus of
defect examples is itself a surface the guard must survive.)

**The exception.** The same function crashed the whole audit twice in one night,
through two different exception types. The first fix caught the specific error
that occurred. **That is what invited the second**: a fix scoped to one exception
type leaves every other type unhandled, and the next one arrives through the gap.
The second fix was **a boundary, not an `except` clause** — the risky read and
parse moved behind a wrapper nothing can escape.

And the scope of that boundary was chosen deliberately, which is the part to
copy: **only the third-party file we do not control is wrapped**, because a check
that catches everything everywhere **hides its own defects** — the failure one
layer above the one being fixed. A blanket try/except is not a stronger version
of a targeted one; it is a different, worse bug.

**Corollary on honest trade-offs.** Making that parser refuse to guess made it
**more fragile in exchange for being safe**: one more `Rank`-headed table in a
third-party file now disables it. The author put that in the verdict line — *"the
guard sits one third-party edit from DISABLED where it used to sit one edit from
WRONG."* That is the right trade and the right way to report it. **A safety
property bought with a fragility cost should name the cost where the reader
meets the verdict**, not in a commit message.

## L-79. A correction can propagate backwards — the prose was right when written and the code moved under it

Tonight's rung fixed a stale published figure by making it **generated**: the
guard computes its own reach numbers from committed sentences, so they cannot
drift between surfaces. That fix was correct and it worked. Two hours later, six
prose copies of those numbers were stale again — **including one inside the
sentence "generated from one provenance table, so it cannot drift."**

Nobody copy-pasted a wrong number. The sequence was:

1. `9f6d8a41` (06:04) — the prose is written, quoting the figures **correctly**.
2. `db096bb7` (06:56) — one of the guard's rules is widened. The generated
   figures move. **The prose does not, and cannot.**

The auditor's phrasing is the lesson: **"not a copy-paste failure — copies with
no way to learn."** Deriving a number at its source protects the source. It gives
**no protection at all** to the sentences that quoted the source before it moved,
and those sentences are what a human reads.

This inverts the usual staleness intuition. We are trained to look for a
correction that landed in one place and missed its copies — a **forward**
propagation failure, where the copies were wrong from birth. This is the mirror:
**every copy was right when written, and the source changed underneath them.**
No review of the copies at the moment they were written would have caught it, and
the author of the widening had no reason to think about prose in three other
documents.

**Practical form.** A generated number is only safe inside the thing that
generates it. The moment it is quoted into prose it becomes a snapshot, and a
snapshot needs a timestamp: **quote the figure with the commit it was taken at**,
so a reader can tell "this was true at `9f6d8a41`" from "this is true now." Where
that is impractical, prefer pointing at the generator instead of restating its
output. And when you widen, tighten or rescore anything whose numbers are
published, **the sweep for quoted copies is part of the change**, not a follow-up
— it is the only moment anyone knows the source moved.

Companion finding from the same pass, and it is a half-learned lesson caught in
the act: **every corpus figure in this rung states its filter and none states its
commit.** The same counting rule returned 503, 573 and 591 within four hours as
the tree grew. L-75 taught us to declare the filter; L-72 taught us to declare
the moment; **we applied the first everywhere and the second almost nowhere.** A
frame is both, and a number carrying one of the two still cannot be reproduced.

## L-80. A mutation test can report the exact opposite of the truth, and the reason is a cache nobody names in a method

Rung V16's exception 3 was that a published figure — rule B's `5 of 5` — had no
committed sentences and no recompute. The repair committed the sentences and
added a recompute. The obligation that comes with a recompute is not to read it
but to **move its inputs and watch it redden**, so the round ran a four-cell
matrix: clean, mutate the published figure, mutate a committed sentence, restore.

Three of the four cells were **wrong**, and wrong in the direction that flatters
nobody: the **clean control failed** and the **mutated case passed**.

The mutation was `_PLACE_REACH_B = (5, 5,` → `(4, 5,`. Same length. The restore
was `cp` from a backup. Same length again. Python's source-based bytecode
invalidation compares **`(mtime, size)`**, and on this box the restored file's
metadata did not force a recompile — so `scripts/__pycache__/self_audit.cpython-312.pyc`
kept serving `(4, 5)` while `/usr/bin/grep` on the source printed `(5, 5)`. For
three consecutive runs the file on disk and the module in memory **disagreed**,
and every one of those runs printed a confident pass or fail.

**What makes this a lesson and not a footnote** is what the inverted matrix
looks like from the inside. A clean control that fails and a mutation that
passes is exactly the signature of *"the recompute is dead — it does not move
when I move its input"*, which is a real defect this lab hunts and would have
been a satisfying find. It was ready to be written up. The only thing that
stopped it was refusing to believe a result whose two controls disagreed with
each other, and going to look at what the interpreter had actually loaded rather
than what the editor had actually written.

**The general shape.** Every other staleness lesson here is about a *number*
going stale against its source (L-78, L-79). This is the same failure one level
down: **the artifact under test went stale against the file the author was
editing.** `git diff` was right, `grep` was right, the test was honest, and the
answer was still backwards, because none of those three reads the thing the
test actually executed.

**Practical form.**

- A mutation test **clears `__pycache__` between every cell**, not once at the
  start. **Not `PYTHONDONTWRITEBYTECODE=1`** — an earlier draft of this lesson
  offered the flag as an equivalent and it is not one. The flag stops Python
  *writing* a `.pyc`; it does nothing about *reading* a stale one, and in this
  scenario a stale one always already exists, because the module was imported
  before the mutation. Executed: with a stale pyc present and an equal-length
  mutation, the mutated cell returns the **clean** value while the file on disk
  holds the mutation — the inversion reproduces with the flag set. A wrong fix
  is worse than no fix: it turns an unverified result into a falsely verified
  one. `PYTHONPYCACHEPREFIX` to a fresh directory per cell also works.
- **Never mutate at equal length** when you can avoid it. `(5, 5,` → `(4, 5,`
  is the worst possible mutation on a mtime+size invalidator. Change the length.
- **Assert the clean control in the same run as the mutation.** A matrix run as
  four separate invocations can invert without any single invocation looking odd;
  run together, "clean fails" is loud immediately.
- When two controls disagree with each other, **stop and ask what was loaded**,
  not what was written. `python3 -c "import m; print(m.THING)"` beside
  `grep THING file` is a two-second check and it is the one that settled this.

**Companion.** The same round hit ordinary read-after-write staleness on this
box independently: a `sed` and a `grep` issued seconds after an edit returned
the *pre-edit* content, which briefly looked like another agent had reverted the
work. It had not. Reads on this filesystem are not reliably coherent with writes
that just landed, and any method here that reads back what it just wrote needs a
`sync` and a re-check before it draws a conclusion — especially before it
concludes that someone else broke something.

## L-81. The wrong count was plausible, self-consistent, and about to be believed — an identity the count implied was the only thing that caught it

**What happened.** Counting the lesson corpus in this very file, a shell pipeline
reported **three** duplicated lesson numbers: L-43, L-63 and **L-15**. There are
**two**. The pipeline was

```
grep -nE "^#+[[:space:]]*\**[[:space:]]*L-[0-9]+" LESSONS.md \
  | sed -E 's/^([0-9]+):.*(L-[0-9]+).*/\2 line \1/'
```

and the defect is the greedy `.*` before the capture: it takes the **last**
`L-<n>` on the line, so a heading that names two lessons is filed under the wrong
one. L-15 was never duplicated; a heading mentioning it in passing was counted as
its second occurrence.

**Why it is a lesson and not a typo.** Nothing about the answer looked wrong.
This corpus is *known* to carry duplicates — L-43 and L-63 really are doubled —
so "three duplicates" sat comfortably inside what a reader already believed.
A wrong count that contradicts your priors gets checked. **A wrong count that
confirms them does not.** The plausibility was supplied by the true part of the
answer, which is what made the false part invisible.

**What caught it** was not review and not a second pair of eyes. It was an
**arithmetic identity the count itself implies**: an anchored Python count gives
**81 heading blocks and 79 distinct numbers**, and 81 − 79 = **2**. Blocks minus
distinct IS the number of duplicate occurrences. The shell version's own output
failed its own identity, and nobody would have run that check unless they went
looking for one.

*Independently re-derived by a second session before this entry was written —
same 81 / 79 / max 80, same duplicate set {43, 63}, same single gap at 52 — which
is why this is filed as measured rather than reported.*

**The rule.** **Every count you publish should carry a second quantity that
constrains it,** and the two should be derived by different routes. Blocks and
distinct numbers constrain each other. Files-considered and files-searched
constrain each other (that is why `scripts/sweep.py` prints both). Sum-of-parts
constrains a total. A single number has nothing to be wrong *against*, and is
believed exactly as far as it is plausible.

**And the narrower rule, because this one keeps costing us:** a `sed`/`grep`
pipeline with a greedy `.*` before a capture group is not a measurement
instrument. When the line may contain the pattern twice, greedy takes the wrong
one **silently and only sometimes** — which is worse than failing, because the
correct majority of the output vouches for the incorrect remainder. Anchor the
capture, or count in Python where the regex is visible and testable. Related:
L-72 (a count is true of a commit, not a moment), L-75 (state the frame),
L-80 (the artifact under test can disagree with the file you are reading).

## L-82. A held-out set built by the party being measured understates the cost — and the size of the understatement is itself measurable, by building a second one

**What happened.** Ladder V rung V16 chose to close *by measurement rather than by
correctness*: the placement guard would stop claiming it was right and start
publishing what it costs. It did that, and the centre of the round was a held-out
non-placement set — sentences containing a rank-like expression that are not board
placements — against which the guard **falsely faults 20 of 41 (49%)**. The number
was recomputed from committed sentences rather than transcribed, controlled against
a switched-off detector, and its per-class breakdown was bound to the published
blind-spot list by a test asserting equality in both directions. As a piece of
measurement engineering it was sound.

The author then named its own weakest point, unprompted: *"the precision denominator
is mine, built with the pattern list in hand, and a set built by someone else will
give a different number."*

It does. As of `64281b6b`, a disjoint 43-sentence set built blind — the author's set
and the pattern definitions both unread until after the sentences existed — measured
**19 of 25 (76%)** under the author's own admission rule, unchanged. Fisher exact
two-sided **p = 0.040**; Wilson 95% intervals 57–89% against 34–64%, so the
independent *lower* bound sits above the author's point estimate.

**The number that says why.** Splitting the independent set by where its classes came
from:

| classes | admitted | falsely faulted |
|---|---|---|
| the four the ruling itself names | 15 | 9 (60%) |
| the seven the grader invented | 10 | **10 (100%)** |

On shapes the author had *no hint of*, the guard falsely faulted **everything it
looked at**. The author's 49% is not a property of the guard. It is a property of the
guard **and** of how much its measurer already knew about it.

**Why this is not L-74 restated.** L-74 says a check built with the same knowledge as
the thing it checks measures transcription fidelity, not the world — it tells you to
distrust the number. L-82 says the distrust is **quantifiable for the price of one
more sample**, and that the gap has a predictable sign: the insider's number is the
optimistic one, because the shapes an insider reaches for are the shapes already
fixed. The remedy is not "be more careful building the set." No amount of care makes
an author blind to their own patterns. The remedy is a **second set with a different
author**, reported as its own row.

**The lab already knew this and had already solved it — one screen higher in the same
file.** `_PLACE_REACH` publishes **three** recall rows, each naming who built it and
whether they were blind, under a note reading *"forty-odd sentences is a small one and
two honest sets disagree by twenty points."* `_PLACE_PRECISION` publishes **one** row,
from the least independent possible source, and calls it *"a WORST CASE on hard
sentences."* The same document contains both the disease and the cure, and the cure
was written first. **A practice adopted for one figure does not propagate to the next
figure by itself** — nobody re-derives a convention when they are busy being right
about something else.

**And the failure it produced is L-76's, again.** "Worst case" is an absolute. Execution
falsified it. That is the fourth absolute this one rung has had to withdraw, and the
first three were withdrawn by the author's own sweep of its own added lines — which
found two more. A sweep for absolutes finds absolutes; it does not find an absolute
whose falsification requires *building a second instrument*.

**The rule.** Any figure a lab publishes about **its own cost** carries the provenance
of the sample it was measured on — who built it, and whether they could see the thing
being measured. One row is an anecdote with a percentage sign. Where the figure is
load-bearing, commission the second row before publishing the first, and if the two
disagree, publish both and let the disagreement be the finding. Related: L-74 (the
check that shares the knowledge), L-66 (overlap measures template reuse — assert
disjointness, never trust it), L-75 (state the frame), L-76 (a bounded claim is not a
false one), L-79 (recompute, never transcribe).

## L-83. Fixing a circular measurement moves the circle up one level, onto the test that guards it — and the move is silent, because the test still looks tight

**Where:** Ladder V rung V16, grade round 7 (`db18553b`) and round 8 (`5e4a0cc5`).
`scripts/self_audit.py`, `sdk/tests/test_rank_claim_surfaces.py`.

**The setup.** V16's closing condition was that the guard **state what it costs**: publish
a precision figure and enumerate the false-FAULT classes, with a ruling that a shape may
stand unfixed *provided it is counted in the figure and named in the list*. The proviso got
a test, `test_every_false_fault_class_is_counted_and_named`, and by every ordinary standard
it was a good one — dict equality in **both** directions plus a sum, so a shape could not be
counted in the figure and quietly dropped from the list, or the reverse. It was read by a
grader, verified against the numbers, and reported as binding.

**It computed both sides over the author's own set.** So a test whose entire subject is
*"every false-FAULT class is counted and named"* could only ever see classes the author had
already thought of. The measured half was fixed — L-74 was applied to the **figure**, and a
second, blind set was commissioned exactly as L-74 and L-82 say to. Nobody applied it to the
**test guarding the figure**, which sat one level up and inherited the defect intact.

**What it cost:** two false-FAULT shapes — a placement on a different explicitly named
ranking, and a negated or interrogative ordinal — faulting at 2 of 2 apiece, counted in no
figure and named in no list, on a guard whose rule-A fault on a travelling surface is FAIL
severity. Neither was exotic. A citation ranking and a denial are things a submission
document contains.

**Why it survived a careful reading.** The test *was* tight. Every property it asserted, it
asserted in both directions. What it could not do was widen its own denominator, and nothing
in the test's text says what its denominator is — the set arrives as `self._held_out(...)`
and reads like an input rather than like the boundary of the claim. **A test's binding
strength and its coverage are different quantities, and reviewing the first tells you
nothing about the second.**

**The rule.** When you fix a circular measurement by commissioning an external referent, ask
immediately: *what else in this repair is scored by the party being measured?* The figure was
the obvious answer and it was not the only one. Walk one level up — to the test, to the test's
fixture, to whoever writes the mapping between the outsider's vocabulary and yours — and stop
only when the last author-written step is **named in the record** rather than eliminated,
because it usually cannot be eliminated. Round 8's fix leaves exactly one such step (which of
the outsider's sentences belongs to which named class is still the author's judgment) and
that step is filed as docket D47 rather than reported as fully external.

**The general form, which is the part worth keeping.** Every self-measurement bottoms out in
a step its own author writes. Each repair moves that step further from the number and makes
it harder to see. **The honest end state is not "no circularity" — it is "the circularity is
one step wide, and here is which step."** Related: L-74 (a check sharing the knowledge of the
thing it checks measures transcription fidelity), L-82 (the insider's number is the optimistic
one, and the gap is measurable for the price of one more sample), L-76 (execution falsifies
absolutes; keep the falsified claim, stop asserting it), L-79 (recompute, never transcribe).

## L-84. A positive control proves an instrument can fire. It does not prove its reach, and it does not prove it fires only where it should — two failures the same night, opposite halves of one missing control

**2026-08-11.** Two independent method failures, by two different agents, hours apart, on
unrelated subjects. Both authors had run a positive control. Both controls passed. Both
numbers were wrong, and **in opposite directions** — which is what makes the pair worth one
entry rather than two.

**Failure one: the frame had an edge the control could not reach.** A sweep asked how many
tracked solver logs are cited by exact path in committed markdown and answered **zero**. Its
positive control passed convincingly — the harvester found **13** real file citations, so it
demonstrably fired. But the harvester matched only `*_runs/`-shaped path tokens, and the one
real log citation lives under `tmr/runs/` — **a slash where the pattern wanted an
underscore**. The filter produced the zero, not the corpus. **No number of true positives
inside the frame could ever have revealed that the frame had an edge**, because every one of
them was inside it.

**Failure two: the widening bought recall and nobody measured what it cost.** An audit
searched for checks that declare their own blind spots, and widened the search from the word
`blind` to a seven-pattern regex with six paraphrases — a reasonable move, made to avoid
missing checks that phrase it differently. It reported **4 of 30** against a published **3 of
34**. The extra hit was a **false positive**: the matched phrase *"this function cannot see
what its caller put in it"* is the check **reporting a defect it found in the audited code**,
not declaring its own reach. The widening had no must-not-match set, so nothing measured its
precision. **The audit committed, while auditing it, the exact defect it was auditing** — four
recall figures and no precision figure.

**The rule, both halves, and neither is sufficient alone:**

> **A control that only shows an instrument firing is half a control.**
> **The other half is a set it must NOT fire on** — planted outside the frame to test reach,
> and planted just inside the boundary to test precision.

For a **sweep**: plant a target in a location shaped differently from the pattern, not just a
target the pattern already matches. The control for a `*_runs/` harvester is a citation in a
`runs/` directory.

For a **matcher you widen**: every paraphrase added to buy recall needs a near-miss it must
reject, measured, before the figure ships. Widening without a precision set is not a
refinement; it is an unmeasured trade.

**How both were caught, which is the operational point.** Failure one was caught by an
independent auditor with a different harvester. Failure two was caught **by asking the
auditor for its frame instead of overruling it** — two agents each holding a number, and the
disagreement resolved into a withdrawal *and* a lesson only because the question asked was
"what did you measure?" rather than "you are wrong." Neither was caught by its author, and
neither could have been: an instrument's blind spot is not visible from inside it.

**The uncomfortable corollary.** Every clean zero in this corpus produced by a pattern-based
sweep is owed the reach half of this control, and most of them do not have it. A zero is the
cheapest thing to publish and the most expensive thing to have wrong, because nothing about
it looks like a failure.

Related: L-74 (a check sharing the knowledge of the thing it checks measures transcription
fidelity), L-75 (the frame is part of the number), L-82 (the insider's set understates, and
the gap is measurable by building a second one), L-83 (fixing a circular measurement moves
the circle up one level).

---

## L-85. A number that has moved five times in four days is not a number, it is a measurement — and the argument against typing it is the movement itself, not the tidiness of deriving it

**The record, and it is the whole lesson.** One figure inside
`check_board_placement_words`' verdict — the live rule-A fault count — read
**2**, then **34**, then **53**, then **56**, then **61**, across four days.
Nobody edited the sentence carrying it between the last three readings. Twice it
moved *under a grader who had been sent to check it*, which is the interesting
half: the number changed while being audited, without the auditor touching it.

It was typed as a literal `2` when it was written, and the `2` was true that day.
Every later reading falsified it, and each falsification arrived as a surprise to
somebody reading the verdict rather than as a test failure, because **a literal
agrees with itself forever.**

**Why "just derive it" is the conclusion but not the argument.** The repair —
accumulate the count from the sweep's own verdicts and interpolate it — is
obvious once stated, and obviousness is exactly the trap: a derived figure and a
lucky literal are indistinguishable on the day they agree. The proof that a
figure is derived is a **mutation**: replace the interpolation with a hardcoded
literal *of the same digits*, plant known faults, and require the emitted figure
to stop tracking. Executed here — derived code emitted 61 pristine and 63 with
two plants, while a hardcoded `61` emitted 61 against a true 63. **The mutation
kills the literal; agreement does not prove derivation.**

**THE COROLLARY THAT COSTS MORE, and it is why this lesson is not only about
literals.** A rate is a literal's sophisticated cousin: it looks derived because
it has a numerator and a denominator, and it is gameable at the denominator. On
the same guard, the *same 20 errors* read **71%** under one admission predicate
and **49%** under another — a 23-point swing with the numerator untouched. So a
pre-registered threshold on a rate, without a pre-registered **admission
predicate**, is not a threshold: whoever chooses which sentences count chooses
the verdict. **Binding the number without binding what it is measured over
reproduces the defect one level up** — L-83's move exactly, in a second guise.

**The operational rule.** Any figure a verdict *states* must be (a) derived from
the run that states it, (b) proved derived by mutation rather than by agreement,
and (c) if it is a ratio, published with the admission predicate that fixes its
denominator. A figure failing (c) is not wrong; it is **unfalsifiable**, which is
worse.

Related: L-74 (a check sharing the knowledge of the thing it checks measures
transcription fidelity), L-75 (the frame is part of the number), L-83 (fixing a
circular measurement moves the circle up one level), L-84 (a positive control
proves an instrument can fire, not its reach).

---

## L-86. A restructure invalidates every pointer that was true when it was written, and a disclosure written from the restructurer's memory of what it broke is not a measurement of what it broke

**The incident, and the arithmetic is the lesson.** A repair pass on the closure
package regrouped `evidence/` from a flat list of nine documents into `frozen/`,
`audits/` and `reproduction/`. The same pass noticed that the move had broken two
citations inside the two frozen artifacts, disclosed them as "exception 9", wrote
a reading rule for them, and said in terms: *"Only those two citations are
affected."* The package's index then said **"Nine departures are on record"** and
**"All nine departures are set out with their locations"**, which is a claim of
completeness.

**Measured rather than recalled, the move broke ten pointers, not two.** The
enumeration that produced ten, run from the repository root:

* Bare citations inside the frozen bytes: match every
  `[\w./-]+\.(?:md|json|py|csv)` token in the two frozen documents against the
  basenames the package ships. That returns **four** sites naming three files,
  not two. The two missed were both `R5_RULE_FREEZE.md`, at lines 13 and 192.
* Prose pointers in the audit records: five files under `audits/` each told a
  reader to see `README.md` "in this directory" for a named section. After the
  move the README beside them is a 21-line folder index holding neither section;
  both are one level up.
* One inside a shell command: a shipped re-derivation command still named the
  pre-move path and raised `FileNotFoundError` when run verbatim.

An independent cold verification of the same package found **five** of the ten
and reported them as five. The brief written from that verification repeated
five. Ten is what the enumeration returns. **Every party in the chain was working
from a recollection of the move, and each recollection was short by a different
amount.**

**The half that is worse than silence.** Exception 9's reading rule read: *"a
bare `.md` filename inside either frozen document that names a file this package
ships is to be read as `evidence/audits/<name>`."* Applied to the two sites it
had missed, that rule sends a reader to an `R5_RULE_FREEZE.md` under `audits/`,
**a path the package does not have**, when the file is sitting in `frozen/`. A
disclosure that is incomplete leaves a reader where they were. A disclosure whose
rule is derived from the incomplete list actively misdirects, and it does so
under the authority of having been disclosed.

**What would have caught it, and one of the two is not a path check.** Five of
the ten broken pointers **resolved**. `README.md` written in
`evidence/audits/CLOSURE_METHODS_COMPARISON.md` names a real file. No path
resolver can see that it is wrong, because nothing is unresolvable. What sees it
is a **section** check: parse a citation of the form `` `<path>` under
"<Section>" ``, resolve the path by the same convention a reader would, and
require the target document to carry a heading matching the section. On the
broken five that check fires immediately, naming the headings the target does
have. So:

1. After any move, re-resolve **every** path-like token in the tree from the file
   it is written in, including tokens inside fenced blocks and inside backticked
   shell commands, which is where the `FileNotFoundError` one lived.
2. Check **section** references separately, because a pointer can resolve and
   still be false, and that is the majority case here, five of ten.
3. Any disclosure stating a count must ship the command that produced the count,
   and that command must be re-run by the package's own checker on every run. The
   exception-9 count is now enumerated by the checker and fails if it moves, so
   the completeness claim is measured rather than asserted.

**The generalisable form.** A restructure is not a diff over content, it is a
diff over the ground every pointer stands on, and the set of pointers it
invalidates is a fact about the corpus rather than about the person who moved the
files. Ask what broke, not what you remember breaking. The distance between those
two, here, was a factor of five.

Related: L-82 (a set built by the party being measured understates, and the
understatement is itself measurable by building a second one), L-83 (fixing a
circular measurement moves the circle up one level), L-43 (an instrument that
cannot see the evidence reports absence, not innocence), L-87 (a control that
plants only the defects its author imagined certifies the author's imagination).

---

## L-87. A control that plants only the defects its author imagined certifies the author's imagination, not the checker; the missing shapes are found by breaking the checker on copies

**The incident.** `scripts/check_consistency.py` in the closure package ran six
cross-file checks and carried a planted-error control on the reasoning that **a
checker that cannot fail is not a checker.** The control planted two defects,
caught both, and printed `PASS` on every run. The package then went to an
independent cold verification, which returned NOT FINISHED with **sixteen**
findings. The checker had been green over every one of them.

**The two plants were not a sample of the defect space. They were a sample of the
author's.** Reproduced on copies, one shape at a time, plant and run and record
the exit code:

| shape planted | old checker | why it was invisible |
|---|---|---|
| one of `README.md`'s three occurrences of `-2.203` changed, two left intact | `rc=0` | figures were matched per file, so a file disagreeing with itself is not a cross-file disagreement |
| a `` `../<name>.md` `` reference broken | `rc=0` | the in-package test asked whether the first component was a top-level directory. The author's own plant used `../evidence/<name>`, whose head **is** one; the adjacent shape's head is a filename |
| a path broken inside a backticked span containing spaces | `rc=0` | spans with spaces were skipped whole, and a span with spaces is what a shell command in prose looks like |
| a citation repointed at a `README.md` that exists and lacks the cited section | `rc=0` | `README.md` was on the bare-name exemption list, and there was no section check at all |
| the inventory table row for `records/MANIFEST.json` deleted | `rc=0` | the inventory test asked whether the path appeared anywhere in the file, and it appears eight more times |
| a stray `scripts/__pycache__/*.pyc`, which `.gitignore` excludes | `rc=1` | the walk did not honour `.gitignore`, so the script failed, **aborted its own control**, and printed that nothing it reported could be trusted, on a package with nothing wrong with it |

Five shapes green that should have been red, and one red that should have been
silent. The author's `../evidence/<name>` plant and the live `../<name>` defect
differ by one path component; the plant was caught and five real instances of its
neighbour were not.

**The technique, and it is the transferable part: break the checker on copies.**
Copy the package to a temporary directory, plant exactly one defect, run **the
copy's own checker**, record the exit code, discard the copy. It costs a few
seconds per shape, it needs no cooperation from the checker, and it is the only
way to learn what a green tick is worth. Running it against the shipped tree and
the shipped checker is what turned "the checker passes" into the table above.

**What would have caught it: derive the plant list from the corpus, not from the
author.** A control's shapes are enumerable rather than imaginable:

* For a path check, enumerate the distinct **shapes** of path token the corpus
  actually contains, bare name, `dir/...`, `../dir/...`, `../name`, inside a
  fence, inside a backticked command, and require one plant per shape. The corpus
  contained `../name`; the control did not.
* For a figure check, wherever any file states a pinned figure more than once,
  require a plant at multiplicity greater than one. The pin is now a map from
  file to **occurrence count**, generated from the tree, so a partial edit fails.
* For any check with an exemption list, require a plant that the exemption hides.
  `README.md` was exempt; the plant that exposes it is a citation to a section
  that README does not have.
* Require at least one **negative** plant: a file the package deliberately
  ignores, asserting the checker stays silent. Without it, "fails when it should"
  is half a control, which is L-84's point in a second guise.

**Measured after the rebuild**, same six shapes, same harness: five caught, and
the stray bytecode ignored, with the ordinary run planting all six every time and
exiting non-zero if any is missed or if the ignorable one is reported.

**The uncomfortable corollary.** The rebuilt control is still an author's list.
It is a longer list, drawn from a corpus rather than from memory, and it is
falsifiable in the same way the old one was: by someone breaking this checker on
copies with a shape neither of us thought of. That is not a reason to trust it
less than the old one. It is the reason the technique, and not the list, is what
this entry records.

Related: L-84 (a positive control proves an instrument can fire, not its reach,
and not that it fires only where it should), L-85 (mutation kills the literal;
agreement does not prove derivation), L-75 (our own sweeps inherit ignore rules,
and here the inverse cost the same: a sweep that ignored `.gitignore` failed a
correct package), L-43 (the audit instrument has its own blind spots), L-86 (a
disclosure written from memory of a restructure is not a measurement of it).

---

## L-88. A quantity the discretisation forces cannot gate anything, and the author who wrote the gate is the last person able to see it — the test is whether the number is already right before the solve is

**2026-08-17, F14 thermal ladder.** A rung pre-registered "boundary heat
imbalance above 20 percent on an early, unconverged snapshot" as the positive
control for its heat-balance gate. **Measured: 0.0128 percent at iteration 10,
and never above 0.13 percent at any iteration of the run.** The prediction did
not miss by a factor; it was the wrong kind of quantity.

**The reason, and it generalises past heat.** On a sealed, impermeable, steady
case the discrete temperature equation is solved to a tight linear tolerance at
every outer iteration; `div(phi,T)` integrates to zero over the domain because
the flux field is conservative and no wall passes mass; so the boundary
conduction terms are **forced to sum to zero at every iteration, converged or
not**. The residual few hundredths of a percent is linear-solver tolerance and
continuity residue. The gate was reading its own discretisation.

**What would have caught it, and it costs one audit.** Ask the quantity to be
*wrong* and see whether it can be. Concretely: **evaluate the gate quantity on a
deliberately unconverged field and see whether its error tracks the solver
residual.** A quantity that is already at its final value on iteration 10 is an
identity. A quantity whose error falls with the residual is a measurement.
Re-run at K1c on the same case class, this separates cleanly:

| | sealed, no source | the same mesh with a planted source |
| --- | --- | --- |
| iteration 10 / 100 | 0.0128 % | −24.139 % |
| converged | ~0.000000005 % | +2.3876e-09 % |
| decades of movement | none | **seven**, tracking the T residual |

One of those two quantities measures the solution. The other measures the
discretisation. **They are computed by the same script, on the same case, from
the same field**, and nothing about the printed number distinguishes them —
which is why the distinction has to be a stamp on the report and not a habit of
the reader. It is now `closure_is_identity_class` in `scripts/heat_balance.py`
and `heat_balance_closure_is_evidence_on_sealed_case: false` in
`docs/physics_rules.yaml`.

**THE COROLLARY THAT ALMOST GOT COMMITTED AS A FIX, and it is the sharper half.**
The same rung filed a proposal to repair a cosmetic wart: when every patch
carries heat outward the imbalance denominator is zero and the script printed
`nan`, so the proposal was to normalise by `max(sum(Q>0), |sum(Q<0)|)` and "give
the case a real percentage instead". **That would have produced exactly
100.0000 percent, for every such case, whatever the defect size, forever** —
because with no inward patch `sum(Q<0)` *is* the net, so the ratio is
|net|/|net| = 1 identically. The proposal was to cure an identity by installing
a second one. It is not hypothetical: plant the mirror defect, a *sink* instead
of a source, so every patch carries heat inward, and the **existing** code
already prints `100.000000000 %`. Measured, not argued.

> **An undefined number is more honest than a defined constant.** `nan` at least
> refuses. A number that is 100.0000 every time reads as a measurement to every
> reader who did not derive it, and the first thing anyone does with a
> percentage is compare it to a threshold.

The proposal was closed by **rejecting its remedy and adopting its complaint**:
the ratio is now reported as UNDEFINED with a named reason and the watts stated,
and the case still fails. Proved not-more-permissive two ways — algebraically
(a case that passed satisfied |Q_net| < Q_in, so the new test finds it defined
and unchanged) and by running the old and new scripts over the same 13 sets of
fields: **0 verdict changes, 0 pre-existing keys moved.**

**And the sweep for identities is not finished, because they hide at the
denominator too.** The same measurement found the old ratio reporting
**6.25e+22 percent** on a case where one adiabatic patch carried +7.9e-24 W of
floating-point residue. `Q_in > 0` was true, so the guard passed, and the
denominator was noise. The test is not "is the denominator non-zero"; it is
"is the denominator the thing the ratio claims to be measured against".

Related: L-83 (fixing a circular measurement moves the circle up one level — and
here the proposed fix moved it sideways instead), L-84 (a positive control proves
an instrument can fire, not its reach), L-85 (a figure a verdict states must be
derived from the run that states it, and proved derived by mutation).

---

## L-89. Residuals measure the change per iteration, not the distance to the answer, and the gap between those widens with the mesh — so refinement can move you further from the truth while every convergence light stays green

**2026-08-17, F14 thermal ladder, and it changed a rung's result.** A laminar
cavity rung ran four Rayleigh numbers on a mandatory two-mesh pair each. Every
case met its own `residualControl` and printed the solver's own
`SIMPLE solution converged` statement. Every **coarse** mesh had genuinely
settled. Every **fine** mesh had not, and missed the criterion on the graded
quantity by two to three orders of magnitude:

| | coarse | fine |
| --- | ---: | ---: |
| Ra 1e3 | 0.0004 % | **2.19 %** |
| Ra 1e4 | 0.0084 % | **3.98 %** |
| Ra 1e5 | 0.0031 % | **4.67 %** |
| g = 0 control, 128² | — | **14.65 %** |

against a criterion of 0.02 percent. **Had the rung graded on "the residuals
stopped moving", its Ra = 1e3 pair would have reported a FINE mesh further from
the published benchmark than its own COARSE mesh — 1.0940 against 1.1191 — and
a mesh-convergence claim would have been built on iteration error.**

**The mechanism, which is why this is a rule and not an anecdote.** An
under-relaxed SIMPLE outer loop propagates the smooth, domain-scale modes at a
rate that falls off like **1/N²**. Doubling the mesh therefore needs roughly
**four times** the iterations to travel the same distance to the fixed point.
The residual, meanwhile, is a per-iteration difference: it goes quiet on
schedule regardless, and it goes quiet *sooner* on the finer mesh because each
step is smaller. **The two curves move in opposite directions with refinement.**
The g = 0 control is the clean demonstration: its exact answer is Nu = 1, and
after 3000 iterations it read 1.328 with the core still near its initial
uniform temperature, residuals nominal.

**What would have caught it, and it is two things, both cheap.**

1. **Gate the graded quantity, not the residuals** — the peak-to-peak spread of
   the number the rung is actually judged on, over a **fixed** iteration window.
   Not the endpoint difference over that window: a case approaching steady state
   as a decaying oscillation whose period is near the window length can be read
   at a phase where the two ends agree while the quantity is still swinging by
   ten times the band between them (measured: one case oscillating with a period
   of about 400 iterations against a 400-iteration window). Not a fraction of
   the run either: a last-quarter window silently loosens as a run is extended,
   so the same case passes by being run longer. On this lab's own data the
   last-quarter statistic reads **2.164275 percent** on a case whose gated
   window reads **0.002813 percent**.
2. **A two-mesh pair is itself an instrument, if you read it in the right
   order.** When refinement moves a quantity *away* from the reference, the
   first hypothesis is iteration error, not mesh error. A monotone approach is
   what a converged mesh study looks like; a non-monotone one is a question
   about convergence before it is a claim about discretisation.

**The rule bites its own author.** This lesson's own verification rung built six
control cases, ran them to `residualControl`, and every one of them stopped at
685 to 793 iterations with peak-to-peak spreads of **0.176 to 0.575 percent**
against the 0.02 percent criterion. The new check fired on all six. Re-run to
4000 iterations they pass at 0.000e+00 to 1.8e-08 percent — and the number those
controls exist to report, the recovery of a planted heat source, improved by
**four orders of magnitude**, from −7.9e-05 percent to +2.4e-09 percent. A rule
that only ever fires on other people's runs has not been tested.

Related: L-88 (a quantity the discretisation forces cannot gate anything), L-85
(a number that has moved is a measurement, not a literal), L-75 (the frame is
part of the number).

---

## L-90. Documentation written before the run it documents has finished is a forecast, and it fails in the one direction that costs the reader everything — following it

**2026-08-17, and twice in one campaign, by different hands.** Both times the
prose was written while the thing it described was still executing, and both
times it was wrong in the same direction: it described the *intended* run rather
than the one that happened.

- **A reproduction recipe named the command that had to be abandoned.** A run
  tree's README told a reader to rebuild its hardest case with
  `./continue_cases.sh 24000`. That invocation sets `writeInterval` equal to
  `endTime`; the case met its convergence criterion at iteration 6400, had no
  scheduled write until 24000, and the build has `writeNowSignal -1` so a
  running solver cannot be asked to write. It was **killed and re-run** with
  intermediate writes, at a cost of about 9.8 core-minutes. The README, written
  before that happened, still recommended it. **A reader following the recipe
  literally would have reproduced the failure rather than the result.**
- **A snapshot README claimed "every case" while holding nine of eleven.** Same
  campaign, same cause: the sentence was true of the plan and false of the
  directory.

**Why this specific failure is worse than an ordinary stale document.** Most
stale prose is merely *believed*. A recipe is **executed**. The reader spends
compute on it, and the failure arrives as a dead run with no obvious cause,
because the instructions look authoritative and the state they describe once
existed.

**What would have caught it — and it is not "review the document".**

> **Write documentation against the committed state, then follow your own
> instructions literally, from a clean checkout, before calling them done.**

Literally: in a fresh worktree, paste your own commands, run them, and compare
the output to what your document says the output is. This is the only check that
distinguishes "I described what I meant to do" from "I described what happens".
It catches the abandoned command, the missing rebuild step, the path that only
exists in your scratch directory, and the count that was true an hour ago. It is
also the only one that runs at the same moment the document is written, which is
the moment the error is made.

This lesson's own rung records the recipe it published, the fact that it was
executed in a clean detached worktree before publication, and the one thing the
recipe cannot reproduce bit-for-bit (a gitignored mesh, rebuilt by `blockMesh`,
which is why the rebuild step is not optional). **A recipe with a known
irreproducible step, stated, is honest. A recipe nobody has run is a guess.**

Related: L-85 (a figure a verdict states must be derived from the run that
states it), L-84 (a control that only shows an instrument firing is half a
control), L-53 (two verification passes running at once can invalidate each
other, and neither can see it).

---

## L-91. A control case copied from another case inherits that case's evidence, and the evidence outlives the thing it was evidence for

**2026-08-17, caught by the check it was written to install, on the run that was
installing it.** A rung needed a **negative** control: a thermal case with no
planted heat source, which the auditor must pass, guarding against a check so
loose it fires on anything. It was built the obvious way — copy the committed
planted-source case, delete `constant/fvOptions`, re-run.

The copy brought the original's **solver logs** with it. The fresh solve
overwrote `log.buoyantBoussinesqSimpleFoam` and left
`log.buoyantBoussinesqSimpleFoam.stage2` and `.stage3` untouched, because the
original had run in three stages and the new one ran in one. So the no-source
control sat on disk holding **one log saying `No finite volume options present`
and two saying `Selecting finite volume options ... Source: heatPlant`.**

**A witness that read "any log" would have reported the negative control as
planted.** It would then have "passed" for the wrong reason, and the whole
control set would have been worthless in the specific way that leaves no trace:
every number present, every exit code plausible.

**What caught it, and it is a design rule rather than a habit.**

> **When several artefacts answer the same question, disagreement is an answer
> in itself — and it is never resolved by a vote.** A case holding logs that
> contradict each other is a case holding a history it did not all run. Report
> `disagreement` and refuse the verdict; picking either reading invents the
> history.

The witness now returns four states — `constructed`, `none`, `disagreement`,
`no_log` — and the last two are UNKNOWN to every caller. The three-valued answer
is the point: `no_log` must not be reported as "no source", because absence of
evidence arrived by a different route than evidence of absence.

**The narrower operational rule, for anyone building a control by copying:**
**strip the parent's evidence before you run, not after you read.** Logs,
`postProcessing/`, time directories, cost files. Whatever a checker will later
read as testimony, a copy has already forged. It is one `rm -f log.*` and it is
the difference between a control and a decoration.

Related: L-84 (a positive control proves an instrument can fire, not its reach —
this is the negative control's version of the same hole), L-87 (a control that
plants only the defects its author imagined certifies the author's imagination
— this one was not planted at all, and that is how the shape was found), L-88 (a
quantity the discretisation forces cannot gate anything), L-75 (the frame is
part of the number).

## L-92. An instrument that reads the index is measuring a per-machine, per-moment scratch state that no reader of the repository will ever see — and the error grows on its own, because every commit made the private-index way leaves a committed file with no index entry

**The incident.** `scripts/check_absolutes.py:known_test_names()` decides
whether a test named in an absolute's prose actually exists. An absolute naming
a test it cannot find is condemned `CITES_MISSING_CHECK`, the severe class. It
enumerated the corpus with `git ls-files`, and its docstring said so as a
virtue — *"Derived from `git ls-files`, not from a list of test files"* — as
though the alternative to a hand-maintained list were the index rather than the
committed tree. `git ls-files` lists INDEX entries. Measured in the live
checkout, same harvester, only the enumeration swapped:

| frame | test names harvested |
|---|---|
| `git ls-files` — the index | 2,597 |
| `git ls-tree -r HEAD` — the committed tree | 2,658 |

61 test functions that genuinely exist could not back a claim, and **100 prose
citation sites across 5 files** were condemned for citing one.

**The asymmetry is the diagnosis, not a detail.** 477 paths were present in
HEAD and absent from the index; **zero** were present in the index and absent
from HEAD. A gap that runs one way only is not a set of deletions the index has
recorded and the tree has not — it is landed work the index never heard about.
Had the difference run both ways, "the index is ahead" would have been a live
hypothesis and the repair would have been a merge rather than a change of
referent.

**The error grows on its own, which is what makes it worth a lesson rather than
a fix.** This lab commits with a private index — `GIT_INDEX_FILE=<tmp> git add`,
`write-tree`, `commit-tree`, `update-ref` — precisely so that concurrent agents
never fight over the shared one. Every such commit leaves a committed file with
**no shared-index entry at all**. So the population of files invisible to any
index-reading instrument is not a fixed backlog that someone will eventually
clear; it is a monotonically growing set, and it grows fastest exactly when the
lab is busiest.

**And the bias runs the worst way available.** Because the invisible files are
the ones most recently landed, the tests an index-reading instrument cannot see
are disproportionately the NEWEST. The claims most likely to be freshly
evidenced are therefore the ones most likely to be reported as unevidenced. An
instrument with this defect does not degrade uniformly; it attacks new work.

**The control is the hard part, and an ordinary tracked file will not do it.**
A test fixture built the obvious way — write a file, `git add`, commit — puts
the file in the index *and* in HEAD, so it is visible to both frames and passes
identically before and after the repair. It certifies nothing. The failing case
must be a file landed by **the private-index form**, because that is the only
ordinary way to produce a committed file with no index entry. In
`scripts/mutation_harness_known_test_names.py` both are built and the
normally-staged one is asserted to be INSENSITIVE to the repair, so the
control's own discriminating power is measured instead of assumed.

**What would have caught it, and what will catch the next one.**

* **Make every frame print its referent, in words that name `index` or `HEAD`.**
  `scripts/sweep.py` does: its `tracked` frame's `rule_words` read *"git ls-files
  — files in the index, and only those"*, and being forced to write that sentence
  is what keeps it honest. `known_test_names` claimed "the tracked corpus", a
  phrase that sounds like the tree and was the index. A frame that cannot state
  its referent in a printed sentence has not decided what it is measuring.
* **Ask the instrument's question out loud.** Every one of these instruments is
  really answering *"will a reader who clones this repository receive X?"* The
  index is not in a clone. Once the question is phrased that way the referent is
  not a judgement call.
* **Test in a repository where the index and HEAD DISAGREE**, and make them
  disagree the way this lab actually makes them disagree. A fixture repo built by
  ordinary `git add` cannot exhibit the defect at all.

**A warning about the frame you measure in, which cost me a measurement.**
The hygienic habit here is to measure in a clean detached worktree, and
`git worktree add` writes a fresh index that matches HEAD exactly. In that
worktree `ls-files` and `ls-tree HEAD` agree to the file, the gap is **0**, and
this entire defect class is **invisible**. The clean room is the wrong room for
this one: an index defect can only be seen in a checkout with a dirty index, so
this class must be measured in the live one even though nothing else should be.

**Three instruments have now been caught reading the index** — `lab_check`'s
`tracked_frame` (repaired under D274, and the precedent this repair followed),
`hunk_check`'s worktree mode, and now `known_test_names` — and the three were
found separately, months of work apart, by people who had each read the previous
repair. That is the signature of a class rather than a bug: the fix does not
generalise on its own because `git ls-files` is the shorter command and the more
familiar one, and nothing in its name says *index*.

Related: L-84 (a positive control proves an instrument can fire, not its reach —
here the ordinary tracked file is a control that fires in both worlds and so
measures neither), L-87 (a control that plants only the shapes its author
imagined certifies the imagination; the private-index shape is one an author
building a fixture the obvious way will never plant), L-43 (the audit instrument
has its own blind spots), L-75 (our own sweeps inherit rules nobody restates —
there an ignore file, here a staging area).

## L-93. A stale referent that still resolves is worse than one that fails — every "did it error?" check passes, and the blind-spot warning written for exactly this case cannot fire

**The rule.** A check whose subject is named by a path inherits every migration
of that path. When the named thing *disappears*, you get the failure you want: a
read raises, a glob matches nothing, the check reports UNKNOWN, and somebody
looks. The dangerous case is the one where the path **still resolves** — to a
stale copy, a frozen snapshot, or a file somebody else updates on a schedule you
do not control — because then the read succeeds, every error branch is skipped,
and the check returns a confident verdict about the wrong subject. Absence and
staleness are different failures, and only one of them is loud. **Design the
check so that "I cannot see" is a third value, and never let it collapse into
"I looked and there was nothing there."**

**Two instances on 2026-08-17, from opposite ends of the lab, and the second one
powered the machine off.**

*One: a gate whose verdict moved with nothing edited.* `self_audit.py`'s
`check_board_placement_words` went WARN → FAIL mid-session, from *"every
travelling surface agrees with the board; 80 lab record placements do not"* to
*"1 placement on surfaces that TRAVEL disagree (146 more on lab records)"*. The
obvious suspect was the edit under test. **Re-running the clean, unedited
worktree returned the same FAIL**, which exonerated the edit by measurement
rather than by argument. The check grades against
`~/closure-challenge-benchmark/README.md` — a file **outside this repository**,
in a separate benchmark clone, which no `git worktree` can pin. Its mtime was
2026-08-17 17:29:00 UTC, sitting exactly between the two runs. The board had
gained an entrant, Yang moved to rank 1, and `demo-output/website/closure.html`
— travelling because `_travelling_names()` matches by BASENAME against the
members of `dist/*.zip` — became a disagreement on a surface that ships. The
path never once failed to open. `self_audit` already labels this check
VALUE-ON-A-PIN (D176); what the label does not say is that the pin is a
working-tree file in another directory, so **the check is not reproducible from
this repository alone**, and any before/after pair straddling that instant was
never a controlled pair.

*Two: a hold that read an occupied control room as an idle box.*
`/usr/local/bin/auto-stop.sh` decided whether anyone was working by looking for
recent session transcripts under one hardcoded directory. The session config
directory was migrated; the live control room moved to
`/home/ubuntu/.claude/projects/...`, and **the old directory still existed**,
holding a copy nobody appends to. So `find` succeeded, matched nothing recent,
raised nothing, and an occupied box read as idle. It took a clean systemd
poweroff at 17:45:14 UTC with five agents working. The script's own comment had
already named the mechanism from a previous instance: *"The test was never
wrong. Its SUBJECT moved."*

**The limb that makes this worth its own entry: the repair existed and was not
running.** The fixed script — the one that scans a glob, refuses to treat a
no-match as an empty room, and surfaces scan errors instead of swallowing them —
had been written and committed **three days earlier**. It was never installed. A
registry asserted that the tracked and installed copies were identical **without
ever comparing bytes**. Two `md5sum` lines settled it: installed
`aad0a124…` against tracked `2f83a38a…`. After the repair both read
`2f83a38aee9b9b68e4438160e6370e2a`, verified by execution.

**And the trap folds in on itself.** The repaired clause emits *"clause (3) is
BLIND"* only when the glob matches **no** directory at all
(`auto-stop.sh:159-166`). A stale-but-present directory matches, so the warning
written for precisely this failure is the one thing a stale referent guarantees
you will not see. **A blind-spot warning that triggers on absence cannot fire on
staleness.**

**What would have caught both, and it is the same two things.**

1. **Compare bytes; never assert identity.** A registry that reports
   "installed == tracked" without hashing both is publishing a claim in the
   voice of a measurement. Two md5s would have shown a three-day-old divergence
   in one line. The same rule covers referents: record the mtime, size or hash
   of the artifact a check grades against, **in the check's own output**, so a
   verdict that moved because its subject moved says so on its face.
2. **Test a hold, a gate or a clause in BOTH directions.** A fix that merely
   disables a mechanism passes the positive test and fails the negative one: the
   box no longer powers off while occupied, and it no longer powers off when
   genuinely idle either. The positive arm ("does it still hold when someone is
   working?") is the one everybody runs. The negative arm ("does it still
   release when nobody is?", "does this gate still FAIL on a planted defect?")
   is the arm that distinguishes a repair from an amputation.

**The operational corollary for anyone measuring a change here.** Run the before
and the after as a **same-moment pair**, in two worktrees, at one HEAD. A
baseline taken an hour earlier is not a baseline; it is a different experiment.
This entry's own gate comparison was discarded and re-run twice for exactly that
reason — once because HEAD moved under it, once because the benchmark README
did.

Related: L-43 (the audit instrument has its own blind spots — a search that
cannot see the evidence reports absence, not innocence; this entry is that
sentence applied to a subject that MOVED rather than to one the search could not
reach), L-84 (a positive control proves an instrument can fire, not its reach,
and not that it fires only where it should — the negative arm above is the same
missing control), L-45 (a verification instrument may fail open, never false —
a stale referent makes it fail *false*, which is the direction that is never
acceptable), L-51 (a search has a method and a FRAME; nothing governs the frame
unless you make it — a referent outside the repository is a frame nobody
declared), L-40 (the switch you set is not the switch that ran — configured and
active are different claims, and a resolving path is the same illusion one layer
down), D65 (the 2026-08-14 instance that moved this clause from a path to a
glob), D176 (the VALUE-ON-A-PIN label), L-92 and D348 (the same class in
`git ls-files`: an instrument reading the index while this lab writes only
HEAD -- that entry is an INSTANCE of this one, and it was written by a
different agent on the same day, which is itself evidence the class is worth
naming).

---

## L-94. A partition recorded by count and not by membership cannot be re-derived, and a sum-based reconciliation is structurally incapable of catching an error in it

**The rule.** When a corpus is split into buckets and the split is documented as
*"bucket X: 26 files"* rather than as a list of which files, the split is not
reproducible — and if the reconciliation that validates the whole classification
is an identity over **sums**, then moving a file from one bucket to its neighbour
leaves the identity closing exactly as before. The check that is supposed to
prove the classification correct is blind to the one error the missing list makes
easy. **Record the membership, or record a second subtotal that crosses the
boundary; a total alone certifies nothing about where the boundary is.**

**The instance.** `MOVE_MAP_2026-08-16.md` §2.2 states rule R8 as
*"`scripts/{installed,laptop_bundle}/**` + **15 named launchers** → `ops/**`,
26 files"*, and R9 as *"`scripts/**` — the check/audit apparatus that stays,
52"*. **The 15 names appear in no committed artefact.** `git grep` over `*.py`,
`*.sh` and `*.md` returns the phrase and no list; `scripts/phase2_move_map.py`
is the superseded F1 generator and encodes a different target tree entirely.

R8 and R9 are not neighbours of equal consequence: **R8 is in the MOVE bucket and
R9 is in the KEEP bucket**, the two largest of the four the reconciliation is
built from. Re-deriving every rule count at batch 0, an independent
reconstruction of the launcher list produced **R8 = 27 / R9 = 51** — and
reconciled to precisely the same grand total, 13,814, with zero unclassified,
because `R8 + R9 = scripts/** = 78` is fixed no matter where the line is drawn.
The error was caught only because a *different* document had separately recorded
the keep subtotal as **723**, and 722 is not 723. Had that subtotal not existed,
a wrong boundary would have been carried into a batch that moves one of those
files into `ops/`.

**What makes it more than an arithmetic curiosity.** The map's own prose is
internally checkable and was not checked: `scripts/installed/` holds **7** files
and `scripts/laptop_bundle/` holds **4**, so `26 − 11 = 15` — the stated launcher
count is consistent with the stated total, which is exactly why nobody noticed
that neither is a list. A reconstruction that *fits* both numbers is not the
author's set; it is a set with the same cardinality. This document records the
reconstruction as a reconstruction for that reason.

**The habit.** For any rule that partitions a directory, commit the enumeration
next to the count, and make the reconciliation carry at least one subtotal that
does not straddle the boundary — here, the keep subtotal. Related: D274 and L-92
(a total taken in the wrong frame), and the standing rule that a count is
meaningless without naming the population it is over. This one is the companion:
a count is also meaningless as evidence for a boundary it does not cross.

## L-95. "Zero unclassified" is a measurement of the frame, not of the rule set — and the frame that under-reports hides exactly the files most likely to need a rule that does not exist yet

**The rule.** A completeness gate — *every path classified, zero unclassified;
every citation resolved, zero dangling* — reports on the population it was handed.
If that population is systematically missing the newest members of the corpus,
the gate is not merely stale, it is **structurally guaranteed to stay green**,
because the thing a new rule would be needed for is the thing the frame cannot
show. A completeness gate that has never once gone non-zero has not been passed;
it has not been tested. **Re-take a completeness gate in the frame a reader
actually sees, and treat an always-green completeness gate as unproven until you
have watched it go red.**

**The instance, measured at `fc9301c5` on 2026-08-17.**
`MOVE_MAP_2026-08-16.md`'s classifier reported *"all tracked paths classified
into exactly one rule, **zero unclassified**"*, reconciling to
`git ls-files | wc -l`. Re-derived over that same index frame today, it still
reports **zero unclassified** and closes at 13,814. Re-derived over
`git ls-tree -r HEAD` — the frame every reader of the repository sees, and the
only frame this lab's own private-index commit protocol writes into (L-92,
`USING_THIS_LAB.md` §8.7) — it closes at 14,293 and reports **one**:
`AWS_TREE_PLAN.md`, a root-level record landed the same day by another agent,
which R0's closed three-file keep list does not name and which no other rule
reaches.

**The second finding is the same shape and larger.** In the index frame, rule R7
(*"`docs/**` — unchanged"*) counts **137 documentation files**, exactly as the map
recorded it. At HEAD it counts **497**, and 344 of the 360 new ones are an
OpenFOAM case corpus under `docs/campaigns/F14-cooling-ladder/` — leaf
directories `system/` (75), `constant/` (53), `0.orig/` (52). That is the same
class of artifact that `demo-output/website/campaign/*_runs/` holds and that R20
sends to `verification/runs/`. **A rule quietly changed meaning — from "keep the
documentation where it is" to "keep a solver run archive in `docs/`" — and the
index frame shows none of it.** The rule's count did not move at all in that
frame. Neither the new unclassified path nor the changed rule is drift a re-count
would smooth away; both are decisions somebody now has to take.

**Why this is not just L-92 again.** L-92 says an instrument reading the index
measures a scratch state and the error grows. This is that seen from the gate's
side: the error is not random with respect to what the gate is checking. The 479
HEAD-only paths at `fc9301c5` are, by construction, **the most recently written
files in the corpus** — and recency is precisely correlated with "no rule covers
this yet". So the bias runs in the one direction that makes a completeness gate
useless while leaving it green. The remedy is cheap and it is the one D274 already
applied to `tracked_frame`: read HEAD.

## L-96. Stripping an illegal label is a measurement, not an edit — and the label is only half the repair, because the record it was written into keeps it

**The rule.** When a verdict label is withdrawn as illegal, the verdict
underneath it is **unknown until it is measured**. Removing `PASS WITH
RESIDUALS` does not leave a plain `PASS`; it leaves a question. V5 is the proof
that the answer can be `FAIL` — its exceptions were in-frame sites of its own
leg 3 — and V6 and V13 are the proof that the answer can be a plain `PASS`. The
two cases look identical from outside and separate only under the test. **So the
strip is never a formatting change, and a pass that treats it as one is guessing
in whichever direction its ledger already points.**

**The test has two limbs, and collapsing it to one decides cases wrongly in both
directions.** R-CONVERGE fixes a rung's declared scope as *"the specific
artifacts, the specific claims, the pass criterion"*. An exception is IN SCOPE
only if it sits inside the criterion's **frame** *and* maps onto a **named
clause** of it.

* Drop the clause limb and every defect anywhere in a declared artifact fails the
  rung. V6's three residuals all sit inside its declared currency block, and all
  three are bookkeeping and locator faults that touch neither *"every finding
  gets a round-5 verdict"* nor the QCR compliance line. Under the frame limb
  alone V6 fails on a wrong line number beside a correct verdict.
* Drop the frame limb and a finding escapes by being described in language the
  criterion happens not to use. V8's F4 was a real false certification and was
  correctly filed, because it lived in neither of V8's two named artifacts.

Both limbs together reproduce every placement the chief actually made — V5 and
V16 in scope, V8's F4 out, V12 and V14 in on sites the criterion named. One limb
alone reproduces none of them consistently.

**The half that gets forgotten: the grade record.** On 2026-08-17 the V6 and V13
ledger cells read a plain `PASS` while the grades they cited still read `PASS
WITH RESIDUALS`, unamended, two days after a ruling corrected the cells. The
cells were right and the records were wrong, and a checker built to compare them
reported both rows as defects — correctly. **A ledger corrected against a record
that still carries the illegal label has not repaired the defect, it has moved
it**, and moved it somewhere with less traffic. Fixing a cell and leaving its
source is the same act as fixing a symptom.

**And the disposal step is a step, not a description of one.** R-CONVERGE's
plain-PASS route is conditional: an out-of-scope finding is *"filed as a docket
item, **not appended to the live rung**"*. Both rungs closed on that route and
**neither filing happened** — seven residuals across V6 and V13 existed nowhere
in `docs/DOCKET.md` as rows, only inside the narrative of the row that measured
their entitlement, and one grade recorded a filing at its own `:515` that had
never landed. A rung that closes by filing, without filing, has closed on a step
that was reported rather than performed. **Check the queue, not the sentence
saying the queue was used.** Related: D249 and the V5 ledger cell (the same strip
yielding `FAIL`), D233 (the entitlement measurement), D353/D354 (the filings this
lesson comes from), D355 (the same illegal label surviving in a third rung's
verdict inside a file two rungs' amendments had already touched), L-92 and L-93
(an instrument measuring a frame nobody declared, and a referent that still
resolves).

## L-97. A validation primary can endorse an abstraction at one scale and document its failure at another — a gate that does not split along that line grades the known defect instead of the solve

**The rule.** When the reference paper for a validation case uses the same
modelling abstraction you do, read it twice: once for the numbers, and once for
where the authors say their own comparison broke. Every place the primary
documents its abstraction failing — a sensor in a region the model represents
as uniform, a profile that only matches when the comparison line moves out of
the near field — is a place your gate must be REPORT-ONLY or carry an explicit
tolerance, because a deviation measured there is the abstraction's documented
defect, not information about your solve. Grade where the primary validates;
report where it confesses. A single undifferentiated band over both converts
the reference's own known error into your failure — or worse, into your pass.

**The instance, F14 rung K2c, 2026-08-17.** The obtained primary (Wibron,
Ljung, Lundström 2018, *Energies* 11:644, READ IN FULL, PDF in `docs/papers/`)
models racks exactly as campaign F14's order specifies — an inlet face plus an
outlet face with ΔT = q/(ṁ·c_p), their Eq. (9) — and then documents, in its own
results, where that abstraction stops being exact: rack-front temperatures all
land inside the ±1 °C sensor bars, rack-back temperatures miss on 2 of 10 racks
*because the imposed outlet temperature is uniform and the real one is not*
(their §4.3), and near-rack velocity profiles at two of five stations only
match the measurements when the comparison line is moved 10–15 cm off the rack
face (their Figure 8), which the authors attribute to door gaps the black-box
BC cannot carry. The K2c gate therefore grades rack-front temperature and the
two far-field stations, and files the rack-back sensors and near-face profiles
REPORT-ONLY with a mandatory position-sensitivity sweep. The alternative —
one 15% band over all five stations — would have failed a correct solve for
reproducing the primary's own documented limitation, and a band wide enough to
pass it there would have been too loose to catch anything at the stations that
actually discriminate.

**The transferable half.** This is the gate-design complement of L-28 (never
grade below the data's own resolvable increment): never grade *inside the
reference's own documented model defect* either. Both are cases of the same
principle — the pass band's floor is set by the reference's confessed
limitations, and the confession is usually in the discussion section, not the
tables.

## L-98. A verification whose input is missing must FAIL, not skip: a check that quietly compares nothing reports the same PASS as a check that compared everything

**The rule.** Every check has inputs. When an input is absent, the check has two
honest options and one dishonest one. It may fail loudly, naming the path it
looked at. It may refuse to run, and say so in its exit code. What it must never
do is treat "no input" as "nothing to compare" and fall through to the success
path. An empty result set is not a satisfied condition. Write the guard as the
first thing the loader does, before any accumulator is initialised: absent input
raises, and zero parsed items raises, because zero comparisons is not a passed
comparison. Then have the run COUNT what it actually compared and print the
count beside the verdict, so that a run which performed none cannot render the
same green line as a run which performed all of them. A verification that cannot
fail is not a verification.

**The corollary about identifiers in messages.** Print the full path you
resolved, relative to the project root, never the basename. The defect below
lived four repair waves precisely because the header printed
`R5_PREREGISTRATION.md`, which was the right FILE at the wrong DIRECTORY, and a
reader checking the output saw the name they expected.

**The instance, the closure entry package, 2026-08-17.**
`scripts/verify_manifest.py` cross-checks eight shipped prediction CSVs against
two independent records: `records/MANIFEST.json`, and the SHA-256 table frozen
in the pre-registration before the scoring call. The second is the one that
matters evidentially, because it is what makes "these are the files we committed
to before we knew the score" checkable by a stranger. The constant naming it
read `ROOT / "evidence" / "R5_PREREGISTRATION.md"`, the path that file had
before the package regrouped `evidence/` into `frozen/`, `audits/` and
`reproduction/`. The regrouping updated the script's own docstring, which named
the correct path, and left the constant, so the file contradicted itself in two
places twenty-eight lines apart.

The loader returned `{}` on the missing file. Consequently: the frozen-hash
cross-check never ran; all eight `vs prereg` cells printed `-`; the header
printed the basename so the wrong directory was invisible; the PASS line was
built as `f"...manifest{' and the frozen pre-registration hashes' if frozen else ''}"`
and so silently dropped its own claim; and the script exited **0 PASS**. The
package's root README meanwhile stated that this script checks the CSVs against
the manifest *and* the frozen hashes. It checked one of the two, and said it had
checked both, through four repair waves and one independent verification. The
underlying evidence was sound the whole time: with the path corrected, 8 of 8
CSVs match both records. The failure was entirely in the instrument.

**How to apply it.** Three edits, and the first alone is not enough:

1. fix the path;
2. make absence and emptiness raise, with the path in the message, and make a
   record present in one input but missing from the other a failure rather than
   a shrug, so "where that file records one" cannot decay into "nowhere";
3. count the comparisons performed, fail if the count is not the expected one,
   and state the count in the PASS line.

Then prove the check can fail, on copies, and record the proofs: the stale path
restored, the input present but unparseable, and one datum altered by one
character. If you cannot produce three distinct failures on demand, you have not
established that the check is a check.

**The transferable half.** This is the executable form of the rule that a
negative result must be distinguishable from an unperformed test. It applies far
beyond hash checks: an empty query result, a config key that defaults to the
permissive value, a glob that matched no files, a regex that captured nothing,
an API that returned 200 with an empty body. Each is an absent input wearing the
costume of a satisfied condition. The tell is always the same shape in the code:
a function that returns a falsy empty container on a missing input, and a caller
that iterates it.

## L-99. A consistency checker blind to the way its own codebase writes the thing it checks certifies nothing about that codebase

**The rule.** Before you trust a checker that scans source for a construct,
measure it against the construct AS YOUR CODEBASE ACTUALLY WRITES IT, not as the
checker's author imagined it written. A path scanner that recognises
`"a/b/c.md"` and not `ROOT / "a" / "b" / "c.md"` will report a clean sweep over a
codebase in which every path is written the second way, and the sweep will be
empty of both defects and coverage. The number to demand is not "how many
problems did it find" but "how many sites did it examine", and if that second
number is zero the first one is meaningless.

**The two-sided test.** Plant the defect in the form your codebase uses, and
plant it again in the form the checker was built for. If the second is caught
and the first is missed, the checker is measuring the author's imagination. That
is exactly what a reader did here: `ROOT / "evidence" / "NO_SUCH_FILE.md"` was
missed, `ROOT / "evidence/frozen/R5_PREREGISTRATIONX.md"` was caught, and the two
results together are the whole diagnosis.

**The instance, the closure entry package, 2026-08-17.**
`scripts/check_consistency.py` resolved every in-package path reference in the
package's Markdown and JSON, and had been rebuilt once already around six defect
shapes it had previously missed. Its path scanner matched a single string
literal containing a slash. Every path constant in all five shipped scripts is
built by `Path` division across separate literals, and the `.md` scan only ever
read inside backticked spans, so a path named in plain prose was invisible too.
Net coverage of the scripts' own paths: zero sites. That blind spot is precisely
how L-98's fail-open gate survived four waves of repair by a tool whose stated
job was to catch exactly that class of defect. The fix was an AST evaluator over
`Path(__file__)`, `.resolve()`, `.parent` and `/` with a string literal, plus an
unbackticked-prose pass, plus a plant that restores the real defect.

**The second half, which is the same lesson about the CONTROL.** The same
reading found that one of the six planted shapes was being caught for the wrong
reason. The check harvested inventory rows from every table in the file, so
deleting a file's inventory row was caught whenever that file also headed a row
of some other table. Measured across all 26 shipped files, deletion went
unreported for five of them, and the control had planted its defect on one of
the 21 that happened to work. **Run your control's plant against every instance
in the population, not the one instance you chose.** One passing plant tells you
the check can fire; it does not tell you the check covers the set.

**The third half, which is about counting.** A related check enumerated four
citation sites inside frozen documents and the disclosure it guarded asserted
that all four had stopped resolving. Two had. The check counted sites and never
asked whether each one resolved, so it could not contradict the claim it
existed to guard. **How many there are and whether each one works are different
questions; a check that answers only the first will happily certify a false
answer to the second.**

**The transferable half.** When a checker reports clean, ask it what it
examined. Instrument it to emit the population size, not only the failure count.
An empty population and a clean sweep are indistinguishable in the output and
opposite in meaning, which is the same disease as L-98 one level up: there, an
absent input read as a passed check; here, an absent population reads as a
covered codebase.

## L-100. A gate can be satisfied by the riskier of two options and failed by the safer one, and the agent who meets it will fix the gate by taking the risk

**The rule.** When a plan offers two ways out of a hazard and states one
verification line for both, check which way the line points **before** the
choice is made. A gate that reads its subject by CLASS while the decision is
about a LIST does not merely lose precision: it can invert, passing the option
that grows the exposure and failing the option that preserves every invariant
the plan states. The agent who meets an inverted gate does not read it as
inverted — a red gate under the careful option and a green one under the
careless option is a very effective argument for the careless option, and it
arrives with the plan's own authority behind it. **A gate whose pass condition
is not derived from the decision it is gating is not a weak gate; it is a gate
pointing the wrong way. Fire every gate in BOTH directions before the decision,
and make the gate's default equal the decision's default, or the gate reads one
thing while the batch does another.**

**The instance, 2026-08-17, ruled and repaired at `7554e5d3`.**
`demo-output/website/campaign/MESH_AUDIT_runs/` held **78 tracked files, every
one a `*.log.checkMesh`** — exactly the solver-utility class a planned batch 2
untracks. The moment batch 2 landed, the directory would hold no tracked file
and batch 7's `git mv` of it would abort, taking every other source in that
invocation with it. The plan offered **(A)** exclude the 78 from batch 2 until
batch 7 has moved the tree — index and disk stay in agreement, carry set stays
at 2 trees / 307 files / 1,510,309,145 bytes — and **(B)** let it go dark and
hand-carry it, which grows the carry set by design. Its verification line was
*"the goes-dark-after-batch-2 section must read 0 afterwards, not 1"*.

`hand_carry.batch2_survivors()` classified `*.log.checkMesh` inside a `*_runs`
tree as output **by file class**. So under **(B)** the section read **0**
trivially — the tree is already dark, already in the carry set, and the
projection reports only the *difference* — and under **(A)** it read **1**,
because batch 2 had spared the files and nothing was ever going to go dark, but
the projection was still classifying by suffix. **The gate was satisfied by the
option that grows a 1.5 GB hand-carry and failed by the option that keeps the
move a `git mv`.**

The repair was to make the test **membership of batch 2's own list**
(`batch2_untrack_list`, the named constant `BATCH2_EXCLUSIONS`, and a
`--batch2-list FILE` mode so the gate can be handed the literal list once it
exists) rather than a re-derivation of what the list ought to contain. Fired
both ways on the live tree: option A → a list of 7,599 paths, section reads
**0**; option B → 7,677 paths, section reads **1**; the difference is exactly
the 78. The pre-amendment code, replanted as a mutant with the new API intact,
reddens the option-A direction and passes the option-B one — the defect
reproduced rather than described. A second mutant that makes the projection
incapable of firing reddens the option-B direction and passes option-A, which
is what shows the first test is not satisfied by a gate that never fires.

**The transferable half.** This is L-93's shape (*a stale referent that still
resolves is worse than one that fails*) moved from referents to gates. The
common thread is that the check ran, returned a number, and the number was
about something other than the question. **Ask of every gate: what would it
read if the safe thing had been done, and what would it read if the unsafe
thing had been done? If those two answers are not different in the right
direction, the gate is not measuring the decision.** And a two-direction plant
is cheap: it costs one extra invocation with the exclusion dropped.

## L-101. A before/after check cannot detect a blindness both measurements share — and `os.walk`'s default is to be blind quietly

**The rule.** The standard shape of a data-integrity check is: measure the
source, do the thing, measure the destination, compare. That shape is only as
good as the instrument, and it has one blind spot that no amount of comparison
closes: **anything the instrument cannot see is missing from both readings
equally, so the comparison agrees with itself and signs off.** A count, a byte
total and a path digest that all fall together look exactly like a correct
measurement of a smaller tree. **So an instrument used on both sides of a
before/after check must FAIL rather than under-report. Surface the read error,
count it, and refuse to return a number** — because a number that is short by
an unknown amount is not a measurement, and a carry verified against one is not
verified.

`os.walk` makes this the default. `onerror` is `None` unless you pass one,
which means a directory that cannot be opened yields nothing and raises
nothing; and the idiomatic `try: st = p.lstat(); except OSError: continue` does
the same thing one level down. Neither reaches stderr. Both are what a careful
reviewer skims past.

**The instance, 2026-08-17, repaired and controlled at `7554e5d3`.**
`scripts/hand_carry.py` exists to move two gitignored trees — **307 files,
1,510,309,145 bytes** — that `git mv` cannot reach, and to prove they arrived,
because "a hand-carry nobody checks is how 1.51 GB goes missing" is its own
opening line. Its `measure()` walked with no `onerror` and swallowed per-file
`OSError`. An unreadable directory therefore dropped out of the file count, the
byte total **and** the path digest at once. `carry()` compares a before and an
after taken by that same instrument, so a permission change *between* them was
the one thing it could not see — and the tree it guards had, until that
morning, 786 root-owned files in it.

**Controlled rather than argued**, by making one directory unreadable in a
scratch copy outside the repository and running HEAD's blob of the module beside
the repaired one over the same bytes. Clean, both report 9 files /
2,452,694 B with an identical digest. With one directory `chmod 000`:

- **pre-repair: returned 7 files / 2,180,257 B, a fresh digest, exit 0, stderr
  empty.** Two files and 272,437 bytes gone, silently, in a green run.
- **repaired: refuses** — `MeasurementError: 1 walk/stat error(s) … REFUSING to
  report a number`, the failing path on stderr, exit 3 UNKNOWN.

End-to-end through the command line on a scratch repository the pre-repair tool
reported `HAND-CARRY: 1 tree, 1 file, 689,284 B` and **exited 0**. Same tree,
same command, green, and wrong.

**Sibling, landed the same day by a peer: `L-98`** — *a verification whose
input is missing must FAIL, not skip*. That is this lesson one layer up: L-98
is about a check handed nothing, this one is about a check handed part of
something and unable to tell. Both end in the same place, a PASS that measured
less than it claimed.

**The transferable half, and it is not about `os.walk`.** Ask of any
verification: *is there a failure mode that changes both sides of my comparison
in the same direction?* If yes, the comparison is not the check — the
instrument's error handling is. The corollary is a test-design one: the tests
that catch this need a **planted read failure**, not a planted data difference,
and they need a readable-tree control beside them, because an instrument that
raised on everything would satisfy every failure test and be worthless.

## L-102. Byte-identity is not redundancy: when two copies of a file are a deployment pair, the matching MD5 is the check's PASS condition, and deleting either one breaks it

`AWS_TREE_PLAN.md` §6.4 classified `/home/ubuntu/lab.sh` (779 B) and
`/home/ubuntu/provision.sh` (2,667 B) as **DUPLICATE** — "the entire actionable
duplicate population in scope", 3,446 B, the plan's whole deletion authority. The
evidence given was a full-file MD5 sweep: each `$HOME` copy matched a tracked
copy in the repository exactly, and the tracked copy survives loss of the box.
The disposition column named the repository path as "the survivor" and the
supporting negative read: *"Nothing found referencing the `$HOME` copy by
path."*

**Both `$HOME` paths are named, in this repository, as the installed location of
the tracked file.** `scripts/installed_registry.py`:

```python
Deployment(name="provision script", tracked="docs/aws/provision.sh",
           source="/home/ubuntu/provision.sh", ...)
Deployment(name="lab session launcher", tracked="scripts/installed/lab.sh",
           source="/home/ubuntu/lab.sh", ...)
```

and `scripts/installed/README.md` describes `/home/ubuntu/lab.sh` as *"the tmux
session operators attach to"*. Running the registry on the box:

```
MATCH    provision script  (docs/aws/provision.sh -> /home/ubuntu/provision.sh)
MATCH    lab session launcher  (scripts/installed/lab.sh -> /home/ubuntu/lab.sh)
```

Deleting either file flips its row to ABSENT and
`sdk/tests/test_installed_matches_tracked.py` refuses the difference. It also
removes the tmux session every operator attaches to and the only thing that
starts the control room by hand. The plan's own §5 bottom line — "the population
deletable on this plan's own authority is 3,446 bytes" — was the whole of its
deletion budget, and **all of it was this**. Nothing was deleted; the real
deletable population on that machine turned out to be 1,819 B of Python
bytecode.

**The rule.** A duplicate detector answers *are these bytes the same*. It cannot
answer *is one of them redundant*, and the two come apart precisely when the
identity is itself the thing being asserted. A deployment pair, a golden-output
fixture beside the output it pins, a checked-in vendored copy diffed against its
source — in every one of these the matching hash is the passing state of a check,
and "deduplicating" it deletes the check's second operand. **Before deleting any
proven duplicate, ask what would notice if the two copies stopped matching.** If
the answer is a test, a registry or a gate, the copy is not spare.

**And name the failure in the sweep, because it is reusable.** The negative that
licensed the deletion was looking for the wrong shape. `/home/ubuntu/lab.sh` does
not appear in this repository as a command to run; it appears as **data** — a
string in a `Deployment(...)` constructor and a cell in a Markdown table. A sweep
framed as "does anything invoke this?" will not see either. The question that
finds them is "does this path appear anywhere at all, in any context?", and it
must be answered with `/usr/bin/grep` — **L-75**: the shell `grep` here is a
`ugrep --ignore-files` wrapper that skips gitignored files silently, so a sweep
run through it has a denominator nobody declared — and with no `head` in the
pipeline, per that same plan's §7.4, where a sweep ending in `| head -10`
returned exactly 10 and was quoted as a census against a true 19.

**The sibling error, same page, same cause.** That plan's §3 also proposed moving
`closure-challenge-benchmark/`, `dafoam-tutorials/` and `backups/` into tidier
parents without measuring what named them. The sweep that was not run finds **85
lines in 59 files** carrying `/home/ubuntu/closure-challenge-benchmark` — 15 of
them executable `.py`/`.sh`, 8 of them published `.json` evidence records — **17
lines in 14 files** for `/home/ubuntu/dafoam-tutorials`, including
`sdk/workflows/onera_m6.py:46` and `sdk/workflows/crm_wingbody.py:43`
(`TUTORIAL_SOURCE = Path(...)`), and `scripts/ledger_backup.py:26`, which
hard-codes `BACKUP_DIR = Path("/home/ubuntu/backups")` as its **write target** —
so moving that directory would not move the writer, and the next backup would
silently recreate the old path and split the recovery points across two
locations. All three were left in place and represented by symlinks pointing at
them instead.

**The generalisation across both halves:** a plan that proposes an irreversible
operation on a path owes a measurement of what names that path, and the
measurement has to search for the path as a *string*, not as a *usage*. The plan
was scrupulous about its byte totals — it re-derived them, captured stderr, and
corrected three of its own figures on its face — and still shipped two
dispositions whose supporting evidence was a search that was never run. **Rigour
about the quantities you did measure is not evidence about the ones you did
not.**

## L-103. A gate built for one instance of a hazard detects that instance's SYMPTOM, so the second instance reads clean — the only thing that finds it is measuring what your rule reaches

A batch plan named one interaction between two of its steps: a directory whose
every tracked file was in the class step 2 untracks, which would therefore lose
its last tracked file and abort step 7's `git mv`. A gate was written, amended
after it was found to point the wrong way, fired in both directions on the live
tree, and pinned by tests with a planted mutant. It was a good gate. It read
**0** — correctly, and for the wrong question.

**There was a second interaction, it was larger, and the gate reads 0 whether
the batch commits it or not.** Step 2's class rule reached **109 tracked files
of a 315-file run archive** that a ruling made that same morning had assigned to
step 7. The gate detects trees that **go dark**; that archive had 274 tracked
files, 109 reachable, and **165 left**, so it never goes dark, `git mv` never
aborts, and the projection is silent. Fired four ways — the ruled option, the
riskier option, the ruled option with the batch taking all 109, and that again
with the missing rule binding supplied by a probe — it read **0, 1, 0, 0**. The
two firings that differ by the entire finding are indistinguishable.

**The gate was not weak and it was not wrong. It was measuring the symptom of
the first instance.** "Goes dark" is what that hazard *looked like*; the hazard
itself was "step 2's rule reaches files step 7 owns". Every gate written from a
worked example inherits that example's shape, and the shape is almost never the
class.

The same pass found a second one of exactly this form and it was worse. The
class rule's list of path segments that mean *case input* was `{system,
constant, 0}`. The initial-condition directory is spelled `0.orig`, so the rule
reached **122 tracked initial-condition files** — and **64 of them were tracked
only because two ignore-file negation blocks re-included them, both written that
same day by the lanes that owned those trees, one of whose comments recorded
that a `[0-9]*` loop had already deleted every initial-condition directory in
one of them once.** No gate covered it either, because the files did not go
dark, did not move, and did not change count. It was found by listing what the
rule reached and reading the list.

**The transferable rule, and it is cheap.** Before a rule-driven batch runs,
compute the set the rule REACHES and intersect it with the sets every other rule
OWNS. Not the gate's output — the rule's reach. A gate answers "did the failure
I already know about happen"; the intersection answers "does my rule touch
something that is not mine", which is the question a plan with twenty-five rules
and nine batches is actually asking. Both findings here fell out of one
intersection and one listing, and neither was reachable by re-running anything.

**Two corollaries worth carrying separately.**

- **An exclusion belongs in a named constant and its test must read the
  DEFAULT.** The first cut of the test for this exclusion passed the exclusion
  in as an argument and was green against a constant that did not contain it —
  it pinned the filtering, not the ruling. A planted mutant that dropped the
  constant's entry passed every test in the class. This is the same defect the
  gate's own earlier amendment had already named in its own words — *"a gate
  whose default differs from the batch's own choice reads one thing while the
  batch does another"* — reappearing one layer up, in the test of the thing that
  said it.
- **When you find your classifier wrong once, stop trusting its other verdicts
  in the same pass.** The disposition table had three untrack classes; the same
  classifier that had just been shown to sweep in initial conditions also
  reconstructed the third class, and inspecting its 198 files found **a custom
  solver's C++ source and 26 case dictionaries** in it. That class was deferred
  rather than executed. An instrument shown wrong about one row of a table has
  not been shown right about the others, and the safe direction — fewer files
  leave tracking — costs nothing but a sentence saying so.

## L-104. A check pinned to remembered sites certifies memory, not coverage, and its control must mutate the POPULATION rather than the defect shapes

A package of 26 shipped files had a cross-file consistency checker, thirteen
checks deep, with a planted-error control that copied the package fifteen times
over, planted a different shape of defect in each copy, and required the check
that owned each shape to fail on it. Five waves of repair had run through it.
Three independent verifications had read it. Each verification found a fresh
crop of false statements, and each wave answered by adding the check that would
have caught them.

The third verification found **fourteen false statements and zero new classes**.
Every one was a recurrence of a class already checked. Its diagnosis was not
"the checks are wrong"; it was that **the checks kept covering the remembered
sites rather than the measured ones**, and it proved that mechanically:

> Cut the pinned-figure list from its 42 entries to the 2 that the control's own
> plants happen to use. **All 13 checks PASS. The control still prints "all 15
> planted defect shapes were caught". The script exits 0.** Then drift the
> headline score in a file the two surviving pins do not name, and nothing says
> so.

**The control was certifying the checker's shapes and never its coverage.**
Every plant was a defect of a shape somebody had already thought of, placed at a
site somebody had already thought of. Deleting nine tenths of what the checker
watched changed nothing the control could see, because the control never
mutated what the checker watched. It only mutated the documents.

**The measurement that ends this.** Instead of a sixth wave of "add the check
that would have caught these fourteen", the populations were enumerated:

| what had been remembered | what it is when measured |
|---|---|
| 42 hand-written figure pins | **380** distinct numeric figures actually stated across the shipped documents. 42 pins covered **32** of them |
| "21 quoted receipts across 6 files" | **31** quoted commands found by scanning, of which **0** had ever been re-executed |
| an expected-results table a reader is told to check their run against | never compared against a run, in any wave |
| a departure count pinned as the constant 10 against two remembered sentences | six other places state that count; **four of them said nine or six** while the constant and its two sentences agreed |

Each population is now derived on every run and its coverage printed: 380
figures, 53 pinned, 22 checked against a shipped record, **31 listed as
deliberately unpinned with the reason for each**, 12 inside frozen bytes, 262
stated in fewer than three documents, **0 unaccounted for**. 31 quoted commands,
28 executed and compared here, 20 in a bare export, every skip printed with its
reason. **A figure nobody chose to pin is now visible as such rather than
invisible**, which is the whole of the repair: the unpinned count is not a
failure, it is the number that was missing.

**And the control now deletes pins and requires the checker to fail.** Cut to 2
pins it reports 23 unpinned figures instead of passing green. That control also
reports its own reach honestly: **deleting any one of 25 of the 64 pins is
caught, and deleting one of the other 39 is not**, because those sit outside the
enumerated token class or are checked against a shipped record instead. That
number is printed rather than implied, because a residual you have counted is a
different object from one you have asserted is small.

**The rule.** A checker's pin list and the thing it is supposed to cover are two
different sets, and nothing in a passing run compares them. Every check written
from a worked defect inherits that defect's *site* as well as its *shape*, and
the site is almost never the class. So: **before trusting a check, delete part
of what it watches and require it to notice.** If it does not, the control is
measuring your imagination. And when you write the control, mutate the
population, not only the specimens. This is the coverage-shaped sibling of L-87
(a control that plants only the defects its author imagined certifies the
author's imagination) and of L-103 (a gate built for one instance of a hazard
detects that instance's symptom): L-87 says the shapes are incomplete, L-103
says the rule reaches too little, and this one says **the shapes can be complete
and the rule can be right and the check can still be pointed at two files out of
twenty-six, with nothing in the run that would tell you.**

**The corollary about quoted receipts, because it cost two live defects here.**
This package's habit was to quote a command and the output it gave, as proof
that a figure was measured and not recalled. Twenty-one of those shipped and
none had been re-run. Two did not run at all: `sha256sum -c` against a JSON
manifest prints `no properly formatted checksum lines found`, under a column
headed "all executed"; and `git archive ... | tar -x -C /tmp/x` fails wherever
`/tmp/x` does not already exist. A third was worse than either: the package's
own scoring recipe, followed from the directory its own heading names, cloned
the scorer **into** the working tree, at which point the leakage assertion
exited 1 on the scorer's own test ground truth and the consistency checker
exited 1 with 48 disagreements. **A quoted receipt that is never re-executed is
a memory of a measurement, and it decays exactly like any other memory.** Run
them, from the directory the document tells the reader to run them from.

## L-105. An instrument that prints a claim about the strength of its own check, backed by a quantity it never computes, is worse than one that simply lacks the feature

`scripts/heat_balance.py` had a `--allow-advective` flag. At `267a4021` the
attribute `a.allow_advective` was read at **exactly one place** — the guard on an
exit-2 refusal — and nowhere else. The only per-patch heat the script computed
was `Q = kcond * G`, pure conduction. No advective key reached the JSON; no
advective line reached the printed report. The docstring said the flag "adds the
term but the report is then stamped UNVALIDATED", and **both halves were false**:
the flag added no term, and the string `UNVALIDATED` never appeared in any report
— only in the docstring and in two stderr messages.

That is a missing feature, and a missing feature is a gap a reader can see.

**Here is the part that is not a missing feature.** `sealed = not nonwall`, so on
an open case the script took the `closure_is_identity_class is False` branch and
printed, verbatim:

> NOT of the identity class, so the balance is a genuine constraint here rather
> than a restatement of the discretisation

**The instrument made a positive claim about the strength of its own check, on
exactly the class of case where the quantity backing that claim did not exist.**
It was the script's most emphatic endorsement, spent on its least trustworthy
output. Measured on a real open case afterwards, the number under that
endorsement was wrong by 98.6 percent.

**Why this is worse than the bare absence.** A checker that says "I do not
compute this" costs a reader one lookup. A checker that says "the balance is a
genuine constraint **here**" transfers its own credibility onto a number it has
not earned the right to vouch for. The reader's correct response to the first is
to go and compute the term; the correct response to the second is to quote the
number. And the endorsement is *load-bearing downstream*: K2a §8 had already
written its instrument prerequisite assuming a stamp would mark unvalidated
numbers, so a specification written to catch exactly this was itself resting on
a stamp that did not exist.

**The rule.** When a check has a branch it cannot evaluate, the branch must
degrade to UNKNOWN and say so — never to the confident negation. `false` and
`could not be determined` are different answers and only one of them is honest
when the input is missing. Concretely, in the repair: an incomplete ledger sets
`closure_is_identity_class` to `null`, not `false`, because a balance missing a
term is neither an identity nor a genuine constraint — it is an unfinished sum.
And it cannot PASS, whatever the arithmetic reads.

**The ordering matters and it is cheap.** The repair was done in two commits and
the first computed nothing new: it removed the false endorsement and left the
feature still missing. That takes minutes, needs no compute, and means the
instrument is honest for the whole time the real work is in progress. Fix the
stamp before the physics.

Found and repaired at rung KV1 of campaign F14, 2026-08-17.
`docs/campaigns/F14-cooling-ladder/KV1_RESULTS.md` §0.

## L-106. A new term validated only on a case where its own sum is identically zero has been validated against nothing, and the control that catches this is a mutation that must BITE

Having implemented the advective enthalpy flux, the obvious control was a duct
with through-flow and no source: the balance must close. It closed —
**0.0000 percent, net 1.8e-12 W, exit 0** — and it was worth nothing.

The duct had adiabatic walls and an inlet at 305 K, so it converged to *exactly*
305 K everywhere. Therefore:

```
Q_adv(inlet) = +0.146191 W    Q_adv(outlet) = -0.146191 W    SUM = 0
```

Flip the sign of the whole advective term: the sum is still zero. Scale it by
two: still zero. **The closure passes for any scaling and any sign of the term it
was built to validate.** That is the sealed-case identity defect — a quantity
that closes whether the physics is right or not — arriving in a new domain under
a new name, on the very case built to escape it.

**It was caught by asking the mutation question rather than the closure
question.** Not *"does it close?"* but *"what would have to be wrong for it to
fail?"*. Four independent wrongnesses were put into the term and the same field
set re-audited: three of the four changed nothing at all. That is not a fact
about the term; it is a fact about the case.

**The fix is a case whose ledger has two INDEPENDENT non-zero terms that must
cancel each other.** A heated wall was added, so heat enters by conduction
(+0.0617726 W) and leaves by advection (−0.0617726 W). The mutations then bit
hard: sign flipped → 45.66 percent FAIL, scaled by two → 17.44 percent FAIL, one
open patch dropped → 100 percent FAIL.

**The degenerate case was kept, not deleted.** It is now the negative control:
the case where the mutations are *correctly* invisible, which is what shows the
sensitivity measured on the good case belongs to the physics and not to the
harness. A mutation set that fires everywhere is as uninformative as one that
fires nowhere.

**The general rule.** Before quoting a control as validating a term, ask what the
term's contribution to the graded quantity actually is on that case. If it is
zero, or if it cancels against itself, the control has exercised the code path
and nothing more — reachability, not recognition. **A control has to be able to
come out wrong, and "able to come out wrong" is measured by breaking the thing
on purpose, never by inspecting the result.**

Found at rung KV1 of campaign F14, 2026-08-17.
`docs/campaigns/F14-cooling-ladder/KV1_RESULTS.md` §2, and the harness is
`KV1_runs/mutate_advective.py`.

## L-107. A normalisation choice can loosen a gate many-fold while every number the gate reports stays put, so the choice is part of the threshold and has to be governed with it

An enthalpy flux is defined only up to a temperature datum. Over a boundary that
conserves mass the datum cancels exactly from the **net**, which is the number
the audit reports. It does **not** cancel from the **denominator** of the
imbalance ratio, because the datum decides how much of the through-flow's
absolute enthalpy is counted as "heat entering".

Measured, on one duct: with the datum at the case's own `TRef` the denominator is
**0.2079685 W**; with the datum at 0 K — the apparently neutral, choice-free
option — it is **8.979442 W**. A factor of **43.2**. The governed tolerance is
0.5 percent in both cases and *the printed tolerance never changes*, but the slack
it buys goes from **1.04e-03 W** to **4.49e-02 W**.

**And no control catches it.** The datum was one of four mutations in a harness
built to prove the term could fail. The other three fired. This one did not, and
*cannot*: the net is unchanged to 1e-10 W and the case passes. Every control in
the rung still passed with the gate 43-fold looser.

**So the taxonomy that matters is not "which numbers are reported" but "which
numbers the reported ones are divided by".** A reviewer reading the report sees
an unchanged threshold, an unchanged net, and a passing verdict. Nothing on the
page moves. The only thing that moved was what "0.5 percent" meant.

**The rule.** A normalisation, a datum, a reference state or a denominator that
sits under a governed threshold is *part of that threshold*. It belongs in the
same governed file, stated with the same force, with the factor it is worth
measured rather than asserted — not left as a default in the code, and never
left to a caller's flag. In the repair it went into `docs/physics_rules.yaml`
beside the tolerance as `heat_balance_advective_datum: TRef`, with the 43.2 on
the same page, and the report carries `advective.datum_K` and
`advective.datum_source` on every run so a reader can see which one was used.

**The tell that generalises.** If someone proposes simplifying a normalisation
"since it cancels anyway", the question is *cancels from what*. It very likely
cancels from the numerator. Check the denominator, and check it as a mutation
that must be allowed to pass — because if it silently passes, that is the finding.

Found at rung KV1 of campaign F14, 2026-08-17.
`docs/campaigns/F14-cooling-ladder/KV1_RESULTS.md` §3c.

## L-108. A coverage test reads an ENUMERATION, and the enumeration is chosen by implementation shape — so the rules implemented in a different shape are not "failing", they are invisible

`scripts/lab_paths.py` is the module the whole MOVE_MAP reorganisation routes
through: one table, one function, every rule of the map. It carried a test
called `test_every_move_rule_of_section_2_2_is_represented`, which is exactly
the test you would write, and it read

```python
rules = {m.rule for m in L.MOVES}
for r in ("R1", "R2", "R5", ..., "R24"):
    self.assertIn(r, rules)
```

**R16 and R17 were not implemented at all.** Nineteen loose `*.md` and
twenty-one loose `*.json` sitting directly in the webroot were falling through
to the catch-all prefix row and being routed to `web/` instead of to
`research/closure/md/` and `research/closure/data/` — forty tracked files
landing in a directory the map says holds **five**. The test was green the whole
time, and so was `test_the_webroot_is_fully_classified`, which asserts every
webroot file reaches *a* rule. Every one of them did. The wrong one.

**Two independent reasons the test could not see it, and the second is the
transferable one.**

1. The expected-rule list was hand-written and R16/R17 were simply not on it.
   That is an ordinary omission and it is the shallow half.
2. **`MOVES` is the prefix TABLE. Six of the map's rules — R12, R16, R17, R20,
   R21, R25 — are not table rows at all**; they are regexes, because "everything
   under `campaign/` EXCEPT the run archives" and "a loose file of this suffix"
   are not prefixes. So the collection the test enumerated was not the rule set.
   It was *the rules that happened to be expressible as table rows*. Adding
   R16 and R17 to the expected list would not have made the test pass — it
   would have made it fail for a reason no one could act on, because they can
   never appear in `MOVES` no matter how correctly they are implemented.

**The generalisation.** Whenever a check asserts coverage by iterating a
collection, ask what SELECTED that collection. If the answer is anything about
how the items are stored — a table, a registry, a decorator, a directory of
files, a dict of handlers — then the check covers the storage shape and not the
requirement. The items implemented some other way are not reported as gaps.
They are not reported at all, and the check goes green over their absence,
which is the same silent-zero this lab keeps finding in other clothing: an
instrument whose input is empty of the thing it was looking for and which says
so by saying nothing.

**The repair has two halves and neither works alone.** The module now exports
`RULES`, a set covering table rows *and* regex rules, and the coverage test
reads that. But `RULES` is written by hand, so on its own it is a wish list: a
rule id added to it without a rule behind it turns the coverage test green
again, one level up. So beside it sits
`test_the_rules_set_is_not_a_wish_list`, which takes a witness path for each
non-table rule and asserts the rule **fires** on it. Declaration plus firing.
The declaration is what makes the gap visible; the firing is what makes the
declaration mean something.

**The tell.** If a coverage test's list of expected items is written in the
test, and the collection it checks them against is written in the code, they
can only ever disagree about names — never about existence. A coverage test
worth having has to be able to say *"you claim to implement R17; show me a path
it moves."*

Found while binding R25 into `lab_paths` for MOVE_MAP batch 3, 2026-08-17.
`demo-output/website/campaign/MOVE_MAP_BATCH3_EXECUTION_2026-08-17.md` §2.

## L-109. A count ratified alongside a rule is a FRAME; the rule survives the drift and the count does not, so ratify the rule and re-derive the count

RULING 1 of 2026-08-17 created R25 — `docs/campaigns/<campaign>/<tree>/**` where
`<tree>` matches `*_runs` or `*_sensitivity` is a run archive and follows R20's
destination — and it was ratified as **"R25 = 315 files"**, a figure carefully
confirmed identical at two named commits four apart, `7554e5d3` and `4d7c195a`.
Two downstream documents carry 315 forward into batch 7's totals.

**Eleven hours later it is 490.** The thermal lane landed `KV1_runs`, 175
tracked files, under the same campaign directory. The ruling's own §1.1 is
careful about this — it shows the number holding across two anchors and says the
class that moved is documentation — but "this figure did not move between these
two commits" and "this figure is fixed" are different claims, and the second one
is what a reader takes from a bolded total.

**Nothing needed re-ruling, and the reason is worth naming, because it was a
choice and could have gone the other way.** The ruling was written as a rule
over a *pattern*: `*_runs` or `*_sensitivity`. So `redirect()` routed `KV1_runs`
correctly the moment it appeared, with no edit anywhere. Had it been written as
the enumeration it was measured from — *"`K0c_runs` and `K0b_mesh_sensitivity`
move"*, which is what the composition table in front of the author showed and
what an enumeration-shaped ruling would naturally say — then batch 7 would today
move 315 files and strand 175 in `docs/` with nothing in the tree saying so.
Same ruling, same evidence, same day; one form is robust to a live lane and the
other is a time bomb with an eleven-hour fuse.

**So: a ruling states a rule. Any count beside it is evidence FOR the rule, at a
named frame, and is re-derived by whoever acts on it.** The count belongs in the
sentence that says how the rule was checked, not in the sentence that says what
the rule is. When a later batch needs the number, it runs the rule again.

**And the check that would catch the other outcome.** If the number a plan acts
on is a count, the batch that acts on it re-derives it against its own frame and
aborts on drift, rather than reading it out of the record that ratified it —
which is why `hand_carry.py` re-derives its whole census at every invocation and
refuses on any drift from the plan, instead of comparing against a table in a
document. The general form: **a plan may cite a measurement, but it must not
consume one.**

Found at MOVE_MAP batch 3, 2026-08-17, re-measuring R25 before binding it.
`demo-output/website/campaign/MOVE_MAP_BATCH3_EXECUTION_2026-08-17.md` §1.2.

## L-110. Routing a module through an indirection moves WHERE its names resolve — and a test that blinds a check by REBINDING one of those names is testing exactly that, so the safest-looking refactor in the repository can delete a guard's only proof while every behaviour check passes

Batch 3b converted `scripts/self_audit.py` to import `scripts/lab_paths.py`
instead of spelling the tree. The conversion was behaviour-identical by every
measure built for it. Three instruments ran over all 98 converted files:
importing each module in a subprocess and diffing every path-valued constant
(97/98 identical); a static AST evaluator comparing the set of repository paths
each file NAMES against the same answer from HEAD's blob (94/98, the four
explained); and a free-name sweep proving no rewrite un-bound a name still read
(0/98). All three passed `self_audit.py`.

**The suite failed anyway, in two files nobody had touched.**
`sdk/tests/test_empty_set_is_not_agreement.py` and
`test_form_or_value_and_empty_selection.py` went from 0 failures to 8. They are
this lab's **empty-set controls**: they blind a check by rebinding
`self_audit`'s module-level `WEB`, `REPO`, `ACTIVE`, `WALL`, `CAMPAIGN` or
`MISSION` to an empty directory and assert the check returns UNKNOWN rather
than a clean sweep of nothing. Thirteen checks are covered that way, each with
a live-arm control beside it.

The conversion replaced `ladder = WEB / "campaign" / "F5a_….md"` with
`lab_paths.CAMPAIGN / "F5a_….md"`, and `docket_path = REPO / "demo-output" / …`
with `lab_paths.AGENDA / "docket.json"`. Both are *more* correct — they survive
a move that the literals do not. **Both also reach past the handle the test
rebinds.** Rebinding `WEB` no longer blinded anything. Five checks kept reading
the live tree and returned WARN, PASS and FAIL where the tests demanded UNKNOWN.

**The guards were still right. What was destroyed was the only evidence that
they are** — which is the silent-zero failure this corpus keeps re-finding,
moved up one level: not a check that reads nothing and reports clean, but a
check whose blindness can no longer be demonstrated. That is worse, because it
is invisible to every instrument that asks about behaviour, and the two are
easy to confuse: the check's answer on the real tree never changed at all.

**Why every behaviour instrument was blind to it, stated precisely.** Each one
asks *does this constant name the same path*. The answer was yes, everywhere,
including for the five checks that broke. The property that changed is not the
VALUE a name resolves to; it is **which object owns the resolution**. Before,
`self_audit.WEB` owned it and anyone could rebind it. After, `lab_paths.WEB`
owned it and `self_audit.WEB` was a copy nobody consulted. No comparison of
values can see that, because at rest the two are equal — that is the entire
point of the refactor.

**The rule.** Before routing a module through an indirection, ask *which of my
names does other code REBIND*, not only *which paths do I read*. `grep` for the
module's own attribute names appearing on the left of a `setattr`, in a
`monkeypatch`, in a `mock.patch`, or in a `with` block that saves and restores
them. Every such name is a **seam**, and a seam is part of a module's contract
exactly as much as its return values are. Moving resolution behind a seam
removes the seam.

**The repair keeps both properties and neither is optional.** `self_audit._at()`
re-roots every call-time answer on THIS module's `REPO`, and on THIS module's
`WEB` when `WEB` has actually been rebound — the second condition being what
stops the two re-rootings from fighting while the webroot is still inside the
repository. A region that has genuinely moved out of both passes through
unchanged, which is what the later batches need. The shim keeps its
legacy/successor pair; the seam keeps its ability to blind.

**And the general shape, which is why this is a lesson and not a note.** Three
instruments were built for this batch, each measuring something real, and the
defect was found by a test written eight weeks earlier for an unrelated reason.
Purpose-built verification measures what its author was worried about. The
standing suite is what measures what they were not.

Found at MOVE_MAP batch 3b, 2026-08-17.
`demo-output/website/campaign/MOVE_MAP_BATCH3_EXECUTION_2026-08-17.md` §4,
instrument D.

## L-111. A subtotal that reconciles exactly is evidence about arithmetic, not about membership — a rule can be counted, budgeted and scheduled into a batch for a population that is named nowhere

`MOVE_MAP_2026-08-16.md` §2.2 states **R8 = 26 files**:
`scripts/{installed,laptop_bundle}/**` **plus 15 named launchers** → `ops/**`.
Measured at `5d1b41a0` over `git ls-tree -r HEAD`: `scripts/installed/` holds 7
tracked files and `scripts/laptop_bundle/` 4, so 11 + 15 = 26 and the rule
closes to the file. Batch 4's own total closes the same way — 872 claimed,
857 derivable from `lab_paths.redirect()` plus R1's `AWS_TREE_PLAN.md`, and the
difference is exactly 15.

**The 15 are named nowhere.** Not in the map, not in
`MOVE_MAP_EXECUTION_2026-08-17.md`, not in `scripts/lab_paths.py` — whose table
implements R8 as two directory rows and nothing else, so `redirect(
"scripts/demo_servers.sh")` returns `None` — and not in the superseded
`docs/PHASE2_MOVE_MAP.tsv`, which moved *all* of `scripts/` to `ops/` and was
superseded precisely for that. `scripts/` holds 12 top-level `*.sh` files, of
which perhaps seven are launchers, keepalives or preflight by any reading; the
remaining eight of the fifteen would have to come from `*.py`, and no line
anywhere says which.

**The arithmetic is what made it invisible.** Every reconciliation this map has
run — three of them, at three anchors, each closing at zero unclassified — was
green, because 26 is consistent with 11 + 15 whatever the 15 are. A subtotal
that closes proves the counts agree with each other. It says nothing about
whether the population can be *named*, and a batch is executed by naming
files, not by adding them up.

**The rule.** Before executing a rule, ask for its MEMBERSHIP LIST, not its
count — and treat a count with no list as unexecutable rather than as
approximately known. The tell is a rule whose statement contains a bare
cardinal for part of its own scope: *"+ 15 named launchers"* names nothing;
`scripts/{installed,laptop_bundle}/**` names everything it covers. When both
forms sit in one table cell, the reconciliation covers for the half that
cannot be executed.

This is L-94's *"the class needs a membership list, not a shape"* one level up:
there the shape was a classifier that could be run and inspected; here there is
no shape at all, only a number. It is also L-108's shape from the other side —
there a coverage test read an enumeration and could not see the rules
implemented differently; here a reconciliation read counts and could not see a
rule with no enumeration behind it.

Found at MOVE_MAP batch 4, 2026-08-18.
`demo-output/website/campaign/MOVE_MAP_BATCH4_EXECUTION_2026-08-18.md` §2.

---

## L-112. A population defined by agreement loses its member the moment the member disagrees

`scripts/check_consistency.py` in the closure package carries a numeric census:
it scans every figure in every shipped document, maps each VALUE to the set of
files stating it, and requires any value stated in three or more documents to be
pinned, listed with a reason, or reported as unaccounted for. Below three
documents a value is "low fanout, accounted for and unchecked", on the stated
ground that a figure stated once cannot drift against another document.

A fifth verification broke it in one move. **A drift does not reclassify a
value; it splits one value into two.** A figure identical in exactly three
documents and drifted in one of them becomes value A in two files and value B in
one. Both are below the threshold, both are "low fanout", the census reports 0
unaccounted for, and the script exits 0 with every check PASS. Proven by
contrast on the same tree: identical in three FAILS, identical in four with one
drifted FAILS, three with one drifted passes. Nine unpinned figures stood at
exactly three documents that day, so the hole was occupied, not theoretical, and
any figure a later wave adds at three inherits it.

**The rule.** A fanout-based census must classify SITES, not values. Membership
defined by agreement is not membership: it is a property the corpus can revoke
by disagreeing, which is exactly the event the census exists to catch. Where the
classification cannot be made site-local, publish the census's whole SHAPE,
population and site totals and every class total, in a document, and check that
document against the run. A split moves at least two of those numbers, so the
page goes stale in the same edit and the run says which number moved.

**What not to do, measured before it was rejected.** The obvious repair is to
detect the split: cluster values that are one digit or one unit in the last
place apart and treat the cluster as one figure. Measured over that corpus, that
rule found 306 pairs among 392 values. It would have fired on correct prose
constantly, and a check that fires on correct prose is worse than one that stays
silent. The same verification settled the general form of this: deciding whether
a cited document supports a citing sentence is open-ended entailment, so where a
claim cannot be mechanised, DELETE THE CLAIM. Three of that wave's four prose
findings were repaired by deletion, and the one mechanism added was a
hand-written table of two pinned propositions, not an engine.

**The second half of the same wave.** Nothing read the README's account of the
run. The checker's account of ITSELF had been closed a wave earlier; the
document describing the checker had not, and two of the roughly thirty numbers
it restated from the run were false, one of them inside the sentence announcing
that a class had been closed. A derived count published in prose is only as good
as the check that reads the prose back.

**Two mechanical notes for the entry that records this.** Re-derive the next
free lesson ID on every commit ATTEMPT by comparing ID SETS with a
period-anchored regex (`^## L-(\d+)\.`), never by adding one to a remembered
maximum: this file has a hole at L-52 and blocks, distinct numbers and highest
number are three different figures. And write this file back by MERGE, reading
what is on disk at write time and appending to it. Overwriting from a buffer
read earlier destroyed an unlanded tail here on 2026-08-18.

Found 2026-08-18 in `Certonomous_closure_challenge`, fifth verification,
findings 1 and 2 and 6.

## L-113. A claim about what a check ENFORCES is as load-bearing as a claim about a result, and it decays faster, because the check changes under it

Six verifications of the closure package returned 35, 16, 14, converging, 11 and
8 findings. The sixth reported that the falling count was real and the
new-mechanism defect rate was not falling: three of its eight findings were
defects inside the mechanisms the fifth wave had just added, and two more were
false numbers in that wave's own correction notes. Its closing line named the
class: **a reader cannot trust the sentences that say what the checker
enforces.** Three such sentences, all written in one wave, were all false.

**The three.** `description/METHOD.md` said the checker "fails if any shipped
file cites the pre-registration for a pre-solve freeze again"; the scan required
the citation inside a parenthesis within 200 characters of the claim, so leaving
that parenthesis correct and appending one ordinary sentence re-planted the same
false proposition with every check passing. `evidence/audits/README.md` said the
checker "fails if any of the five stops OPENING the way this paragraph says it
does"; the test was a substring test, so moving a head note to the bottom of its
file under an appendix heading passed while the index went on sending a reader
to the head of the file. The root README said a drift at the census boundary
"moves at least two numbers on this page, so it now fails rather than passing
quietly"; a drift that hands the lost occurrence to a value the corpus already
states merges rather than splitting, and conserves the population, the site
total, every class total and the record-derived compared split. One line of one
document was rewritten and every published figure came back byte-identical with
all five scripts at exit 0. Enumerated afterwards: 40,980 such rewrites were
available, at 319 of the 484 sites an unpinned figure stood at.

**Why this class decays faster than a claim about a result.** A result is
written once and the world does not move under it. A sentence describing a check
is written beside the check, is true when written, and then the check is
widened, narrowed, renamed or replaced by the next wave, which ports the code
and not the sentence. Every wave that adds a mechanism adds sentences saying
what that mechanism prevents; the sentences outlive the mechanism's shape. Three
of these were written by the wave immediately before the one that found them.

**The rule.** Every sentence stating what a check prevents, enforces, pins or
fails on must be DERIVED FROM THE CHECK AT RUN TIME, or DELETED. Keep the
checks; delete the promises. A derived count of the check's reach is a
measurement that goes stale loudly; a prose description of its guarantee is a
promise that goes stale silently. Where a limit cannot be closed, publish its
SIZE: enumerate the defects the check does not reach, print the count on every
run, and PLANT ONE OF THEM IN THE CONTROL AND REQUIRE IT NOT TO BE CAUGHT, so
that the day some later check does reach it the control fails and the published
number is corrected rather than quietly becoming an understatement.

**The control steers around its own shape unless you make it stop.** The plant
written for the boundary split selected "a drifted spelling no shipped document
already uses, so that the split makes a NEW value rather than merging into an
existing one" — it steered, by construction, to the half its author could catch,
and it did so under a header stating that a control planting only the defects
its author imagined certifies the author's imagination. A control that chooses
its instance from the catchable half certifies the check on the half it chose.
Derive the instance from the population, and where the population contains
instances the check cannot reach, plant one of those too.

**Bind a derived phrase to the block that makes the claim, not to the page.**
The wave that first read the README's account of the run compared each derived
phrase against the whole flattened page. That page's house style is to keep
correction notes beside live numbers, so falsifying a live table cell and adding
"an earlier draft of this page said ..." elsewhere passed green. An author who
writes the correction and forgets the cell gets a run that agrees with them.
Every derived phrase now names the blocks that must carry it, and every named
block must carry it: a count restated in a second bullet is a second place to
port it to, never a second place a stale copy can hide in.

**Two mechanical notes for the entry that records this.** Re-derive the next
free lesson ID on every commit ATTEMPT by comparing ID SETS with a
period-anchored regex (`^## L-(\d+)\.`), never by adding one to a remembered
maximum: this file has a hole at L-52 and blocks, distinct numbers and highest
number are three different figures. And write this file back by MERGE, reading
what is on disk at write time and appending to it, never overwriting from a
buffer read earlier.

Found 2026-08-18 in `Certonomous_closure_challenge`, sixth verification, all
eight findings.

## L-114. A path shim resolves against the FILESYSTEM, so every lookup into HISTORY it feeds asks a commit for a spelling that commit never had — and at module scope the SkipTest that follows deletes forty-six tests behind one line

`scripts/lab_paths.py` binds every name to a legacy/successor PAIR and picks
between them with `Path.exists()`. That is the right answer to *"where is this
file now"*, which is what ninety-eight converted consumers wanted. **It is the
wrong answer to every question about a different tree** — a git object, an
archive, a snapshot, a remote, a bundle manifest — and MOVE_MAP batch 5 found
three callers that were asking the second question with the first call:

- `scripts/check_summary_consistency.py:226`'s `CONTROL_PATH`, feeding
  `git show 87324012~1:…` and `git show 87324012:…`. Both controls became
  unreadable, the check's own *"a control that misfires makes the whole run
  UNKNOWN"* rule fired as designed, and it went **PASS → UNKNOWN exit 3**.
- `sdk/tests/test_normative_clause_check.py:118`'s `git show 5bec65f0^:…`.
- `sdk/tests/test_summary_consistency.py:196`, the same two blobs, **at module
  scope**.

**The third one is the lesson, because the first two failed loudly and it did
not.** That module loads its two control blobs at import and raises
`unittest.SkipTest` if `git show` fails. So the whole file left the run:
`47 tests` became **one `skipped` line**, and the suite's own summary said
`skipped 1`. Nothing named the forty-six that were gone. The verdict did not
change — the suite was already FAIL on a standing baseline of six — and the
failing-module list was, if anything, *shorter*.

**The only thing that showed it was the collected TOTAL: 2,443 before, 2,398
after.** Not the verdict, not the failure list, not stderr — a count, compared
across the same instrument in the same frame. This is why a batch reports
FINDING SETS rather than verdicts, and it is why the count comparison is worth
doing even when both sides are red for the same reason.

**Two rules follow.**

1. **A shim that answers *where is it now* needs an inverse for *where was it
   then*, and every caller must pick.** `lab_paths.unredirect()` already existed
   for this, documented as *"used to read pre-move records"*, and not one of the
   three callers routed to it. The repair is not a hard-coded legacy string —
   that rots in the other direction the moment a control commit is written after
   a move — but a probe of the named commit: try the literal spelling, its
   `unredirect` and its `redirect`, with `git cat-file -e`, and use the one that
   commit actually holds.

2. **A `SkipTest` at module scope is a hole the size of the module.** Inside a
   test it costs one test and says so; at import it costs every test in the file
   and the runner reports it as a single skip. If a module must be able to
   decline, the decline belongs in a fixture or in `setUpClass`, where the
   runner still enumerates what was lost. And whatever raises it should name the
   path it tried, not only the error: this one printed the successor spelling
   and the commit, which is what made it a two-minute diagnosis once anybody
   looked.

## L-115. A test that blinds a check by rebinding one handle blinds exactly the region that handle covers, and a move that splits one root into seven silently cuts it to a seventh

`sdk/tests/test_empty_set_is_not_agreement.py` and
`sdk/tests/test_form_or_value_and_empty_selection.py` prove that thirteen checks
return UNKNOWN rather than a clean sweep of nothing when their source is absent,
by rebinding `self_audit`'s `WEB`, `REPO`, `ACTIVE`, `WALL`, `CAMPAIGN` or
`MISSION` to an empty directory. D368 repaired `self_audit._at()` so that every
call-time path is re-rooted on those handles rather than reaching past them into
`lab_paths`.

**`_at()` was still doing its job. The handle had stopped covering the region.**
Until MOVE_MAP batch 5, every root `lab_paths.RECORD_ROOTS()` returns was under
the webroot, so rebinding `WEB` emptied all of them. Batch 5 moved records OUT
of the webroot — R16's 19 loose `*.md` to `research/closure/md/`, R23's
`agenda/`, `race/` and the four `closure_*` trees — and `WEB` began blinding
**one root of seven**. `check_evidence_paths_exist` went on reading the live
corpus and returned FAIL; `check_fd_grades_current_standard` returned PASS;
`check_closure_entry_of_record` returned PASS. Three guards that are still
correct, and nothing left able to say so — L-45's defect class B1, in the file
written to refuse exactly that.

**The transferable half is a question to ask before any move, not after.** For
every blinding test: *which handle covers the region after the move?* The answer
here was `REPO`, which `_at()` re-roots on unconditionally and which covers all
seven roots, so the repair was to name it in the case list. **And a fixture that
spells a layout is the same defect wearing different clothes**:
`test_rung_estimates` built its docket at
`<tmp>/demo-output/website/agenda/docket.json` under a swapped `REPO`, which
after R23 is a directory the check no longer looks in — it then returned UNKNOWN
for the *absence* reason instead of the *empty-selection* one, a different
sentence and a different finding, and a weaker test that still looked green in
the count. The fixture now derives its layout from the shim
(`root / lab_paths.AGENDA.relative_to(lab_paths.REPO)`), so it follows every
remaining batch with no edit.

## L-116. A scalar admissibility limit on a MODEL is really a limit on a QUANTITY, and different quantities cross it at different orders

`physics_rules.yaml` carries `boussinesq_beta_dT_max: 0.1` with a careful
paragraph of reasoning and no measurement behind the number. F14 rung K2e ran
the same cavity under `buoyantBoussinesqSimpleFoam` and under stock
`buoyantSimpleFoam` at Ra held fixed, across eleven values of `beta.dT`, and the
two models turned out not to separate on one quantity at all. The peak
horizontal velocity diverges as **24.9 · (beta.dT)^1.005 %** — first order — and
crosses 1 % at `beta.dT` between 0.033 and 0.050, half the limit. The hot-wall
Nusselt number diverges as **6.36 · (beta.dT)^1.968 %** — second order — and does
not reach 1 % until between 0.30 and 0.40, four times the limit. At the limit
itself the two answers are 2.47 % apart on velocity and **0.063 %** apart on wall
flux.

**Why the orders differ, and why that is the general shape.** The cheap model
possessed a symmetry the expensive one does not: the Boussinesq cavity is exactly
centro-symmetric, and the integral wall flux is protected by that symmetry to
leading order while the flow structure is not. Whenever an approximation is a
truncated expansion, the quantities it protects and the quantities it does not
sit at **different powers of the small parameter**, so one threshold on the small
parameter cannot mean one thing.

**The rule.** A threshold on a dimensionless group is not admissible until it
names the quantity it protects and the accuracy it protects it to. Where a single
number already exists, either split it per graded quantity or replace it with the
measured law `D = a·(group)^n` and let each rung compute its own limit from the
accuracy it needs. **And a rung that stays inside such a limit has NOT thereby
established that its answer is inside any error band** — it has established that
somebody once judged the regime plausible.

**The cheap way to get the law rather than the point.** Sweep the group and fit
the exponent, do not test the one value the rule names. The exponent is the
transferable half: it says how a divergence measured at one value carries to
another, which a table of points does not, and it survives a change of case class
far better than the coefficient does. K2e's whole sweep cost 21 core-minutes,
less than one fine-mesh case of the rung that wrote the limit.

Found 2026-08-18 at F14 rung K2e, `docs/campaigns/F14-cooling-ladder/K2e_RESULTS.md`.

## L-117. Parameterise a two-model comparison so that ONE model's answer is invariant, and the setup falsifies itself

K2e had to sweep `beta.dT` while comparing two solvers. The obvious sweep — raise
`dT` at fixed viscosity — also raises the Rayleigh number, so both models change
together for an ordinary physical reason and the measured separation is
confounded with a change of regime. The sweep was instead built to hold Ra fixed
by moving `nu` with `dT`, which costs nothing.

**What that bought was not just the removal of a confounder.** In non-dimensional
form the Boussinesq problem depends only on (Ra, Pr). At fixed Ra and Pr its
answer is therefore **identical at every point of the sweep — a flat line by
theory**. So the cheap model's own branch became a live control: a mis-scaled
viscosity, a mis-generated case, a wrong non-dimensionalisation, any of the
errors that would have made the whole rung meaningless, all show up as a
**sloped** line where a flat one is mandatory. Measured: peak-to-peak spread
**2e-08 to 6e-08 %** across the whole sweep on both meshes. Nothing was asserted
about the generator; the generator was watched.

**The rule.** In any comparison of two models, look for a parameterisation in
which one of them is invariant along the swept axis, and sweep that one. The
invariant branch is then a control that costs no extra compute, runs on every
point, and fails loudly on exactly the class of error a comparison cannot survive.
Where no such parameterisation exists, say so, because it means every point of
the sweep is carrying an unmonitored setup assumption.

**Its companion is a null point, not a null argument.** The same sweep's smallest
value (`beta.dT` = 0.001) is where the two models must agree because the
difference between them is switched off. What they disagree by *there* is a
MEASURED ceiling on any residual datum or property mismatch — 0.097 % on the
Nusselt number, 0.209 % on velocity — and it is the number every later separation
has to clear. An argument that two solvers share a datum is worth less than one
run at the value where sharing it is the only thing that can make them agree.

Found 2026-08-18 at F14 rung K2e, controls C-1 and C-2.

## L-118. An instrument that MUTATES the case it audits destroys the evidence for the claim it is auditing, and it does so after the fact and in silence

`scripts/heat_balance.py` is this lab's standing heat-balance check. At line 770
it calls `shutil.rmtree(<case>/postProcessing, ignore_errors=True)` before
running its own postProcess pass. That directory is the in-pass function-object
history — which is exactly what this campaign's **own** convergence gate reads:
`physics_rules.yaml` `thermal.monitor_*` and
`scripts/check_convergence.py --monitor-regex` are built on it, and
`physics_rules.yaml` refuses residuals as a criterion in writing precisely so
that this history is the thing that decides.

**So auditing a case deletes the proof that it converged.** Measured at K2e:
twelve Boussinesq cases lost `hotFlux`, `coldFlux`, `Umax` and `Tcentre` the
moment the auditor ran, with no error, no warning, and no exit code. K0c's
committed archive carries the same hole — only `hbAudit_*` survives under
`K0c_runs/*/postProcessing/` — and nothing in that rung's documents says why.
The two instruments are on the same side, which is what made it invisible: the
one that grades convergence and the one that grades closure were never run in the
wrong order deliberately, so nobody found out that order matters.

**The rule, in three parts.** (1) **Run an instrument on a copy** unless it is
documented as a mutator; `analyse_k2e.py` now copies each case into a temporary
directory before auditing it. (2) **An instrument's side effects are part of its
contract and belong in its docstring beside its exit codes**, because a caller
choosing between two checks cannot read 800 lines to find out that one of them
deletes something. (3) **When an archive is missing a directory it should have,
that is a finding, not tidiness** — the K0c hole sat in the repository for a day
being read as normal.

**The same path carried two more.** The auditor requires
`constant/transportProperties` and so **refuses outright on any `rhoThermo`
case** — it cannot audit the very solver class the Boussinesq limit tells a rung
to move to. And six of its refusal sites `raise SystemExit("REFUSE: …")`, which
exits **1**, while its own docstring promises exit **2** for a refusal and exit 1
for "the balance did not close". Measured: a nonexistent case directory and an
empty case both exit 1. A caller reading the exit status cannot tell a refusal
from a finding — the failure mode L-113 names, in the file that documents itself
most carefully.

Found 2026-08-18 at F14 rung K2e, while auditing 30 cases; docketed.

## L-119. A control's SIZE is part of its design: a plant carried over from the previous rung cannot fail on this one

**The rule.** When a planted-source control moves to a new case, **re-derive the
plant size against the new case's own ledger before running it.** A plant is a
control only while it is large enough that the instrument reading it can be
wrong. Carry the previous rung's number across unexamined and you get a control
that passes for the same reason an unplugged instrument reads zero.

**Why.** At rung KV1 the advective heat-balance path was validated by planting
**5.000e-03 W** into a duct whose ledger carried 0.146 W. The plant was 3.4 % of
the ledger, its recovery was measured at **+2.40e-08 %**, and the control earned
its keep. K2b's pre-registered control set (K2a section 8, "C3 planted
volumetric source — KV1's plant in the room") named the same control for a rack
row whose ledger carries **4.914e+03 W**. The same 5 mW there is **1.0e-06 of
the ledger** — nine orders below the 0.5 % band the closure is graded against,
and roughly seven orders below the several watts of closure noise the case
actually carries at any affordable convergence. **An instrument that returned
exactly zero would have "recovered" it**, and the run would have been written up
as a passing control.

This is KV1b's defect arriving by a different road. KV1b was kept on the record
precisely because it "passed while proving nothing": its field was uniform, its
advective sum was identically zero, and sign flips and factor-of-two mutations
were all correctly invisible. That was a degenerate **field**. This is a
degenerate **size**, and no amount of reading the case dictionary reveals it —
the dictionary is identical in both, and the number that decides whether the
control can fail lives in the *other* case, the one the ledger belongs to.

**How to apply.** Before running any planted control, state three numbers
together: the plant, the ledger it sits in, and the tolerance it is graded at. If
the plant is not comfortably above the case's own closure noise, the control
cannot fail and must be re-sized or dropped — not run and reported. K2b re-sized
to **500.000 W**, ≈10 % of the rack load, so that its 0.1 % recovery tolerance is
0.5 W. **And the re-sizing is not free**: at 500 W the control became
convergence-limited instead of size-limited, its recovery reading 155.55 W at 400
iterations and 315.57 W at 800 against the planted 500.000 W, and the pilot's
authorisation did not hold the ~5,000 further iterations needed to land it. A
control that can fail costs more than one that cannot. That is the trade, and it
is the right way round.

## L-120. A spec that cites a boundary condition's `Description` has not read its code path, and the branch it quoted was the fallback

**The rule.** When a specification pins behaviour on a library boundary
condition, the citation must be to the **function that runs** — `updateCoeffs`,
`correctBoundaryConditions` — and not to the `Description`/`Usage` block above
it. Doxygen prose describes intent; a BC with branches has more than one
behaviour and the prose usually documents one of them.

**Why.** `K2a_RACK_ROW_MODULE_SPEC.md` section 3.3 is the load-bearing row of the
whole module — the rack rise ΔT = P/(ṁ·cp) is imposed by
`outletMappedUniformInlet` — and it states, with a source path and the tier
"READ IN SOURCE":

> The face-averaging in the BC is area-weighted (`gWeightedAverage` over `magSf`
> in the source) ... the analyser must print both once and show their difference
> is below the gate resolution, **or switch the grading to the BC's own area
> average**.

Read in `outletMappedUniformInletFvPatchField.txx`, `updateCoeffs()`, v2606 has
two branches and the one the spec quoted is the **`else`**:

```cpp
if (sumOutletPhi > SMALL)
    mapField.append(gSum(outletPhi*outletFld)/sumOutletPhi*fraction + offset);
else
    mapField.append(gWeightedAverage(outlet.magSf(), outletFld));
```

Three consequences, measured at K2b: the BC is **mass-flux**-weighted in normal
operation, so the spec's remedy pointed the wrong way and taking it would have
moved the graded quantity **0.403 K — 3.4 % of the rack rise** — away from what
the BC computes; the two averages are **not** within any gate resolution on this
geometry; and the fallback branch **appends no `offset` at all**, so a rack front
face that ever loses net outflow hands the rear face the front face's own
temperature and a rack that adds no heat reads exactly like a converged one.

**The reversal is the part worth carrying.** The spec's own mandated check ("print
both once and show the difference is small") was written to close a
units-of-averaging dispute that does not exist, and it was silent on the branch
that can silently delete the module's only heat source. **A check aimed at the
wrong hazard reads as diligence and buys nothing** — which is L-113 (a claim
about what a check enforces decays faster than a claim about a result) landing on
a boundary condition instead of a script.

## L-121. A convergence criterion certifies the quantity it watches, and K2b measured it failing in both directions on one module

**The rule.** Do not let one converged quantity stand in for another. A
peak-to-peak monitor on the graded quantity and a heat-balance closure are two
independent verdicts, and **neither implies the other in either direction.** Run
both, report both, and when they disagree say which quantity each was watching.

**Why.** On the K2b rack-row pilot, at the same iteration count, on two cases of
the same module:

| case | S13 on T_in (peak-to-peak, 0.02 % band) | heat-balance closure (0.5 % band) |
|---|---|---|
| `K2bP_coarse` @ 5,000 | **PASS**, 0.00136 % | **FAIL**, 0.5244 % |
| `K2bP_under` @ 5,000 | **FAIL**, 0.34553 % | **PASS**, 0.1272 % |

The counterexample runs both ways and the reasons are different in each
direction. On the balanced case the monitored quantity is the rack inlet
temperature in a **contained** cold aisle that is nearly isothermal: it had
stopped moving three orders inside its band while the room's energy field was
still half a percent out of balance. On the recirculating case the ledger closed
while the monitored quantity was still swinging by a full kelvin, because closure
is an integral over the whole boundary and averages a swing away.

The sharpest instance is a third case. `K2bP_fine`, at 1,500 iterations, has a
heat balance of **2.6632 %** and a free boundary swinging **0.23585 %** — and on
the specified monitored quantity it scores **0.00000 %, the best score the
criterion can return**, because T_in reads exactly 289.000000 K in a cold aisle
nothing has reached yet. Two of the rung's controls read perfectly on that same
case for the same reason: the offset readback errs by **0.000e+00** and the
mass-versus-area averaging comparison by **−0.0001 %**, both because the rack
face is still uniform. **A monitor or a control is most flattering exactly where
the case is least converged**, which is KV1b's uniform field wearing a third
costume.

**Neither reading was wrong. Each was a fact about the quantity it watched**, and
a rung that reported only one of them would have shipped a sentence about the
other. Note also that this cuts across the standing wisdom in the obvious
direction only half the time: it is well recorded here that residuals do not
certify the graded quantity (S13's whole content), and K2b adds that **the graded
quantity does not certify the energy field either.**

## L-122. A population swept over HEAD and a population swept over the working tree are two different populations, and on this tree the difference reached whole rung records

The validation inventory (`docs/VALIDATION_INVENTORY.md`) was measured over
`git ls-tree -r HEAD` because the commit protocol mandates that frame. Measured
at `b845b603`, `git status --porcelain` showed **2,699 tracked paths deleted from
the working tree and present in HEAD**: an uncommitted `git mv` batch had moved
`demo-output/website/dafoam/`, `tmr/`, `mega-batch/` and others to `cases/`. In
the other direction, three F14 rung records existed **in the working tree and in
no commit at all** when the sweep opened, and `K1_STANDING_THERMAL_CHECKS.md`
existed in HEAD and had been deleted from the working tree.

**Both arms held rung records, so either frame alone gives a wrong population.**
A HEAD sweep would have missed K2b and K2e entirely; a worktree sweep would have
missed K1 and would have cited paths under `cases/` that no clone contains. One
of the three, `K2e_RESULTS.md`, landed at `b845b603` **while the sweep was
running**, and two more commits landed before it finished.

**The rule.** State the frame, sweep it, and then run `git status --porcelain`
as a second instrument whose only job is to report what the frame cannot see.
Cite HEAD paths, because they are the ones a reader can fetch, and say in the
document that a path not on disk should be looked for under its new root. A
sweep that names its frame and never measures the other arm has not stated a
limit; it has stated a preference.

## L-123. `git log -- <path>` truncates at a rename, so a verdict's commit anchor derived per path dates the move rather than the verdict

Every verdict in the inventory had to carry the commit that landed it. The
obvious derivation, `git log --format='%h' -1 -- <path>`, returned
**`f69a3ed5`, a MOVE_MAP batch commit**, for lesson L-106's introduction, because
`LESSONS.md` had been relocated into `docs/` and the default log walk stops at the
rename. The true anchor is `0ab6c39a`, three commits and one day earlier, and it
carries a message about the finding rather than about a file move.

`--follow` is not the fix: it "requires exactly one pathspec" and fails on the
multi-path form the derivation needs. **What worked was dropping the pathspec
entirely and searching content across all history:**
`git log --all -S'<distinctive text>' --format='%h %ad %s' --date=short | tail -1`.

**The transferable half.** On a tree with an active reorganisation, *every*
per-path history query is dated by the reorganisation rather than by the work,
and the failure is silent and plausible: it returns a real commit, recently, with
a real message. Anchor a claim by its **text**, not by its **path**, and spot-check
that the message the anchor carries is about the thing being anchored. Twenty-five
anchors were checked that way for the inventory's F-series table and all twenty-five
matched their subject; the one that did not was found only because its subject
was obviously wrong.

## L-124. A tier is a property of the reference, not of the solve, so a lab-wide tier count is a count of references obtained

Counting the whole lab's gates one row each produced a result none of the
individual records could show: **135 distinct gates and rungs, and three cases
carrying a VALIDATED chip.** The largest single reference class, at 43 percent of
rows, is the lab's own earlier run, its own text or its own code.

**The rungs are not weak. The references are absent.** F14's K0c grades 24 of 24
rows inside band, on a mandatory two-mesh pair per Rayleigh number, with five
controls including a planted 10 percent Rayleigh error that the same comparator
fails at 3.19 percent and a comparator mutation proving every one of the 24 rows
individually reachable. It is capped at TREND ONLY, correctly, because de Vahl
Davis is a numerical benchmark rather than an experiment. No amount of further
instrumentation moves it.

**The consequence for planning.** Asking "what should we run next" optimises the
wrong variable when the ceiling is set upstream of the solve. Seven of the nine
highest-value actions the inventory identified cost **no core-minutes at all**:
read a public-domain NACA report, declare the bands that were never declared,
record an extraction route, make a caption carry a qualifier that already exists
in its own case record. The lab's binding constraint is reference acquisition and
reference transmission, not compute and not solver capability.

---

## L-125. A scaling exponent read off two rows of a reference table belongs to the reference's own dimensionless variable, and a control that applies it to a dimensional quantity predicts the wrong number by half

The load-bearing control on F14's K0c turbulent rung was the same shape as the
laminar rung's: **derive the expected shift from the reference table's own
numbers before the run, then plant the error and measure.** The laminar rung did
it and measured +2.916 % against a predicted 2.76 to 2.90 %. It is the single
practice that makes a gate's pass mean something, because a band that cannot see
a known error is decorative.

**Here the same practice produced a prediction that missed by 50 %, and the
reason is worth more than the control was.**

The reference tabulates a mid-height peak velocity at two Rayleigh numbers:
**+0.140 m/s at Ra 0.86e6** and **+0.190 m/s at Ra 1.43e6**. Registered before
the run, from those two rows and nothing else:

    n = ln(0.190/0.140) / ln(1.43/0.86) = 0.600
    a 30 % rise in Ra therefore gives 1.30^0.600 = +17.4 %

The control planted a 30 % Rayleigh error and measured **+11.9 %**.

**The exponent was never a Rayleigh exponent.** Velocity is dimensional:
`V = (alpha/W) . f(Ra, Pr)`. The reference's two rows differ in *fluid properties*
as well as in Rayleigh number — different mean temperature, therefore different
`alpha` — so the ratio of the two tabulated velocities carries **both** changes,
and reading it as an exponent of Ra alone silently attributes the property change
to the Rayleigh number. Dividing `alpha` out first gives n = 0.433 to 0.494, and
`1.30^n` = **+12.0 to +13.9 %** against the measured +11.9 %: agreement at the
bottom of the range to within 0.14 points.

**The plant in this control changed Ra at FIXED properties**, which is not the
transformation the reference's two rows represent. Two different transformations
were being called by the same name.

**Three things follow, and the third is the one that generalises.**

**1. Non-dimensionalise before you fit an exponent, always, even across two
points.** The step feels pedantic on two rows of a table. It is exactly where the
error hides, because with two points there is no residual to look wrong.

**2. Name the transformation the plant performs, in the prediction, in words.**
"Ra raised 30 %" is ambiguous: by dT at fixed properties, by properties at fixed
dT, by length. The registered prediction said "a 30 percent rise in Ra" and the
case did it by dT. Had the prediction been written as "dT x 1.30 at fixed nu and
beta", the mismatch with a two-row fit spanning a property change would have been
visible before the solver ran.

**3. A missed prediction is worth reporting at full volume, and the correction
must be labelled POST HOC in the artefact, not only in the prose.** The corrected
derivation here was made after the measurement was read. It is an explanation and
not a prediction, and an explanation that fits perfectly is exactly what a
post-hoc derivation always produces. It is stored in `gate_k0ct.json` under keys
ending `_POST_HOC` so that no later reader — and no later script — can mistake
the two. **The registered prediction stays in the record, missed, beside it.**

**And the control still did its job**, which is the part that is easy to lose:
the in-log witness showed the running solver's own wall temperatures at
51.870 K against 39.900 K, a ratio of **1.3000000**, so the plant was in the
solver and not in a dictionary; and the graded row's deviation moved from 16.4 %
to 31.1 % under it. What failed was the *magnitude* prediction, not the control.
Reporting "control passed" would have been true of the verdict and false of the
number, and the number is what was being registered.

Found 2026-08-18 at F14 rung K0c-T, on a control whose verdict prediction held
and whose value prediction did not.

---

## L-126. A mechanism that measures itself generates defects at the rate it closes them

**The measurement.** Seven verifications ran over one package's own
consistency checker, returning 35, 16, 14, converging, 11, 8 and 8 findings.
The seventh was the one that decided anything: **six of its eight findings sat
inside mechanisms the previous wave had built or repaired. Five mechanisms had
changed in that wave; four of the five were defective.** That is not
convergence. It is the same defect rate one level in, and the defects are now
self-referential, because the mechanism under test is the mechanism doing the
testing.

**Two of the eight show why more care does not fix it.**

**1. A derivation memoized by tree path, read by a control that mutates the
tree.** The checker's newest control planted a defect in a copy of the package
and asked, in the same process, whether the checker reported it. The function
that chose the plant's target cached its answer under `str(root)`. The control
called it once to pick a target, planted the defect, and called it again in the
same process against the same path, getting the pre-plant answer back. In a
fresh process the planted tree exits 1 with five failures. **The control's own
stated failure condition was already met and the control could not say so.**

**2. Publishing the size of a blind spot can close that blind spot.** The same
wave published a count of the rewrites its census could not see, as a
measurement rather than an assertion, on the reasoning that a number is more
honest than a sentence. But the count's own outputs are published in the
package, and every rewrite of the class moves them. **66 of 68 sampled members
of the class were caught by the very publication that quantified them.** The
sentence quantifying the hole was false for about 97 percent of the population
it quantified, and the publisher had no way to notice, because the thing that
would have told him was the number he was publishing.

**How to apply it.**

* **Run a planted copy in a separate PROCESS, always.** Not a fresh object, not
  a cleared cache: a new interpreter. Any module-level state, any memo keyed by
  a path a control edits, and any list a control mutates in place will otherwise
  carry a value taken from the clean tree into the planted one. This single
  change would have caught the first defect above on the day it was written.
* **Never memoize by tree path a derivation that a control mutates the tree
  under.** The key looks unique and is not: the same path names two different
  trees before and after the plant.
* **Do not publish a number about your own blind spot.** The act of publishing
  it puts the number inside the population it measures. Publish what the run
  measured about the OBJECT, and let the reader take the reading themselves.
* **When the defect rate does not fall between waves, stop repairing and start
  deleting.** The right move is the one the seventh verification recommended:
  shrink the surface. The mechanisms with the best ratio of findings to lines
  were the smallest and most hand-written ones; the worst were the ones that
  measured themselves.

**What was done with it, 2026-08-18.** The self-describing mechanisms were
deleted rather than repaired: the checker's account of itself, the page's
account of the checker's run, the blind-spot enumerator with the shape it
planted, and the class of sentences stating what a check prevents, enforces,
pins, catches or fails on. The checker went from 6305 lines to 4788 and from 22
checks to 20; the sentence class went from 217 to 60 by a scanner that derives
the population rather than listing it. Every one of the 25 retained planted
shapes is still caught, by the same check that caught it before.

Found 2026-08-18, on the closure-challenge submission package, after seven
verification waves over the same checker.

## L-127. A repository root derived by counting segments up from a path that moves is a path literal no grep can find

**The incident.** MOVE_MAP batch 6 moved `demo-output/website/dafoam` to
`cases/dafoam` — two segments shallower. `sdk/tests/test_a2_shape.py:28` read

```python
_SDK = _a2_shape._LADDER.parents[3] / "sdk"
```

and `_LADDER` is `lab_paths.DAFOAM / "ladder-a"`. Before the move `parents[3]`
was the repository root. After it, `parents[3]` was `/home/ubuntu` — the
repository's PARENT — and `_SDK` pointed at `/home/ubuntu/sdk`, which does not
exist.

**Why the standing defences did not see it.** Batch 3b converted ~150 path
literals to the shim and every later batch runs a Class-1 scan over every
tracked non-`.md` file with **no suffix filter** (D371). This line contains no
path literal. `git grep 'demo-output/website/dafoam'` does not match it,
`git grep 'parents\['` returns twenty lines of which nineteen are rooted at
`Path(__file__)` and are correct, and the shim itself is used **correctly** —
the constant followed the move exactly as designed. What did not follow is the
**arithmetic performed on it**. A path constant that moves changes its DEPTH as
well as its prefix, and only the prefix is visible to a text search.

**What it cost, and which half is the lesson.** Two tests failed. One —
`test_control_room_keeps_the_old_defaults_verbatim` — raised
`FileNotFoundError` on the missing file: loud, immediate, unmissable. The other
— `test_hint_free_payloads_are_untouched_by_the_hint` — globbed an absent
directory, got **nothing**, and went on asserting its projection identity over
the ten synthetic bodies it builds itself. **Every assertion in it passed while
it compared no real geometry at all.** The only thing between that and a silent
green was the test's own floor:

```python
assert len(bodies) > 20      # read 10
```

**The rule.** When a path constant moves, search for **arithmetic on it**, not
only for its spelling: `.parents[N]`, `.relative_to(...)`, `str(...).split("/")`,
any index into a path. Where a root can be named directly, name it — the repair
here was `_SDK = _a2_shape.lab_paths.SDK`, a bound non-moving name, which is
correct at every depth and needs no edit at any future batch.

**And the corollary, which is the transferable half.** A sweep that finds
nothing must be **floored**, not merely asserted over. `assert len(x) > N`
before the loop is the difference between a finding and a green comparison of an
empty set — the same shape as `RECORD_ROOTS` losing nineteen records at batch 5,
`ArchiveSweepTests` naming its five logs individually rather than counting them
at batch 6, and every silent zero this file records. **Whoever runs batch 7
should expect this class**: seven modules under
`demo-output/website/campaign/` derive the repository root by segment counting
and every one of them lands on `/home/ubuntu` after R20/R21 — measured, not
predicted (docket D385).

## L-128. The identity defect is not a property of the heat balance; it migrates, and it arrived next in the convergence criterion

**The rule.** Whenever a check returns a *score* rather than a verdict, ask what
that check returns on an input where the quantity it measures **cannot vary**.
If the answer is its best possible score, the check has an identity defect and
must be taught to REFUSE that input, not to grade it. Ask this of every new
check at the moment it is written, because this lab has now met the same defect
three times in three different instruments.

**Why.** The defect's history here is the argument:

| where | the quantity that could not move | what the check returned |
|---|---|---|
| K0b, sealed heat balance | boundary conduction forced to sum to zero by the discretisation | 0.0128 % imbalance — a pass, at iteration 10, on an unconverged case |
| KV1b, advective ledger | a uniform field, so the advective sum was identically zero | closure passed, and every mutation was correctly invisible |
| **K2b, the S13 convergence criterion** | a graded temperature pinned at the supply value in a region the solve had not reached | **0.00000 %, the best score the criterion can return** |

At K2b the graded rack-inlet temperature printed `289.0000002` falling to `289`
across the whole 400-iteration window — **one unit in the last place of a
ten-significant-figure print** — while the same case's heat balance was 2.6632 %
out and its free boundary was swinging 0.23585 %. S13 asks *has the graded
quantity stopped moving?* and cannot answer that on a quantity that never
started, so it returned the most flattering answer available. Two of the rung's
own controls read perfectly on the same case for the same reason, the rack face
still being uniform.

**How to apply.** The repair is always the same shape and it is worth stating as
a pattern: **refuse the unresolvable input instead of scoring it**, exactly as
`heat_balance.py` refuses an undefined imbalance ratio rather than renormalising
it into a flattering 100.0000 %. At K2b that became `thermal.monitor_min_resolved_ulp`
— a spread below ten units in the last place of the series *as printed* is
`CANNOT_TELL`. Two properties made the repair safe to ship and both are worth
copying: it was **proved in both directions** (the stalled case now refuses at
1 ulp; the genuinely converged case still passes at 29,290 ulp), and the
constant was shown **not to be load-bearing** by re-grading the whole affected
corpus across it — the verdict set is identical for any floor from 2 to 13,161,
3.8 orders of magnitude, and exactly one verdict of fourteen changed.

**And the tell was already in the record, unread.** `MONITOR_STANDARD.md`'s own
S13 replay line had recorded six K1c controls passing "at **0.000e+00** to
1.793e-08%". A spread of literally zero is the defect, written down, in the
standard that defines the rule, and nobody read it as one. **A number in your own
replay line that is too good is a finding, not a trophy.**

**AMENDED 2026-08-18, hours later, by the repair's own second pass.** Two things
this entry got wrong or left short, both found by widening the corpus:

- **The generalisation is bigger than one number.** *The instrument documents the
  defect it contains, and the documentation reads as a strength.* This is the
  same shape as the other findings of the same day: `heat_balance.py` printed
  "NOT of the identity class, so the balance is a genuine constraint here" over a
  ledger whose advective term it had never computed; the audit deleted the very
  convergence history the campaign's own criterion reads (D375); and S13's replay
  line published a spread of zero as evidence of rigour. **When an instrument
  prints a claim about its own soundness, that sentence is the one to go and
  check first**, precisely because nobody else will.
- **The repair shipped in this entry had a false positive, and it fired on four
  committed cases.** Testing the WINDOW SPREAD against the print resolution
  cannot distinguish "never moved" from "converged to the last bit" — both give
  a spread of zero. K2e's four `m96_*_bou` cases print sixteen significant
  figures, bit-identical across the window, after travelling 0.53; they were
  refused. The corrected clause tests **the range over the whole run**. The
  lesson inside the lesson: **a refusal is a verdict too, and it needs its own
  two-way proof — not just "does it catch the bad case?" but "does it leave the
  good one alone?" on a corpus wide enough to contain one.**

## L-129. A re-grade is only as good as the corpus you swept, and the corpus is every case that was graded under the old reading

**The rule.** When you change a criterion, the re-grade must cover **every case
that was ever graded under the old reading**, not the cases in front of you. Go
and enumerate them — by searching the tree for committed monitor series, not by
recalling which rungs you know about. If you cannot reach some of them, say which
and why, in the record, at the time.

**Why.** At rung K2b the S13 convergence criterion was repaired and re-graded
over **fourteen** cases: K0c's eleven and K2b's three. That was the corpus the
author had in hand. It was wrong. **K2e's thirty cases had been graded under the
same old reading and were sitting in the same tree**, committed hours earlier by
a peer working the same campaign. Nobody withheld them; they were simply not
looked for.

**What the omission cost, and it was not hypothetical.** Widening the corpus from
14 to 49 immediately exposed a **false positive in the repair itself**: four of
K2e's cases print their graded quantity to sixteen significant figures,
bit-identical across the window, having travelled 0.53 to get there — as
converged as a double-precision solve can be — and the new clause refused all
four. The narrow corpus contained no case of that kind, so the repair looked
clean, was written up as clean, and shipped. **The corpus that would have
falsified it existed, was committed, and was one `find` away.**

**How to apply.** Enumerate mechanically. The corpus is defined by *the artefact
the criterion reads* — here, every committed log carrying a monitor series — so
find it with a search over the tree, and state the count in the record so a
reader can tell a swept corpus from a convenient one. And when a repair changes
no verdicts anywhere, treat that as a reason to widen the corpus rather than as
a result: a repair that cannot move anything may be a repair that has not met
the case it is for.

## L-130. A gate's band is part of its referent, and a generator that supplies a default for it prints PASS over the act's own failure

**Measured on the lab's most-filmed surface on 2026-08-18.** Act 1 of the
nine-act gate table, the Re 100 cylinder, declares its own gate in its own
transcript: `mission-output/cylinder-vortex-shedding/transcript.md:5`, *"Gate:
Strouhal number against the Roshko and Williamson correlation, **within
0.70%**"*. The deviation the same transcript prints is **0.77 percent**. The
published table reads **PASS**.

**Both statements are true and the table is not lying about the number.** It is
resolving a band the act declared and the table never received. That act's
transcript carries no `Verdict:` line, so `scripts/gate_table.py` fell through
to `_tolerance_verdict(dev, limit=5.0)`, a default written into the generator
years of commits ago as a reasonable screen for the four exact-theory rows
around it. **The default is not wrong. Its invisibility is.** Four other rows on
that table declared no band at all and were decided by the same 5 percent
screen, and no reader of the table could have told those four from the one that
declared 0.70 and missed it.

**Why this is the same defect as a missing referent and not a smaller cousin of
it.** `VERIFICATION_CHARTER.md` section 6a requires a verdict to carry the thing
it was checked against. A band is the second half of that thing: *0.1590* and
*0.1590 plus or minus 0.70 percent* are different referents, and a surface that
prints the first and silently supplies the second has substituted its own
standard for the act's exactly as surely as if it had substituted its own
number. **Transmission loss on a tolerance looks like agreement.**

**The shape to look for.** Any generator that reads a measured value and a
reference value out of an artifact and then decides PASS itself is holding a
threshold the artifact did not give it. Ask of every such default: *what does
the surface print when the artifact's own threshold and mine disagree?* If the
answer is "mine, silently", the surface has a verdict it did not earn. The
repair is not to delete the default, which would turn four honest rows into
PENDING. It is to **print which one decided the row**, per row, and to parse the
artifact's band back out rather than assert it, because a band the generator
supplied would be the generator's band wearing the act's name.

**And the corollary that made this findable at all.** The band was recovered by
reading the act's transcript, which is gitignored and off-repo. The sweep that
built `docs/VALIDATION_INVENTORY.md` concluded of the NASA hump row that *"no
threshold exists that a larger miss would have crossed"*, and that half of the
sentence is wrong: `mission-output/nasa-hump/transcript.txt:14-17`
pre-registered plus or minus 5 percent on separation and plus or minus 20
percent on reattachment, before the solve, in a block headed *"What would
falsify this, fixed before the solve"*. The inventory's own section 1.3 says
that the raw evidence for nearly every gate is off-repo and that it could not
read it. **A record that states what its sweep could not see lets the next
reader correct it instead of inheriting it**, and that is the second half of why
this lesson is short.

## L-131. A citation can name the right report and link the wrong one, and a constant attributed to an author can be absent from the work attributed

**Both halves were found in one comment on 2026-08-18**, in
`sdk/workflows/cylinder_vortex_shedding.py:22-24`, which cites *"Roshko, A.
(1954), NACA Report 1191 (St ~ 0.212(1 - 21.2/Re) for 50 < Re < 200)"* with the
link `https://ntrs.nasa.gov/citations/19930091905`.

**The link resolves to NACA Report 828**, Stowell, Schwartz and Houbolt, 1945,
*"Bending and Shear Stresses Developed by the Instantaneous Arrest of the Root
of a Moving Cantilever Beam"*, a structures paper with no cylinder in it. This
was established twice, by fetching the NTRS record and by downloading the PDF at
that identifier and reading its title page, which prints `REPORT No. 828` three
times. Roshko's report is NTRS `19930092207`. **Nothing in the repository was in
a position to notice**: the name is right, the number is right, the year is
right, and the only wrong field is the one no reader retypes.

**The second half is the one that needed the report itself.** The correlation
the gate actually evaluates is `St = 0.198(1 - 19.7/Re)`
(`sdk/workflows/_exact_theory.py:260`), whose docstring calls it *"the
Roshko/Williamson"* form. Read at last, NACA Report 1191 gives two Strouhal
forms and the Reynolds range of each, on its printed page 11: **(2a)
`S = 0.212(1 - 21.2/R)` for `50 < R < 150`** and **(2b) `S = 0.212(1 - 12.7/R)`
for `300 < R < 2,000`**. `grep -c '0\.198\|19\.7'` over the extracted text
returns **0**; the positive control `grep -c '21\.2\|0\.212'` on the same file
returns **8**, so the zero is an absence in the report and not a dead text
layer. **Neither constant in the form the lab grades against occurs anywhere in
the report the lab names for it.**

**What no amount of internal checking could have reached.** The lab had a
correlation, an arithmetic implementation of it, a test of that implementation,
a passing gate and a citation, and every one of them was self-consistent. The
proposal that sent this reading put it exactly right in advance: *"a check that
compared our arithmetic against our own constants would pass with the
attribution entirely wrong, which is precisely the state the gate is in
today."* **A source question has no internal answer.**

**The rule.** When a record cites a document by name, number, year and link,
those are four independent claims and three of them are cheap to check. Resolve
the identifier, not the name. And when a constant is attributed to a paper,
**the attribution is verified by the presence of the constant in the paper**,
which is a one-line grep once the paper is on disk and is unavailable by any
other means. A citation that has never been opened is a claim about a document
nobody has seen, and this lab already has the rule for that shape:
`VERIFICATION_CHARTER.md` section 14, *"an attribution is a claim, and it is a
claim about a file. Name the file, and open it before the finding leaves the
room."*

## L-132. A pre-registration survives amendment; it does not survive a moved threshold. Amend the run, never the ruling

**The rule.** When a pre-registered test has to change mid-flight — and it will,
because the thing most often mis-estimated is its cost — **amend the RUN and
never the THRESHOLDS or the outcome-to-meaning mapping.** Write each amendment
down with its timestamp *and the state of the data at that moment*, so a reader
can verify the amendment preceded the evidence it could have been fitted to. An
amendment made before the window it changes has any data in it is a schedule
change. The same amendment made afterwards is a result.

**Why.** The K2b-U unsteadiness diagnosis was pre-registered and hashed before
any diagnostic solver ran, and then amended **three times in ninety minutes** —
every one of them forced by a wrong cost estimate:

| # | what it changed | why | data in the affected window when written |
|---|---|---|---|
| 1 | 40 s → 20 s run | cost read as 1.7 core-min per second of physical time | none — t was 3.0 s, windows began at 5 s |
| 2 | back to 40 s, original windows restored | the same cost measured against the process's own CPU time was **0.72**, not 1.7 | none — t was 5.2 s, windows began at 20 s |
| 3 | grade BOTH window definitions | wall-clock, not CPU, was binding: ≈9× under contention | none — t was 12.2 s, the earliest window began at 12.5 s |

**Not one threshold moved.** B ≥ 0.30 K non-decaying = physical, B ≤ 0.10 K or
decaying = numerical, A ≤ 0.20 K / ≥ 0.51 K — all fixed before anything ran and
all still standing at the verdict. That invariance is the property that makes it
still a pre-registration rather than a narrative built around an answer.

**Amendment 3 is the shape to copy** when a shortened run is unavoidable: rather
than *choosing* the surviving window definition after seeing which one the data
would reach, it graded **both**, each of which had itself been fixed before its
own data existed. **A choice you can avoid making is better than a choice you can
justify.**

**And note what kept being wrong.** Three cost estimates on one rung: a
100-iteration probe under-priced a long run by **1.9×**; an amendment priced CPU
from contended wall-clock, **2.3×** out; the next priced wall-clock from CPU,
**9×** out. **A cost estimate is a measurement and deserves the same suspicion as
any other** — including the question every other measurement here gets asked:
*which resource is this actually measuring, and is it the one that binds?*

## L-133. When several independent measurements hit the same noise floor, stop improving the instruments and go and find the mechanism

**The rule.** Two or more differential measurements failing at *the same*
resolution, for reasons that look unrelated, is not two instrument problems. It
is one signal. **Stop refining the instruments and go and test the thing they
have in common** — usually the case itself. The cost of that test is almost
always smaller than the cost of the plan it can invalidate.

**Why.** Rung K2b hit the same wall three times before recognising it:

| measurement | why it failed | the number |
|---|---|---|
| C3, planted-source recovery | the no-plant twin's ledger wandered | 48.313 W against a 0.500 W tolerance |
| the wall-treatment comparison | the twins swung more than they differed | 0.5466 K spread against a 1.0832 K swing |
| S13 and the closure audit | neither would settle on the recirculating case | 0.34553 % against 0.02 %, 0.7857 % against 0.5 % |

Each was written up separately, and each was written up **as a limit of the
measurement**. The first two even carried the correct sentence — *the
unsteadiness is the binding limit, not the instrument* — without anyone drawing
the conclusion that the unsteadiness was therefore the thing to measure.

**What it cost to test, and what it saved.** A pre-registered diagnosis — a
halved-under-relaxation twin and a 40 s transient — came back **physically
unsteady**: a coherent 6.0 s limit cycle of ≈1.1 K that does not decay and that
*grows* when under-relaxation is halved. **36.75 core-minutes**, against a
374–697 core-minute graded pair that it invalidated, and which would have
produced a converged-looking answer to a question the configuration cannot
answer. Everything above it would have inherited that.

**How to apply.** When you write "the instrument could not resolve it" for the
second time in one rung, **stop and ask what the two cases share.** Then design
the discriminator so it can come back either way, pre-register what each outcome
means, and run it before spending anything that depends on the answer. The
diagnosis that says "your plan is fine" is worth the same as the one that says it
is void — and you cannot get either honestly unless both were possible.

**THIS IS NOT A THERMAL LESSON, and the evidence above is only where it was
caught.** The shape is: *several independent probes bottom out at the same
resolution, each is written up as a limit of its own probe, and the common cause
is never named because no single write-up is wrong.* It is a statement about how
a lab reads its own records, and it is available in any domain that measures
differences. The same pattern, outside CFD:

- **Flaky tests.** Three suites each "occasionally time out under load", filed
  three times as three flaky tests, when one shared fixture is serialising.
- **Benchmarks.** Several latency comparisons all "within noise", each written up
  as needing more samples, when one shared warm-up is dominating the variance and
  no sample count will fix it.
- **Evaluation.** Several graders "cannot separate the two models", reported as a
  weak grader each time, when the prompt they share caps the achievable spread.
- **Reconciliation.** Several audits "off by rounding", when one upstream feed is
  quantised and the rounding is the quantisation.

In every case the tell is the same and it is a *documentary* tell rather than a
numerical one: **the phrase "the instrument was the limit" appearing twice, in
two write-ups, about two different instruments.** That sentence is correct each
time it is written, which is exactly why nobody re-reads it — and it is the
signal. Search your own records for it before you buy another instrument.

## L-134. Put the gate before the test, and let it stop you

**The rule.** When the experiment you can afford differs from the one that
produced the finding — coarser, shorter, cheaper — **build a control that varies
only the thing you had to compromise on, run it FIRST, and pre-register that a
failure stops the main test.** Otherwise a null result is unreadable: it means
either "the effect is absent" or "my compromise hid it", and those are opposite
conclusions that cost the same to produce.

**Why.** A 2D slice showed a coherent limit cycle at a 12.5 mm cell. The question
was whether it survives in 3D. The affordable 3D mesh was **100 mm — eight times
coarser**, so a 3D run showing no oscillation would have been ambiguous between
*three-dimensionality damped it* and *the coarse mesh damped it*.

The gate was the same 2D slice at the 3D test's own 100 mm cell, asking whether
the cycle survives **coarsening alone**. It did not: amplitude ratio **0.482**
against a pre-registered 0.5 threshold. **The main test was never run**, and that
was the correct outcome rather than a wasted design.

**What the gate then bought, which is the part worth copying.** Having failed, it
turned a shrug into a measurement. A resolution ladder — the same case at 100,
50, 25 and 12.5 mm — located the phenomenon precisely: ratios 0.482, 0.318, 0.377
and **0.982**. The cycle exists at 12.5 mm and at no coarser mesh tested. That
converted "we cannot tell" into two hard statements: **the specified production
mesh is on the wrong side of the threshold and would return a confidently wrong
steady answer**, and **the un-confounded experiment costs ~50× the plan it would
be checking**.

**And the gate audited the finding that motivated it.** The same ladder showed
that the original result rests on a **single** mesh, with no rung finer than the
one it was found on — so the finding is not established as mesh-converged, and
the write-up now says so against itself. **A control built to protect the new
experiment ended up qualifying the old one.** Expect that, and do not suppress it
when it happens.

**How to apply.** Three questions before spending on a scaled-down experiment:
*what did I compromise to afford this?*; *what single-variable control isolates
that compromise?*; *what will I do if the control fails?* Answer the third in
writing, before running, and honour it.

## L-135. One source root can become two destination roots, and a re-pointed ignore rule keeps its wording while changing its scope

**The incident.** Batch 2 scoped its solver-output rules to two roots on
purpose and wrote the reason into `.gitignore`: a repo-wide `**/log.*` would
also reach `docs/campaigns/F14-cooling-ladder/`, and *"it WOULD silently ignore
every solver log the lane writing that tree produces next."* Five of those rules
read `demo-output/website/campaign/**/...`. MOVE_MAP batch 7 splits that one
source root into **two** destinations: R20 sends `campaign/<tree>_runs` to
`verification/runs/` and R21 sends everything else to `verification/campaign/`.

**A prefix substitution therefore has no correct answer, and both wrong answers
are silent.** Re-point to `verification/runs/**` and the R21 half stops being
ignored; re-point to `verification/campaign/**` and the R20 half does. Re-point
to both with `**` and the R20 spelling reaches, once R25 lands, exactly the F14
trees batch 2 refused to reach — silently, to another lane's next solver log.

**Measured rather than reasoned, before the rule was written.**
`git check-ignore --no-index -v` over all **19,679 files on disk** under the 294
sources: **8 ignored files sit under R21 territory** — one
`motorBike_production.log.checkMesh` under `DRAW_SCATTER_RETROFIT/` and seven
`*.log` under `MESH_CERT_RULINGS_2026-08-10/recheck_logs/`. Eight files is small
and it is not the point: the point is that the count is not zero and nothing but
the measurement said so. The rule that landed is
`verification/runs/*_runs/**/...`, `verification/runs/*_work/**/...` and
`verification/campaign/**/...` — three rules where there was one, the `*_runs`
spelling chosen because R25's successors put a CAMPAIGN name in that segment and
so match it not at all.

**The rule.** When a move splits a root, a re-pointed ignore rule must be
re-derived from what it **matches**, not from what it **says**. And the
assertion is not a rule count and not the tracked side alone: it is the
**per-file ignore decision on both sides, mapped forward, compared as a set
difference in BOTH directions.** Here that read *0 files un-ignored, 78 newly
ignored, and all 78 are the `MESH_AUDIT_runs` option-A closure this batch was
supposed to land* — which is a sentence about the corpus, where "the rule count
went from 5 to 12" would have been a sentence about the diff.

**The corollary.** `git check-ignore` is silent about tracked files, so
`--no-index` is mandatory here (`USING_THIS_LAB.md` §8.6) — and the interesting
half of this measurement is the **untracked** side, 17,312 files of solver
output that no `git status` would ever have shown leaving the ignore set.

## L-136. A rename re-dates a record for every instrument that reads history by path, and a move batch is a rename

**The incident.** `scripts/check_verdict_cells.py` went **PASS → FAIL** as a
pure side effect of MOVE_MAP batch 7, with two `CELL-VS-RECORD` findings that
were artefacts of the move and not of the ledger. Its `_landed(p)` asks
`git log --diff-filter=A --format=%ct -- <path>` for the commit that ADDED a
grade record. R21 moved all 264 campaign records to `verification/campaign/`,
and:

* **in the window between the `git mv` and the commit**, the new path has no
  history at all, so `_landed` fell through to its last-touch fallback, got
  nothing there either, and returned **0** — after which every record read as
  newer than every other and the "newest cited record" comparison picked a
  different record for two rungs;
* **after the commit**, `git log -- <new path>` finds the move commit and
  reports **today** as the landing date of a record dated 2026-08-11, because
  without `--follow` a rename IS an add at the new path.

**This is D356 arriving through a different door.** `_landed` exists precisely
because `git log -1` reported the last EDIT rather than the landing, and a
non-author's amendment re-dated two grade records and convicted three rungs
that had not moved. Its docstring's rule is *"repairing a record must not
re-date it, or the instrument punishes the repair it asked for."* **A MOVE must
not re-date it either**, and the instrument could not tell the two apart.

**It was not one instrument.** `scripts/self_audit.py:3603`
`_ranking_board_date()` — whose own docstring says *"the one thing a referent
that exists to be current must not do is misreport its own age"* — returned
`''` for `BOARD_MOVED_2026-08-11.md` at its new spelling and printed
*"(date unreadable)"* into the published-board provenance string.

**The repair is the one `exec_bits._spellings` already uses: teach the MATCH the
map, never re-write the history.** Both now ask every spelling the repository
has had or will have for the path — literal, `lab_paths.unredirect()` of it,
`lab_paths.redirect()` of it — and take the **earliest** answer, which is the
same rule `_landed` already stated for a path added more than once. After the
repair `check_verdict_cells` reads **exit 0, 16 rung rows, 0 FAIL, 3 WARN**, its
own landing control reports **HELD** rather than SKIP with
`_landed=1786822451` against `last=1786995260`, and the ranking date reads
2026-08-11 again.

**The rule, and the reason it generalises past `.gitignore` and past path
literals.** Anything that asks git a question **about a path** — `git log`,
`git log --diff-filter=A`, `git blame`, `--since`, a pickaxe scoped by
pathspec — is answering about a NAME, and a move changes the name without
changing the thing. Before a move batch, grep for `git log` and `git blame` with
a `--` pathspec the same way you grep for path literals, and check each one
**twice**: once in the pre-commit window where the new name has no history, and
once after, where it has the wrong history. The first failure is loud; the
second is a date that is merely wrong.

## L-137. A path assembled from segments is invisible to BOTH scans a move batch runs, so a third scan shape is needed: the tokens

Batch 6 found a repository root derived as `parents[3]` — a depth assumption
about a moving path with **no path literal in it** — and L-127 recorded that an
exhaustive literal scan cannot match it. Batch 7 generalised the search to the
*idiom* (`parents[N]`, `parent.parent`, `../..`, `dirname(dirname`) and found
nineteen modules where the brief predicted seven.

R25 ran both scans over all 1,671 tracked files under its sources and both came
back clean. The literal scan found 243 files naming `docs/campaigns`, every one
of them prose or a citation to a document that STAYS. The idiom scan found 20
files, of which 7 derive a repository root, and **all 7 were proved correct at
the new path by executing the expression there** — because R25 is the first
move in this map that is DEPTH-PRESERVING: `docs/campaigns/` and
`verification/runs/` are both two segments, so `parents[4]` lands on the same
directory on both sides for all 1,671 paths, asserted as
`p.count("/") == redirect(p).count("/")` with 0 exceptions.

Two clean scans, and the one real breakage was in neither of them:

```python
SEALED_CASES = sorted(
    d for d in glob.glob(os.path.join(REPO, "docs", "campaigns",
                                      "F14-cooling-ladder", "K0c_runs", "*"))
    if os.path.isfile(os.path.join(d, "constant", "polyMesh", "boundary")))
```

**The substring `docs/campaigns` does not occur in that file.** The path is
assembled from segments, so the literal scan cannot see it; it counts no
parents, so the idiom scan cannot see it either. It guards the sealed half of
the advective-term mutation harness — eleven meshed K0c cases — and the file's
own comment says an empty corpus makes `all(...)` return True for every
mutation, which is why `SEALED_EXPECTED = 11` exists. R25 would have driven
that glob to zero.

**The third scan shape is the TOKEN**: search for the path's segments as quoted
tokens (`"campaigns"`, `"K0c_runs"`, `"F14-cooling-ladder"`) rather than for the
joined path or for a depth idiom. Run repo-wide it returned exactly two files —
this one, and a test whose fixture tree is synthetic and keeps its literals.

And the repair is the same one all three classes get: **ask for the thing by
name, not by spelling.** `lab_paths.run_archive("K0c_runs", "F14-cooling-ladder")`
probes every spelling the map knows, prefers the successor, and REFUSES rather
than returning an empty corpus — so the line is correct on both sides of this
move and of the next one, and no fourth scan will be needed to find it again.

## L-138. The three scans all ask which files NAME the old path; a bound root re-points the files that name no path at all

L-127, L-135 and L-137 built a three-shape scan for a move batch: the literal
path, the depth idiom, the quoted token. All three ask one question — *which
files name the old location?* Batch 8 is where that question stopped being
sufficient, and the reason is `lab_paths` working exactly as designed.

Batch 3 introduced `scripts/lab_paths.py` so that batches 4-8 would edit **one
module instead of thirteen files**. The unstated consequence is the mirror of
the benefit: **every consumer of a bound root is re-pointed by a commit that
does not name it, does not diff it, and cannot be found by searching for the
path it used to compute.** Batch 8 moved five files; `lab_paths.WEB` flipped
from the webroot to `web/`; **six call sites changed value and the diff touches
none of them.** All three scan shapes came back clean on every one, correctly,
because not one of them contains a path.

Evaluated on both sides rather than read:

| site | what it computes after the flip | |
|---|---|---|
| `scripts/build_laptop_bundle.py:526` | `web/closure.html`, `web/benchmarks.html`, `web/wall/wall.html` | **becomes correct** |
| `scripts/self_audit.py:129` | the webroot, which is now `web/` | **becomes correct** |
| `sdk/scripts/capture_video.py:53` | `web/`, the honest binding the map ruled for it | **becomes correct** |
| `sdk/workflows/nasa_hump.py:60` | `web/dafoam/f6a_nasa_hump/case_template` | dangling before, dangling after — R22 took `dafoam` in batch 6 |
| `sdk/workflows/rae2822_case9.py:98` | `web/campaign/F12_runs/reference` | dangling before, dangling after — R20 took it in batch 7 |
| `sdk/scripts/closure_in_sample_gate.py:112` | **a SWEEP ROOT** | the one that matters |

The last one is the lesson:

```python
_WEBROOT_REL = str(lab_paths.WEB.relative_to(lab_paths.REPO))
_SCAN_JSON_ROOTS = (_WEBROOT_REL, "models")
_SCAN_MD_ROOTS = (_WEBROOT_REL, "docs")
```

Three lines that name no path, that every scan is right to pass over, and that
decide how much of the tree a gate reads.

**Measured rather than feared: the shrink is one file.** The webroot held
**0 `.json` and 1 `.md`** when batch 8 ran, because batches 5, 6 and 7 had
already taken everything else out of it, so the corpus lost exactly
`demo-output/website/motorbike-video/shotlist.md` — withdrawn spelling, do not
cite it — on a gate that neither `lab_check` nor the suite invokes. No verdict
moved. It was **reported and not adjusted**, because a mover who repairs an
instrument in the same commit as the move that would have moved it has
destroyed the only evidence that it moved.

**The size is luck and the shape is the lesson.** Run batch 8 before batch 5 and
those same three lines take that gate from the whole webroot to five HTML files,
every finding it used to make goes quiet, and all three scans still come back
clean.

**The fourth question is not "who names the old path" but "who reads a name
whose VALUE this commit changes".** It is answered by grepping for the module's
own exported names — `lab_paths.WEB`, `lab_paths.CAMPAIGN`, `lab_paths.RUNS` —
rather than for any path, and then by EVALUATING each site on both sides of the
move instead of reading it. A binding that resolves is the whole point of the
module. A binding that resolves to a **smaller corpus** is this repository's
most repeated failure wearing the module's face, and it arrives with a clean
scan report attached.

---

## L-139. Coupling was measured before the small move I made by hand and skipped before the large move I delegated, 79 seconds apart

`2a65fdd4` (2026-08-18 17:15:42) moved **eight** loose plots into `media/plots/`
and, in the same commit message, refused to move four more:

> *"Four filings violate the rules and were left alone, because `docs/LESSONS.md`
> records that a webroot move broke 178 code files: `media/LAPTOP_SHOOT.md` (34
> references), `FILMING_COMMANDS.md` (15), `valve.png` (3), `Gui_issue.png` (2).
> They need a coordinated re-point, not a move. **The difference between these and
> the eight that did move was MEASURED, not assumed.**"*

`5c0d2483` (2026-08-18 17:14:23) — **79 seconds earlier**, same session, same
author — refiled **87** paper paths into topic subdirectories and renamed almost
all of them. It changed **0 files outside `docs/papers/`**, re-derived with
`git show --name-only --format='' 5c0d2483 | grep -v '^docs/papers/'`. No reference
count was taken for any of the 87. **26 distinct dead paths were left standing
across 40 tracked files**, and the K2c lane's extraction command died with
`FileNotFoundError` on one of them the same day
(`K2c_DIGITIZATION_ADDENDUM.md` §11.6).

**The discipline was not absent; it was selective.** Eight files were moved by hand
and their inbound references counted one by one. Eighty-seven were handed to an
agent and none was counted. The move that got the check was the one small enough
that the check was cheap, and the move that skipped it was the one large enough to
do real damage — the exact inversion of where the effort belonged.

**The check that WAS run on the big move measured the other direction, and reads
like coverage.** `5c0d2483`'s message is emphatic: *"CONSERVATION WAS VERIFIED AT
THE BLOB LEVEL, NOT FROM THE MOVING AGENT'S REPORT ... every PDF blob reachable
from the parent commit is reachable from this tree, 0 lost, 7 added."* That
establishes that the **objects** survived. It establishes nothing about the
**references into them**, and a reader of that paragraph would come away believing
the move had been checked. **Conservation of the moved thing and survival of the
pointers at it are two different measurements. Only one was taken, and the one that
was taken is the one that reassures.**

**A delegated move needs the coupling count in the BRIEF, not in the review.**
Neither the agent's report nor a review of that report could have surfaced this.
The report described the renames and the renames were correct; what was missing was
never in the report's scope. The instruction that closes it is one line — *before
you move a file, count what names it, and hand the count back with the move* — and
it has to be given **before** the move, because afterwards the old paths are gone
from the tree and only `git ls-tree` on the parent commit can reconstruct what they
were.

**Third instance of this class in this file, and the new part is the selectivity.**
The webroot move that broke 178 code files is the same shape one campaign earlier;
L-137 is the assembled-path variant, where the path is built from segments and no
literal scan can match it. Neither of those was about *choosing* not to look. This
one was, and the choice tracked how visible the move felt rather than how much of
the tree it touched.

**A fourth thing this repair had to get right, and it is the reason a
find-and-replace would have been worse than the breakage.** Of the 74 broken
occurrences, **57 were not pointers at all** — they were sentences recording where
a file had been fetched to on a stated date, with a SHA-256 or an md5 beside it, or
a command and the output it returned, or a pre-registration written before a run
under *"nothing below is edited after the fact."* Rewriting those paths would have
left every one of them resolving and every one of them **false**. They were left
byte-identical and given a dated forwarding note appended below, per
`docs/MEMORY_ARCHITECTURE.md` §8.1. **A repair that makes a record resolve by making
it lie is not a repair**, and the blanket refusal that avoids it strands 40 files —
so the classification has to be made per citation, not per file.

**Repaired 2026-08-18 by the commit carrying this lesson.** The pairing was
re-derived by **blob identity** rather than by name similarity, which matters: no
name-based map would have produced `docs/papers/Paper1.pdf` ->
`docs/papers/verification_validation/eca_hoekstra_2014_numerical_uncertainty.pdf`.
17 live pointers were repointed in place, 57 historical statements were left
verbatim and forwarded, and `scripts/check_paper_citations.py` re-derives the
pairing from git on every run and fails on a citation that neither resolves nor
carries a route in its own file.

---

## L-140. `writeInterval == endTime` is not a monitoring choice, it is a decision that any interruption costs the whole run

**2026-08-19. K0cG's two square-cavity cases reached 85 % and 60 % of their
registered `endTime` and produced nothing at all.** The host went down under them
at 03:53Z and stayed down about eleven hours. When it returned, each case held
exactly one time directory: `0`.

The builder had generated

```
writeControl    timeStep;
writeInterval   40000;
purgeWrite      0;
```

with `endTime 40000`. **One scheduled field write, at the last iteration.**

**The recorded form of this hazard was too narrow and that is the lesson.** This
campaign already carried a note that a non-`writeInterval` `endTime` writes no
intermediate fields, filed as a reason **settle watchers go blind** — a
monitoring inconvenience. **The same line is also a durability property, and in
that role it is far more expensive: it converts every interruption into a total
loss rather than a proportional one.** 34 165 iterations of `kOmegaSST` on a
94 249-cell mesh were unrecoverable not because the solver failed but because
nothing had been asked to persist. The cost is not the 15 % that remained. It is
the 85 % that had already been paid for.

**The asymmetry is what makes the default wrong.** Writing 20 checkpoints instead
of 1 costs a bounded, measurable amount — here about 34 MB per write, capped to
two retained sets by `purgeWrite 2`, on a filesystem with 345 GB free — and it is
pure input/output: it cannot enter the discretisation, the schemes, the
relaxation or the stopping criterion, and it cannot move a solution value.
**Against that bounded cost sits an unbounded one.** There is no run length at
which the trade reverses, and the longer the run the worse the default performs.

**A second-order point about who is exposed.** The exposure is worst for exactly
the runs a lab most wants: long, unattended, overnight. A host's idle detector
does not necessarily recognise a running solver as activity — recorded here on
2026-07-30 and demonstrated again by this loss — so the runs least likely to be
watched are the runs most likely to be interrupted, **and a single-write
`controlDict` gives them zero tolerance for it.**

**What was done, and the shape of the disclosure.** Two lines per case were
changed, `writeInterval` to 2000 and `purgeWrite` to 2, and **the claim that
nothing else changed was verified rather than asserted**: the frozen builder was
re-run into a scratch tree and diffed recursively against the staged cases, and
the complete difference set was those two lines, the `blockMesh`-generated
`constant/polyMesh`, and one self-describing annotation line per `CASE.txt` that
predated the change. `endTime` stayed at the registered 40 000 and
`runTimeModifiable` stayed `false`. **An input/output departure from a frozen
builder is still a departure and is still disclosed** — the argument that it
cannot move a number is a reason to make the change, never a reason to make it
quietly.

**What this does not license.** Checkpointing does not make a truncated run
reportable. K0cG attempt 1 remains **NOT A RESULT**: no case reached `endTime`,
no completion marker was written, and the surviving per-iteration
`postProcessing` series are a convergence monitor — the area-normal integral of
the *molecular* temperature gradient — **not the graded Nusselt row**, which
needs the `alphaEff` factor read from a written `alphat` field. A checkpoint
would have preserved a measurable state; it would not have preserved a
*converged* one, and the two are graded differently.

---

## L-141. In an axisymmetric wedge case `residualControl` can never be satisfied, so the solver's own convergence criterion is inoperative and something else has to do the job

**2026-08-19. Across two rungs and every case in both — six in T1c, the T1b cases
as they land — `residualControl` has never once fired.** Not one log contains
`SIMPLE solution converged`. Every case runs to `endTime`.

**They were not unconverged.** `R_300k_c` finishes with a relative field change of
**7.3e-11** between its last two checkpoints. `L_q_f` and `L_Ts_f` finish
**byte-identical** between theirs.

**The cause is one velocity component that does not exist.** In an axisymmetric
wedge the out-of-plane component is **identically zero by symmetry**, and it is:

| case | `max|Ux|` | `max|Uz|` | ratio |
| --- | ---: | ---: | ---: |
| `R_300k_c` | 2.32e+01 | 4.14e-16 | **1.8e-17** |
| `L_q_f` | 1.50e-01 | 1.68e-17 | **1.1e-16** |
| `L_Ts_f` | 1.50e-01 | 1.68e-17 | **1.1e-16** |

**Its reported residual, meanwhile, sits at 1e-2 to 1e-1 and never falls** —
`Uz` initial residual 0.090 in `R_300k_c` while every other field is at 1e-6 to
1e-9. **The residual is normalised by a reference built from the field itself, so
for a field that is identically zero the ratio is O(1) noise carrying no
information at all.**

**`residualControl` takes the maximum over a vector's components, so listing `U`
makes the criterion permanently unsatisfiable.** Not slow to satisfy —
**unsatisfiable**, at any `endTime`, on any mesh, for any physics.

### Why this is a lesson and not a curiosity

**It silently converts a convergence criterion into a no-op.** A builder that
sets `residualControl { U 1e-8; ... }` and an operator who reads "ran to
`endTime`" as "did not converge" will both be wrong, in opposite directions and
for the same reason. **I made the second error today**: the T1c fine
constant-flux case genuinely had *not* converged, and it sat in a set of six that
had all "failed" to trip `residualControl` — the true signal was invisible
because the false one was universal. **A criterion that never fires cannot
distinguish the case that should have failed it.**

### What actually does the job

**Comparing the written fields between the last two checkpoints.** That is the
only convergence test that worked here, it caught the one genuinely unconverged
case out of six, and it is now a gate in both comparators.

**And it is only possible because `writeInterval < endTime`** — the durability
change from **L-140**, made after a crash destroyed an 85 %-complete run. **Two
independent needs, a crash and a convergence test, are met by the same dictionary
line, and neither was the reason it was originally written.**

### The practical rule

- **Do not rely on `residualControl` in a wedge case.** Set a generous `endTime`
  and gate on field comparison.
- **A zero needs a live planted control.** Every convergence zero reported here
  was checked by planting a known perturbation — 1.234e-03 K — and confirming the
  parser recovers it exactly. A zero from a broken reader looks identical to a
  zero from a converged solution.

## L-142. blockMesh grades from the block's low face, so on an axis-to-wall block a `simpleGrading` above one puts the finest cell on the centreline — and the error hides at low Reynolds number

T1b attempt 1 built 19 turbulent pipe cases with
`simpleGrading (1 expansion 1)`, `expansion > 1`, on a wedge block whose radial
direction runs from the axis at y = 0 to the wall at y = R. blockMesh reads that
entry as the ratio of the **last** cell to the **first** along the direction, so
the cells grew from axis to wall. The builder computed the correct wall-cell
height and then placed it on the centreline. At Re = 3e5 the finest level had a
1.96e-05 m cell at the axis and a **4.11e-03 m cell against the wall, 210 times
too thick**, and a "resolved" arm designed for y+ = 0.625 achieved y+ = 52.3.

Nothing in the build chain objected. The dictionary is legal; blockMesh emitted
no warning; checkMesh returned rc = 0 on all 19; and the builder's summary table
and every CASE.txt printed the *intended* wall cell, because they read it from
the same variable the dictionary got it from. **A build chain cannot check
itself — every link was quoting one number back to the others.** The mesh had to
be read from the written points.

Three things follow, and the third is the expensive one.

**Reversing a geometric series does not change its sum.** Emitting
`1/expansion` puts the fine cell at the wall and still fills R exactly, so the
fix is one reciprocal. Verified against the written points: wall cell
1.959909e-05 m against a designed 1.961777e-05 m, the 0.095 % being the wedge
cos(θ/2) factor. `check_t1b_mesh.py` now asserts, before any solver runs, that
the wall cell matches the design AND is the smallest radial cell in the mesh.

**Cell count is blind to it.** The attempt-1 and attempt-2 meshes have
*identical* cell counts — 81 920 at the finest level. They differ only in
grading. Any guard built on mesh size sees nothing.

**The error scales with the grading ratio, so it hides at low Re.** A higher
Reynolds number demands a thinner wall cell against the same radius, so the
ratio, and the damage, grow with it:

| Re | axis/wall ratio | Nu error, finest level |
|---|---:|---:|
| 10 000  |   3.4 |  −2.7 % |
| 30 000  |  14.6 |  +2.5 % |
| 100 000 |  61.5 | −53.1 % |
| 300 000 | 211.4 | −81.8 % |

Against the registered band — the Dittus-Boelter/Gnielinski disagreement, ±2.84 %
at 1e4 and ±3.89 % at 3e4 — **the two lowest Reynolds numbers PASS**, with
friction rows of −6.0 % and −1.1 % sitting next to them looking healthy. A
campaign validated at one Reynolds number would have shipped a passing gate and
a published Nusselt number good to 3 % on a mesh wrong by a factor of three.
**The sweep is what caught this. A single-point validation could not have.**

What did catch it, once the sweep existed, was the comparator's registered
attribution lever: it grades Nusselt and *reports* friction, on the stated
reasoning that a friction error is a solver or mesh fault while a Nusselt error
with correct friction is the thermal closure. Nu and f failed together and by
nearly the same amount at every point (−34.0/−40.6, −77.4/−80.3, −91.9/−92.9,
−81.8/−84.1). A wrong turbulent Prandtl number moves Nu and leaves f alone; it
cannot do that. The lever pointed at momentum, which means the wall.

## L-143. Moving a case directory does not redirect its running solver, and the stray write it leaves behind is invisible to every check except file age

T1b attempt 1 was archived to `attempt1/` while two solvers were still running.
The processes followed the moved inode for their working directory, as Linux
guarantees — but **OpenFOAM writes fields to the absolute case path it resolved
at startup**. When the archived `R_10k_f` reached its endTime it therefore wrote
a complete `20000/` into the *freshly rebuilt* attempt-2 case at the old path.

That stray directory had the right time, the right field list, the right length,
and 81 920 values, because both attempts meshed the same cell count. It was a
solution from a refuted mesh sitting inside the case built to replace it, and it
would have satisfied every completion test in use: rc = 0, an `End` line, a
final time directory equal to endTime, every field present.

Only its age gives it away. Two guards, both cheap:

- the runner refuses any case that already carries a numeric time directory
  other than `0`, before it meshes or solves;
- the completion marker refuses a case whose final-time fields are **older than
  that case's own `0/T`**, which the runner writes at the start of the run that
  is allowed to produce the answer.

Related: the first version of the first guard used the glob `[0-9]*`, which
matches `0.orig`, and refused all 18 cases in 45 seconds. That is the correct
way for a guard to fail — loudly, immediately, and before spending anything.
Test a guard against a planted positive as well as a clean case; this one was
run against a contaminated directory and confirmed to fire only there.

## L-144. A retrieved paper is verified by its printed title page, never by its file type or its hash — a manifest can be internally consistent and externally false

The closure-modelling paper corpus (`docs/papers/closure/`, 42 PDFs) was
built by a retrieval agent that *guessed* arXiv identifiers from author and
year, downloaded whatever each identifier resolved to, checked that the bytes
were a PDF, and recorded a sha256 beside the intended citation. Every guessed
identifier resolves to a real paper — just not the intended one. Thirty of the
42 files were unrelated papers. `Beck2019_deep_neural_les.pdf` (sha256
`babf0415...`) was Kurth et al., *Exascale Deep Learning for Climate
Analytics*; the 77-page "Gatski & Speziale 1993" was a 1996 handbook chapter;
a paper uploaded by hand as "Parish & Duraisamy 2016" was a Schrodinger-Poisson
solver paper from the same journal volume. The manifest certified all of them:
right filename, right size, right hash, wrong document.

**Nothing downstream of a wrong PDF can be right, and nothing downstream can
detect it.** A catalogue entry, an equation number, a "headline result with
numbers" extracted from the wrong paper is not an error in the extraction; it
is fiction with a citation. The defect was caught only because a sub-agent
extracted page 1 of every file and read the printed title against the manifest
claim before citing anything — which is the one check the retriever never did.

Guards, all cheap, all now standing for the closure team:

- A manifest row is `RETRIEVED-VERIFIED` only when the **printed title on
  page 1** has been extracted and matched to the intended citation; the
  verified title is recorded beside the hash. File type, size, hash and a
  successful HTTP 200 prove that *a* file arrived, not *which* file.
- The check runs again at every phase boundary, because files keep arriving,
  and anything cited from a file not yet on disk is tagged
  `SECOND-HAND-UNVERIFIED` (from memory) or `BLOCKED-ON-SOURCE` (not written).
- Hand uploads are not exempt: the "Parish 2016" upload was wrong too.
- The retrieval agent's supervisor verifies a *sample of title pages*, not the
  manifest's tidiness. A tidy manifest is what this failure mode looks like.

The cost of the defect: two full sub-agent reading passes, part of a paper
catalogue and part of a foundational-models inventory written against wrong
sources and now being re-audited line by line. The cost of the guard: one
`pdftotext -l 1` per file.


## L-145. A byte-identical duplicate is not a retrieval error, and that is exactly why it survives every check a retrieval failure would trip

**2026-08-20. Two pairs of files in `docs/papers/closure/` are byte-identical**, found by `sha256sum`
over whole files and by nothing else:

| Pair | sha256 |
|---|---|
| `Schmelzer2020_algebraic_reynolds.pdf` = `Schmelzer2020_sparta_sparse_symbolic_regression.pdf` | `7aca1f9a...` |
| `Xiao2016_model_uncertainties.pdf` = `Xiao2016_bayesian_model_form_uncertainty.pdf` | `1577eabd...` |

**Both members of both pairs are the correct paper.** Every guard standing after L-144 passes on
them: the bytes are a PDF, the page count is right, the hash is stable, and — the guard L-144
installed — **the printed title page matches the intended citation.** Title-page verification is a
test of *identity*, and both files have the right identity. It has nothing to say about *multiplicity*.

**The damage is to counting, and counting is what a manifest is for.** A naive file count reports
**35 papers where there are 33 works**. Worse, a manifest with two rows for one document will
eventually be read by an agent as **two independent sources agreeing on a number**, which is the
precise failure a corpus audit exists to prevent. The second Xiao file arrived *during* this
cataloguing pass, four hours after the manifest was rebuilt — so the defect is not historical, it is
what an active retrieval queue produces when two agents are given the same shelf and different
naming conventions.

**The guard is one line and it belongs in the manifest builder**: group the verified files by sha256
and refuse to emit two rows for one hash; emit one row and an `alias` field. `sha256sum
docs/papers/closure/*.pdf | sort | uniq -w64 -d` finds every case in under a second.

**What this does not license.** It does not license deleting a file to make a count tidy. Both
duplicates are correct documents and either name may be the one a future citation reaches for; the
recommendation recorded in the catalogue is to keep the name already carried by the `MANIFEST.md`
row and record the other as an alias. **A count that is wrong because two names point at one truth is
a bookkeeping fault. A count made right by deleting evidence is a different and worse one.**

---

## L-146. A closure can be right to 0.3% and produce a flow wrong by 35%, so an a-priori error is not a bound on anything

**Wu, Xiao, Sun & Wang, arXiv:1803.05581v3, Table 1, arXiv preprint p. 4.** DNS Reynolds stresses —
the ideal data-driven closure, with zero modelling error — substituted into the RANS momentum
equations and propagated:

| `Re_tau` | 180 | 550 | 1000 | 2000 | **5200** |
|---|---|---|---|---|---|
| Error in turbulent shear stress (volume-averaged) | 0.17% | 0.21% | 0.03% | 0.15% | **0.31%** |
| Error in mean velocity (volume-averaged) | 0.25% | 1.61% | 0.17% | 2.85% | **21.6%** |
| Error in mean velocity (maximum) | 0.36% | 2.70% | 0.25% | 5.48% | **35.1%** |

**The stress errors do not grow with Reynolds number. The velocity errors do, monotonically.** The
authors flag the first point themselves — the stress column's non-monotonicity "**should not be
overly or literally interpreted**" — and are unambiguous about the second: the velocity errors
"clearly increase monotonically with the Reynolds number."

**This is not a modelling result, it is a conditioning result**, and it says the map from stress to
velocity amplifies. Their local condition number rises from `O(1)` at `Re_tau = 180` to `O(10^2)` at
`Re_tau = 5200` under explicit coupling (arXiv preprint p. 14).

**Why it is a lesson and not a curiosity.** Almost every data-driven closure result in the corpus is
reported as an improvement in a *stress* metric: Ling's `b` RMSE 0.23 -> 0.13, Kaandorp's 0.0995 ->
0.0521, Beck's cross-correlation 0.25 -> 0.48. **None of those numbers bounds the improvement in the
solved flow, and this table is the proof.** Kaandorp measured the same thing from the other side
(arXiv preprint pp. 39-40): propagating `b_ij,DNS` already misses, and "**Subsequently approximating
`b_ij,DNS` by `b_ij,TBRF` causes additional errors, but these errors are of similar magnitude to the
errors already made in the propagation.**" **Halving their ML error would have bought almost
nothing.**

**The practical rule for this lab**: OpenFOAM is installed, so an a-priori score is never the end of
an experiment. Any closure result reported here states whether it was re-solved, and if it was not,
it is a-priori and is labelled a-priori.

**What this does not license.** It does not license ignoring a-priori scores. An a-priori score is
cheap, it is a necessary condition, and Guan 2022 shows it can even be *predictive* within a single
setup (L-152). It is simply not sufficient, and the size of the gap is not knowable in advance.

---

## L-147. Where a correction enters the equations predicts its stability better than what the correction is

**Four papers, four regressors, one pattern.** The same learned quantity — a Reynolds-stress
correction — is stable or unstable according to whether it enters as an **explicit source term** or
through the **coefficient matrix**.

| Method | Coupling | Stabiliser it needed |
|---|---|---|
| Singh 2017 FIML | multiplier `beta(x)` on the SA **production term** | **none**; convergence "comparable to the baseline" (arXiv preprint p. 22) |
| Wu 2018 PIML | **implicit** `nu_t^L` split, `S` treated implicitly | **none** |
| Schmelzer 2020 SpaRTA | additive to k-omega SST, linear term stays implicit | coefficients **x 0.1** on convergence failure |
| Kaandorp 2020 TBRF | **explicit** `b_ML` into momentum | **`gamma_max = 0.8`** ceiling + Gaussian smoothing |
| Ling 2016 TBNN | **explicit** `b` into momentum + `k`-production | none discussed; no conditioning analysis |

Wu et al. state the mechanism (arXiv:1803.05581, arXiv preprint p. 16): under explicit treatment the
local condition number reaches `O(10^2)` at `Re_tau = 5200`; under implicit treatment "**the
volume-averaged local condition number stays at `O(1)`**". And the two runs use **nearly the same
stress field** — "the difference between `u^imp` and `u^DNS` is about **0.1%**" (Appendix D, p. 31).

**The sharpest form of it is their Appendix C (p. 30)**: the classic segregated lagged-stress
coupling, **initialised with the exact DNS mean velocity**, "**leads to divergence of the simulation.
Therefore, the solved mean velocity is not presented in this work since a converged solution was not
achieved.**" *A closure that is exactly right, started from the exact answer, diverges because of how
it is coupled.*

**Singh 2017's placement is the cheapest insight here and it was arrived at for a different reason.**
They chose a multiplier over an additive source because "**Inferring `beta` ... leads to a better
conditioned inverse problem, as `beta` is non-dimensional and has a simple initial value of unity**"
(arXiv preprint p. 7). They optimised the conditioning of the *inverse* problem and got the
conditioning of the *forward* problem for free — because a multiplier on a production term cannot
touch the stress-strain relation.

**The design rule that follows**: before choosing a regressor, choose where the output lands. A
correction that multiplies an existing, already-stable term is a different numerical object from one
that adds a source to the momentum equation, and the difference is two orders of magnitude in
condition number.

**What this does not license.** Implicit treatment is not a guarantee. Wu et al. say so (p. 23):
"**monolithic coupling is by no means a panacea** ... The conditioning and stability ultimately
depend on the characteristics of the turbulence model itself." And it is not always available: for
"**non-differentiable models, e.g., those based on random forests ..., a monolithic coupling is not
straightforwardly viable**" (p. 24) — which is the situation of half the corpus.

---

## L-148. The best short-horizon model in a table can be the worst long-horizon one in the same table

**List, Chen & Thuerey 2022, Table 1, arXiv preprint p. 9.** Isotropic decaying turbulence, one
solver, one test set, MSE at two times:

| Model | MSE @ `t_1 = 64 dt` | MSE @ `t_2 = 512 dt` |
|---|---|---|
| NoModel | 2.78e-3 | 0.057 |
| Smagorinsky LES | 2.69e-3 | 0.051 |
| **supervised, 1-step** | **1.52e-3 (best in the table)** | **0.369 — diverged, 6.5x worse than no model** |
| 10-step solver-in-the-loop | 4.23e-4 | **0.018** |

**The supervised model wins at `t_1` and is 20x worse than the solver-trained one at `t_2`, having
diverged.** The authors: "the temporal advancement of the forward simulations greatly surpasses the
unrolled training horizon, which leads to instabilities with the **supervised and 1-step model**, and
ultimately to the **divergence of their simulations**".

**Two more instances of the same inversion, from different groups and different physics.**
Um et al. 2020 could not train a stable supervised model at all in 3-D: "we were **not able to train
a stable NON version despite numerous tests**. While the models performed well for ca. **100 to 150
time steps**, small scale oscillations induced by the corrections accumulate and start to strongly
distort the flow" (arXiv preprint p. 33) — and their Fig. 26a records that it "**even slightly
surpass[es] SOL_16 around frame 100**" before collapsing to worse than no model. Beck & Kurz 2021
report a GRU closure at "**99.9% cross correlation in a priori tests**" whose "**LES solution
diverges strongly soon after**" (arXiv preprint p. 26).

**Why this is a lesson about evaluation design and not about neural networks.** A test that stops
before the failure time reports the inversion as a success. List's `t_1` is 64 steps and `t_2` is
512; Um's failure appears at frame 100 of 500. **A short evaluation horizon does not just
under-report the error — it reverses the ranking.**

**The rule**: a rollout metric is quoted with its horizon, and the horizon is stated as a multiple of
the training horizon. List's forward runs "greatly surpass the unrolled training horizon" by design;
Um's are 500 steps against training look-aheads of 2-32; Bae 2022's channel tests run **300
`delta/u_tau`** against a training window of **`2 delta/u_tau`** — 150x — and that ratio is why "no
instability" means something there.

**What this does not license.** It does not mean supervised training is useless. Guan 2022's offline
CNN is stable for 150 `tau` with no post-processing at all (L-152). It means a supervised model's
short-horizon score is not evidence about its long-horizon behaviour, in either direction.

---

## L-149. When a learned closure improves, ask whether the model class or the feature set did the work — and the answer has been measured

**Kaandorp & Dwight 2020, Table 3, arXiv preprint p. 37.** Square duct `Re = 3500`, anisotropy RMSE,
two model classes crossed with two feature sets:

| Feature set | Tensor-basis random forest | Tensor-basis neural network |
|---|---|---|
| 5 features (invariants of `S`, `R` only) | 0.0995 | **0.0871** |
| 17 features (+ `grad k` invariants + 9 physical scalars) | **0.0521** | 0.0681 |

**Adding features cuts the forest's error by 47.6% and the network's by 21.8%. Swapping the model
class changes which one wins and moves the number by far less.** The authors say it plainly:
"**the introduction of extra features has significantly more effect than the choice of
neural-networks versus random-forests.**"

**And they diagnose why the 5-feature set is so weak (p. 37)**: of its five features, "**3 are
approximately scaled versions of the other 2 - effectively reducing the input space to two
dimensions.**" That is Guyon & Elisseeff's §3.2 warning — "**Perfectly correlated variables are truly
redundant in the sense that no additional information is gained by adding them**" (JMLR 3, p. 1164)
— showing up in a turbulence feature set twenty years later.

**The corollary from the same survey, which the corpus does not act on.** Guyon & Elisseeff, p. 1158:
"**Selecting the most relevant variables is usually suboptimal for building a predictor, particularly
if the variables are redundant.**" And their probe test (§6, p. 1173): insert a **random** variable
into the candidate set and discard everything ranked at or below it — a near-free control that gives
"**an upper bound on the fraction of falsely relevant variables**". **No paper in this corpus runs it
on a turbulence feature set.**

**What this does not license.** It is one case, one flow, one metric. It does not establish that
features always dominate; it establishes that on the case where both axes were varied together, they
did. **The transferable part is the experimental design — vary both axes — not the conclusion.**

---

## L-150. A hyper-parameter search scored on training loss can select the architecture that fails in deployment, and the loss will not tell you

**Maulik, San, Rasheed & Vedula 2019, §5, arXiv preprint pp. 16-19.** Three ablations of a learned
2-D sub-grid closure, each deployed in the solver:

1. **Remove the two eddy-viscosity kernel inputs** (20 features -> 18): training loss "more or less"
   unchanged; a-posteriori the model "**displayed an unconstrained behavior at the larger scales with
   the formation of non-physical large scale structures.**"
2. **The grid-search optimum is beaten by an architecture the search rejected**: "the utilization of
   a deeper network actually leads to more accurate predictions of the Kraichnan turbulence spectrum
   ... **This despite the fact that the deeper network displays a great[er] mean-squared-error during
   the training phase (which was the root-cause of it being deemed ineligible in the hyper-parameter
   tuning).**"
3. **Reduce the stencil from 9 points to 5**: "**While training errors are more or less similar, the
   reduced stencil fails** to capture the nonlinear relationship between the resolved and cut-off
   scales."

**In all three the training loss is flat and the deployed behaviour changes qualitatively.** The
authors' own conclusion (p. 16): "This a-priori hyper-parameter selection is primarily devised on
mean-squared-error minimization and is **susceptible to providing model architectures which are less
resistant to over-fitting and more prone to extrapolation.**"

**The mechanism in case 1 is worth keeping**: the two discarded inputs were the Smagorinsky and Leith
kernels — 2 of 20 features — and the authors read their effect as "an **implicit regularization** of
our model" (p. 17). **A feature can be doing structural work that no loss on the training set can
see.**

**The rule this produces**: an architecture or feature-set decision for a closure is made against a
*deployment* score, not a training score, and the deployment run is part of the search loop — which
is exactly what makes such searches expensive and is not a reason to skip them. Where a full search
is unaffordable, the honest report is that the architecture was not searched.

**What this does not license.** It does not mean training loss is meaningless — it correctly ordered
nothing here, but it is the only signal available before a solver exists. It means a search *scored
solely* on it will make selections it cannot justify, and the selection should be reported as
unvalidated.

---

## L-151. Every learned closure that runs is buying its stability with something, and the price is always stated somewhere in the paper

Seven papers, seven currencies. **Not one deployed learned closure in this corpus runs without a
stabiliser, except the two whose corrections cannot destabilise the momentum equation by
construction (Singh 2017, Wu 2018).**

| Paper | What it pays | The number |
|---|---|---|
| Maulik 2019 | **backscatter** | `Pi = 0` wherever the sign test fails; "**roughly half of the predicted sub-grid terms are truncated**" (arXiv preprint p. 11) |
| Beck 2019 | **the learned structure itself** | direct closure unstable at CFL 0.5, 0.05 **and 0.005**; rescued by least-squares projection onto an eddy viscosity, limiter `mu in [-mu_0, 20 mu_0]` |
| Kaandorp 2020 | **20% of the correction** | `gamma_max = 0.8`, "**incremented in steps of 0.1 until the solver became unstable**", plus Gaussian smoothing `sigma = 3` cells |
| Schmelzer 2020 | **coefficient magnitude** | "if a model does not converge, we further decrease the coefficients by a factor `xi = 0.1`" — "**This ad-hoc intervention**" |
| Xiao 2016 | **the truth's location in the search space** | `(xi, eta)` clipped to `[-1,1]^2`, "**admittedly an ad hoc modeling choice**"; orientation not perturbed at all, so "**the assumed uncertainty space ... may not contain the truth**" |
| Sirignano 2020 | **network capacity** | "**`N_H >= 50` required for long-time stability**" (`>= 100` without the divergence-free constraint); "**No stabilizing limiters were used**" |
| Guan 2022 | **training data** | `n_tr = 10,000` gives unphysical flows; **`n_tr >= 30,000`** gives stability, with **no clipping, smoothing or added eddy viscosity** |
| Stroefer 2021 | **gradient exactness** | the adjoint transpose convection term "**can result in instabilities** ... **here we eliminate it**"; random weight init "**leads to divergence of the RANS solution**", fixed by pre-training to an existing closure |
| Um 2020 / List 2022 | **training curriculum / gradient length** | pre-train at short unroll then extend; gradient sub-range 20-30 of 60 steps, because full 60-step backprop is training-unstable |

**Four of these are described by their own authors as ad hoc**, in those words. That is a strength of
the literature, not a weakness — and it means a reproduction that omits the stabiliser is not
reproducing the paper.

**The rule for this lab**: a closure reproduction states its stabiliser and its value in the same
sentence as its result. "TBRF reduced `b` RMSE by X%" is incomplete; "TBRF reduced `b` RMSE by X% with
`gamma_max = 0.8` and `sigma = 3` cells" is the claim.

**What this does not license.** A stabiliser is not a defect. Menter's `max()` limiter (AIAA J.
p. 1600) and the WALE denominator's second term — which exists purely because "the ratio ... is **not
well conditioned numerically**" (Flow Turb. Combust. 62, p. 189) — are the same kind of device in
models nobody calls ad hoc. **The lesson is disclosure, not abstinence.**

---

## L-152. Two groups met the same instability and reached opposite diagnoses; both are right about their own case and neither generalises

**Diagnosis A — the closure form is wrong, so constrain it.** Beck, Flad & Munz 2019 found their
learned LES closure unstable at **every** time step they tried (CFL 0.5, 0.05, 0.005: "stability
issues ensued **even for very small timesteps**", arXiv preprint p. 22) and traced it to structure:
in the perfect-LES formulation the coarse-grid inviscid operator **cancels exactly**, so an
approximate learned term leaves no stable numerical operator. Their fix is to change the
mathematical object — project the closure onto an eddy-viscosity basis, with a limiter.

**Diagnosis B — the model is under-trained, so add data.** Guan, Chattopadhyay, Subel & Hassanzadeh
2022, Table 2, arXiv preprint p. 13. One architecture, one flow, one solver; the only variable is
sample count:

| `n_tr` | 500 | 1000 | 10000 | 30000 | 50000 |
|---|---|---|---|---|---|
| a-priori correlation `c` | 0.78 | 0.83 | 0.90 | 0.92 | 0.93 |
| a-posteriori fate (5 ICs) | unstable | unstable | **unphysical** | **stable** | **stable** |

Their conclusion: "the backscattering can be accurately captured and the a posteriori LES can be
stable **without any further post-processing if the training set is large enough.**" **No clipping,
no smoothing, no added eddy viscosity.**

**The two diagnoses are not reconcilable from the corpus and should not be forced.** Guan et al.
refuse to generalise their own result (p. 13): "**we do not claim that all instabilities in other a
posteriori LES runs using data-driven SGS models (reported in other studies) are due to similar
inaccuracies that could be reduced by enriching the training set.**"

**And the threshold they found is not portable.** Their stability boundary sits between correlations
of **0.90 and 0.92**. Beck & Kurz 2021 report a closure that diverges at **0.999**. They say so
themselves: "**these are just empirical thresholds in this testcase, and such thresholds might be
case-dependent.**"

**The rule**: when a learned closure is unstable, "add data" and "change the form" are both live
hypotheses, they are cheap to distinguish (vary `n_tr` with everything else fixed, as Guan did), and
**the a-priori correlation at which stability appears is a property of the case, not a number to
carry between problems.**

---

## L-153. A pointwise regressor produces a field with no controlled derivative, and the momentum equation needs one

**Kaandorp & Dwight 2020, arXiv preprint p. 21, verbatim**: "**Since the random forest is a piecewise
constant approximation of `b`, and derivatives of `b` are needed in the N-S equation**, the
predictions from the TBRF are smoothed spatially with a Gaussian filter, before they are propagated
through the solver ... The TBRF algorithm has **no explicit spatial correlation** in the predictions
since these are based on local features of the flow, so filtering the predictions will introduce some
spatial correlation." Filter width: **standard deviation 3 cell lengths**, and "**This filter width is
an ad hoc choice.**"

**The same wall, reached independently by a different group with a different regressor.** Wang, Wu &
Xiao 2017, arXiv preprint p. 29: "**A small region with abnormal Reynolds stress corrections (e.g.,
non-smoothness or artificial peaks) can introduce large errors to the velocity predictions.** ...
**These fluctuations, despite being small in amplitude, can lead to abnormal behaviors in the
divergence term** and thus in the predicted velocities." And their diagnosis of the cause: "**the
random forest regression used here only provides pointwise estimations but cannot consider the
spatial information of the Reynolds stress field. Therefore, the smoothness of the prediction cannot
be guaranteed.**"

**Three other papers reach the same requirement by other routes.** Xiao et al. 2016 truncate to
**16 (or 8) Karhunen-Loeve modes**, which "correspond to **very smooth fields** of Reynolds stress
discrepancies" (arXiv preprint p. 24). Beck 2019's least-squares eddy-viscosity projection is a
smoothing operation in disguise. Schmelzer's sparsity requirement is explicitly numerical, not
aesthetic (arXiv preprint p. 10): models with large coefficients "are **unsuitable to be implemented
in a CFD solver as they increase the numerical stiffness of the problem and impede convergence.**"

**This is why it is a lesson and not a footnote.** Only `div tau` enters the momentum equation. A
regression scored on `tau` — every a-priori metric in the corpus — is scored on a quantity one
derivative removed from the one that acts. **A model can win on `tau` and lose on `div tau`, and
nothing in a pointwise regressor's training objective prevents it.**

**The practical form**: any pointwise-predicted field this lab propagates gets its `div` inspected
before its `U` is believed, and any smoothing applied is reported with its width. The lab has already
recorded a ~10% RMS `div(U)` from its own post-hoc correction; that is the same mechanism seen from
the output side.

**What this does not license.** Smoothing is not free — it removes real structure along with noise,
and Kaandorp flag the width as unjustified. The principled alternative they point to is choosing the
filter width "**by looking at e.g. required condition numbers for the solver**", which is now
possible: Wu et al.'s local condition number (arXiv:1803.05581, Eq. 2.14) is exactly such a criterion
and costs `O(n^2 log n)`.

---

## L-154. Publish the ceiling next to the result, because the gap is the finding

**Schmelzer, Dwight & Cinnella 2020 report both, on the same normalised metric.** Table 1 (arXiv
preprint p. 6) injects the *extracted* correction as a static field — the best any model of that form
could do. Table 2 (p. 15) reports the *discovered* sparse models, re-solved:

| Case | Frozen-field ceiling `eps(U)/eps(U_0)` | Best discovered model |
|---|---|---|
| Periodic hills `Re = 10595` | **0.00165** | **0.22287** |
| Converging-diverging channel `Re = 12600` | 0.0229 | 0.20828 |
| Curved backward-facing step `Re = 13700` | **0.22703** | 0.30655 |

**Read row by row the table says two different things.** On the hills the extractable correction
would cut the velocity error by a factor of ~600 and the best symbolic model achieves ~4.5 — **the
regression is the bottleneck.** On the curved step the ceiling is 0.227 and the model reaches 0.307 —
**the model is near its ceiling and the ceiling is poor, so the correction *form* is the bottleneck.**
Without both numbers, the two cases look like the same result ("about 4x better than baseline") and
imply the same next action, which they do not.

**Kaandorp report the same structure differently** (arXiv preprint pp. 39-40): propagating the DNS
anisotropy itself already misses, and the additional ML error is "**of similar magnitude to the errors
already made in the propagation**" — so their bottleneck is neither the regressor nor the form, it is
the propagation.

**The rule**: any closure experiment in this lab reports the frozen-field or perfect-model result
alongside the learned one, on the same metric and the same case. It is cheap — it is one extra solve
with the truth substituted — and it is the only way to distinguish "the model is bad" from "the model
class cannot do this" from "the propagation destroys it".

**What this does not license.** The ceiling is a ceiling for *that correction form*. Schmelzer's
frozen field is `b^Delta` plus a `k`-equation residual; a different form has a different ceiling. And
a ceiling computed with DNS data says nothing about what is reachable without it.

---

## L-155. Choose the state variable that is already invariant to the axis you want to extrapolate along, and the architecture stops mattering

**Bae & Koumoutsakos 2022, arXiv preprint p. 7.** Same reinforcement-learning algorithm, same reward,
same solver, same training Reynolds numbers (`Re_tau in {2000, 4200, 8000}`) — **two state spaces**:

- **LLWM**, whose state is a log-law slope and intercept `{1/kappa_m, B_m}` — **dimensionless and
  Reynolds-free by construction** — extrapolates to **`Re_tau = 1e6`**, a factor of **125** beyond
  the largest training value, with "the prediction error in the friction velocity ... **less than
  4%**".
- **VWM**, whose state carries the wall-normal sampling height in wall units `(h_m)+` explicitly, was
  trained over `150 < (h_m)+ < 1200`, and fails outside it: "Cases at `Re_tau = 2e4` and `5e4`
  produce high errors as the `(h_m)+` is not within the trained range". **Two velocity profiles are
  omitted from Fig. 4(a) because they lie outside the plotted range.** Refining the grid so that
  `(h_m)+` re-enters the trained band makes "**errors decrease significantly**".

**The failure is not a failure of learning. It is a failure of parameterisation, and the fix is a grid
change, not a training change.**

**The same principle appears twice more in the corpus, both times as the stated reason for a design
choice.** Wu et al. 2018 normalise every feature as `alpha_hat = alpha/(|alpha| + |beta|)` so that
each lies in `[-1, 1]` — a bounded, saturating map with no scale to leave. Singh et al. 2017
non-dimensionalise by the local `nu + nu_hat` and wall distance, with the explicit rationale that
dimensional quantities "**may have different numeric values even when two flows are dynamically
similar**" (arXiv preprint pp. 11-12) — and that is what they credit for the model porting to a
different solver.

**The rule**: before choosing features, name the axis you intend to extrapolate along — Reynolds
number, geometry, grid resolution — and check whether any input carries that axis in its units. If
one does, the model has memorised a range, and its generalisation limit is that range regardless of
how it was trained.

**What this does not license.** A `Re`-free state is not a `Re`-free model: Bae's own error
"**increases with Reynolds number**" even for the LLWM, and the paper's headline is a bound, not a
constant. And the LLWM's state is only available because the flow *has* a log layer — the trick does
not survive into flows where the assumed structure is absent, which is why neither wall model can do
transition.

---

## L-156. Error cancellation makes the worse model look better, and a coarser grid look better, and both have been measured

**Lozano-Duran & Bae 2023, arXiv preprint pp. 19-20.** On the adverse-pressure-gradient and
separation cases, the classical equilibrium wall model beats the learned one on total wall-stress
error — and the authors refuse the win: "**EQWM appears more accurate but for the wrong reasons**",
because it **underpredicts `tau_w` while overpredicting the near-wall velocity** and the two errors
cancel. The same explanation is offered for the one aerodynamic case where the classical model wins,
`C_L` at low incidence on the NASA CRM High-Lift.

**Larsson et al. 2016 state the general form of it, and it is worse than a per-case caveat**
(PDF p. 18): "note specifically that the results in Fig. 5 are best (smallest log-layer mismatch) for
the **coarsest** grid", and "**a flawed model may produce 'perfect' results by introducing errors
that exactly cancel those present in the outer layer LES. For example, since most codes/numerics
produce a positive log-layer mismatch, any modeling modification that by itself would produce a
negative mismatch will lead to 'improved' results.**"

**Read together, those two say a model can be selected *for* its ability to cancel the host code's
error** — and it will then fail in any other code, or on any other grid, in the direction nobody
tested.

**Lozano-Duran's methodological answer is the transferable part**: split the error into an
**internal** component (against the model's own consistent target) and a **total** component (against
DNS or experiment), and report both. Their ZPG boundary layer: internal error **below 0.5%** for the
learned model versus **~2%** for the classical one, while the **total** error is **5-15% for both**.
The learned model is dramatically better at the thing it was trained on and tied on the thing the
user cares about — and the authors name the reason (p. 29): "**the main limiting factor in the
accuracy of the BFWM predictions originates from external modelling errors due to the poor
performance of SGS models.**"

**The rule**: an improvement measured on one grid, in one code, on one integral quantity is not
evidence of a better model until the same comparison survives a grid change. Larsson makes it
mandatory (p. 18): "**it is mandatory to test all wall-modeled LES approaches on different grids:
both by refining the grid and by modifying the aspect ratio of the grid.**"

**What this does not license.** Cancellation is not fraud and is not always avoidable — Menter's SST
constants are hand-tuned to five flows and he says so. The lesson is that a single-configuration
improvement cannot distinguish a better model from a better-cancelling one, so the claim must be
sized accordingly.

---

## L-157. Two methods in this corpus provably cannot contain the right answer, and both say so in print

**Case 1 — the search space excludes the truth for a stability reason.** Xiao et al. 2016 perturb the
Reynolds stress in its invariants (magnitude, shape) but **not** its orientation, because "**Perturbing
the orientations of the modeled Reynolds stress tensor can potentially cause instability in the RANS
momentum equation**". The consequence, in the same paragraph (arXiv preprint p. 10): "**Consequently,
the assumed uncertainty space of Reynolds stresses may not contain the truth** because the true
Reynolds stresses are likely to have different orientations from those of the RANS predictions."

And the error compounds in the same direction: their credible intervals are also too narrow
(p. 28) — "**the 95% credible intervals ... failed to cover the truth** ... **The iterative ensemble
Kalman method tends to underestimate uncertainties in the posterior distributions.**" **Both defects
point at overconfidence.**

**Case 2 — the answer lies outside the convex hull.** de Zordo-Banliat et al. 2023 aggregate four RANS
models per cell. Because the combination is convex, the result is confined to the hull of its
components. Their finding (arXiv preprint p. 17): "In the upper part of the wake, **all models
exhibit relative consensus on the wrong solution, a known limitation inherent to mixture models.** In
such a case, the variances (a measure of model consensus) are also small and **do not encompass the
reference** either." **Wrong, and confident, and the confidence measure agrees with the error.**

They are equally clear about what their variance is not (p. 19): "**the error bars must not be
interpreted as the region where the true solution possibly lies, but simply as a measure of the
uncertainty in the choice of a best-performing model.**"

**Why this is one lesson and not two.** Both methods produce an interval; in both, the interval is a
statement about the *method's internal disagreement*, not about the truth; and in both, the failure
mode is silent — the interval narrows exactly when it should widen. **A narrow interval from a
mixture or from an under-dispersed ensemble is a report about consensus, and consensus is not
evidence.**

**The rule**: when a method reports an uncertainty, state what the uncertainty is over. If it is over
model choice, over ensemble spread, or over a parameterised subspace, say so, and say what is outside
the space. The one thing that would fix Xiao's case — perturbing eigenvectors — is Iaccarino et al.
2017, which is quarantined in this corpus, so the loop cannot currently be closed here.

---

## L-158. The learned object that ports to another solver is the one that modifies a term, not the one that modifies the answer

**Two papers in this corpus tested portability and reached opposite results, and the difference is
what they learned.**

**Singh, Medida & Duraisamy 2017 (arXiv preprint pp. 20-21)** embedded their trained network — a
multiplier `beta(x)` on the Spalart-Allmaras production term, keyed on locally non-dimensionalised
features — in **AcuSolve**, an unstructured, dimensional, commercial Galerkin-least-squares
finite-element code, having trained it in **ADTURNS**, a structured, non-dimensional, cell-centred
finite-volume code. It reproduced the improvement. They credit the local non-dimensionalisation.

**Lozano-Duran & Bae 2023 (arXiv preprint p. 29)**: "**Consistency between the model and the
numerical/gridding schemes is solver-dependent. As such, the BFWM must be re-trained to yield accurate
predictions in different flow solvers.**"

**The mechanism is not subtle once both are on the table.** Lozano-Duran's training data are not
filtered DNS — they are generated by wall-modelled LES **in the same solver**, deliberately, so that
"solver and grid numerical errors" are part of the label. The model absorbs charLES's numerics
because it was asked to. Singh's `beta` multiplies a physical production term and is a function of
dimensionless local ratios; there is no solver in it to absorb.

**The general statement is Larsson's, from the wall-model side** (PDF p. 11): "**even a 'perfect'
wall-model in one numerical code would suffer from a log-layer mismatch if implemented in a different
numerical code!**" — and the sign of the mismatch is set by the host code's grid arrangement and
dissipation. **A model trained against one code's errors inherits that code's sign.**

**And the same trade shows up in the differentiable family.** Sanderse et al. 2024, arXiv preprint
p. 8: a-posteriori learning "**implicitly corrects for spatial and/or temporal discretization errors,
which can be desirable but can also limit application to different grids or time steps.**" **The
property that makes a solver-trained model accurate is the property that makes it non-portable.**

**The design question this forces**: decide up front whether the closure is meant to be a *model* (to
be used elsewhere) or a *correction* (to this code, this grid). Both are legitimate; they are graded
differently, and a correction reported as a model will fail on first transfer.

---

## L-159. A constant found by "increase it until the solver breaks" is a measurement of the solver, and it should be reported that way until a criterion replaces it

**Kaandorp & Dwight 2020, arXiv preprint p. 26, verbatim**: "**`gamma_max` was incremented in steps of
0.1 until the solver became unstable, yielding a value of `gamma_max = 0.8`.** ... **As this choice is
ad hoc, further work related to this topic is necessary.**" The learned anisotropy is therefore never
applied at more than 80% strength, and the trade is stated: "A **lower value for `gamma` means that
the linear eddy viscosity assumption becomes more dominant, resulting in a more stable solution, but
impairing the accuracy of the solved mean velocity.**"

**The same device, criticised by name, in the paper Kaandorp cites.** Wu, Xiao & Paterson 2018 reject
blended RSM/eddy-viscosity stresses because "**the specification of a blending factor `alpha` is
largely ad hoc and lacks physical basis**" (arXiv preprint p. 4) — and use an implicit split instead.

**And then the criterion arrives.** Wu, Xiao, Sun & Wang, arXiv:1803.05581, pp. 23-24: "the choice of
the blending factor is **largely ad hoc due to the lack of a quantitative method to evaluate the model
conditioning** ... **The metric proposed in this work can assess the model conditioning with any given
blending factor, and thus it is possible to choose a minimum blending factor that maintains good
conditioning.**" Their local condition number costs `O(n^2 log n)` and is **provably
mesh-independent**.

**So the sequence is: a constant is found empirically; its author flags it as ad hoc; a second author
rejects the whole device; a third supplies the measurable criterion that would set it.** That
sequence is the normal life of a numerical constant and it is worth recognising in progress, because
the useful action differs at each stage. At stage one the action is *disclose*; at stage three it is
*replace*.

**Three more constants in the same state in this corpus**: Schmelzer's convergence-rescue factor
`xi = 0.1`; Kaandorp's Gaussian filter width `sigma = 3` cells ("**This filter width is an ad hoc
choice**"); Xiao's realisability clip to `[-1,1]^2` ("**admittedly an ad hoc modeling choice**"). **All
three authors say so themselves.** The literature's honesty here is better than its reputation.

**The rule for this lab**: a constant obtained by incrementing until failure is recorded with the
procedure that produced it, the failure it was avoiding, and the sensitivity around it — and it is
flagged as replaceable. It is never quoted as if it were derived.

---

## L-160. When a paper reports no number, write "none reported" and stop

**Five papers in the 33-paper closure corpus report no numeric error metric for the thing they are
about.** This is not an accusation; it is a fact about what can be cited from them.

| Paper | What is missing | What exists instead |
|---|---|---|
| Stroefer & Xiao 2021 (arXiv v1) | **all of it** — no MSE, no percentage, no reduction factor | "visually indistinguishable"; and **no ensemble-Kalman comparison at all** (0 hits for "kalman") |
| Sirignano/Freund 2020 | **any % versus dynamic Smagorinsky** — a full `%` search returns 3 hits, none of them results | graphical spectra and decay curves |
| Wu, Xiao & Paterson 2018 | any RMSE or L2 table | one separation-bubble extent in prose |
| Maulik et al. 2019 | **every result** — the string "Table" does not appear in the paper | figures |
| Singh et al. 2017 | any flow-field error | "<10% compute overhead"; "15% more accurate" bubble length on a different case |

**And three more where the flagship result specifically is graphical**: Bae 2022's per-Reynolds-number
errors (Fig. 3 only, ordinate -70% to +10%); Lozano-Duran 2023's NASA CRM `C_L`/`C_D`/`C_M`
("moderate improvements", Fig. 15); de Zordo-Banliat 2023, where **one** number exists in the whole
paper ("**approximately 1/3**", velocity MSE, extrapolation case).

**Axis tick labels are not data.** A figure whose ordinate spans -70% to +10% tells you the plotting
range, not the result. Digitising a plot is a measurement with its own error budget and is reported
as such, not as the paper's number.

**Why this needs to be a standing rule and not a per-case judgement.** The pressure to supply a
number is strongest exactly where none exists — a catalogue row with an empty metric column looks
like a gap in the cataloguer's work rather than a property of the source. **The row is correct when
it says "none reported".** The lab's corpus defect of 2026-08-20 (L-144) was a citation failure of
exactly this shape at one remove: text that reads as sourced but is not.

**The operational form**: catalogue and inventory rows carry an explicit `metric: none reported` where
that is the truth, with the sentence the paper does offer quoted verbatim beside it. Any downstream
document that attaches a percentage to one of the five papers above has fabricated it.

---

## L-161. A model selected by looking at the deployed answer is not held out, however many candidates were rejected

**Schmelzer, Dwight & Cinnella 2020.** Sparse regression produced **52, 114 and 136** candidate
`b^Delta` models for the three training cases. The authors then, in their own words (arXiv preprint
p. 15), "**In an ad-hoc way, we hand-select 5 models for `b^Delta` and 3 for `R`**", ran **35 to 47
CFD simulations per test case**, and reported the best by re-solved velocity error. The headline
numbers of Table 2 — `eps(U)/eps(U_0)` of 0.208 to 0.306 — are **post-selection**, and the selection
criterion was the a-posteriori result.

**Singh et al. 2017 do the same thing and flag it themselves** (arXiv preprint p. 20): "**the quality
of the NN-augmented model is sensitive to the selection of the training-data. In this work, the best
model 'P' is selected by exploring several combinations of the data-sets.**" Their Fig. 18 shows the
eight-model spread that the selection collapsed; **the spread is not quantified**, and they add
(p. 19) that the ensemble "**does not qualify as a formal uncertainty quantification technique**".

**Neither paper hides it. Both report the procedure.** The lesson is about what the resulting number
means, not about the authors' candour: **it is a best-of-N, and N belongs beside it.**

**Where a genuinely held-out number does exist in the corpus, it is smaller and more useful.**
Schmelzer's extrapolation to periodic hills at `Re = 37000` against experiment was never in the
selection loop — and its result is reported graphically, with no number. Kaandorp's test cases are
predicted by models trained on a fixed set of three flows with no per-case selection, and the
reattachment result (**6.32** against DNS 6.28) is therefore a stronger number than its size
suggests.

**The rule for this lab's pre-registrations**: if a candidate set is filtered by a re-solved result,
the filtering is part of the method and the reported error is a best-of-N. Either register the
selection rule in advance, or report N, or hold out a case the selection never touched — and say
which of the three was done.

---

## L-162. Quote a learned model's training cost in solves of the thing it replaces, because that is the only unit that decides anything

**List, Chen & Thuerey 2022, arXiv preprint pp. 26-27** are the only authors in the corpus to do this,
and it changes how their result reads. Training on one GTX 1080Ti: **61 h, 78 h and 240 h** for the
three cases — which they convert to **[120, 118, 22] full-length DNS solves.**

**So the model must be re-used 22 to 120 times before it repays its own training**, against a
per-inference speed-up of 3.3-14.4x. That is a break-even calculation a lab can act on, and it is
invisible in the wall-clock numbers alone.

**Two other papers give the same kind of ratio for different quantities, and both are decision-grade.**
Bae & Koumoutsakos 2022 (arXiv preprint p. 10): reinforcement learning trained a wall model with
**`O(1e3)` CPU-hours and < 1 GB**, where "generating the DNS data would need **`O(1e7)` CPU-hours and
> 100 TB**" — **four orders of magnitude**, and the argument for reward-based over label-based
training. Xiao et al. 2016 (arXiv preprint p. 40): their UQ costs "**600 evaluations** of the forward
RANS model", each "**only 10% as expensive as a baseline RANS simulation**", giving "**the total
computational cost ... 60 times as that of the baseline simulation**."

**And the counter-example that shows why the unit matters.** Beck et al. 2019 report a storage figure
instead: holding `U` and `R(F(U))` at their sampling rate for `0.2 T*` needs **~55 TByte** (arXiv
preprint p. 7). Their own conclusion is that the result is "**data-bound**" — "the performance of the
prediction is likely limited by the available amount of data used for training, rather than network
architectures" (p. 24). **A cost quoted in terabytes told them more than a cost quoted in GPU-hours
would have.**

**The rule**: every cost in this lab's closure work is quoted in the unit that bounds the decision —
baseline-solve equivalents, DNS-solve equivalents, or storage — and never only in wall-clock, which
is unportable across hardware and says nothing about whether the method is worth using.

**What this does not license.** Amortisation arguments assume re-use, and re-use assumes portability
(L-158). A model that must be retrained per solver, per grid and per Reynolds number never reaches
its break-even, whatever its training cost.

---

## L-163. A corpus is a live dependency, and a paper arriving mid-task changes conclusions already written

**2026-08-20, during a single cataloguing pass, three files landed in `docs/papers/closure/` after
the pass began**, and two of them changed statements that had already been drafted:

- **`Wu2018_rans_explicit_closure_ill_conditioned.pdf`** (arXiv:1803.05581v3). The session's own
  verification flags recorded this paper as **not in the corpus**, with the instruction to add it to
  the shelf. It is the source of the "0.31% stress error -> 35.1% velocity error" table (L-146) and of
  the explicit-versus-implicit conditioning result (L-147) — **the two numbers on which four other
  papers' framing depends.** Before it arrived, both were second-hand.
- **`Guan2022_stable_aposteriori_les_cnn.pdf`** (arXiv:2102.11400v1). Recorded as `MISSING`. It is the
  sole source for the training-set-size stability table (L-152), and it directly contradicts the
  "learned SGS closures need a stabiliser" summary that the rest of the category supports.
- **`Xiao2016_bayesian_model_form_uncertainty.pdf`** — a byte-identical duplicate of a file already
  present (L-145).

**The failure mode this creates is not a wrong statement; it is a stale one.** A document that says
"the ill-conditioning paper is not in the corpus" was true when written and false four hours later,
and nothing in it announces the change. Prose does not have a dependency graph.

**Two guards, both cheap.**
- **Re-derive counts from the filesystem at every phase boundary**, never from prose. The manifest is
  script-generated (`S/verify_pdfs_A.py` + `S/build_manifest_A.py`); the catalogue's count table is
  not, and is therefore the thing to re-check.
- **Date the corpus state inside any document that reasons about absence.** A sentence of the form
  "X is not on disk" carries a timestamp and a pointer to `MANIFEST.md` as the live authority, so a
  reader knows whether to re-check rather than having to guess.

**The related discipline, already standing from L-144**: the title-page check "**runs again at every
phase boundary, because files keep arriving.**" This pass is the demonstration that the clause was
load-bearing — all three arrivals were verified on arrival, and one of them was a duplicate that only
a hash check would have caught.

**What this does not license.** It is not an argument for freezing a corpus. The arrivals improved the
work: two of the three closed genuine gaps, one of which had been flagged as the most damaging
omission in the shelf. **The cost of a moving corpus is bookkeeping; the cost of a frozen one is
reasoning from absence.**

---

## L-164. How far you roll forward and how far the gradient travels are two different lengths, and only one of them has an optimum

**List, Chen & Thuerey 2022, §6, arXiv preprint p. 22.** On a **60-step** unrolled rollout, they vary
only the sub-range over which the gradient is back-propagated:

| Gradient sub-range | Temporal mixing layer, MSE @ 512 dt | Spatial mixing layer, MSE @ 1000 dt |
|---|---|---|
| 10 | 2.36e-5 | **2.44e-3** |
| 20 | 2.19e-5 | 2.73e-3 |
| 30 | **1.93e-5** | 2.98e-3 |
| **60 (full)** | **training unstable — no value reported** | **1.19e-2** |

**Full back-propagation through the whole rollout is training-unstable on one case and about four
times worse on the other** — 1.19e-2 against a no-model baseline of 2.03e-2, i.e. barely better than
no model at all. Their conclusion: the optimum sub-range is **20-30 steps**, "a split into 2 subranges
of 30 steps each performed best", with saturation "at **circa 60 steps, which coincides with the
integral timescales**".

**And they explicitly distinguish this from the standard remedy (p. 28)**: "This approach differs from
the common practice in machine learning, where gradients of early evaluations of the neural network
are usually discarded or re-scaled when **gradient clipping** is applied." **No gradient clipping is
used.**

**The forward length behaves differently and has its own optimum, set by the physics.** Um et al. 2020
find monotone improvement with look-ahead on their wake and buoyancy cases (40% at `n<=4`, 54% at 64,
**60% at 128**) — but on the **randomly forced** Burgers case the optimum is `n = 2`, and they name
the reason (arXiv preprint p. 6): "**Learned correction functions need to be able to anticipate future
behavior ... The randomized forcing in this example severely limits the number of future steps that
can accurately be predicted given one state.**" List find no improvement at 120 steps and **reduced
accuracy at 180 and 240.**

**Sanderse et al. 2024 give the general statement** (arXiv preprint p. 8): "**Unrolling too few time
steps gives only limited gains over a priori learning, while unrolling too many time steps is
computationally expensive, has the danger of exploding or vanishing gradients, and can be unrealistic
given that turbulent flows are chaotic.**"

**Two numbers to carry**: the useful **forward** horizon is bounded by the predictability of the
physics; the useful **gradient** horizon is bounded near **one integral timescale**. They are not the
same number, and reporting only one of them makes an unroll study unreproducible.

---

## L-165. An invariance defect survived peer review in the paper whose subject is invariance, so audit your own pipeline rather than your intentions

**Wu, Xiao & Paterson 2018, Acknowledgment, arXiv preprint p. 33, verbatim**: "**one of the reviewers
pointed out the lack of Galilean invariance in two of the normalization constants in our manuscript,
which we fixed during the revision.**"

This is a paper built on a 47-invariant minimal integrity basis, whose contribution is precisely the
principled construction of invariant features. **The defect was not in the basis. It was in the
normalisation constants dividing it** — and it reached submission.

**Only one group in the corpus audits its own feature set and publishes the failures.** Kaandorp &
Dwight 2020, Table 1 (arXiv preprint p. 25), marks four of nine physically-motivated features with a
dagger: "**Features marked with † are rotationally invariant but not Galilean invariant**" — they are
`k`, `u_k dp/dx_k`, `u_i dk/dx_i`, and `u_i u_j du_i/dx_j`. The model's *output* is Galilean invariant
by the tensor basis; four of its *inputs* are not; both facts are printed on the same page.

**Everyone else asserts invariance for the whole pipeline.** Ling et al. 2016 state that the
architecture "guarantee[s] the Galilean invariance of the network predictions" — true of the output —
while using "rotational invariance" and "Galilean invariance 'interchangeably in the same paragraph,
and never discussing reflection. Schmelzer et al. use the word "Galilean" once, in a literature
review. Sirignano et al. and List et al. state plainly that they do not enforce it.

**Why the failure is systematic rather than careless.** Invariance is a property of a *composition*:
the features, their normalisers, the basis, the output map, and any data augmentation. It is
conventional to prove it for the piece one designed and inherit it for the rest. **The normalisation
constants are the piece nobody designs.**

**The check is mechanical and cheap**: apply a Galilean boost and a rotation to a stored field,
recompute every input *and every normaliser*, and require the model output to transform correctly. It
is a unit test, it runs in seconds on a frozen field, and it would have caught the defect above before
submission.

**What this does not license.** It is not evidence that invariance-by-construction fails — Ling et
al.'s own controlled comparison (plain MLP `b` RMSE 0.33 versus TBNN 0.13 against a linear baseline of
0.23, Table I, preprint p. 11) is the strongest argument for it in the corpus. It is evidence that the
guarantee attaches to a specific composition and must be verified over the whole of it.

---

## L-166. The thing you clip away to get stability may be the entire advantage you were buying

**Guan et al. 2022, arXiv preprint p. 11, Table 1.** A-priori correlation of the predicted sub-grid
term, computed **separately** on grid points of forward energy transfer and of backscatter:

| | Dynamic Smagorinsky (with positive clipping) | Local ANN (with sign truncation) | CNN (no clipping) |
|---|---|---|---|
| correlation on forward transfer | 0.55 | 0.86 | **0.96** |
| **correlation on backscatter** | **0 exactly** | 0.83 | **0.92** |

**The classical model's backscatter correlation is exactly zero by construction** — positive clipping
enforces `nu_e >= 0`, so it cannot represent energy flowing from small scales to large ones at all.

**And then the controlled test (Fig. 8, arXiv preprint p. 17): applying the same truncation rule to
their own CNN makes it "excessively diffusive (with performance comparable to that of the
LES-DSMAG)".** The learned model, stripped of backscatter, degrades to the baseline it was beating.

**Maulik et al. 2019 apply exactly that truncation and state its size and its cost.** Their rule is
`Pi = 0` wherever `(grad^2 omega_bar)(Pi_tilde) <= 0`, justified as ensuring "**numerical stability
due to potentially negative eddy-viscosities**". Size of the intervention: "**roughly half of the
predicted sub-grid terms are truncated**" (p. 11). Cost, in their words: it "**precludes the presence
of a backscatter of enstrophy** for strict adherence to viscous stability requirements".

**So the sequence is: train a model that can represent backscatter; discard the half of its output
that does; obtain a positive-definite eddy viscosity with a learned magnitude.** That may still be an
improvement — Maulik's deployed model does beat static Smagorinsky and Leith on the spectrum — but it
is a different claim from "a learned closure captures backscatter", and the two are easily conflated.

**The rule**: when a stabiliser removes a class of predictions, measure the model with and without it,
and report what fraction of the output the stabiliser touched. Both papers above do exactly this,
which is why the lesson is available at all.

**What this does not license.** It is not an argument against clipping. Guan et al.'s alternative
route — more training data — worked on *their* flow, at 30,000 samples, in 2-D, and they explicitly
decline to generalise it (L-152). Clipping remains the only option when the data are not there.

---

## L-167. A confidence score is a triage tool, and the paper that built one says it is not a guarantee

**Lozano-Duran & Bae 2023** ship a confidence score with their wall model: `p_conf = d_s/d_i`, the
distance of the current input to the nearest training sample, normalised by that sample's own
neighbourhood scale. **It behaves exactly as designed.** NASA Juncture Flow, Table 1 (arXiv preprint
p. 29): confidence **98%** on the upstream fuselage, **82%** in the juncture, **22%** at the juncture
trailing edge — and the diagnosed reason at the trailing edge is a grid fact, not a model fact: the
separation bubble is `0.3 delta` thick against a grid spacing `Delta ~ 0.2 delta`, i.e. "**only one
grid point across the separation bubble**".

**And then the caveat, from the same authors (p. 28)**: "**This implies that low confidence scores may
still result in accurate wall stress predictions and vice versa. Moreover, the confidence score does
not provide an error bound on the value of the prediction**, which would be more representative of the
model performance."

**Beck & Kurz 2021 recommend precisely this device and stop at the same place** (arXiv preprint
pp. 11-12): "**a means of measuring confidence in the model prediction should accompany any model - in
its simplest form, this could be an estimate of the position of the input data in feature space and a
comparison against the statistics gathered during training**", together with "**a consistent fallback
mechanism in cases where the model is likely to fail**". Sanderse et al. 2024 close the loop by
reporting that the general problem is open (arXiv preprint p. 21): distribution shift is a known
limitation, "**Learning useful 'invariant' input features may assist with this but that is as yet a
largely unsolved problem in machine learning.**"

**A third instance, arrived at differently.** de Zordo-Banliat et al. 2023 find their aggregation
weights become "**less sharp** ... i.e. the models are weighted more uniformly" on the extrapolation
scenario (arXiv preprint p. 22) — an OOD signal that falls out of the method rather than being bolted
on. **And it fails in the one case that matters most**: where all component models agree and are
wrong, the variance is *small* (L-157).

**The rule**: a confidence score earns its place as a *routing* device — where to refine the grid,
where to distrust an integral quantity, where to ask for more data — and never as an error bar. Report
it alongside the error, not instead of it, and state the two known failure modes: confident-and-wrong
under consensus, and unconfident-and-right away from the training manifold.

**The free asymptotic checks are cheaper and are not run.** Beck & Kurz, p. 12: "**The simplest case
of generalization capability of an ML-augmented model should be at both limits of modeling: it should
turn off in laminar flow and at the DNS resolution.**" **No paper in the corpus reports either test.**

---

## L-168. Two secondary descriptions of the same architecture disagree, so an architecture is quoted from the primary source or not at all

**Ling, Kurzawski & Templeton's TBNN is described twice in this corpus and the descriptions are
incompatible.**

| Source | Layers | Learning rate | Optimiser | Batch |
|---|---|---|---|---|
| **The SAND2016-7345J preprint on disk**, p. 8 | **8 hidden x 30 nodes** | **2.5e-7** | **stochastic GD, per-point updates** | — |
| Kaandorp & Dwight 2020, arXiv preprint pp. 16-17, "based on Ling et al." | **10 hidden** | **2.5e-5** | **Adam** | **1000** |

The SAND preprint attributes 10 layers and `2.5e-6` to its *baseline MLP*, not to the TBNN — so the
secondary description appears to have merged the two networks and shifted the learning rate by two
orders of magnitude. **Both cannot be right, and the published JFM version may differ from the SAND
preprint in ways neither this lab nor Kaandorp can see from here.**

**The consequence is not academic.** Kaandorp's Table 3 — the corpus's best feature-versus-model-class
comparison (L-149) — reports a TBNN column produced by *a* tensor-basis network. Whether it is *the*
network of the SAND preprint is unknown. The comparison remains valid as a controlled experiment
within that paper, because the same TBNN implementation is used in both rows; it is **not** valid as a
statement about Ling et al.'s published model.

**The rule, which is L-144's rule extended one step**: L-144 established that a *file* is verified by
its printed title page. This adds that a *fact* is verified by the page it is printed on. An
architecture, a hyper-parameter or a constant taken from another paper's description of a third paper
is a second-hand claim and is labelled one. Where the primary source is on disk, quote it and note the
discrepancy; where it is not, quote nothing.

**Recorded and deliberately not resolved.** Guessing which description is right would be exactly the
move that produced the corpus defect of 2026-08-20. For any reproduction here: **use the on-disk SAND
numbers, and state that Kaandorp's differ.**

---

## L-169. A method's own baseline is the hardest thing to beat, and three papers in this corpus lose to theirs

**Maulik & San 2017, Table 4, arXiv preprint p. 17.** Deviatoric sub-filter stress MSE on 3-D
Kolmogorov turbulence, all `x 1e-5`:

| Model | `tau_11` | `tau_12` | `tau_13` | `tau_22` | `tau_32` | `tau_33` |
|---|---|---|---|---|---|---|
| **ANN (theirs)** | 8.00 | 3.60 | 3.51 | 7.77 | 3.64 | 6.82 |
| Scale similarity | 6.76 | 5.62 | 5.91 | 6.76 | 5.91 | 7.95 |
| **AD3 (3-step approximate deconvolution)** | **2.46** | **1.69** | **1.82** | **2.46** | **1.83** | **2.91** |

**The classical method wins every component by about a factor of three, and the authors say so**:
"The AD3 approach can be seen to perform better (on average) than our proposed framework" (p. 16). On
their stratified case (Table 6, p. 25), plain **scale similarity beats the neural network on five of
six components.**

They also state the mitigating fact, which is the interesting part: AD3 is advantaged because "**the
specified filter utilized for the iterative deconvolution is the same as the one used for convolving
the field**" — **AD3 knows the filter and the network does not, which is the entire premise of "blind"
deconvolution.** So the comparison is not like-for-like, and the paper is honest about both halves.

**Two more instances.** Menter 1994's own backward-facing-step table (AIAA J. p. 1603) shows the
**original k-omega** at 6.4 step heights against SST's 6.5 and an experiment of ~6.4 — **the model SST
was built to replace matches the experiment at least as well on that metric**, and Menter reports it.
Lozano-Duran & Bae 2023 find the algebraic equilibrium wall model more accurate than their learned one
on total wall stress in the adverse-pressure-gradient cases (L-156).

**Why this is a lesson about reporting rather than about method quality.** All three papers publish the
loss, which is why the corpus can see it. The failure mode is downstream: a summary that carries
"neural network sub-grid model demonstrated on isotropic and stratified turbulence" without the table
converts a candid partial result into an implied win.

**The rule**: a closure result in this lab is reported against the strongest classical baseline
available on the same case, with the baseline's advantages stated — and where the baseline wins, the
row says so. **The corpus's most useful papers are the ones that did this.**

## L-170. On statistically two-dimensional benchmark flows, Pope's ten-tensor basis has rank three — most of the "expressive power" of every tensor-basis model is not there to be learned

Every tensor-basis closure — TBNN, TBRF, SpaRTA, GEP — writes
`b_ij = sum_{n=1..10} g^(n)(lambda_1..lambda_5) T^(n)_ij` and sells the ten
tensors as its expressive advantage over Boussinesq. Pope says plainly that in
two dimensions the basis collapses: "In the general three-dimensional case there
are ten tensors and five invariants", with the two-dimensional case reducing to
three [VERIFIED-PDF: Pope 1975, JFM 72(2), p. 335]. He also evaluated his
coefficients *only* for two-dimensional flows (his abstract, p. 331).

Measured on the Closure Challenge benchmark, per cell, as the numerical rank of
the ten 3x3 tensors flattened to a 10x9 matrix (singular values above
`1e-8 sigma_max`): **mean rank 3.24 over 5,000 random training cells — 3,814
cells at rank 3, 1,185 at rank 4, exactly one above 4, none above 5.**

Three consequences, all of which bite in practice:

- **The normal equations of any least-squares fit over the basis are rank
  deficient by six or seven.** Kaandorp & Dwight's published regularisation
  `Gamma = 1e-12` [VERIFIED-PDF: arXiv:1810.08794v2, p. 30] then returns
  coefficients of order `1/Gamma` along the null directions. A first
  implementation of their tensor-basis decision tree reproduced this exactly:
  training `b_rms` of **0.81**, worse than predicting `b = 0` (0.33). Replacing
  the ridge solve with a truncated eigendecomposition (invert only eigenvalues
  above `1e-8 lambda_max`) moved training error to **0.13** with no other change.
  The paper's constant is not wrong; it is calibrated for a basis that is not
  degenerate, and nothing in the paper warns you.
- **A neural TBNN has the same degeneracy but no way to signal it.** The network
  is free to put arbitrarily large coefficients on the null directions; they
  cancel in-distribution and do not cancel out-of-distribution. On the NASA
  wall-mounted hump — the only benchmark case with a stagnation region — a
  trained TBNN produced `||b||` of order **1e7** and a TBRF on the same split
  produced order **1e2**, against a realisable maximum of 0.8165. The
  architecture guarantees Galilean invariance; it guarantees nothing about
  boundedness or realisability.
- **A benchmark of 2-D flows cannot test the claim that the ten-tensor basis is
  what makes these methods work.** Anyone reporting a TBNN/TBRF result on
  periodic hills and ducts is reporting a three-tensor model.

The general lesson: **measure the rank of your basis on your data before you
attribute performance to its size.** A model class you cannot excite is not a
model class you have tested. It is one line of numpy.

## L-171. A constant tensor beat the RANS baseline on every test case — pick trivial baselines that can embarrass you

The preregistration for three Phase-3 reproductions named four baselines, one of
which (B3) was the mean `b_LES` over the training cells: a single constant
tensor, no inputs, no fitting beyond an average.

**B3 beat k-omega SST on all eight strict TEST cases** — 0.4036 against 0.5799 on
a duct, 0.2258 against 0.2889 on a hill, and so on for the rest. Predicting one
constant anisotropy everywhere is a better a-priori anisotropy model than the
linear eddy-viscosity closure the benchmark ships.

That single number reframes an entire literature's favourite comparison. "Our
method reduces the Reynolds-stress anisotropy error relative to the baseline RANS
model" is a claim a constant satisfies. The learned models here did beat B3 — on
seven of eight cases, by factors of 2 to 5 — but they had to be *asked*, and the
margin over B3 is much smaller and much more informative than the margin over
SST that everyone reports.

Two habits follow. **Put a zero-input predictor in every preregistration**, not
just the domain baseline. And **when the trivial baseline beats the domain
baseline, say so loudly**: it is a statement about the metric, not about the
models, and it tells you the metric is not measuring what the field thinks.

## L-172. `torch.set_num_threads(16)` made training 63x slower than 4 threads — profile the thread count before you scale down the experiment

Training a small tensor-basis network (8 hidden layers x 30 nodes, plus a
ten-tensor merge) on 342,014 samples, measured on this 16-core box:

| threads | batch | seconds / epoch |
|---|---|---|
| 16 | 4096 | **49.39** |
| 4 | 4096 | 0.78 |
| 1 | 4096 | 0.90 |
| 8 | 32768 | **0.39** |

Thread-pool contention on sub-millisecond GEMMs dominates completely; the
default "use all the cores" is catastrophic for this shape of problem. The first
full run was projected at **66 hours** and finished in about **one**.

The trap is that the slow configuration looks like a physics problem. The natural
next moves — cut the epochs, cut the seeds, subsample the training set, declare
the reproduction infeasible on CPU and label it a scaled-down VARIANT — would all
have been wrong, and all would have been defensible in a write-up. **Before
concluding that an experiment does not fit the machine, profile one epoch across
thread counts and batch sizes.** It costs three minutes. For small models,
parallelise over seeds and models, never inside the GEMM.

## L-173. Re-run the generator and diff the artefact; the prose inside a generated document is not regenerated

`sst_baseline_metrics.py` was re-run from a clean invocation and its output JSON
came back **byte-identical** to the stored one (md5 `4fc917f2300bcada2fa6eb25f454e9b5`
before and after) — the strongest form of "this reproduces" a deterministic
script can give, for the cost of one command.

The same exercise found the limit of the check: the *tables* in the generated
`BASELINES.md` are correct, but its *prose* says "41 benchmark cases" and
"641,662 cells" where the JSON has 40 cases and the cell counts sum to 641,652.
Hand-written sentences inside a generated document are never regenerated and so
are never checked by re-running the generator. Either derive the sentence from
the data or expect it to drift — and note that the numbers a reader quotes are
usually the ones in the sentence, not the ones in the table.

## L-174. Write the falsifier so it can fire on the paper's own control, and name the numbers you cannot target before you start

Two preregistration habits that paid for themselves within the hour.

**The falsifier has to be the paper's own control.** Ling et al. compare their
tensor-basis network against a plain multilayer perceptron on identical inputs;
that comparison, not the RMSE, is their claim. Preregistering "if the plain MLP
equals or beats the TBNN, the invariance-embedding claim is not reproduced" lets
the experiment return a real negative. Preregistering only "beat the baseline
RANS model" cannot — and, per L-176, is satisfied by a constant.

**Name the numbers you cannot hit before you start.** None of Ling's nine flows
is on this machine, so their headline `b` RMSE of 0.13 on a duct at `Re_b = 2000`
is not a target — a fact that belongs in the preregistration, in bold, where it
cannot later be quietly reinterpreted as a target that was met. By contrast
Schmelzer et al.'s periodic hill at `Re = 10595` and curved step at `Re = 13700`
*are* our cases, and their errors are normalised by the k-omega SST baseline, so
those numbers are genuine targets. Sorting a reading list into "same case,
comparable number", "same method, different flow" and "neither" is a one-hour
exercise that determines what every downstream result is allowed to claim.

## L-175. State the a-posteriori gap as a capability fact, not a scope excuse

Three a-priori reproductions in this phase predict an anisotropy field and stop.
The honest sentence is not "a-posteriori propagation was out of scope"; it is
"**OpenFOAM v2606 is installed at `/usr/lib/openfoam/openfoam2606` and
`simpleFoam` runs on this machine, so stopping at a-priori scoring is a scope
decision, not a capability limit**". The first sentence is unfalsifiable; the
second tells a reader exactly what it would cost to finish and invites them to
ask why it was not done.

It matters more than usual here, because the map from `b` to `U` runs through the
momentum balance and is not monotone: a model that halves the anisotropy error
can still make the velocity field worse or fail to converge — the failure mode
the ill-conditioning literature was written about
(`Wu2018_rans_explicit_closure_ill_conditioned.pdf`, VERIFIED-PDF on disk,
arXiv:1803.05581v3). An a-priori improvement is not a weak version of an
a-posteriori improvement; it is a different claim. And when 6-15% of the
predicted cells are outside the realisable set, predicting that the solve would
diverge is not pessimism, it is the only defensible reading.

## L-176. Two agents with the same role, one filesystem: name your scratch artefacts after your instance

A second agent carrying the same role wrote `scratchpad/lessons_B.md` and
`scratchpad/numerics_B.md` — the exact filenames this instance had been told to
own — and **overwrote both**, losing a full set of entries that had to be
reconstructed from conversation context. It also joined
`cases/RANS_LES_closure_models/Kaandorp2020_TBRF/`, replacing that
directory's `PREREGISTRATION.md` with its own (better, more faithful) version
while this instance's run was still writing checkpoints beside it.

Nothing here was malicious and both bodies of work are good. The failure is
purely in naming and ownership: **a role name is not an identity**. Cheap guards,
all of which would have prevented it:

- Scratch artefacts get an instance-unique suffix, not just a role letter.
- A supervisor handing the same brief to two agents should partition the
  deliverable paths explicitly, or say plainly that the second is a replication.
- Before writing into a directory you did not create in this session, `ls -la` it
  and check the mtimes; a directory that changed five minutes ago has an owner.
- Append, never overwrite, for any file whose name you were *given* rather than
  chose.

## L-177. The third agent in three weeks was told to reproduce a paper the lab had already reproduced — and the record that says so was written by the second one

Assigned: run the SpaRTA reproduction (Schmelzer, Dwight & Cinnella 2020),
budget 20 core-hours, staged ceiling → discovery → a-posteriori. A repository
search performed *before* any solve found the whole thing already done, dated
**2026-08-01**: a purpose-built solver pair in `sdk/openfoam/sparta/`, two
preregistrations, ceiling and Table-2 campaigns in
`verification/campaign/W2_SPARTA_{FROZEN_CBFS,REGRESSION}.{md,json}`, and twenty
run directories in `verification/runs/W2_sparta_runs/`. Total prior cost:
**2.7 core-hours**.

Worse: `verification/campaign/W5_SPARTA_GATE_STATUS.md`, dated 2026-08-04,
records that **two approved docket items had already been filed demanding the
same already-completed work**, diagnoses the cause — *"nothing links a gate to
the record that satisfies it"* — and notes that the session which found this had
itself begun by treating the items as runnable work. This task was the **third**
occurrence, and the diagnosis had been sitting in the repository for nineteen
days.

A search costing about two minutes replaced a task budgeted at twenty
core-hours, and produced a *better* answer than a fresh run would have, because
the existing campaign carries preregistrations, graded bands, sign-flip control
experiments, and a solver validated to `6e-15` against an independent Python
implementation.

The guards, in the order they would have caught it:

- **Before writing code for a named paper, `find`/`grep` the repository for the
  paper's name, its method's name, and its case names.** Two minutes, every time.
  I wrote and compiled an entire OpenFOAM application before doing this.
- **A gate clause must name the record that satisfies it.** W5 identifies exactly
  this: an item whose gate is "reproduce X" should be closed by a pointer to the
  artefact, and the docket should refuse to serve an item whose gate already has
  one.
- **A completed campaign should register itself where the next agent will look.**
  Nothing in `cases/RANS_LES_closure_models/` or `docs/closure/` pointed at
  `verification/campaign/W2_SPARTA_*`; the closure work tree and the verification
  campaign tree do not cross-reference, and the collision lives in that gap.
- **Report prior art as a finding, not as an embarrassment.** The most valuable
  output of this task was a path, not a number.

## L-178. Delete your own duplicate, and record the deletion

Before finding the prior art I wrote, compiled and successfully linked an
OpenFOAM application implementing the same frozen-RANS extraction as the lab's
existing, validated `kCorrectiveFrozenFoam`. Leaving it in the tree would have
put two frozen-RANS solvers side by side — one validated to `6e-15` with twenty
run directories behind it, one written in half an hour and never run — with
nothing in either to tell the next agent which is which.

I deleted mine, source and binary. The rule that matters is the second half:
**a deleted artefact that is not recorded is a hidden action.** The deletion, its
reason and the surviving path are written into the reproduction's `RESULTS.md`
under a dated Departures heading. Sunk cost is not a reason to ship a duplicate;
silence about the sunk cost is a reason to distrust the record.

## L-179. Features moved the error by tens of per cent; the architecture moved it by a few. Spend the next hour on inputs, not on layers

Three anisotropy models, one split, one metric, on the eight held-out Closure
Challenge cases:

| Model | inputs | mean `b_rms` on the 7 in-domain test cases |
|---|---|---|
| tensor-basis random forest | **17 bounded flow markers** | **0.0448 - 0.2018** |
| tensor-basis random forest | 5 Pope invariants | 0.0788 - 0.2365 |
| tensor-basis neural network, 8x30 | 5 Pope invariants | 0.1105 - 0.2364 |

Swapping a 100-tree forest for an eight-layer network with the same five inputs
changes the answer by a few per cent, in both directions depending on the case,
and inside the seed spread on three of seven. Adding twelve bounded flow markers
to the same forest improves every case by **15% to 43%**, far outside the seed
spread of 0.0001-0.023.

This reproduces Kaandorp & Dwight's own conclusion — *"the introduction of extra
features has significantly more effect than the choice of neural-networks versus
random-forests"* [VERIFIED-PDF: arXiv:1810.08794v2, p. 36] — on different flows,
with a different feature list, against a third model they did not use. It is one
of the more transferable findings in the data-driven-closure literature and it is
almost always buried in a discussion section while the architecture gets the
title.

Two riders, because the win is narrower than it looks. The extra features did
**not** fix the out-of-family case (NASA hump: 208.6 with 17 features against
197.3 with 5, both catastrophically outside the realisable bound of 0.8165), and
they did **not** fix realisability (9.66% of test cells outside the barycentric
triangle against 10.2-11.4%, versus the truth's own 0.79%). **More features make
the model better where it already worked and no safer where it did not.** So:
spend the hour on inputs — and do not let the resulting improvement be read as
evidence that the model has become trustworthy outside its training envelope.

## L-180. "Report it" is not "gate on it" — and I moved my own goalposts to cover the gap

My preregistration for the TBNN reproduction listed four baselines, three
acceptance criteria, an explicit falsifier, and a section 8 requiring the
realisability violation fraction of the predicted anisotropy to be **reported
beside the truth's own**. It did exactly what it said. It also had a hole big
enough to drive an unphysical model through: **no criterion gated on
realisability.**

The measured result: the network put **6.5–15.3% of test cells** outside the
barycentric triangle — against 0.79% for the LES/DNS truth and 0.10% for the RANS
baseline — and reached `||b||_F ~ 1e7` on one case, against a realisable maximum
of 0.8165. On the preregistered ladder that model scores **7 of 8 against every
baseline** and is on track for a PASS.

What I then did was worse than the hole. I wrote **GATE FAIL** into the results
and justified it with a falsifier reading "model output must remain a physically
meaningful anisotropy" — a clause that appears nowhere in the preregistration. I
invented it after seeing the numbers. It felt defensible because it was *harsher*
than the registered ladder, and that is exactly why it was not: a preregistration
that can be tightened after the fact can be loosened after the fact, and the
reader has no way to tell which happened.

The correction, and the rule:

- **Score the run on the ladder as written, even when the ladder is wrong.** The
  honest verdict was PENDING (one criterion's control still training), not GATE
  FAIL.
- **Then say the ladder was wrong, in the results, as a finding about the
  preregistration.** "A model that is unphysical on an eighth of the domain can
  score a PASS here" is a more useful sentence than a retro-fitted failure.
- **Fix it in the NEXT preregistration, with the wording frozen before the next
  run.** Ours: *NOT A RESULT if the predicted `b` is non-realisable in more than
  3x the truth's own violation fraction on the same cells, or if `max ||b||_F`
  exceeds `sqrt(2/3)` by more than a factor of 2, regardless of RMSE.*
- **Generalise: every quantity a preregistration asks you to report is a
  candidate criterion.** Ask, for each one, "what value of this would make me
  disbelieve the result?" If there is such a value, it belongs in the ladder. If
  there is not, ask why you are reporting it.

The tell that something was wrong: I had written L-179 — *write the falsifier so
it can fire on the paper's own control* — an hour before I broke it. Writing the
lesson is not the same as being governed by it.

## L-181. The invariance embedding bought in-domain accuracy and bought out-of-domain catastrophe — and the unconstrained control was the only survivor

Ling et al.'s claim is that embedding Pope's tensor basis in a network makes it
generalise better than an unconstrained network on the same inputs. Run against
their own control on one split, four models, eight held-out cases:

| Model | 7 in-domain cases | the 1 out-of-family case (NASA hump) | cells outside the realisable set |
|---|---|---|---|
| tensor-basis RF, 17 features | **best on all 7** | 340 | 9.3-9.7% |
| tensor-basis RF, 5 invariants | 2nd-3rd | 197 | 10.2-11.4% |
| tensor-basis NN (TBNN) | 2nd-3rd | **1.48e+07** | 6.5-15.3% |
| **plain MLP, no basis** | **worst on all 7** | **0.3664** | **1.24%** |
| (k-omega SST baseline) | -- | 0.3318 | 0.10% |
| (realisable bound `sqrt(2/3)`) | -- | **0.8165** | -- |

Both halves are real. In-domain the embedding earns its keep: the TBNN beats its
own unconstrained control on **7 of 7** cases, by more than the seed spread on
**6 of 7**. Out-of-domain it is the *cause* of the failure: `b = sum g^(n) T^(n)`
is unbounded, the basis has numerical rank 3.24 on 2-D flows, and six or seven of
the ten coefficients multiply directions the training data cannot pin down. They
cancel in-distribution. They do not cancel outside it. The plain MLP has no such
directions — it regresses six components and its output is bounded by its own
last layer — so it is worse everywhere it interpolates and the only one still
usable where it extrapolates.

The seed spreads locate the mechanism exactly: the 17-feature forest's two seeds
agree to **0.0001-0.0013** in-domain — four significant figures — and to a
**factor of 2.3** on the hump. Reproducibility that collapses by four orders of
magnitude at the edge of the training envelope is not degraded accuracy; it is
the model reporting that those coefficients were never determined.

Three things follow for closure work:

- **A structural guarantee is not a safety guarantee.** Galilean invariance
  constrains the *form* of `b`. Nothing in the architecture constrains its
  *magnitude* or its eigenvalues. If you need realisability, project onto the
  barycentric triangle explicitly; do not expect the basis to do it.
- **Report the unconstrained control on the out-of-domain case, not just
  in-domain.** Had this study reported only the seven in-domain cases — the
  natural thing, since the hump is "obviously" out of distribution — it would
  have concluded the embedding is a clean win.
- **Seed spread is an extrapolation detector.** It costs one extra training run
  and it flagged the failing case without being told which case was failing —
  the same case the pre-registered Mahalanobis statistic flagged (13.2% of cells
  beyond the training 99th percentile, against 0-0.7% elsewhere). Two independent
  cheap diagnostics, same answer.

## L-182. A path is occupied until you have checked it is not, and a lost file lives in every transcript that ever carried its bytes, not only in Write calls

2026-08-20, cases/RANS_LES_closure_models/Kaandorp2020_TBRF/. Two sub-agents were assigned the same
paper one hour apart after a harness restart. The second wrote its tensor-basis random forest to
`tbrf.py` at 20:54:57Z without checking whether the path was occupied. It was: the first agent had
created `tbrf.py` at 20:50:27Z, `run_tbrf.py` imported it, and a training process that had loaded it
was running. The second agent then searched for the original, found no git blob (the directory was
untracked), found only its own bytecode in `__pycache__`, found no Write tool call in any transcript
carrying the source, and wrote a placeholder declaring the file "NOT RECOVERABLE".

It was recoverable. The first agent had written the file through a Bash heredoc, so its bytes sat in
the Bash command text of that transcript, not in a Write call. Searching all transcripts for the class
name (`TensorBasisRandomForest`) found it in seconds; the extracted file parses, exports what
`run_tbrf.py` imports, and was restored. The running process was never affected, because Python had
already loaded the module.

Two guards, both cheap:

- **Before any write to a path inside a shared case directory, test whether the path exists**, and
  read the tool's own signal (the Write tool says "created" or "updated"; a heredoc `>` says nothing,
  so `set -o noclobber` or an explicit `[ -e f ]` check does the job). A directory that two agents
  have been told about is shared by definition.
- **When a file is lost, search every transcript for the bytes themselves** - a class name, a
  distinctive comment, a constant - not for the tool that might have written it. Heredocs, `Edit`
  calls, `sed -i` invocations and `cat` outputs all carry source. The search that failed here looked
  for the wrong thing; the search that succeeded took one grep.

And one disclosure rule: a recovered file is **recovered**, and the recovery route is part of the
record. Here the extracted heredoc body hashed to 6799 bytes and the restored file to 6800: the
difference is the trailing newline a `cat > file <<EOF` heredoc always writes, so the restored file is
the heredoc's exact output, and no later `Edit` or `sed -i` on the path exists in any transcript. Write
that chain down - body hash, semantics of the writing tool, search for later edits - rather than
either asserting byte-identity bare or refusing to assert it when the evidence is in hand.

## L-183. A second moment is not a verdict: the same closure prediction was 156x worse than the baseline and better than it, depending on which statistic of the same error field was reported

The Kaandorp & Dwight 2020 TBRF reproduction preregistered
`b_rms_F = sqrt(mean ||b_pred - b_LES||_F^2)` as its metric, because that is the
convention `_common/BASELINES.md` uses for the k-omega SST comparator and the
comparison had to be apples to apples. On the curved backward-facing step the
16-feature forest returned `b_rms_F = 47.68 +/- 46.40` (5 seeds) against an SST
baseline of 0.3051. Read as a verdict that is a rout: the machine-learned closure
is 156x worse than the industrial model it is meant to replace.

The error field says something else. Its **median** is 0.170 — better than SST's
own `b_rms` of 0.319. Its p90 is 3.40 and its p99 is 153.9. The RMS is a report on
the tail, and the tail is **15.0 % of cells** whose predicted anisotropy violates
`||b||_F <= sqrt(2/3)`, a bound no realisable Reynolds stress can violate at all.
Projecting exactly those cells back onto the bound — a post-hoc rescaling that
adds no information — takes the RMS from 47.68 to **0.567**.

Neither number is wrong. "The model is 156x worse than the baseline" and "the
model beats the baseline in the median cell and is unbounded in a seventh of them"
are both true, and only the second one tells you what to fix. A single moment
cannot distinguish uniform mediocrity from a good model with a divergent tail, and
those two failures need opposite responses: retrain versus constrain.

Standing rule for this lab's closure work, now applied in
`Kaandorp2020_TBRF/RESULTS.md`: **report the median, p90, p99 and max of the error
field beside any RMS, and beside them the fraction of predictions that violate a
hard physical bound.** If a physical bound exists for the quantity — and for the
anisotropy tensor one does — the violating fraction is the first number, not a
footnote, because it is the one that predicts what happens in a solver.

The preregistered verdict still stands on the preregistered metric. It has to:
choosing the statistic after seeing which one flatters the model is the whole
reason preregistration exists. The distribution goes *next to* the verdict, not
in place of it.

## L-184. The stabiliser inherited from a sibling pipeline was the destabiliser, and the preregistration is what made that finding legible instead of embarrassing

`_common/tensor_basis.py` bounds the turbulent time scale below by Durbin's
`6 sqrt(nu/eps)`. It was written for the sibling TBNN reproduction, it is a
standard and defensible guard against `T -> 0` at a wall, and this reproduction
inherited it and **disclosed it as departure D2 in `PREREGISTRATION.md`, with the
stated reason "`k/eps` is unbounded in the low-`k` freestream"**.

That reason was wrong, and the departure was the single largest error source in
the run. `k/eps = 1/(0.09 omega)` is bounded wherever `omega` is; it is
`6 sqrt(nu/eps)` that diverges when `k` and `eps` vanish together. Worse, `k/eps`
is Reynolds-similar and `6 sqrt(nu/eps)` is not — it carries `nu` explicitly, so
it means something different on a non-dimensional periodic hill (`H = 1`) than on
a duct meshed in millimetres. The bound was the active branch in **72 % of duct
cells and 46 % of step cells** against 9-11 % of the training hills, and it
inflated the normalised time scale by up to **2500x** on the duct. A feature set
whose entire purpose is to make different flows comparable was being handed
features that were not comparable.

What made this recoverable rather than a silent bias:

- The departure was **written down before the run**, with its rationale, so when
  the results came back wrong the rationale could be checked and found false.
  An undocumented `np.maximum` in a helper module would have been invisible.
- The rationale was **falsifiable and cheap to test**: one script measuring which
  branch of the `max` is active, per case. Four minutes.
- The fix was run as a **labelled post-hoc diagnostic**, not swapped into the
  headline. The preregistered configuration keeps its verdict; the corrected
  configuration is reported beside it as "post-hoc, would have been". Relabelling
  the better run as the headline is how a tuned result gets published as a
  preregistered one.

The general shape: **a numerical guard copied from a neighbouring case is an
untested assumption about the new case**, and guards that mention a material
property (`nu`, `rho`, a length) rather than only the flow's own quantities are
the ones that break similarity between cases. Check which branch of every
`max`/`min`/clip is actually active, per case, and report the fraction.

## L-185. Reproducing a paper's headline contrast means reproducing its confound too, and the honest move is to run both arms

Kaandorp & Dwight's Table 3 is the evidence for the claim this lab flagged as F18
— that the feature set matters more than the model class. Their case C3 (5
features) and case C4 (17 features) are the two arms. But the paper states, in the
same paragraph, that C3 also used **fully grown trees and all features per split**
while C4 used **9 samples per leaf and 11 of 17 features**. The two arms differ in
the feature set *and* in the tree depth *and* in the split randomisation.

A reproduction has two defensible choices and they answer different questions:
run the paper's exact pair, and you reproduce a confounded contrast; hold
everything but the feature set fixed, and you test the claim the contrast is used
to support but no longer reproduce the paper.

We preregistered the second as the headline and the first as a secondary, said so
before running, and got numbers that differ: the paper-faithful fully-grown
5-feature configuration beat the depth-matched one on every held-out case. Had we
run only one arm we would have reported either "the claim reproduces" or "it does
not" with equal confidence and no way to tell which effect we had measured.

**When a paper's headline comparison changes more than one thing, say which one
you are testing, run both if they are cheap, and never let the choice be made
after the numbers are in.** Here both arms together cost under two core-hours.

## L-186. The session scratchpad is not a handoff channel: it was wiped three times in one day, and the only things that survived were the ones already in the repository

2026-08-21. The closure team's supervisor and two lanes used the session scratchpad
(`/tmp/claude-.../scratchpad/`) to pass drafts between agents: lesson and numerics drafts
awaiting review, the commit helper script, the verification flag list, the verbatim relay of
Sanaa's restart ruling, the recovered pre-patch copy of an overwritten source file. Another
workstream sharing the same session cleared and repopulated that directory mid-task. It was the
third overwrite on that path in a day; the first two were agents with the same role writing the
same filenames.

Nothing was lost, and that is the lesson rather than a consolation: every item that mattered had
already been committed (lessons L-145..185, the doctrine file, the incident record, the
pre-patch copy under its repository name), and every item that had not been committed was
reconstructable from an agent's context. The scratchpad held no unique bytes, by luck.

The rule, applied from that hour:

- **Drafts that another agent must read live under the case directory they belong to** -
  `<case>/aposteriori/LESSONS_DRAFT.md`, `NUMERICS_DRAFT.md` - and the supervisor commits from
  there. A draft in the repository tree is uncommitted but not unowned; a draft in `/tmp` is both.
- **Tools the team depends on live in the repository** (`_common/commit_private.sh`), and any
  state they need at run time (the private git index) lives under a path no session cleaner
  touches (`/home/ubuntu/closure-data/`).
- **A repository document never cites a scratch path.** The doctrine file, the incident record
  and the flag list all pointed at `/tmp/...` files; after the wipe those were dangling
  pointers inside committed history. The source a document cites must be as durable as the
  document.
- **The scratchpad is for one agent's own intermediates** - extracted text, run logs, a JSON it
  will read back in the same task - and nothing a second agent, or a later session, will need.

## L-187. A guarded branch in a differentiated routine can return an exactly zero derivative at the only state you ever evaluate at

2026-08-21, DAFoam team, Ladder A. IDWarp's `getRotationMatrix3d` guards a removable coordinate
singularity at `src/utils/vectorUtils.f90:58` with `tol = 1.4901161193847656e-08`, which is
`sqrt(eps)`. Tapenade's reverse mode, at `src/adjoint/outputReverse/vectorUtils_b.f90:123-128`,
takes that branch and zeroes `magv2b`, `axisb` and `axismagb` — so `dMi/dnormals = 0` **exactly**.
At an undeformed baseline `axisMag = sqrt(1e-30) = 1e-15 < tol`, so **branch 0 is guaranteed at
every non-corner surface node**, which is precisely the state every `check_totals` and every
design iteration 0 evaluates at. A1's aggregate gradient error is **11.4274 %** with component
idx6 sign-flipped at **640 %**; with the four-line analytic limit restored in the generated code,
**0.03796 %** and no flip. The upstream issue this answers, `mdolab/idwarp#57`, has been open
since 2021-07-14 with a `bug` label applied eight seconds after creation and **zero comments in
five years**.

Three transferable parts. **A guard that is numerically harmless in the primal can be fatal in
the derivative**: the primal is bit-identical either way (md5 `8fafe12f848af490a5041c865112b5fb`,
max difference 0.0), so no primal test can find this. **The failure hides at the baseline**, the
one point every verification harness evaluates, so it looks like a modelling error rather than a
branch. And **the repair belongs in the generated file, not the source**: patching
`vectorUtils.f90` would change the primal's floating-point path, so a proof-of-concept required
to leave the primal bit-identical must edit the Tapenade output — which is why the fix is a
patch and not a pull request. Ask of any differentiated code: *which branch does the baseline
take, and what does the reverse sweep do inside it?*

## L-188. A converged Krylov solve is a statement about the solver, not about the operator it solved

2026-08-21, DAFoam team, Ladder A rung A4. The Ahmed-body adjoint at np=4 under DAFoam's default
`scotch` decomposition finishes at `PetscConvergedReason: 2`, true residual **1.7e-07**, and
returns a gradient **8.95 %** from its own decomposition's finite difference. The same case, same
mesh, same design variable, decomposed `simple` 4x1x1, returns **0.00054 %**. The operator the
parallel reverse tape applies is not the transpose Jacobian: the mapped `scotch` adjoint vector
under the serial operator leaves a cross-residual of **328.8x ‖b‖**, against an np=1 floor of
1.141e-04. The effect is np-dependent — np=2 **0.26 %**, np=3 **6.05 %** — and the intuitive
hanging-node explanation is refuted backwards: `scotch` cuts **4 of 456** refinement-interface
faces and `simple` cuts **68**, and the 68-cut arm is the clean one.

Transferable: **convergence and correctness are different gates, and an iterative solver reports
only the first.** Any parallel adjoint number carries its decomposition method and subdivision in
the same table as the number, and a finite-difference reference measured at one rank count is not
a reference for another — this lab has a stored FD reference for one component that is
np=4-specific and was very nearly quoted as the case's. Verify serial first, then parallel, and
report both.

## L-189. The remedy a library hard-codes over is unreachable from its own options channel, and the log will not tell you

2026-08-21, DAFoam team, Ladder B rung B3. A wall-resolved separated case returns PETSc
`KSPConvergedReason = -9` at iteration 0 because the ASM sub-block **incomplete** factorization
hits an exact zero pivot; the same assembled matrix factors and solves under a complete LU with
pivoting at every pivot threshold. PETSc's own developers prescribe `-sub_pc_type lu` for exactly
this signature. It cannot be reached. `DALinearEqn.C` calls `KSPSetFromOptions` and then
overrides `-ksp_type`, `-pc_type` and `-sub_pc_type` at thirteen later call sites, and the
sub-block loop runs **after** `KSPSetUp` has applied the `sub_`-prefixed options, so last write
wins. Measured on a build that relocates `KSPSetFromOptions` to the end of the routine
specifically to let runtime options through: `-sub_pc_type lu` on the command line, and
**`PC Object: (sub_) … type: ilu`** in the same run's own `-ksp_view` dump. No "unused option"
warning, because the option *was* consumed — and then overwritten. Serial does not help either:
np=1 returns the same `-9`, matching an offline `scipy.sparse.linalg.spilu` result on the
assembled whole matrix with no MPI in the loop.

Transferable, and it is a diagnosability lesson rather than a numerics one: **a user who
diagnoses their own problem correctly still cannot act on the diagnosis, and nothing in the log
says so.** The library's own `printInfo` echoes the values it was *configured* with, so it
reports a solver that did not run. When a documented remedy appears to do nothing, dump the
effective object — `-ksp_view`, `PCView`, `KSPGetType`/`PCGetType` after the options call — and
compare it against what you asked for. An upstream fix that only relocates the options call
**would look like a fix and would not be one**.

## L-190. A finite-difference plateau is a per-component property, and a gate without a wrong-step control is not a gate

2026-08-21, DAFoam team. Twelve invocations on a 4,032-cell case, one step varying and nothing
else, gave a full-vector error against step of **94.95 / 52.88 / 17.64 / 12.27 / 11.52 / 11.43 /
10.47 / 8.94 / 4.28 / 9.83 %** from 1e-8 to 3e-2, with the primal itself failing at 5e-2 and
1e-1. The 4.28 % dip is not a minimum: it is one component whose estimate is sign-flipped and
unstable at every other step, crossing the adjoint's magnitude once on its way to +110 %.
Excluding the three flagged components the curve is **dead flat at 2.5-3.0 % from 1e-4 to 3e-2**,
cosine 0.99998. Separately, the same lane's registered wrong-step control — the identical probe
at a step deliberately an order out — returns **132.75 %** where the real probe returns 0.038 %,
and a neighbouring gate scored on the *baseline* gradient alone, an array with no result in it,
returned **35.38 %** against the hypothesis's achieved 26.86 %: the trivial baseline beat the
hypothesis.

Three transferable parts. **Read the plateau per component**, because a vector norm can dip for
reasons no component supports. **Run the sweep at the tolerance the graded run uses**: at a loose
primal tolerance the same three probes missed by a systematic `fd/adj ~ 0.7` — 25.9 / 32.0 /
32.2 % — and one pair re-run two decades tighter went **25.9 % -> 0.032 %**, so the step was
never the problem. And **register the wrong-step control before its own run**, because a gate
that returns the same verdict for the hypothesis and for a deliberately broken version of it is
reporting, not measuring.

## L-191. Predict the memory envelope before the adjoint launches, and name the container the number came from

2026-08-21, DAFoam team. A 579,072-cell adjoint was graded **BLOCKED** from a prediction of
**94.7-116.0 GiB against a 30 GiB box** rather than from an out-of-memory death — the verdict
cost nothing and is more informative than an OOM would have been, because it also names the
independent conditioning blocker beside it. The opposite error is on the same record: a smaller
adjoint that works at 63,920 cells and fails at 79,560 **with over 4 GB of headroom unused** is
bound by convergence, not RAM, and a hardware recommendation was once made in the wrong
direction on that confusion. And a run ended by a `docker stop` on a shared box at
`MemAvailable` 1.62 GB was reported as a boundary until the record was corrected: **no PETSc
memory error was ever on that run's log**, and the causal claim was withdrawn.

A fourth part, learned today and cheap to repeat: the measured peak for a 21,000-cell
complete-LU adjoint is **9.044 GiB**, comfortably inside a 12 GiB cap — against a **22 GiB** cap
that earlier runs were given and that had been carried ever since as if it were a requirement.
Nobody had measured it. **And the raw maximum in the same watcher log was 9.786 GiB, which
belonged to a different lane's container**: `docker stats` reports every container on the box,
so a peak-RSS figure is a claim about a *named* container or it is not a measurement.

## L-192. An optimiser that stops on a wall clock or an iteration cap has not converged, whatever its objective did

2026-08-21, DAFoam team, Ladder A rung A2. A real IPOPT 3.13.5 / MUMPS / limited-memory-BFGS run
completed **47 of a possible 100 major iterations inside a 60-minute box** and reduced drag
**28.275488 %** at matched lift. The extracted history is sound and its primary source is hashed.
What the log does not contain is a result: `converged_to_optimizer_tolerance: false`,
`convergence_statement_in_log: null`, and IPOPT prints no EXIT line anywhere — *"the table simply
stops after iteration 47."* The lab's standing picture had recorded that no optimiser had ever
run; the true statement is the weaker and more useful one, that **no optimiser run has ever
converged**.

Transferable, and it generalises past optimisers: a solver's iteration cap is a budget, not a
settle criterion, and the two are recorded differently or the ladder inherits a guess as a
measurement. A time-boxed optimisation is graded on its registered intermediate threshold, never
on the size of the improvement it happened to reach. **And verify the gradient at the design
point the optimiser stopped at, not only at the baseline** — the two AD defects this lane has
characterised behave differently at and away from the undeformed state, so a baseline
verification says nothing about iteration 47.

## L-193. When a session is stopped mid-task, the pre-registration is what makes the work resumable — and an uncommitted results file is what makes it verifiable

2026-08-21, DAFoam team, both lanes. Two lanes were stopped mid-run. What survived was: a
committed pre-registration fixing every arm's prediction *before* its run, a run root outside the
repository holding `ledger.csv`, per-arm logs and staged case directories, and a partial results
file that had deliberately **not** been committed because its numbers were not yet checked
against the logs. A fresh lane picked all of it up, re-derived every carried figure at a stated
`path:line`, found one real error — a provenance list crediting three arms where five had the
property — corrected it, re-ran the two unfinished arms exactly as registered, and completed the
record. **Zero scientific loss**, and no argument about what had been predicted, because the
predictions were on disk and frozen.

Two transferable parts. **The pre-registration is the handoff document**: it is the only artefact
that survives a stop with its meaning intact, since anything written after the numbers are seen
can be argued with. And **holding a partial result out of the index is a feature, not
untidiness** — the commit that preserved the frozen predictions said so in its own message, and
it is what let the next lane treat every number as unverified until it had checked it. Also
worth carrying: name a re-run's superseded log rather than overwriting it
(`*_attempt1_HARNESS_KILLED.log`), so the waste stays inside the cost figure.

## L-194. A rate read off a redirected log is not a measurement; the completed run's wall time is

2026-08-21, DAFoam team, Ladder B. A four-rank solve on a contended box appeared, from counting
solver lines that reached its redirected log over a wall-clock window, to be running about
**400x** slower than its registered basis. That figure was written into a results section and
then corrected within the hour: the run completed, and its own wall time gives **1,529 s against
a registered 71 s — a factor of 21.5**. Output through `docker run > file` is block-buffered, so
the log lags the solver in bursts and a short-window line count under-reads the true rate badly.
The mechanism behind the real slowdown stands and is worth its own note — Open MPI spin-waits, so
one rank descheduled by an unpinned co-tenant stalls the other three at full apparent CPU, and
**`--cpuset-cpus` constrains where a container's threads may run, not who else may run there** —
but its size was overstated by a factor of nearly twenty.

Transferable: when you need a rate, take it from a completed run, from the application's own
internal clock, or from `/proc/<pid>` counters — never from the growth of a buffered stream. And
when a degradation figure is load-bearing in a record, say which of those three it came from.

## L-195. Report the comparator you can defend, not the one that is lying around

The obvious comparator for an a-posteriori closure test is the benchmark's own
shipped baseline field. Measured here, that field is not converged to the
standard the test itself uses: restarting it with zero corrections gives an
initial streamwise-momentum residual of **1.6e-3** on `AR_1_Ret_360` and
**9.3e-4** on `AR_3_Ret_360`, because those cases stopped on a `residualControl`
listing only `k` and `omega` (`k 5e-6; omega 1e-10;`) and never constrained `U`
or `p` at all.

Scoring an injected run against that field silently credits or debits the model
with the benchmark's own convergence gap. The fix is one extra run: a NULL
configuration with zero corrections under the **identical** solver, mesh copy,
stopping rule and iteration cap, used as the comparator, with `NULL - BASE`
reported once as a named quantity so the gap is visible rather than absorbed.

The generalisation: **before using a published or shipped field as a baseline,
restart it under your own stopping rule and read the first residual.** It costs
one iteration to find out whether the number you are about to compare against
means what you think it means.

## L-196. A gate that contains no solve cannot be invalidated by a convergence argument

Mid-task a reviewer warned that a gate of the form "zero-correction re-solve vs
the shipped field, rel-L2 < 1e-10" would fail spuriously, because the shipped
fields are not converged to 1e-10 — a correct warning, and one that had already
bitten the parallel lane.

It did not apply. The gate under review was **pure algebra on the injected
field**: reconstruct `b_total = b_RANS + bijDelta` from the shipped `nu_t`, `k`,
`S` and check it equals the model's own prediction. No solver, no iteration, no
sensitivity to convergence at all. It passed at **1.24e-16**.

Two things worth carrying. First, when a review lands, check whether it describes
the artefact you actually built before acting on it; adopting a correction to a
different design would have meant reporting a non-existent defect. Second — and
this is why the exchange was still worth having — the reviewer's *additional*
gates were genuinely better than mine at what they tested (that the corrected
solver is inert at zero correction, verified here as **bit-identical** over 200
iterations), so the right response was to keep my gate, adopt theirs, and say
plainly which tested what.

## L-197. Register a ceiling configuration, or your model will be blamed for the injection path

This lane set out to test whether a random forest's a-priori anisotropy gain
(`b_rms` 0.4138 -> 0.2213, a clean PASS) survives being solved. The
preregistration required a **TRUTH** configuration alongside it: inject the
*exact* anisotropy `b_LES - b_RANS` and see what the solver does with a perfect
prediction. It also registered, in advance, that a TRUTH row failing to cut
`U_rms` by 50% makes the case NOT A RESULT, and that a TRUTH row *worse* than the
baseline voids every ML row.

Both fired. Injecting the true anisotropy made `U_rms` **57-63% worse** on all
three cases. Without that configuration the ML rows - `U_rms` up 57-63%, `b_rms`
down by a factor of 5 - would have read as a devastating verdict on the model.
The model was never the problem: with `kDeficit = 0`, transported `k` collapses
to a third of baseline, so the realised stress `2k(b_lin + b^Delta)` is wrong by
that factor however good `b^Delta` is.

The general shape: **when you test a component through a pipeline, put the
pipeline's own perfect-input case in the preregistration as a gate, not as a
nicety.** It costs one extra run. Without it you cannot tell "the model is bad"
from "the harness cannot express what the model produces", and the first
explanation is always the more available one. Two supporting habits: register the
threshold *before* seeing the ceiling number, so the gate cannot be argued away
afterwards; and find an independent control that isolates the harness - here, the
lab's own W2 campaign putting `b^Delta` **and** `R` through the *same solver* to
reach the published `eps(U)/eps(U_0)` = 0.00165 (the lab's own W2 measurement: 0.003331, clearing the registered < 0.005 band) [dated correction 2026-08-21: originally quoted '0.0017' as the lab's own number], which proves the path is sound and the `b`-only
configuration is what fails.

The finding that survives is sharper than the one the lane set out to get: an
a-priori `b_ij` score bounds nothing about the solved field, and a closure that
predicts `b_ij` alone cannot be propagated without either a k-correction or a
frozen `k`. That is a statement about a whole class of data-driven closures, and
it came from the control, not the treatment.

## L-198. A 110-feature "maximal" library had rank 96 on the flow family it mattered most for

FS1 built the maximal set the doctrine asks for: Wu, Xiao & Paterson's 47
minimal-integrity-basis invariants of `{S, Omega, A_p, A_k}` under two
normalisations, eleven scalar flow markers, and Pope's five — **110 features**,
nothing selected. FS2 then measured what is actually there:

| family | rank / 110 | algebraically-zero features | condition number |
|---|---|---|---|
| ducts | **96** | **48** | 1.2e33 |
| hills | 100 | 22 | 2.2e17 |
| CBFS | 100 | 25 | 2.0e18 |
| hump | 100 | 44 | 2.8e18 |
| pooled | 100 | 12 | 3.3e17 |

**No family reaches full rank, and on the ducts nearly half the library is
identically zero.** The reason is the same one that collapses Pope's ten-tensor
basis to rank 3-4 (measured here: case means **3.006-3.987**, never above **5**):
every case in this benchmark is a statistically two-dimensional mean flow, and
high-order invariants of three or more tensors vanish.

The practical consequences are sharper than "some features are useless". A
regressor handed 110 columns on duct data is working in a space **14 dimensions
smaller than it thinks**, with a condition number of `1e33`; any L1 path,
mutual-information ranking or permutation importance computed there is
partly ranking noise directions. And a feature that is dead *here* is not dead in
general — the twelve pooled-dead invariants would revive on a three-dimensional
flow, which is exactly why a model fitted on this benchmark cannot be trusted off
it.

**Run the degeneracy audit before the selection method, not after.** It costs
minutes and it changes what the selection method is allowed to claim.

## L-199. A relative-zero threshold across incommensurable features declared 105 of 110 features dead, confidently and wrongly

The first FS2 pass flagged a feature DEAD if its maximum absolute value fell
below an absolute floor **or** below `1e-12` times the largest value anywhere in
the feature matrix. That second clause is standard practice and it was
catastrophic here: the Pope invariants under the Durbin-bounded normalisation
reach `|lam3| = 1.5e11` and `|lam5| = 1.5e14`, so the "relative" threshold
evaluated to **150**, and every bounded feature in the library — all eleven `q`
markers, every normalised invariant, 105 of 110 — was reported algebraically
zero.

The output looked entirely plausible: a long list of feature names under a
correct-sounding heading. It was caught only because five of the names were the
`q` markers, which are bounded in `[0, 1]` by construction and *cannot* be near
zero — a sanity check that came from knowing what the features were, not from
the numbers.

**A relative tolerance presumes a common scale.** In a maximal feature library
there is deliberately no common scale — that is what "maximal" means. Use an
absolute test for "is this identically zero", a per-feature relative test for "is
this near-constant", and never a global-max normaliser across features with
different units. The corrected audit records the bug in its own output rather
than quietly fixing it.

## L-200. A paper's Galilean-invariance proof can be correct and its steady-state implementation still not invariant

Wu, Xiao & Paterson normalise the pressure gradient by `rho |DU/Dt|` (Table 1,
p. 8) and devote Appendix C to showing the feature set is Galilean invariant.
The argument is correct — for the **unsteady** material derivative
`DU/Dt = dU/dt + U.grad U`, where the unsteady term supplies exactly the shift
that cancels the boost.

A converged steady RANS field has no `dU/dt`. The only implementable normaliser
is `|U.grad U|`, which is **not** boost-invariant. Measured on `CBFS13700` with a
boost of `0.37, -0.21, 0.13` times the mean speed: **58 of 110 features move, by
up to a relative 2.0**, and every one of them either contains `A_p` (53) or uses
the raw velocity (5).

This is not an error in the paper and it is not a bug in the code; it is a
property of the steady-state setting that the paper's proof does not cover.
Two habits follow. **Measure invariance on your own implementation rather than
inheriting the claim** — a boost and a rotation applied to one stored field cost
one script. And **when a normaliser is only invariant in the unsteady form,
either say so at the definition or drop the term**: our library keeps it and
flags all 58 by name, because a feature that is useful and non-invariant is a
legitimate choice and a feature that is silently non-invariant is not.

The measurement independently reproduces Kaandorp & Dwight's own annotation
(Table 1 footnote, p. 25): *"Features marked with dagger are rotationally
invariant but not Galilean invariant."* Their five daggered markers are exactly
the five this check flags.

## L-201. Two audits that overlap catch each other's artefacts

The invariance check reported three features exceeding the rotation tolerance —
apparently a failure, since a trace of a rotating product is invariant by
construction. It was not. `trW2SWS2` has a maximum absolute value of **2.6e-18**
across the whole field: it is algebraically zero on a two-dimensional flow, so
the relative measure was dividing float64 roundoff by zero. The third,
`q8_kConvection` at `3.3e-12` for an O(1) feature, is at the tolerance itself.

The degeneracy audit had already flagged `trW2SWS2` as DEAD. **The FS2 result
explained the FS1 anomaly**, and neither audit alone would have resolved it:
invariance testing normalises by a scale that degeneracy testing is designed to
find is zero.

Keep the two adjacent, run them on the same library in the same session, and
**check the magnitude of anything that fails a relative test before calling it a
failure**. The general form: a relative error on a quantity that is identically
zero is not an error measurement, it is a division by zero with extra steps.

## L-202. Three independent instruments agreed on the same case, and none of them needed a model

The NASA wall-mounted hump is out-of-family by every instrument the charter
requires, all measured before any training:

* **Mahalanobis distance** (charter 5a): **13.17%** of cells beyond the training
  p99, against 0.00-0.70% for the other seven test cases.
* **FS5 range coverage** (charter 22.5): **31.79%** of cells outside the training
  range on at least one feature, with **49 of 110** features going out of range —
  against 0.00-0.06% on the hills and 0.96-3.07% on the ducts.
* **Tensor-basis rank** (charter 5b): rank never exceeds 5 of 10 anywhere, so
  `g^(6..10)` are unconstrained the moment a flow leaves the 2-D family.

And every tensor-basis model trained on this benchmark blew up on exactly that
case, by factors of `1e2` to `1e7`.

**The instruments fired before the failure, on data alone.** That is the argument
for making them standing gates rather than post-mortem tools: three cheap,
model-free measurements identified the case that would break four different
models, and they agreed with each other.

## L-203. A second moment is not a verdict: the same closure prediction was 156x worse than the baseline and better than it, depending on which statistic of the same error field was reported

The TBRF reproduction preregistered `b_rms_F = sqrt(mean ||b_pred - b_LES||_F^2)`,
because that is the convention `_common/BASELINES.md` uses for the k-omega SST
comparator and the comparison had to be apples to apples. On the curved
backward-facing step the 16-feature forest returned **47.68 ± 46.40** (5 seeds)
against an SST baseline of **0.3051**. Read as a verdict that is a rout.

The error field says something else. Its **median is 0.170** — better than SST's
own `b_rms` of 0.319. Its p90 is 3.40 and its p99 is 153.9. The RMS is a report on
the tail, and the tail is **15.0 % of cells** whose predicted anisotropy violates
`||b||_F <= sqrt(2/3)`, a bound no realisable Reynolds stress can violate at all.
Projecting exactly those cells onto the bound — a rescaling that adds no
information — takes the RMS from 47.68 to **0.567**.

Neither number is wrong. "156x worse than the baseline" and "beats the baseline in
the median cell and is unbounded in a seventh of them" are both true, and only the
second tells you what to fix: retrain versus constrain.

**Standing rule: report the median, p90, p99 and max of the error field beside any
RMS, and beside them the fraction of predictions violating a hard physical bound.**
Where a physical bound exists — and for the anisotropy tensor one does — the
violating fraction is the first number, because it is the one that predicts what
happens in a solver. The preregistered verdict still stands on the preregistered
metric; the distribution goes next to it, never in place of it.

## L-204. The stabiliser inherited from a sibling pipeline was the destabiliser, and the preregistration is what made that finding legible instead of embarrassing

`_common/tensor_basis.py` bounds the turbulent time scale below by Durbin's
`6 sqrt(nu/eps)`. It was written for the sibling TBNN reproduction, it is a
standard guard against `T -> 0` at a wall, and this reproduction inherited it and
**disclosed it as departure D2 with the stated reason "`k/eps` is unbounded in the
low-`k` freestream"**.

That reason was wrong, and the departure was the largest single error source in the
run. `k/eps = 1/(0.09 omega)` is bounded wherever `omega` is; it is
`6 sqrt(nu/eps)` that diverges when `k` and `eps` vanish together. Worse, `k/eps`
is Reynolds-similar and `6 sqrt(nu/eps)` is not — it carries `nu` explicitly, so it
means something different on a non-dimensional hill (`H` = 1) than on a duct meshed
in millimetres. The bound was the active branch in **71.8 % of duct cells and
46.0 % of step cells** against 8.9-11.3 % of training hills, inflating the time
scale by up to **2500x**. Removing it moved the held-out duct from
`b_rms_F` = 6.382 ± 2.110 to **0.3160 ± 0.0080**.

What made this recoverable rather than a silent bias: the departure was **written
down before the run with its rationale**, so when results came back wrong the
rationale could be checked and found false; the rationale was **falsifiable in four
minutes** (measure which branch of the `max` is active, per case); and the fix ran
as a **labelled post-hoc diagnostic**, not swapped into the headline.

**A numerical guard copied from a neighbouring case is an untested assumption about
the new case**, and guards that mention a material property (`nu`, `rho`, a length)
rather than only the flow's own quantities are the ones that break similarity
between cases. Check which branch of every `max`/`min`/clip is actually active,
per case, and report the fraction.

## L-205. Reproducing a paper's headline contrast means reproducing its confound too, and the honest move is to run both arms

Kaandorp & Dwight's Table 3 is the evidence for the claim flagged as F18 — feature
set matters more than model class. Their case C3 (5 features) and C4 (17 features)
are the two arms. But the same paragraph states that C3 also used **fully grown
trees and all features per split** while C4 used **9 samples per leaf and 11 of
17 features**. The two arms differ in the feature set *and* the tree depth *and*
the split randomisation.

A reproduction has two defensible choices answering different questions: run the
paper's exact pair and reproduce a confounded contrast, or hold everything but the
feature set fixed and test the claim the contrast supports. We preregistered the
second as headline and the first as secondary, said so before running, and got
numbers that differ — the paper-faithful fully-grown 5-feature configuration beat
the depth-matched one on every held-out case. Run only one arm and you report "the
claim reproduces" or "it does not" with equal confidence and no way to tell which
effect you measured. Both arms cost under two core-hours.

---

# SECTION B — from the a-posteriori lane (`RESULTS.md` in this directory)

## L-206. The truth-injection ceiling is the cheapest experiment in a closure lane and it is the one that fires

The lane preregistered a gate before grading any model: inject the **true** LES
anisotropy into the solved momentum equation and require it to cut the velocity
error by at least 30 %; if it does not, the propagation path is broken and every
model number downstream is NOT A RESULT.

It fired. On the held-out square duct, injecting the true anisotropy took `U_rms`
from the SST baseline's **0.1985** to **0.3215** — a 62 % *increase*. The
machine-learned correction, on the same path, gave **0.2594 ± 0.0007**: worse than
the baseline, but **better than injecting the truth**. Without the ceiling
configuration that pair of numbers is unreadable, and the temptation is to report
"the ML correction degrades `U` by 31 %" as a fact about the model. It is a fact
about the propagation.

The ceiling cost **8.5 seconds of CPU**. It is one extra configuration in a lane
that ran nineteen. **Any lane that propagates a learned correction should run the
truth injection first and grade nothing until it passes.**

## L-207. An omitted correction term is not a neutral simplification: dropping R collapsed k by 67 % and inverted the ceiling

Why the ceiling failed was registered in advance as a risk and then measured. The
TBRF predicts `b` and nothing else, so the k-equation correction `R` was set to
zero — a registered choice with the registered consequence "our ceiling is a
b-only ceiling and is necessarily weaker than Schmelzer's".

"Weaker" turned out to be "inverted", and the mechanism is one number.
Injecting `b^Delta` changes the k-production term by
`Gextra = -2 k (b^Delta : grad U)`, which on this flow is strongly negative. With
no `R` to balance it, `k` collapses: mean `k` fell from the SST field's **26.68**
to **8.74** under truth injection and to **0.128** under the train-mean injection,
against an LES truth of **43.42**. `nu_t` follows `k`, the effective viscosity
collapses with it, and the momentum correction `2 k b^Delta` shrinks toward zero
at the same time. Schmelzer's `b^Delta` and `R` are not two independent
corrections you can take one of.

**Registering the omission was necessary and was not sufficient.** The registration
predicted a weaker ceiling; it did not predict a sign change. The lesson is to
measure the quantity the omitted term controls — here `k` — in the truth
configuration, and to treat a 3-to-200-fold departure in it as a stop condition,
not as context.

## L-208. A convergence criterion has to be checked against the flow it will be applied to, and a periodic duct will break the obvious one

The lane registered "converged iff the initial residuals of `p` and `Ux` are both
below 1e-6, sustained 100 iterations". On the streamwise-periodic square duct with
a `meanVelocityForce`, that criterion **cannot be satisfied by a perfectly
converged field**: the cross-plane pressure is nearly uniform, so OpenFOAM's
residual normalisation divides by a near-zero scale and the `p` initial residual
sits at **0.14 after 30,000 iterations** on the zero-correction control — whose
`Ux` residual is **8.4e-16** and whose RMS `div(U)` is **6.1e-18**. The field has
not moved; the residual is an artefact of the normaliser.

Two further traps in the same family, both hit: the duct's baseline has
`Uy, Uz ~ 0`, so their initial residuals are **O(0.3) at restart even with zero
corrections** (this one *was* caught before registering and the components were
excluded); and a solver that stops at first satisfaction of its own
`residualControl` can never demonstrate a criterion phrased as "sustained for 100
iterations", so the registered criterion and the stopping mechanism were mutually
unsatisfiable.

**Before registering a residual-based convergence criterion, run the
zero-correction control and read its residuals.** Register the field-movement
fallback as primary for any flow whose driving pressure gradient is a source term
rather than a boundary condition.

## L-209. Register a threshold only after measuring what the instrument can resolve, on a field you already trust

The lane registered "RMS `div(U)` normalised by the field's own gradient scale
below 1e-3 for every re-solved configuration", against this lab's published
post-hoc figures of 10.5 % and 9.7 %. On the two ducts it held with room to spare
(6.1e-18 for the zero-correction control, 3.8e-4 for the worst injected case).

On the curved backward-facing step it is **unmeasurable**. The divergence is
computed from a curvilinear chain-rule gradient, and on that mesh the estimator
returns **5.2e-3 for the shipped converged SST field and 4.3e-3 for the LES
truth**. Both of those fields are divergence-free to the precision of the solver
and the experiment respectively; the number is the estimator's floor, not the
field's continuity error. **A threshold of 1e-3 on that mesh cannot be met by any
field, including the two references.**

The calibration cost one script and no solves: *run the estimator on fields whose
answer you already know*. The shipped baseline and the LES truth were both sitting
in the case directory the whole time. Do that before writing the number into a
preregistration, and register the threshold per case — the same instrument was
exact to round-off on the ducts, because a fully-developed flow has no streamwise
derivative to discretise, and three decades short on the step.

The consequence for the record is small and specific: H5 is graded on the ducts
and reported as **NOT MEASURABLE** on the step. The consequence for the next
preregistration is that every registered tolerance now needs a line saying what
was measured to justify it.

## L-210. A runtime knob that reaches the factorisation can still be the wrong lever — exact singularity is not perturbation-fixable

DAFoam's adjoint on a wall-resolved separated case fails at GMRES iteration 0 with
PETSc `-9`, caused by an exact zero pivot in the ASM sub-block **incomplete** LU. The
obvious cheap remedy is PETSc's own diagonal-shift machinery, set from the command
line: `-sub_pc_factor_shift_type nonzero`, `-sub_pc_factor_shift_amount`,
`-sub_pc_factor_levels`. Five arms were pre-registered and run
(`cases/dafoam/ladder-b/B3/ilu_shift_runtime/`). **All five returned `-9`, and every
arm's `-ksp_view` dump came back byte-identical to the control's.**

**Two distinct failures were being conflated, and separating them is the lesson.**

*The first is diagnostic.* The logs all print `using diagonal shift to prevent zero
pivot [NONZERO]`, which reads like proof the option landed. It is not: **the control
arm, which set no shift option at all, prints the same line**, because the application
already calls `PCFactorSetShiftType(..., MAT_SHIFT_NONZERO)` itself. The
pre-registration had flagged that row as non-discriminating *before* the runs, and the
misreading happened anyway between the run and the scoring. **A banner that both arms
emit is not an instrument.** The row that actually graded the class was the one where
the requested value and the application's value differ visibly: fill levels 2 was
requested and `1 level of fill` was deployed. **Design at least one arm whose dump
cannot come out the same either way, and grade on that one.**

*The second is numerical, and it is the transferable half.* Shift type, shift amount at
two magnitudes, and extra fill are all **perturbations of an incomplete factorisation**.
Offline, `scipy.sparse.linalg.spilu` returns `Factor is exactly singular` at every
drop-tolerance and fill setting swept, while `splu` — complete factorisation with
pivoting — solves at every pivot threshold. **A perturbation of a singular factor is a
different singular factor.** And the one factor option the application does *not* set,
`zeropivot`, **does** reach the deployed factor — verified in the dump, raised six
decades — and still fails. So the runtime axis closed from both ends at once: *the knob
that lands does not help, and the knobs that would have helped cannot land.*

**The general rule: before buying a tuning sweep, ask which failure mode the knob
perturbs, and whether the measured failure is of that mode.** "Exactly singular" and
"nearly singular" look alike in a log and are different problems; only the second is
reachable by a tolerance. Here a rebuild changing one line — complete LU in the
sub-block — is the minimum working intervention, and every cheaper route (serial,
runtime PC type, runtime factor options) is now measured and blocked. **The sweep was
still worth its 34 core-min, because it converted "we have not tried the shift" into a
row that closes an axis** — but it was worth it as a *closure*, priced as one, not as a
candidate fix.

## L-211. Read the solver before designing the experiment: both registered options were unavailable, and the evidence took ten minutes

The task registered two injection paths. Neither existed. `kOmegaSSTCorrected`
has **no freeze switch** — the class overrides `read()`, `correct()` and the two
`divDevReff` variants, and `correct()` unconditionally solves both transport
equations. `kOmegaSSTFrozen` overrides only `correct()` and `verifyKEquation()`
and **does not override `divDevReff` at all**, so the `tauij` field it
`MUST_READ`s never reaches the momentum equation — it feeds the omega production
and a diagnostic output, nothing else. Running `simpleFoam` with it would have
solved `U` against a plain Boussinesq stress and produced a confident, entirely
wrong answer to a prescribed-stress question.

Ten minutes of `grep` on the class definitions turned "run this" into "here is
the exact gap and a costed 120-line derived class". The rule that produced it:
**before designing around a component, read what it overrides, not what its
documentation says it does.** An inherited method is the easiest thing in C++ to
assume you have changed.

## L-212. Deriving a class to skip work also skips the work you forgot it was doing

`kOmegaSSTCorrectedFrozenK::correct()` deliberately does not call the parent's
`correct()`, because that is where the `k` and `omega` equations are solved. It
is also where `tauijRecon` — the reconstructed Reynolds stress the parent writes
for scoring — is assembled. The frozen model therefore ran correctly and wrote
`tauijRecon = uniform (0 0 0 0 0 0)` in **every one of eighteen** arm-S
configurations.

The physics was untouched: `divDevReff` uses `bijDelta_` and `k_` directly, and
the injected stress demonstrably reached momentum (`max|U_truth − U_null| = 8.89`
on the duct) with `k` exactly frozen (`max|Δk| = 0.000e+00`). Only the diagnostic
was lost, and the fix was to reconstruct `b_total = −(ν_t/k)S + b^Δ` in
post-processing from fields that were written.

Two habits. **When you override a method to remove behaviour, enumerate
everything else that method did** — side effects on registered fields are
invisible at the call site. And **let the scorer fail loudly rather than
defensively**: this was caught because reading a uniform field raised an
`IndexError`, not because anything checked. A scorer that silently substituted
zeros would have reported a beautifully realisable `b` of exactly zero.

## L-213. A case copy is not a case: shipped truth fields can be macros, and they fail at startup, silently, in bulk

Arm L freezes `k` at `k_LES`. The build script copied `0/k_LES` and renamed the
object. **All eighteen arm-L runs died in one second**, because the benchmark
ships that field as `#include "interpolatedFields/k_internalField"` and the
include target was not in the copy. They exited `rc=1`, wrote `log.solve.done`
like any completed run, and produced no time directory — so the arm looked
*finished* to a status check that counted `.done` files.

It surfaced only when the scorer reported `NO OUTPUT TIME DIR` for twelve
consecutive rows. The fix was to resolve the macro through the reader that
already handles it and write a plain field into the **shipped `k` file's**
header and boundary conditions, so the frozen field keeps valid BCs.

**Check exit codes, not just completion markers**, and **when a copied case reads
a field the original resolved through a macro, resolve it at copy time.** The
general form: a file that is an instruction rather than data will not survive
being moved.

## L-214. Verify a review's premises before acting on them — one was false and the other would have hidden the real defect

A review asked for two changes to a committed record: add `div(U)` rows that
"the RESULTS file reports not at all", and grade CBFS continuity **NOT
MEASURABLE** because a chain-rule `div(U)` estimator floors at ~5e-3 on that mesh.

Checked: the file already carried a `continuity` column on **every** case ×
configuration row. And the floor, though real for the chain-rule estimator
(measured here: **9.88e-03** on the CBFS shipped field, **6.83e-03** on the LES
truth), does not apply to the instrument that lane used — OpenFOAM's own discrete
`sum local` continuity residual, which reads **1.45e-13** on the same field, eight
orders of magnitude lower, because it is a flux balance over real cell faces
rather than a finite-difference reconstruction on a curvilinear index space.

Adopting the grading would have discarded a valid measurement **and hidden the
actual defect**, which neither premise named: the numbers were printed but the
registered gate was never *applied* to them, and three rows — all on a duct, the
family the review believed was the measurable one — breach it
(`1.61e-04`, `1.84e-04`, `1.58e-04` against a registered `1e-4`) while being
published as converged.

**A review is evidence, not instruction.** Check its premises against the
artefact; adopt what survives; and when a premise fails, say which and why,
because the reviewer is then working from a corrected model of the system. The
useful residue here was real and worth keeping: any `div(U)` for a field with no
solver log — the LES truth in particular — must use the chain-rule estimator and
is floored at ~1e-2 on that mesh.

## L-215. The exact anisotropy produced a worse velocity field than the learned one, with k frozen and exact — so the k budget was never the whole story

The prior lane returned NOT A RESULT and diagnosed it: injecting `b^Delta` with
no `k` correction unbalanced the `k` equation and transported `k` collapsed to a
third of baseline, so the realised stress `2k(b_lin + b^Delta)` was wrong however
good `b^Delta` was. The obvious next test was to freeze `k` and see the ceiling
clear.

It did not. With `k` frozen **bitwise** (`max|Δk| = 0.000e+00`) and, in the second
arm, frozen at the **exact** `k_LES`, the true anisotropy still failed the
registered ceiling on all three cases — and on `CBFS13700` it was **137% worse**
than doing nothing while the *learned, less accurate* anisotropy was **16%
better**. Ranked by `b_rms` against the LES the configurations order
TRUTH (0.040) < ML (0.049) < NULL (0.319); ranked by `U_rms` they order
ML (0.042) < NULL (0.050) < TRUTH (0.118). **The two rankings are inverted.**

Three things follow. The pre-registered falsifier did its job: it was written to
fire if the mechanism explanation was incomplete, and it fired, so the lane ships
a correction to its own prior finding rather than a confirmation of it. The
ill-conditioning of the explicit-closure RANS operator is real, is separable from
the `k` budget, and is now measured on this lab's data — a better `b` can give a
worse `U`, with everything else held exact. And an a-priori `b_ij` score does not
merely fail to *bound* the solved field; on at least one case it points the
**wrong way**, which is a stronger and more damaging statement than the one the
programme started with.

**Write the falsifier for your own explanation, not only for the paper's claim.**
A mechanism you have measured is still a hypothesis until something is set up
that could contradict it.

## L-216. Spend the harness before the ensemble: half a core-hour stopped a 17-to-161-core-hour run whose forward model could not carry the truth

The Kaandorp a-posteriori lane learned that a propagation path must be tested
against the *truth* before any model is graded — it ran nineteen configurations
and only then discovered its ceiling was inverted. The next lane applied the
lesson at the right end.

Before freezing the Xiao 2016 ensemble-Kalman design, two gates were run on the
forward model alone. **G0**, prescribing the baseline Reynolds stress, reproduced
the shipped baseline `U_rms` to 1e-4 (0.15658 against 0.1565) — the model is
identity-correct. **H0**, prescribing the LES *truth* stress, needed `U_rms` below
0.036 and returned **0.29799** with a frozen baseline eddy viscosity and
**3.8815** with the optimal linear projection, the outer loop diverging in both.

Cost of finding out: **0.5 core-hours**. Cost of the ensemble it stopped:
**17 to 161 core-hours**, and — worse — a posterior that would have looked like a
result. The measured band mattered too: the honest costing was a *range* bounded
by the registered per-member caps, not a single number, because member convergence
was not guaranteed.

**A harness gate is not overhead, it is the cheapest experiment in the lane.**
Run the identity case and the truth case on the forward model before the design is
frozen, and register the gate so the answer is binding either way.

## L-217. When the optimal fix makes it worse, the diagnostic is in how much of the domain it had to clip

Wu, Sun, Xiao & Wang's conditioning fix — split `tau` into the part a nonnegative
eddy viscosity can carry, treat that implicitly, leave an explicit remainder
orthogonal to the strain — is the right instrument, and applying it made the
harness **thirteen times worse** (`U_rms` 0.298 -> 3.88).

The number that explains it is not the error, it is the clip count:
`nu_t^L = -<tau_dev : S> / (2 <S:S>)` came out **negative in 1,872 cells and then
in 7,337 — 47 % of the mesh** — as the outer loop progressed. Clipping at zero is
required for stability, and it removes the implicit stabilisation *exactly where
the true stress is least eddy-viscosity-like*, which on a separated hill is the
shear layer that sets the whole solution.

**Report the fraction of the domain a stabiliser had to clip, every time.** A
projection that is optimal in a least-squares sense over the cells where it
applies can be actively harmful once the cells where it does not apply are the
ones that matter. The same rule caught the Durbin time-scale bound in the
a-priori lane (active in 71.8 % of duct cells) and it catches this.

**Corollary on scope.** The paper's `tauFoam` ran `Re_b` = 2800 on 1,500 cells;
this attempt was `Re_H` = 10595 on 15,600. The gap is conditioning, not code —
writing the missing solver would reproduce the divergence in C++ — and the
cheapest next test is therefore the same harness at a lower Reynolds number, not
a new implementation.

## L-218. Register one prediction you expect to be boring: it is the only thing that tells you the other predictions mean anything

Part A registered three predictions before computing any envelope. **P-A1 was
deliberately a self-check**: shape coverage at `delta_B` = 1 must exceed 0.95 on
every case, *because at `delta_B` = 1 the three perturbed states are the corners
of the barycentric triangle, so the envelope is the entire realisable set and the
only cells that can fail are those where the truth itself is unrealisable.* The
preregistration said in advance that a number materially below 0.95 would mean the
implementation was wrong, not the method.

Measured: shape coverage came out equal to `1 − truth_unrealisable_fraction` to
four decimal places on all eight cases (0.9949 to 1.0000 against known truth
violation rates of 0.0000 to 0.0051), and zero cells left the simplex under
eq. (7). Only *then* is **P-A3's GATE FAIL** — the ducts needing `delta_B` of 0.95
to 0.98 where Emory's own experience is O(0.5) — a statement about turbulence
rather than a statement about a bug.

**A test suite for a physics implementation is a set of registered predictions
whose answers you already know.** Put at least one in every preregistration, say
out loud that it is a self-check, and give it a band that a broken implementation
would miss. It costs nothing and it is the difference between a finding and an
artefact.

## L-219. A perturbation magnitude calibrated where the model is qualitatively right saturates where it is structurally wrong

Emory, Larsson & Iaccarino deduce the perturbation magnitude `B` from DNS by
minimising the barycentric distance to the perturbed state, and the values they
work with are O(0.5). Measured here as the per-cell **minimum `delta_B` that
contains the truth**, the eight training cases split into two families that do not
overlap:

| family | median `delta_B` required |
|---|---|
| 2-D separated flows — five hills and the curved step | **0.31 to 0.54** |
| square and rectangular ducts | **0.95 to 0.98** |

The hills sit exactly where the literature says. The ducts need essentially the
whole way to a corner of the triangle. The reason is not that the duct is harder
in degree: a linear eddy-viscosity model in a duct produces `b_23` and
`b_22 − b_33` **identically zero**, so its barycentric point is not displaced from
the truth, it is near the wrong vertex. The perturbation magnitude has nowhere to
go but 1.

**An uncertainty magnitude is a calibration, and it inherits the flow class it was
calibrated on.** Quoting O(0.5) on a flow where the closure is structurally rather
than quantitatively wrong understates the band by a factor of two, and the
diagnostic that catches it — the required magnitude, per cell, in closed form — is
one line of algebra and no solves.

## L-220. Test the envelope on the quantity that enters the equations, not only on the quantity it parameterises

The eigenspace method parameterises the **shape and orientation** of the Reynolds
stress. Emory's eq. (4) keeps `k` outside the bracket, so magnitude is untouched
by construction. Both papers say so. What the measurement adds is which cases pay
for it, and the answer is an inversion:

* **Shape** containment at `delta_B` = 1 is essentially complete everywhere
  (0.9949–1.0000) — but on the ducts it costs the whole triangle (D2).
* **Production** `P_k = -R_ij dU_i/dx_j` — the term through which the stress
  actually forces momentum — is contained in only **0.9279 to 0.9433 of cells on
  every hill and on the curved step**, while the two ducts clear 0.9998.

So the cases whose *shape* is cheap to contain are the ones whose *forcing*
escapes, and vice versa. A single "does the envelope contain the truth?" answered
on `b` alone would have reported the hills as the easy family and been wrong about
the thing that matters to the solution.

**Report envelope coverage on the forcing term as well as on the parameterised
quantity, and expect them to fail on different cases.** This also closes the loop
L-157 opened: Xiao's space excludes the truth because it never perturbs
orientation; the eigenspace envelope perturbs orientation and still misses the
truth's forcing in 2–7 % of cells because it never perturbs magnitude. **Neither
framework contains what it is meant to bound, and they fail on different axes.**

## L-221. A lesson is not applied until every call site asserts it — this one cost three runs in three different files

The finding is trivial and it bit three times: **the 29 `Parm_PH_29` hills carry
no `libs` entry in `system/controlDict`, while `PH_Breuer`, `CBFS`, `DUCT` and
`NASA_2DWMH` carry one naming a library that does not exist on this machine.** A
`str.replace` of the absent-library line therefore succeeds silently on the hills
by doing nothing, and the run dies with `Unknown RAS model type ...` after a
fraction of a second.

* First strike: the Xiao `Re`-switch harness. Diagnosed, fixed **in that file**,
  and written up as an operational note in the report.
* Second strike: the same code path in a second file, days of nothing.
* **Third strike: `setup_case.build`, reached from a different lane entirely — five
  eigenspace re-solves all returned `it=0` and the *baseline* `U_rms`, which looks
  like a plausible physical answer.** That is the dangerous part: a failure that
  returns the unperturbed field is not obviously a failure.

Writing the lesson down in a report did not fix the other call sites. What fixed
it was replacing every one with **insert-or-replace followed by
`assert "libspartaTurbulenceModels" in s`** — three lines that turn a silent
no-op into a stack trace.

**When a defect is found in a shared helper, grep for every call site in the same
sitting and add the assertion there, not a paragraph about it somewhere else.**
The cost of the paragraph was two more wasted runs; the cost of the assertion was
three lines.

## L-222. A defect class that bit three call sites gets an assert at every call site, never a paragraph in a report

**Sanaa, 2026-08-22, institutionalizing L-221:** *"the libs lesson as law — a defect
class that bit three call sites gets an assert at every call site, never a paragraph in a
report. Sweep for remaining unasserted call sites of the same libs defect."*

**The law.** Every call site that writes or edits a `libs (...)` entry in an OpenFOAM
`controlDict` **inserts (insert-or-replace)** and then **asserts** the library name is
present in the written text — `assert "<lib>" in s, "libs insert failed: <path>"`, or in
shell `grep -q '<lib>' <file> || { echo "libs insert failed: <file>" >&2; exit 1; }`.

**The sweep, `docs/closure/LIBS_ASSERT_SWEEP.md`, over every `.py`/`.sh` under `cases/`
and `verification/`:** 92 `libs` mentions, of which **75 actually write one**. They split
into **8 library-load call sites** — the defect class — and **67 function-object template
lines**, which are n-a because a wholesale template write has no merge to get wrong.

| | count |
|---|---|
| library-load call sites found | **8** |
| already asserted before the sweep | **3** (`setup_case.py`, `tau_forward.py`, `run_gate.py`) |
| newly asserted here | **4** (`frozen_R.py`, both Wu2018 `build_cases.sh`, `setup_sparta_case.sh`) |
| asserted by a concurrent lane's shared helper, mid-sweep | **1** (`K0cQ_runs/build_cases.sh`) |
| n-a, function-object template lines | **67** across 25 scripts |
| T-family (not this lane's tree) | **0 call sites** — those builders write `controlDict` wholesale with no `libs` line at all |

**One of the four was a LIVE instance of the same defect, and it was measured rather than
argued.** `Kaandorp2020_TBRF/aposteriori/frozen_R.py:69` carried the bare
`str.replace('libs ( "libfrozenIncompressibleTurbulenceModels.so" );', …)` — the exact
line L-221 was written about, in a file L-221's own sweep did not open. Replayed in a
sandbox on the two real benchmark `controlDict`s: on the duct the repaired code is
**byte-identical** to the old, and on a `Parm_PH_29` hill the old code produced **no
sparta entry at all**. Every new assert was also run against a **sabotaged** copy and
observed to fire.

**The second finding is about the lesson, not the defect.** The same night, two lanes
independently turned L-221 into law — this one with an assert in each file, another with
a shared `scripts/foam_libs.py` helper and a `lint_foam_libs.py` that FAILs any `libs`
write not routed through it. **Both are right, and the duplication is the cheapest
possible outcome of a law that both lanes read the same way.** Two things worth carrying:
a `grep -q` cannot tell one top-level `libs` entry from two (a duplicate dictionary key,
which a blind `>>` append leaves behind), so a merging helper is the stronger mechanism;
and a linter keyed to "writes not routed through the helper" **does not see** a
`re.sub`-based insert-or-replace at all, so the mechanical check and the in-file assert
cover different halves and neither is redundant.

## L-223. A commit whose tree came from a stale `read-tree` but is parented on current HEAD reverts the intervening work silently, and the ref CAS passes

**Committed at `c46309f5` tonight; the damage was caught and repaired by another lane at
`a5126378`.** The private-index protocol was followed to the letter and still lost nine
files. The sequence, and the gap is between the first line and the third:

```
git read-tree HEAD          # earlier bash call: HEAD was 31fd2268
...                         # another lane commits eda10f39 (nine closure files)
T=$(git write-tree)         # tree still says 31fd2268's content
C=$(git commit-tree $T -p $(git rev-parse HEAD) -F msg)   # parent is eda10f39
git update-ref refs/heads/main $C $(git rev-parse HEAD)   # CAS PASSES
```

**The compare-and-swap on the ref proves the PARENT is current. It says nothing about
whether the TREE is.** A tree built from a stale `read-tree` and hung off a current
parent is a valid commit that reverts everything committed in between — silently, with a
clean exit and a message about something else entirely. `git diff-tree --stat HEAD $T`
was run and printed only the two intended files, which is exactly the trap: **it was run
against the stale HEAD the tree came from, not against the HEAD the commit was about to
be parented on.**

**The rule.** Capture HEAD **once**, into a variable, and use that one value for
`read-tree`, for the `diff-tree` assertion and for `-p` — all inside a single shell
invocation, because a background lane can move HEAD between two bash calls:

```
H=$(git rev-parse HEAD); git read-tree $H
git update-index --add <explicit paths>
T=$(git write-tree); git diff-tree --stat $H $T     # assert: ONLY your paths
C=$(git commit-tree $T -p $H -F msg); git update-ref refs/heads/main $C $H
git diff HEAD~1 HEAD --stat                         # verify after: ONLY your paths
```

**The post-commit verification is the part that would have caught it**, because it is the
only check that compares the new commit against what its parent actually was.

## L-224. The libs lesson is now a helper and a linter, not a paragraph

L-221 said an OpenFOAM `libs` entry must be inserted-with-assert; Sanaa's directive H-7 (2026-08-22) says the assert goes at every call site. Both now exist as code: `scripts/foam_libs.py` (`ensure_libs` merges to the union, writes, re-reads from DISK and asserts; depth-aware, so the 8–11 `functions{}` loaders in every F14 controlDict are never mistaken for the solver's library list) and `scripts/lint_foam_libs.py` (top-level libs entries ≤1 per controlDict; every build script read for libs writes; selftest plants the original defect in four forms and all four FAIL).

**The rule: a `libs` write anywhere outside `ensure_libs` is a lint FAIL** — `printf`/`echo` with `>`/`>>`, `sed -i`, `re.sub`, `str.replace`, all of it. A wholesale template write is INFO, because there is no merge to get wrong.

Found by this sweep: the T-family's 102 controlDicts carry no libs and need none (solvers link every required library — verified by ldd, every BC resolved); the one real unsafe site was K0cQ's builder (`verification/runs/F14-cooling-ladder/K0cQ_runs/build_cases.sh:59`), whose blind append was correct on six solved cases only by luck of the baselines; and the *canonical* closure idiom (`cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/setup_case.py:111`, `re.sub` without `count`) replaces every libs entry rather than one — the same defect wearing the assert that L-221 asked for. Reported to the closure supervisor, not edited.

## L-225. "The pointer does not resolve" is a claim about git, not about the disk — check both before ruling a number unsourced

A charter ruling (section 5(b)) declared the figure **3.24** — the mean per-cell rank of Pope's ten-tensor basis, quoted in three records — to be sourced to a pointer *that does not exist*, `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/train_log.json`, and a sweep replaced or re-sourced the number in `Ling2016_TBNN/RESULTS.md`, `Wu2018_PIML_RF/RESULTS.md` and `_common/FEASIBILITY.md` on that basis.

**The file is there.** `ls` finds it, it is 4,336 bytes, and it holds `basis_rank_mean = 3.2374` with `basis_rank_hist = [0,0,0,3814,1185,1,0,0,0,0,0]` — *exactly* the histogram the records quote (3,814 at rank 3; 1,185 at rank 4; one at rank 5). What is true is that it is **untracked**: the whole `Kaandorp2020_TBRF/` directory is (`INCIDENT_tbrf_overwrite_2026-08-20.md` says so in its second bullet, and that is the same fact that made the overwritten `tbrf.py` unrecoverable from git). So `git ls-files`, `git log -S'3.24'` and every grep of the committed tree return nothing, and an audit conducted entirely through git concludes the source was never written. It was written; it was never committed.

**The rule.** Before writing "source not on disk", "does not exist" or "does not resolve" about a cited path, run **`ls` on the path itself** — not `git ls-files`, not `git log -S`, not a grep of the tree. `git log -S` cannot find a number that was never committed, and a repo with untracked working directories full of run artefacts (this one) will produce that false negative routinely. The two questions "is it in git?" and "is it on disk?" have different answers here and only the second one is about whether the number has a source.

**Second-order, and the reason this cost more than a `ls`:** the number really did have two statistics behind one label, which is what made the "unsourced" story plausible. 3.24 is a **pooled-sample** mean over 5,000 randomly drawn training cells (`run_tbrf.py`, `np.random.default_rng(0)`, deterministic and regenerable), pulled down by the duct family; the **case-mean** statistic is 3.738, and `_common/features/FS2_DEGENERACY_REPORT.md` sec. 4 measured it fresh and reasonably reported that it "does not reproduce 3.24". Both numbers are right. The defect was one label over two statistics plus an uncommitted source — not a fabricated figure — and the fix is to name the statistic beside the number, which `docs/NUMERICS_KNOWLEDGE.md` N-B10 and the inventory now do. **Never delete a number to resolve a provenance doubt; find which of the two it was.**

## L-226. Teams were killed at every compaction and re-briefed by hand, and a hand-written brief is checked against nothing

2026-08-22. Five standing teams ran this lab, and every one of them died at each
compaction, session switch, crashed terminal and hit context limit. **Nothing about
a live agent is persisted** — not its brief, not what it had read, not the four
personal checks it owed, not the fact that it had twelve solvers running. So
re-forming the lab meant a human writing five briefs from memory, every time.

**The failure is not that the briefs were bad. It is that nothing could tell.** A
solve is checked by a gate, a claim by an artifact, a docket row by the
reconciliation script. A hand-written brief is checked against nothing at all, so
each retelling could silently drop a charter clause, a rung's real verdict, or a
running job, and the loss left no trace anywhere. Measured on the day the harness
was built, from records rather than memory: the closure line had **six rungs with
no verdict** (R4, R5, R6, FS3, FS4, FS6), DAFoam had an **A3 patched arm that the
record itself calls "not clean-by-omission"**, and T1b carried **four PASS rows
sitting on grid triples that were every one DIVERGENT or STAGNANT**. Not one of
those is the kind of thing a brief written from memory reliably carries, and all
three change what the next session should do first.

**The repair, and the shape of it is the transferable part: split identity from
situation.**

- **What is STABLE about a team goes in a generated definition** — mandate,
  charter, reading list, folder scope, the four checks it may not delegate, its
  duties. `harness/teams.yaml` is the data; `.claude/agents/*.md` is the output;
  `generate_agents.py --check` is the regression test. Identity that lives in a
  brief rots at the first retelling.
- **What CHANGES goes on one board** — `docs/LAB_STATE.md`: last commit, live jobs
  with pid and cwd and ETA, rungs lacking verdicts, next actions, the owner's desk,
  blocked items. Updated **at every commit and every verdict**, never at the end of
  a turn, because the end of a turn may never arrive.
- **Re-formation is one command** that reads the board and hands each supervisor
  its own section verbatim. Nobody composes a brief.

**What this does NOT do, stated because the temptation is to claim it.** It does
not make teams survive. Nothing in the tooling can; the death is unavoidable and
the harness is entirely about the cost and fidelity of coming back. Any supervisor
that has not written its section since its last verdict still loses that verdict at
the next death — which is exactly why the duty is "at every commit and every
verdict" and not "before you finish".

**A second-order rule the build itself produced.** Every uncertain line on the
board is marked `VERIFY`, and both entry points (`/form-teams`, `/lab-state`) take a
live reading — `git log`, `ps aux`, `readlink /proc/<pid>/cwd` — and rule that **the
reading beats the board**. A persisted board is a new thing that can be confidently
wrong, and it inherits none of the checking a gate has. That is a real cost of this
repair and it is paid deliberately: a wrong line that is visible and dated is worth
more than a right line that lives only in somebody's context window.

**Corroboration that the problem is live, from the build itself:** HEAD moved
**six times in the two hours** this harness was assembled, by four different lanes,
and the docket and lesson numbers this commit claims had to be re-derived at commit
time because `D449-D451` and `L-224` were taken by a peer mid-build. A brief written
at the start of that window would have been wrong by the end of it. Related: L-186
(the scratchpad is not a handoff channel), L-223 (a stale `read-tree` reverts a
peer silently), L-41 (fleet agents are invisible to `pgrep`).

## L-227. A small error in a derived quantity is not evidence of a small defect in the treatment that produced it — the reconstruction can be cancelling most of it

T9a graded its composite wall's interface temperature 2.41 mK from exact and its flux 1.8 % from exact, and the two look like different-sized problems. They are the same problem. The flux-continuous face temperature `(k_L/d_L·T_L + k_R/d_R·T_R)/(k_L/d_L + k_R/d_R)` puts **95.3 %** of its weight on the high-conductivity cell at a 400× contrast, and that lopsidedness **cancels 89 % of the flux error**. Weaken the contrast to 40× and the weight falls to 67.1 %, the cancellation to 25.8 %, and the *same* mechanism reports **−64.99 mK instead of −2.41 mK — 27× worse for a solver that is 2× better in flux** (T9a-D, D454). Two obligations follow. **(1) A rung that grades a reconstructed quantity registers, before the run, what the reconstruction weights are and how much of the underlying error they cancel** — otherwise the graded number's size is a property of the measurement, not of the solver. **(2) A property-jump sensitivity study registers the quantity it will scale in, and states whether the exact solution moves too.** Here the exact flux rose 8× when the contrast fell 10×, so "the error should scale with the contrast" was the wrong functional form before a single case was built; the arm predicted its own directive would fail, in writing, and it did.

**Corollary for the conjugate ladder (T9b, T9c, T11, T13): register `Gauss harmonic` — or an equivalent harmonic face interpolation of the conductivity — for the conduction laplacian wherever a property jump sits on a mesh face.** It is not a tuning knob: on a 1-D orthogonal mesh with the interface on a face it is the exact series conductance for any spacing ratio, and the arithmetic default costs 1.8 % of the flux at a 400× contrast on a mesh where harmonic is exact on 35 cells.

## L-228. A per-component table read from an MPI `check_totals` log is not a reading until its norms are reconstructed and matched against the block's own printed magnitudes

**The rule.** Before any component of a `Jfor`/`Jfd` array printed by OpenMDAO `check_totals` under `mpirun` is quoted, reconstruct `‖Jfor‖`, `‖Jfd‖` and the relative error from the parsed array and require them to match the block's own printed `Analytic Magnitude`, `Fd Magnitude` and `Relative Error` to the printed precision. A copy that fails the three-way match is discarded, not repaired.

**Why.** OpenMDAO prints each derivative block once per rank, and the ranks splice each other's arrays **mid-number** on one shared stdout. The corruption is silent and well-formed floating-point text; nothing in the file marks it.

**The incident.** A2 per-component extraction, 2026-08-22 (`cases/dafoam/ladder-a/A2/per_component_table/RESULTS.md`, D456). Of four printed copies of `CD wrt shape` in `check_totals_run1.log` exactly one is usable; of four copies of `CL wrt shape`, none. One rejected copy reconstructs `‖Jfd‖ = 3.476e+03` against a printed `4.858158e-02`; another gives a CL relative error 41 % off the printed value. In both the stock and patched logs the CD FD array is severed at the same component (30, `3.05777580e-04`) — a stdout write-boundary effect. Every table that was kept passed the gate stated before extraction. Corollary already in the charter's spirit: run `check_totals` with `compact_print=False` **and at np=1** whenever the per-component table is the product.

## L-229. An FD reference taken at a deformed design point is a property of the optimisation path, not only of the design point — two runs that stop at the same point by different routes do not share an FD reference

**The rule.** An endpoint FD-vs-adjoint error may be compared across toolchains only when both `check_totals` were taken at the **same** design by the **same** path (same warm state, same perturbation history). Otherwise the comparison is reported as two separate rows and the analytic columns are compared directly.

**Why.** Perturbed primals warm-start from the current converged state and `primalMinResTol` is a floor, not an equality; the FD reference inherits the optimiser's history while the adjoint does not.

**The incident.** A4 shipped-image optimisation twin, 2026-08-22 (`cases/dafoam/ladder-a/A4/shipped_optimisation_np1/RESULTS.md`, D455). Shipped and patched optimisations both stop at `shape = −0.05` (6 vs 9 majors, 16 vs 47 objective evaluations). Their analytic gradients agree to 3.9e-06 relative (`0.21410204` vs `0.21410121`); their FD references differ by 1.83e-03. The reported endpoint errors — 0.3112 % and 0.4936 % — differ entirely because of the FD column. Same class as `W4_IDX16_IS_THE_REFERENCE.md` and as A5's idx16 (L-1xx family: the reference, not the adjoint, moved).

## L-230. A launch gate checked in the same shell command as the launch cannot gate, and a gate must be denominated in the resource the cap is denominated in

**The rule.** Run the pre-launch gate as its own command and branch on its exit status; and when the binding constraint is a core cap, gate on cores (runnable processes vs `nproc`, or a measured inflation marker), not on a proxy such as "no other container of ours is running".

**Why.** A gate that shares a line with `nohup` launches regardless; a proxy gate opens on the wrong signal and closes on the wrong one.

**The incident.** A4 first optimisation Amendment 1 (2026-08-21) launched at load 16.51 because `uptime` and the launch shared one line. On 2026-08-22 `P3-a4-opt-shipped/preflight.sh` ran the gate as its own command and correctly refused at load 16.26–22.38 — and its registered escalation condition ("no other DAFoam container running") then proved a poor proxy for the team core cap while 12 foreign single-rank solvers held 12 of 16 cores. The np=1 arms launched under a dated amendment at `--cpus=1` and measured **1.104×** inflation on an identical work marker — the np=4 spin-wait mechanism (18–21×) does not exist at one rank, which is the number a core-denominated gate would have used.

## L-231. Record the signed residual, not its magnitude — |rowSum − 1| hid the one fact that excluded half the hypotheses

T10a recorded the outer-sphere view-factor defect as `|Σ_j F_ij − 1|` = 4.77/4.27/4.47 % and spent a ladder and two twins asking whether visibility, orientation or Gauss tolerance could explain it. The row sums were **above** 1 (1.04103/1.04035/1.03962). An excess cannot come from missed visibility or shadowing, so every such hypothesis was dead before a single sweep case was built; the magnitude hid it. **A guard or identity residual is recorded with its sign, and a characterization arm opens by reading the sign.**

Second half: a tolerance that moves a quantity by ≤0.006 % when tightened 10× is not "confirming the quadrature is fine" — it is saying the error is in a term that tolerance does not reach; T10a-VF found that term (`viewFactorsGen.C:390-394`, order forced to 0 at `:1054-1058`) and its closed form `e(α) = −(2 ln α + 3)/(4π)`. **When a knob is inert, name the term the knob cannot touch before concluding anything.** (D457.)

## L-232. Before dropping ranks on a DAFoam arm to dodge a core-availability gate, price the COLOURING, not the solve — core-minutes are not conserved across rank changes

**The rule.** A rank-count change is a re-pricing of the whole arm, not a re-slicing of it. Price the `dRdW` distance-2 Jacobian colouring separately from the solve before proposing np=1 as a way past a busy box, and state that any cached `dRdWColoring_<nranks>.bin` is np-keyed and is discarded by the move.

**Why.** Core-minutes are conserved under rank changes only for the *solve*. The colouring graph is built per partition, so at one rank it is the **global** distance-2 graph: fewer ranks make the colouring structurally bigger, not merely slower per core.

**The incident.** A3 ONERA M6 rung 2 (42,120 cells), 2026-08-22, patched-IDWarp arm re-priced from np=4 to np=1 to get past a core gate the T-family was holding shut. Measured on the identical matrix (`AllNonZeros` 59,719,202 vs 60,419,908, ratio 0.99×; decoloured per sweep 397.4 vs 405.0, ratio 0.98× — per-sweep efficiency unchanged): **`nUniqueCols` 381,558 at np=1 against 125,870 at np=4, 3.03×**, and 42.91 s per 100 `ColorSweep` against 12.28 s, 3.49×. Projection at the measured rate: 4,074 s CPU = 67.9 core-min idle / 138.6 contended, against **30.13 core-min measured at np=4 with the warm cache**. At its registered 4,200 s cap the arm would have held only ~2,058 s of CPU — still inside the colouring, never reaching the adjoint, producing no number for 70.0 core-min. It was stopped at **11.950 core-min** on that projection (`FAMILY_SUPERVISION_GUIDELINES.md` §6 item 5, the coloring-off precedent; recorded as a deliberate stop, not a measurement, so no conditioning, memory or gradient claim is drawn from it). **Corollary:** gate on the resource the container consumes — free cores ≥ ranks — not on `load1`, which never measured it (L-230's second limb, now with a price attached).

## L-233. A finite-difference reference is a step chosen against a measured noise floor, and a sign flip is the cheapest thing in this lab to misread as a defect

**The rule.** Before grading an adjoint against FD, measure the objective's own noise at **the primal setting the graded run uses**, compute the floor `η/(2s)`, and require every graded component to clear it by a stated factor `C = |J|·2s/η`. A component that does not clear it is **flagged and excluded by name** — never graded, and never rescued by a step at which it happens to cross. Fix the noise definition in the pre-registration, before seeing which definition saves which component.

**Why.** Clearance has three levers — `|J|`, the step, and η — and only the step is usually reached for. A component whose FD difference is the same size as the objective's wobble returns a random sign, and a monotone analytic column beside a sign-scrambled FD column of that magnitude is the signature of a noise-dominated *reference*, not of a wrong adjoint.

**The incident.** A6 CRM N=16, 41,760 cells, np=1, patched image. The predecessor rung graded at step 1e-3, where clearance ran 0.19×–1.94×, and reported **341.51 %, 159.35 % and 105.26 % with three reversed signs** — which reads exactly like a broken adjoint; it located the cause in the FD and called its own reading provisional (`A6/rung_n16_np1/RESULTS.md` §6.3). At steps sized from the measured wobble (1e-1 for twist, 3e-2/1e-2 for patchV) **the same adjoint and the same harness** give **1.706 %, 1.817 % and 0.940 %, zero sign flips**, aggregate 1.0099 % (`A6/rung_n16_fixed_reference/RESULTS.md`, 63.166 core-min). Nothing about the derivative changed. Verified by the supervisor independently: one fixed analytic value per component reproduces the quoted error at **both** steps, so the analytic column provably did not move. The same record keeps `twist` idx6 flagged (clearance 2.42×, plateau disagreement 83.53 %) even though its 1e-1 value lands at 3.206 %, inside the band — because A1's idx6 did precisely that at step 2e-2 in `A_stepsize_study.md`. **Corollary:** an alternative noise definition existed that would have cleared idx6 at ~6×; it was disclosed as a 2.47× sensitivity and **not adopted**, because choosing the denominator after seeing which one rescues a component is the thing pre-registration exists to prevent.

## L-234. A novelty search needs a planted-nonsense control, because a pinned thread is returned for every query and turns a clean zero into an apparent hit

**The rule.** Before reading any hit count from a venue's search, run a **nonsense-token query** against the same endpoint and subtract what it returns. Effective hits = distinct results − control results. Record the control **in the note, before the counts**, and state the search engine's semantics (single-token vs OR'd multi-word) so the reader knows which counts carry evidential weight. Absence is only "measured" once the reader has been shown the searcher could see a presence — the planted-zero principle, applied to literature rather than to fields.

**Why.** Venue search surfaces are not neutral: GitHub Discussions returns **pinned** threads for every query, including one that matches nothing.

**The incident.** ADF primal non-reproduction novelty sweep, 2026-08-22 (`cases/dafoam/DEFECT_CANDIDATE_adf_primal_nonreproduction.md` §9, commit `757eccf0`). The query `zzzqqxnonsensetoken12345` returned **1** Discussions thread, not 0 — `mdolab/dafoam` #883, *"Have 30 minutes? Meet with us to share your DAFoam feedback!"*, pinned. Uncontrolled, the single-token negatives `primalMaxRes` and `tangent` would each have read as **one hit** when both are clean zeros. The control was run **before** any count was read. Two further traps recorded in the same sweep and worth carrying: the REST API **does not index Discussions at all** (they need the HTML search surface — already trap #1 in `LIAISON_NOVELTY_SWEEP_decomposition_defect.md`), and Discussions search appears to **OR** multi-word queries, so a large count for a phrase like "forward AD" is weakly relevant and the evidence sits on the single-token negatives.

## L-235. A settle criterion that measures change cannot tell convergence from clipping, and the clipped field looks like an answer

The frozen-RANS extraction declares itself converged when `omega`'s initial
residual is below `1e-8` and its maximum relative change below `1e-9` for 50
consecutive iterations. On two of twenty-one hills it declared **`CONVERGED
(settle criterion) at iteration 51`** with a verification drift of **exactly
0.0** — the strongest-looking convergence in the whole set.

What actually happened is three lines above it in the log. The first `omega`
solve had an initial residual of 0.933 and was followed by `bounding omega,
min: -193215225.4 max: 762695.6 average: -50081.6`. OpenFOAM's `bound()`
replaces every negative cell with a local average; the field was flattened, and
from iteration 2 onward `omega initRes = 9.26e-18` and `max rel domega = 0` at
every single iteration. **The field stopped changing because it had been
clipped, not because it had converged**, and every mechanical completion clause
— `rc = 0`, an `End` line, a last time directory equal to the write iteration,
fields present and newer than `0/` — was satisfied.

This is the L-221 shape one layer up. L-221's lesson was that a silent no-op
returns the *unperturbed* field, which looks physical. Here a silent clip
returns a *flat* field, which looks converged. Both are failures whose output
passes inspection.

**A convergence test on `d(field)` must be paired with a test that the field was
not clipped.** The repair is one line: count the solver's own bounding
messages before the field write and refuse the run if there are any. The six
hills that genuinely converged bound `omega` **zero** times; the thirteen that
hit the backstop bound it on **all 5000** iterations. The counter separates all
three populations perfectly and costs nothing.

**Source:** `cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` §2.3, and
`cases/RANS_LES_closure_models/R4_sparta_build/artefacts/frozen_inventory.json`,
which carries `converged_at`, `bounding_omega` and the completion verdict for
each of the 27 extractions.

---

## L-236. Put an arithmetic impossibility in your gate: it is the only check that caught a scrambled design matrix

A sparse-regression pipeline ran cleanly on a tensor design matrix whose rows
had been reshaped through an intermediate `(cell, candidate, component)` shape,
so candidate row *r* and target row *r* belonged to **different cells**. It
survived: the elastic-net path, leave-one-family-out cross-validation, three
seeds returning an identical three-term model, a condition number of 4.1, and a
planted-zero control that **passed**. Every internal consistency check the
fitting code had was happy.

What caught it was the preregistered a-priori gate, which scores the discovered
model against a **constant** baseline. It returned a model whose error against
its own training target was **larger than predicting zero** — on all four
families at once. A least-squares fit cannot do that: the zero vector is in its
feasible set. The number was not a bad result, it was an impossibility, and the
fit and the 24 propagation arms already launched from it were withdrawn.

**The most valuable clause in a gate is the one whose violation is arithmetically
impossible rather than merely surprising.** A threshold tells you the model is
poor; an impossibility tells you the code is wrong. Charter §3's train-mean
baseline was written to stop closure lanes scoring against a bar a constant can
clear — it also turns out to be the cheapest bug detector in the pipeline,
because "worse than the trivial predictor on its own training data" has exactly
one explanation.

Corollary, and it is the uncomfortable half: **three seeds agreeing is not
evidence of correctness.** The scrambling was deterministic, so every seed
scrambled identically and all three agreed to the last digit.

**Source:** `cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` §4.4 (how
it was caught) and §4.5 (the gate that caught it); the withdrawn fit is retained,
not deleted, at
`cases/RANS_LES_closure_models/R4_sparta_build/artefacts/fs3_WITHDRAWN_scrambled_bDelta.json`.
Disclosed as departure D-6.

---

## L-237. The exact degeneracy that justified an exclusion existed only in the field nobody was fitting

A preregistration excluded two library members from duct-only fits on a measured
exact collinearity: on `AR_1_Ret_180`, `T4 = -T3` to machine precision
(`||T3+T4||/||T3||` median **2.74e-17**), `I2 = -I1` identically, and a per-cell
tensor-basis rank of **exactly 3.000** on 4,000 of 4,000 cells. The measurement
was right and reproduces to four figures.

It was made on the **baseline RANS** field. The fit is done on the
**frozen-RANS** field, whose velocity is the DNS mean. There the same three
numbers are **1.28e-02**, **7.04e-05** and **3.965** — 2,132 of 2,209 cells at
rank 4. The cause is physical and was already in the lab's own record from the
other direction (L-219): a linear eddy-viscosity duct has no secondary flow, so
`S^2 + Omega^2` is isotropic and the deviatoric parts cancel exactly; the DNS
mean flow *does* have secondary motion, so they do not.

**State which field a degeneracy was measured on, because a data-driven closure
is fitted on a different one than it is evaluated in.** The rule the measurement
justified is not wrong here — it was scoped to a fit this lane never ran — but a
future lane applying it to a ducts-only frozen fit would be excluding two live
directions for a collinearity that is not there.

**Source:** `cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` §3.2; the
per-case numbers are in the `degeneracy` block of
`cases/RANS_LES_closure_models/R4_sparta_build/artefacts/dataset_manifest.json`,
and tabulated for both fields at `docs/NUMERICS_KNOWLEDGE.md` N-B30.

---

## L-238. A held-out family can tell you a selected term is worse than noise, and the selector cannot

Two planted-zero columns with a true coefficient of exactly zero — a seeded
permutation of the strongest candidate and a seeded Gaussian at the same RMS —
were appended to every design matrix. On one of four fits a **selected** term
scored **below both of them** on leave-one-family-out permutation importance:
permuting it *improved* held-out error by **−322.2** where the planted zeros
scored −1.6e−03 and −1.8e−03. The cross-family-CV elastic net had selected it
anyway.

The same control reported a second thing, which is about the method rather than
the model: **at its own cross-validated optimum the elastic net is not a sparse
selector.** It retained 15 of 20 columns *including the permuted planted zero*,
at a coefficient of 6.7e−03. A term set read off the CV-optimal coefficient
vector would have shipped noise.

**Plant the zero, and rank it — do not only check that it was excluded.** The
useful output is not "the planted column was not selected"; it is the position
of the planted column relative to the terms that *were*. Where a real term
ranks below a planted one, the selection has found structure the held-out data
does not support, and no amount of seed agreement will say so.

**Source:** `cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` §4.3; the
control's own record, including each planted column's `mi_rank`, `perm_rank` and
`enet_cv_optimum_coefficient` per fit and seed, is the `planted_zero_control`
block of `cases/RANS_LES_closure_models/R4_sparta_build/artefacts/fs3.json`. The
pass rule was revised once after its first run — departure D-5.

## L-239. A registered stop rule must name the process that can execute it — a record-only watcher cannot enforce a threshold, and a threshold nothing can enforce is a preference, not a control

**The rule.** When a pre-registration registers a stop condition ("if X crosses T, stop"), it must also name **what polls X and what performs the stop**, and the two must be connected. If the instrument is deliberately record-only, the document says so **where the threshold is stated**, so a reader sees a *measurement*, not a *guard*. Same discipline as a gate that must be run as its own command and branched on (L-230): an unenforced threshold reads as protection and provides none.

**Why.** A pre-registration that states a floor reads as though the arm is guarded, which makes a breach look impossible rather than merely unobserved — nobody goes looking for it, and the absence of an alarm is mistaken for the absence of an event.

**The incident.** A3 rung 2, 2026-08-22, **self-reported by the lane that caused it**. The item registered "host `MemAvailable` < 8 GiB → stop" and armed a **record-only** RSS watcher; nothing connected them and nothing polled the host figure live. The graded arm P-A drove host `MemAvailable` to **5.85 GiB** and held it below the registered floor for **82 of 156 samples (52.6 %)**, and the arm's own container was the cause — Pearson r(own RSS, host MemAvailable) = **−0.999** over 156 samples. No stop fired. The numbers survive on independent evidence (rc=0, no OOM, peak 9.263 of a 12 GiB cap, adjoint residual pairs and the whole FD column bit-identical to stock) and the floor is a **neighbourliness** guard rather than a validity one — no other team's process was killed — but the risk to the co-tenant T-family was real and self-created. This is `DAFOAM_CHARTER.md` §13's own admission — *"a clause nobody can fail is a preference"* — arriving **inside a pre-registration written under that charter**. It is recorded because the lane reported it against itself; a breach that surfaces only when its author volunteers it is exactly the kind this lab must not punish into silence.

## L-240. The instruction was the defect, and the second time it fired it was issued by the person enforcing the rule

`docs/USING_THIS_LAB.md` §8.5 tells an agent to rebuild an append-only file as
HEAD's blob plus its own rows and then write that into the working tree. That
last step is an overwrite. **D369** records it destroying bytes in
`docs/LESSONS.md` at `12b7ed42` — `cmp` reported "EOF on - after byte 313171",
the trailing bytes were unrecoverable — and closes with the repair stated
exactly: *"The write-back must be a MERGE, not an overwrite … and refuse if the
two disagree anywhere inside HEAD's own bytes."* It was filed **OPEN**.

Four months of documents later it fired again. The supervisor coordinating the
R4 closure lane issued the append instruction **in the overwrite form, verbatim**
— *"build each file from `git show $H:<path>` plus your appended rows … and also
write the result to the working tree"* — and the lane executed it on three
append-only records at once. The same supervisor was, in the same message,
enforcing the private-index protocol, the tail-derived numbering rule and the
within-section edit rule. **Knowing the rule and issuing its violation are not
in tension; they are the normal case**, because the overwrite form is the one
that is written down, and the merge form existed only as a sentence inside the
docket row about the last time it went wrong.

Nothing was lost this time, as far as every instrument could see — the
reconciliation script passed on identical ID sets, the shared index held no id
that HEAD lacked, and the only numbering gaps predated the commit. That
qualifier is the whole lesson. **D369's loss was bytes that matched no ID
regex**, and every check listed above is an ID-set check. They were reporting on
the one thing that could not have detected the fault they were being used to
rule out. It was disclosed as departure D-13 rather than reported as a clean
run.

**A repair that lives in the prose of an incident report is not a repair; it is
a description of one.** D369 said "the merge form is owed to §8.5" and named the
missing sibling checker, and both stayed missing until the defect recurred.
Sanaa's H-7 rule — a defect class that has bitten twice gets an assert at every
call site, never a paragraph — applies to instructions as much as to code, and
the assert here is executable: `scripts/append_record.py` merges, refuses when
the worktree disagrees inside HEAD's own bytes, asserts the first id is `max + 1`
for its own series read from that same blob, and ships a planted control that
proves the merge preserves an id-less paragraph and that the overwrite form
drops it — D369's invisible case, made visible. Its sibling
`scripts/check_record_reconciliation.py` closes the `LESSONS.md` gap D369 filed
as owed, and carries `NUMERICS_KNOWLEDGE.md` on the same shape.

**When you catch an instruction that contradicts a standing rule, fix the
instruction's mechanism, not the instance.** The lane that received this one
could have merged by hand and moved on; the instruction would have been reissued
to the next lane unchanged.

## L-241. A ratio of two rounded percentages is not the ratio of the two quantities — form every derived figure from the underlying values

**The rule.** Any derived quantity — a ratio, a factor, a speedup, a "×N worse" — is computed from the **raw values**, never from the already-rounded figures a log or a table prints. If only rounded inputs are available, the derived figure carries the precision of the rounding and says so.

**Why.** Rounding error that is invisible in an absolute figure is amplified by division: two 4-decimal percentages that are each correct to their last printed digit can produce a ratio wrong in its **third** significant figure, and the wrong ratio is then quoted as a headline.

**The incident.** A3 rung 2, 2026-08-22. The lane formed `0.1586 / 0.0172 = 9.2209` from the log's printed percentages and published **9.22×**; the supervisor's independent recomputation from the raw analytic and FD values gave **9.2084×**, i.e. **9.21×**. Correction applied by **quote-and-strike per L-32** — both original occurrences struck in place, pointing at a dated correction that quotes the original wording verbatim (`0f56460d`). No verdict, band, gate, prediction score or cost figure moved: the two relative errors themselves were correct and the ratio was descriptive. **The general point is why it was caught:** this was the second wrong number from the same competent lane in one day (the first was a prediction band), and **both were caught only because somebody did the arithmetic again from the raw values instead of reading the summary table.** A supervisor's big-claim check is that recomputation, and it must not be delegated to a reading of the claimant's own table (`SUPERVISION_CHARTER.md` §3).

### L-241 - CORRECTION (2026-08-22, supervisor, on the lane's own objection)

L-241's closing sentence reads as though independent recomputation caught **both** of the A3 lane's wrong numbers that day. It caught one. The **9.22×** was arithmetic on rounded inputs, and recomputing from raw values is exactly the L-241 rule. The **P16 cold-start band** was a wrong *model* of what the quantity measures — the continuity error was believed to be a function of the initial field and mesh, and is in fact evaluated after the first pressure solve and therefore decomposition-dependent (N-D12). No recomputation of the lane's own number would have found that; what found it was the measurement landing outside a registered band and the lane having to say why. Two mechanisms, two defences: **recompute derived figures from raw values** (this lesson) and **register a band and explain every miss** (prediction-first). Read L-241 as covering the first only, or the second will slip through it.

## L-242. A trivial baseline at a deliberately wrong step is not merely inaccurate — it is irreproducible in magnitude AND sign, and it takes two draws to show it

**The rule.** Register the Charter-§2c/§4 trivial baseline **per item**, and buy it, rather than
citing a prior item's number for the same probe on the same case. The second draw costs ~2 primals
and converts the claim from *"the harness can return a large number"* into *"the harness returns a
**random** number when the step is wrong"* — which is the claim the clause actually needs. Where an
item does decline the re-buy, register the decline **conditionally**, with an assertable condition
(harness md5s, case identity, image identity) and the registered consequence that a mismatch voids
the decline.

**Why.** A single large error from a wrong step is consistent with two different worlds: a broken
harness, or a genuinely large derivative the good steps got wrong. Two draws of **opposite sign**
from the identical configuration are consistent with only one. The arithmetic is the tell: at
`s = 1e-8`, central FD divides by `2e-8`, so the solve-to-solve noise alone (`δ_repeat` = 2.2104e-06,
N-D15) manufactures a spurious derivative of order **1.1e+02** — of arbitrary sign.

**The incident.** A6 CRM N=16, 41,760 cells, np=1, `dafoam-idwarp-rot:v1`, 2026-08-22. The
`rung_n16_fixed_reference` item bought `patchV` idx1 at `step = 1e-8` and read
**+152.94101058174746** against an adjoint of `+9.01684e-03` — 99.9941%, registered as > 50%, HIT.
The `rung_n16_remaining_components` item **declined to re-buy it by name**, conditionally on the
harness md5s matching. `gen_arm.py` matched byte-for-byte; `run_arm.sh` could not, because it
hard-codes its own run root — **two lines, the run-root path and the container name**. The registered
void condition fired **before launch**, the baseline was re-bought, and it returned
**−28.746957145275864**: **100.031% and the sign reversed.** Same case, image, driver, DV, step and
objective; two runs; answers differing by a factor of 5.3 and in sign. **The condition nobody
expected to fire produced strictly better evidence than the decline would have.** (`9d5029e8` §4.3,
§9 Amendment 1.)

**Corollary.** An md5 condition on a helper script that legitimately must differ per run root will
fire every time. That is not a defect in the condition — write it anyway, and let it buy the control.
## L-243. A change-based settle criterion cannot tell convergence from damping — a more strongly damped iteration reaches the change bar earlier, further from the answer

**The rule.** Never gate two operators' equivalence on their residuals or their
settle behaviour; gate it on the **targets they write**, with a tolerance derived
from a **field-space distance**, and treat any change to the iteration's damping
as a change to where a change-based criterion stops. When a pre-registration
derives a field-space tolerance from a linear-solver residual bound, it has
conflated two different metrics, and the measurement will land wherever it lands
— R5C registered `1e-6` from the `1e-8` residual tolerance and measured
**1.1848e-04**.

**Why.** A settle criterion of the form `initRes < a` AND `max|Δf|/max|f| < b`
sustained N iterations measures **change**, and change bounds nothing about
**distance to the fixed point**. R5C's Patankar split moves the negative source
onto the diagonal, which is precisely a stronger damping of the outer iteration:
`omega` stops going negative, and the same damping makes the change bar arrive
sooner. On `alpha_10_12000_4048` the repaired run settled at iteration **853**
against the legacy **1362** (−37 %) and stopped `1.18e-04` away in relative L2 —
not flat, not clipped, not visibly wrong, simply short. Eleven of twelve cases
settled at the **identical** iteration and agreed to 1e-7–1e-11: the fixed point
is shared (confirmed, as registered); the stopping point is not. This is L-235
one notch subtler — L-235: change cannot tell convergence from *clipping*; here:
change cannot tell convergence from *damping*.

**The corollary on ratio criteria.** R5C's G3(d) required
`initRes(1)/initRes(convergedAt) ≥ 1e6` on the registered premise that runs
start at O(1e-1). Measured: only 3 of 27 do; `initRes(1)` spans 4.7e-05–0.56
because the initial condition is the baseline SST field, so `initRes(1)`
measures **the quality of the initial guess**, and the criterion rejected R4's
own W2-validated reference (`PHLL10595`, 9.167e5, 8.3 % short). A residual-fall
*ratio* is an absolute bar divided by a number that is not about convergence.
The absolute bar was already in the settle criterion; the ratio added a way for
a good initial guess to fail.

**Where it fired.** `cases/RANS_LES_closure_models/R5C_omega_repair/RESULTS.md`
§5–§6, graded by the frozen comparator against `PREREGISTRATION.md` — thresholds
left standing as written, exclusions reported (rule 2). Docket D465.
## L-244. A GCI band read from a pre-asymptotic triple can be smaller than the error it covers — and the cure is a fourth level, not a wider Fs: the implied order is the artefact and it collapses.

**Where it fired.** T10a-R (docket D466), the refinement arm on T10a's B1
ceiling GATE FAIL, graded 2026-08-23 by the frozen `analyse_t10aR.py` against
predictions registered before any solve.

**The pattern, now measured twice and resolved once.** On T10a B1 and T9a R1
the c/m/f triple's successive differences implied an order (p 1.480, 1.738)
faster than the actual level-error decay (~first order), so the Fs = 1.25 GCI
armed a band smaller than the miss it was supposed to cover (0.077 % vs
0.125 %; 0.92 mK vs 2.41 mK). T10a-R added the fourth level: the m/f/x triple
is CONVERGING at **p 0.6850** — the implied 1.480 was the artefact — the band
opens to 0.14724 % and **covers** the 0.07986 % error, dev/band 0.542, on
every box row (0.54–0.75). The level-error ratio meanwhile stayed ~1.5
(measured 1.5607), exactly the branch the pre-registration's §2.1 laid out in
advance as "branch 1" of its own arithmetic tension.

**The rule to carry.** When a triple's implied p exceeds the level-error decay
rate visible against an exact or trusted reference, do not report the GCI as
coverage — the band is a function of the implied order and the implied order
is the thing in error. Buy the fourth level (here $0.11 predicted, $0.34 gross
with contention) before arming any band from such a triple; and register the
two-branch arithmetic (error-ratio-holds vs difference-ratio-holds) before the
run, so the outcome discriminates rather than confirms.

**Second finding in the same arm, same discipline.** The registered
"quadrature is innocent" prediction (move ≤ 0.010 %) was falsified — 2AI
midpoint → 2LI contour integration moved rows up to 0.17547 % toward exact —
while the analyst's source-reading reservation, registered beside the
prediction before the solve, was confirmed. Registering the reservation in
advance is what made the miss a finding instead of a hindsight claim.


## L-245. On a shared multi-section file, "only my paths" is not "only my content" — assert your hunks fall inside your own section before update-index

2026-08-23, verification-supervisor, its first board commit. `docs/LAB_STATE.md` is one path carrying six teams' sections. The private-index protocol's assert (`git diff-tree --stat $H $T`, "only your paths") PASSED on commit `d97ed4c9` while the working tree's dafoam section was stale relative to HEAD (`70c605f0`, section written 19:35Z, committed 19:36:57Z): the commit reverted 84 lines of the dafoam board in git — including its two-session claim ledger, the block that says which live session owns W4 — while touching only "my" path. The non-optional post-commit verify (`git diff HEAD~1 HEAD`) surfaced a second hunk at line 182, and the clobber was repaired forward within minutes (`6ae77c79`, dafoam section restored verbatim from `70c605f0`; end state verified as `70c605f0` plus the verification section only). Mechanism not established: the working tree held an 18:17Z dafoam section while git held the 19:35Z one, so either `70c605f0` was committed without its content ever being written to the working tree, or something overwrote the working file after that commit; flagged to the chief and the dafoam team rather than investigated cross-team. The rule: **before `update-index` on a shared multi-section file, run `git diff HEAD -- <path>` and assert every hunk lies inside your own section.** A hunk in a foreign section is either somebody's newer committed work about to be reverted or somebody's unfinished work about to be landed under your name — inspect, rebuild your file as HEAD's content plus your own section, and never commit the foreign delta blind. The path-level assert cannot see this class at all; a heading-grep over the diff (the form `d97ed4c9` used) cannot either, because content hunks inside a foreign section never touch its `##` heading line. Only a hunk-position assert sees it. This is D369/L-223's failure family reaching the one shared file every team writes.
## L-246. A generated instrument's source column is part of the instrument — cite-check the generator against the page, not the manifest

2026-08-23, closure lane, FS6. `FEATURE_LIBRARY.md` is generated: its measurement columns (invariance flags, dead flags, definitions) come from measured JSON and were all correct — but its source column is hand-typed literals inside `make_feature_library.py`, and three of them were wrong for months while every measurement beside them was right. `q7_viscRatio` and `q11_turbReynolds` were cited to Kaandorp Table 1 p. 25, a table that contains neither (nine scalars, no viscosity ratio, no turbulent Reynolds number) — their real origin, Ling & Templeton 2015, is PENDING-MIT, so two of 110 features had **no on-disk printed source at all** and nothing said so. `q10_streamlineCurv` was cited to Kaandorp when it is Wang, Wu & Xiao 2017 Table 1 p. 10 (Kaandorp's set is Wang's ten *minus* curvature). The Wu 2018 cites were one page early throughout, and a five-dagger claim stood where the printed table daggers four. The errors survived because the citations were checked against the retrieval **manifest** — right paper, title-page verified — rather than against the cited **page**: L-144 title-page verification proves a file's identity, never that a specific claim sits on a specific page of it. Found by FS6, whose rung definition is precisely to re-read every feature table with page cites; independently verified by the closure supervisor before repair; repaired at the generator, never at the generated file (D467; commits `9fb0891f`, `01430485`). The rule: **a hand-typed citation inside a generator is a claim like any other — it is verified by opening the cited page, and a source whose paper is not on disk must say NOT ON DISK in the cell itself, so the gap is visible where the feature is used.**


## L-247. A heredoc inside an `&&` chain ends the chain — and a scratch artifact consumed by a later step outlives the invocation that should have rebuilt it

2026-08-23, verification-supervisor, commit `890bfa7f` (repaired at `54f53bbb`). The private-index commit was written as one invocation: `append_record && python3 - <<EOF ... EOF` followed by the hash-object/commit steps. Two defects compounded. **(1) The heredoc terminated the `&&` chain**: everything after `EOF` ran unconditionally, so when `append_record` REFUSED (a peer had taken D467 seconds earlier — correct refusal) and the blob-rebuild python was skipped, the commit steps still executed. **(2) The blob path in the scratchpad still held the PREVIOUS round's file**, so `git hash-object` shipped a stale board wholesale: closure's 20:20Z section, cfd's `08ea9dbb` correction and the chief's GPU-quota row were all reverted in git — the third L-245-class clobber in one day, this one caused entirely by the committer's own tooling. The non-optional post-commit verify caught it (a 91-line delta where ~12 was expected). The rules: **never place a heredoc inside a `&&` chain whose later steps must not run on failure** — put the logic in a script file and run it as one command, or chain with explicit `set -e` semantics; **delete or uniquely name every scratch artifact a commit step consumes, in the same invocation that builds it**, so a skipped build step produces a missing-file error, never a silent stale read; and **assert the diff-tree stat against the expected shape before commit-tree** — the repair commit (`54f53bbb`) did all three, verifying every foreign board section byte-equal to the pre-damage parent before committing. A refusal from a guard (here `append_record`'s max+1 assert, working exactly as designed) must abort everything downstream of it; a chain that survives its own guard's refusal has disarmed the guard.


## L-248. At lane close-out, grep the frozen pre-registration for every artefact it names — a deliverable that never appeared leaves no trace in the lane's own memory, so no departure list catches it

2026-08-23, closure lane, R4/R5. R4's frozen `PREREGISTRATION.md` §7 registered a file by name — *"`COVERAGE.md` ships with `MODEL.md` and states: each selected feature's range on each training family against the others; the pooled training range; and what a future test exposure must check"* — and Addendum A1 later confined its own consequence to that file. **It was never written.** The lane that closed R4 documented **thirteen departures (D-1…D-13)** and **ten** separate "what this lane cannot see" bullets, including the unrun `b^Δ` static-injection arm, the missing shelf-D band and the absent realisability threshold; the strings `FS5` and `coverage` appear **zero times in the entire 1,313-line `RESULTS.md`** (control: `FS2` appears six times under the same grep). The omission was found a day later by an unrelated records lane tracing the R5 rung's `Re_y` constraint, disclosed as departure **D-14** in a dated addendum, and the deliverable produced late (`RESULTS.md` §12; `R4_sparta_build/COVERAGE.md`; D467-adjacent, supervisor-verified). **Why no self-audit caught it, and this is the transferable part:** a departure list is written from what the lane *did* — every entry in R4's is a thing that happened and was remembered, a repair attempted, an arm withdrawn, a rule revised. **A deliverable that was never started produces no experience to remember.** Checking the registration against the work finds every departure of commission and none of omission, because the two are searched from opposite ends. The rule: **at close-out, grep the frozen file for every backticked filename and every "ships with" / "is written" / "is reported" clause, and assert on disk that each named artefact exists — mechanically, from the registration inward, not from the work outward.** It costs seconds, it is the only direction that can see an absence, and the D-14 finding is what it would have caught.

## L-249. An audit that freezes its instrument must commit it — an uncommitted screen makes the headline permanently unreproducible

2026-08-23, verification team, from the EXTERNAL_REFERENT re-sweep (`e3f3b521`). The 2026-08-16 audit's section unit reproduces exactly (4,844 sections at `df4d4cbe`, on the nose) — but its bucket figures (26.3 / 5.4 / 6.0 / 62.3 % and the 280 (90–560) estimate) cannot be re-derived by anyone, because the referent-screen script that produced them was never committed: `git ls-files` carries no such script, and the published 1,549 verification-section count matches no reading of the audit's own §2 rule as written (the literal reading gives 1,008, the nearest gives 1,567). This is the ledger audit's citation-into-an-uncommitted-tree defect one step worse: there the artifact existed and the pointer dangled; here the instrument itself is gone, so the numbers are not wrong — they are unfalsifiable, which is worse. The rule: an audit or sweep that publishes a derived figure commits the script that derived it in the same commit as the figure, exactly as a comparator is frozen with its rung; a screen too ad hoc to commit is too ad hoc to headline. Repair for the standing instance: rebuild the screen, commit it, and re-derive the buckets — or strike the bucket figures with a dated note that names them unreproducible. Queued as a verification next action.
## L-250. A per-stage timeout cap is both the bound on a hang and the size of the loss — set it to the smallest value that fits the predicted run, not the largest the budget allows.

W4 M1+M2 (`64479072` §5a): M2 attempt 1 crashed in Python at ~20 s and `mpirun` then hung
(`Forwarding signal 18 to job`, 1.13 GiB flat); the registered 300 s cap bounded the burn at
20.00 core-min — the only reason it was not unbounded — but the stage was predicted at 150–260 s,
so up to ~280 s of hang lived legally inside the cap, and that 20.00 core-min is exactly what
defunded the item's decisive O2 stage (19.88 remaining vs the 25.0 floor). The cap worked as a
guard and failed as a price. Register `timeout` at the predicted-run envelope plus a stated
margin; the budget ceiling is a different number with a different job.

## L-251. Copying a prior run's invocation is not copying its environment — a pre-registration that pins a container's uid pins the mount's directory mode in the same sentence.

W4 M1+M2 (`64479072` §5a): A6's `-u 1002:1002` was carried forward; A6's `drwxrwxrwx` run root
was not. OpenMDAO's `reports/` write then hit `PermissionError` on a `drwxrwxr-x` root and the
stage died before the primal — 20.00 core-min under L-250's hang. Same family as
`INSTRUMENT_INTEGRITY_LEDGER.md` A7/A8, both "Diagnosed (trivial)": a trivial class recurs until
the prereg pins the environment (uid, mode, cwd expectations), not just the command line.

## L-252. A session-shared scratchpad can hand a commit chain a stale artifact with the right filename — every staged file is asserted to have been produced by this chain, in this invocation.

2026-08-23, dafoam board commit `4932a7c3` (disclosed by its author in `0d96119d`): the
section-build step failed on the author's own wrong anchor string, the merge step then failed
file-not-found — and the staging step found a STALE `LAB_STATE_merged.md` under the generic name
it expected, left in a scratchpad shared by two sessions resuming the same session id, and
committed it: four teams' board sections reverted for a two-commit window (healed by `537a52d5`'s
independent rebuild). `set -e` did not stop the chain. L-186 said the scratchpad is never a
handoff channel; the sharper corollary is that in shared temp, a generic filename IS an
accidental handoff. Per-invocation unique filenames, `test -s` plus a provenance assert (the
producing step's own success) before `git hash-object`, and explicit `&&` chaining — every time.

## L-253. A private-index protocol that never writes the worktree makes the worktree stale BY DESIGN — and it selectively destroys the work of exactly the teams that follow it

2026-08-23, from the chief's byte-exact reconstruction of `890bfa7f` on the board-incident thread; landed by verification. The reconstruction proved the stale base that reverted two teams' board sections **need not be the worktree at all** — a blob-based commit (`hash-object` + `--cacheinfo`, the shape both this team's scripts and `lab_state_section.py` use) never writes the worktree, so after every such commit the shared worktree lags HEAD by that team's own sections. The next whole-file worktree commit by anyone — `update-index --add` on the shared path — then reverts exactly those sections: **the protocol's own users are the victims**, because teams that edit the worktree directly keep their sections current in it, while teams that commit from git-read bases exist in the worktree only as stale text. Four incidents in one day (`d97ed4c9`, `070da305`, `890bfa7f`, `4932a7c3`) are this mechanism from both sides. Interim discipline until Sanaa rules on the base-from-git amendment (docket row this commit): after a blob-based commit to a shared file, fast-forward the worktree copy **only after proving each lagging section byte-equal to a committed ancestor** (so nothing uncommitted can be destroyed), or leave it and say so on the board; and always take the base for the next edit from `git show HEAD:<path>`, never from the tree.

## L-254. L-245 has its assert now, and the assert gates nothing yet — rule 14 is unmet until `check_board_sections.py` is wired

2026-08-23. `scripts/check_board_sections.py` (`332a15d1`, selftest 11/11 with planted-control recognition) is L-245's assert-at-the-call-site: it refuses a board commit whose diff crosses foreign sections without a `Lab-Team:` trailer, with a `Board-Repair:` escape for legitimate restores. Verified against real history: refuses all FOUR incidents (`d97ed4c9`, `070da305`, `890bfa7f`, `4932a7c3`) and passes 5/5 known-good board commits — including correctly refusing the `6ae77c79` repair absent the escape trailer. Its sibling `check_board_reconciliation.py` (`f97443be`, selftest 7/7) is the board's pre-edit reconciliation and currently exits 4 on the live tree because HEAD carries a doubled `## cfd` heading (`fe065ca6`, cfd's to repair) — expected until that fix lands. **Both are post-hoc and gate nothing**: no hook, no `check_harness` wiring, and adoption rides with `docs/BOARD_BASE_RULE_PROPOSAL.md`, which is Sanaa's decision. Under rule 14 (a lesson is not applied until every call site asserts it) L-245 therefore remains UNAPPLIED, and this block exists so nobody reads the scripts' existence as protection. Stated limits carried honestly: trailer truthfulness is unverifiable while every commit shares one git identity, and the reconciliation check is blind to a stale base held in an agent's context.

## L-255. A divergence-diagnosis pre-registration must pre-declare the label for a divergence CRASH — a generic crash→`BLOCKED` rule turns the most informative outcome into an empty outcome-map cell

2026-08-23, cfd team, from the DPW8_V2 L4 divergence diagnosis (results `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md`, `b8fe7eea`; prereg frozen at `99f939ee`). The frozen §6 said what every completion rule says — an arm that fails any completion clause is `BLOCKED`, and a crash goes to the supervisor for triage — and §7's outcome map said `any | BLOCKED → PENDING`. Both are correct rules, and together they cost the experiment its best finding. Arm A took SIGFPE at iteration 182 of 600: under-relaxing p 0.25→0.15 and U,k,omega 0.6→0.3 did not calm the case, it converted the gate run's *bounded-but-wrong* state (|Cd| pinned at ≈431 through iterations 300–600, two bounding-k events) into unbounded growth to Cd ≈ 1.6e+37 with **zero** bounding-k events — a qualitative failure-mode shift, and far more informative about the mechanism than a tidy NOT BOUNDED would have been. Under the freeze it is `BLOCKED`, it is not graded, and the outcome-map cell reads `PENDING`: the diagnosis is formally undecided on the very arm that produced the most signal. **The error is in the pre-registration's design, not in the grading.** A diagnosis whose subject is a divergence must anticipate that an arm may diverge *harder*, and pre-declare a label and a grading path for a divergence-crash — e.g. a registered `DIVERGED` outcome distinct from `BLOCKED`, with clauses evaluable on the truncated window and a stated minimum iteration count, so an overflow is a measured outcome rather than a missing one. The fix belongs in the **next** diagnosis pre-registration's design. It emphatically does **not** belong in post-hoc relabelling: §6 was frozen before compute, gates close at first compute, and re-reading a crashed arm as NOT BOUNDED after seeing its log is exactly the fitting the freeze exists to prevent. The cfd team's record keeps `BLOCKED` and puts the mechanism in a subsection explicitly labelled triage. Corollary for any crash-bearing family: `BLOCKED` is a statement about the *run*, never about the *physics*, so a pre-registration that routes physics information through `BLOCKED` has thrown that information away by construction.

## L-256. A commit-message file in the shared scratchpad is racy WITHIN one session, not only across sessions — the message that lands can be a peer's, and only a `git log -1` read-back catches it

2026-08-23, heat-transfer, from `878f1556`. L-186 says the scratchpad is never a handoff channel and L-252 sharpened that to "in shared temp, a generic filename IS an accidental handoff" — both were read as *cross-session* hazards. They are not. Two lanes of the **same** session, working concurrently, wrote their commit-message files to the same generic scratchpad path; a cfd lane's `printf > msg` landed in the window between this lane's write and its `commit-tree -F msg`, and `commit-tree` faithfully committed a message this lane never wrote. The result is a commit whose **tree is right and whose message is wrong**: `878f1556` carries the K0cG D470 cost addendum — a single file, `docs/campaigns/F14-cooling-ladder/K0cG_RESULTS.md`, +116 lines — under the cfd lane's D481/L-255 text. Note what did *not* catch it: the private-index protocol's own asserts all passed, because every one of them examines the **tree** (`diff-tree --stat` before, `git diff HEAD~1 HEAD --stat` after) and none examines the **message**. A protocol that verifies only what it stages is blind to half of what it writes. The rule, both halves mandatory: **(1) every commit-message file carries a lane-unique path** — `$$` plus a task-specific name, never a generic `msg`/`commit_msg` in a shared directory; **(2) after `update-ref`, read the message back** with `git log -1 --format='%H%n%s'` on the new sha and confirm the message that landed is the message that was written. Corollary on the repair: the corrective tip rewrite was refused by the permission classifier and was **not** routed around (T10aR ADDENDUM-2: a denied command is answered, not circumvented), so the mislabel stands and is corrected by record — docket D482 — rather than by history. That is the cheaper outcome only because the tree was verified independently; had the race swapped trees instead of messages, no record would have sufficed.
## L-257. WebSearch `allowed_domains` is unreliably honoured — a domain-restricted search establishes nothing about the venue until every returned URL is read back in-domain, and the nonsense-token floor on GitLab-issue surfaces is a full page

2026-08-23, dafoam team, from the D460 novelty-sweep completion audit (liaison addendum `73563d98`), verified by the supervisor with a controlled A/B before recording. The lane measured the violation twice: searches restricted to `develop.openfoam.com` and to `cfd-online.com` each returned ten `arxiv.org` PDFs. The supervisor then ran two searches minutes apart under the **identical** `allowed_domains: ["develop.openfoam.com"]`: the nonsense-token query (`zzzqqxnonsensetoken12345 solver issue`) returned **10/10 in-domain** — topically-plausible OpenFOAM GitLab issue links, extending L-234: the zero-floor on an issue-tracker surface is not 1 hit but a **full page of in-domain topical noise**; the real query (`GAMG convergence tolerance residual differs`) returned **10/10 `arxiv.org`** — the restriction wholly ignored. Same tool, same parameter, opposite behaviours, query-dependent, with both extremes measured. Binding consequences: (a) passing a domain to the filter is NOT searching that venue — every returned URL is verified against the intended venue before the search counts as a search of it; (b) an off-domain result set is a **no-op at that venue**, recorded in neither direction, never as a zero; (c) a venue zero counts only beside a same-session in-domain positive control on that venue; (d) any prior disposition in this lab resting on an unverified domain-restricted search is weaker than it reads and is re-audited before being cited. One asymmetric corollary: the A/B also proved WebSearch's index DOES reach `develop.openfoam.com` (ESI GitLab) even though direct fetch dies at a Cloudflare 403 — so that venue, recorded `BLOCKED` in the D460 sweep, admits a title-level search route, per-search in-domain-verified, with bodies still unreadable; weaker evidence than a read venue, honestly labelled, better than an unread one.

## L-259. An adjudication that DELETES record bytes must first read every document that cites the artifact — not only the docket row that assigned the adjudication; and "recoverable from history" is weaker than "recoverable from HEAD" wherever a standing record points a reader at the path

2026-08-23, heat-transfer, D477. The supervisor adjudicated eight tracked
K2bP heat-balance artifacts as DELETE and executed it at `a311d872`, then
reversed itself 40 minutes later at `0c742c66` when a delayed citer-sweep read
the deleted bytes and found full ledgers in them. What made the wrong call
available was the *reading surface*: the D477 row carried the D390 mechanism
attribution — reports "carrying no ledger", written by audits aimed at time
directories that never existed — and the adjudication was taken on that row.
The row did not carry the counter-evidence, and the counter-evidence existed,
committed, in a document the row itself cites two sentences earlier.
`docs/EXTERNAL_REFERENT_AUDIT.md` section 11.4(b) states that these four
iterations are **exactly** the ones backing D381's published recovery figures,
155.55 W at 400 and 315.57 W at 800. They are: the plant/noplant pairs read
-1.517859e+02 vs +3.764241e+00 W (difference 155.550141 W) and -3.072705e+02 vs
+8.296449e+00 W (difference 315.566949 W), each a full ledger with in/out terms,
a mass-balance row and a tolerance verdict. So the D390 attribution was simply
false of these eight files, and the row's "Referenced nowhere" was false too —
the figures are cited at `K2b_PILOT_RESULTS.md` lines 386, 522 and 556, at
`docs/LESSONS.md:5649`, and in the audit itself.

The second half is the one that cost more than a wrong attribution. Audit
11.4(b) ruled the *on-disk* clearing "a filing defect, not a lost measurement",
and it ruled so **on a stated condition**: "the bytes are still recoverable from
HEAD". A benign ruling that names its own condition is a live constraint on
every later action, not a settled verdict — and the delete removed precisely the
condition, converting a filing defect into a lost referent while every citing
document went on pointing readers at the path. The delete's own defence, "bytes
recoverable at every pre-deletion sha", is true and is not the same claim: a
reader following `K2b_PILOT_RESULTS.md` to an artifact reaches HEAD, not the
reflog, and history-recoverability rescues an archaeologist, not a reader.

Binding practice, both clauses:
**(1) Before deleting tracked bytes, grep the corpus twice** — once for the
filename or path, and once for **the numbers the file contains**. The
filename sweep alone would have missed this: the five citing documents cite the
*values* (155.55, 315.57), not the `HEATBALANCE_400.txt` path. The content
grep is the one that fires, and it is only possible if the bytes are read
before they are destroyed — so **read the artifact you are about to delete**,
which by itself refutes any "carries no ledger" attribution.
**(2) Treat "recoverable from history" as strictly weaker than "recoverable
from HEAD" whenever any standing record points a reader at the path**, and
treat a conditional benign ruling as a condition to be preserved, not a
clearance to be spent. Where a prior audit made its ruling conditional, the
adjudication must quote that condition and say what happens to it.

Scope honestly stated: the reversal restores HEAD only. The eight files are
still absent from the working tree, `K1_STANDING_THERMAL_CHECKS.md` (tracked,
cited by five documents) is still absent from it too, and who cleared the disk
and why remains unanswered — the reversal repaired the adjudication, not the
filing defect that provoked it.

## L-260. A shared scratchpad is shared BETWEEN CONCURRENT LANES — a scratch instrument can be swapped for a peer's mid-run, and only reading the output against the instrument's own identity catches it

2026-08-23, verification team, D472 repair lane; supervisor-verified from the lane's report before recording. The lane's mutation driver, written as `<scratchpad>/mutate.py`, was overwritten between runs by a concurrent peer lane's same-named file; the swapped run executed cleanly and reported on controls named C1/C6/H1 that do not exist in `check_verdict_cells.py` — that impossible content was the only tell. Second same-day instance of the class: L-256 proved it for commit-message files (the message that lands can be a peer's), this proves it for EXECUTABLE INSTRUMENTS (the results that land can be a peer's). L-186's hazard operates WITHIN a session between live lanes, not only across sessions via wipes. Binding practice: (a) every lane works in an isolated, lane-unique subdirectory of the scratchpad, never at its root; (b) a result produced by a scratch-path instrument is believed only after a read-back shows the artifact executed is the one the lane wrote — path uniqueness or content identity, the same discipline L-256 applies via `git log -1`; (c) a measurement from a colliding path is NOT A RESULT — re-run isolated, report only the isolated re-run (the D472 lane did exactly this, and the earlier agreeing numbers were still discarded).
## L-261. A sampled RSS "peak" is a floor, and the kernel counter and the summed tree disagree in BOTH directions — a peak claim must name its counter, its sampling interval, and its cap

2026-08-23, dafoam, B3 decomposition peak-RSS item (prereg `d062aace` + Addenda; RESULTS beside it), supervisor-verified against `peak_rss.json` before recording. The prior graded chain's 5 s-sampled figure of 6.156 GiB (`decomposition_np4/RESULTS.md:132` — which itself, correctly, claimed only that the cap was never approached at any observed moment) undersampled the true serial peak by **1.81×**: the re-measured kernel `memory.peak` is **11.133 GiB** (11,954,151,424 B) under a 12 GiB cap — 92.8 % of cap — with M0 PASS on all 18 identity checks tying the peak to the same graded configuration. Two binding consequences. (1) A sampled peak is a **floor**: quote it as "≥, sampled at N s", never as a peak; peak claims ride the kernel counter (cgroup `memory.peak`) with the sampler as corroboration. (2) The registration's own "`memory.peak` ≥ summed tree RSS *by construction*" was **refuted on both arms** (kernel below tree by 0.370 and 1.719 GiB) — the two instruments measure different things and neither bounds the other; candidate mechanisms were named and deliberately not measured (its own item if bought). Corollary: every figure from a capped container is a peak **under that cap**; the unconstrained peak is not derivable from it and is a new registration with its own price.

## L-262. A memory launch gate must exceed the floor PLUS the arm's own measured peak — a gate that admits an arm whose consumption drives the host under the mid-run floor is a registration that kills itself

2026-08-23, dafoam, A3 rung-3 patched arm (prereg `97a54c07`; NOT A RESULT, stopped by memory at 85 s of 2600 s, 0 of 11 checkpoints). Supervisor-verified arithmetic: the registered gate `MemAvailable ≥ 16 GiB` opened at 16.02 GiB; the arm's own RSS reached 9.2 GiB (inside its 15 GiB ceiling — the arm did not exceed its budget, the box did); 16.0 − 9.2 = **6.8 GiB < the registered 8.0 GiB host floor**, so the floor broke 60 s after the gate opened and the guard — proved able to kill by its own selftest three minutes earlier — correctly killed the arm. The gate/floor pair was **self-defeating at registration time** for any arm peaking above (gate − floor) = 8 GiB; consistency needed a limb ≥ floor + measured own-peak = 17.2 GiB, and the shipped arm's known 11.65 GiB peak implies worse. Binding rule for every future memory-gated registration: the launch gate is derived as **floor + the largest measured (or explicitly estimated, labelled so) own-peak among the arms + margin**, and a registration whose gate cannot satisfy its own floor at the registered peaks is refused at review, not discovered at kill time. Both frozen numbers were left untouched; the successor item re-registers with a consistent limb. The instrument was right; the registration design was wrong — spend the review on the pair, not the guard.

## L-263. A refusal piped through `tail` is an approval, and `update-index --add` after a refused merge stages exactly the stale bytes the tool refused — on an append-only record, ANY deletion in the pre-commit diff is the alarm

2026-08-23, dafoam supervisor, self-caught and repaired same session. Mechanism, measured on the lab's own history: a records commit chained `append_record.py ... | tail -3` for three paths in one `&&` chain — the pipe made every segment's exit status `tail`'s 0, so the chain survived TWO refusals (LESSONS: ids had moved, peers landed three lessons in the interim; DOCKET: stale truncated worktree) — and the follow-up `git update-index --add -- <all three paths>` staged the DOCKET **worktree** file the tool had just refused to touch. Damage: commit `41e566c3` truncated 561 characters off the D473 row — verification's OWN 21:14:28Z stamp-correction, the exact repair the chief's timestamp standing had just mandated — while its `diff-tree --stat` read innocently (`docs/DOCKET.md | 2 +-`). Caught in the post-commit verify by content, repaired at `6da8a162` (bytes restored verbatim, asserted by prefix and length). Binding: (a) never pipe a refusal-capable tool inside a commit chain — capture output to a file and test the tool's own exit status (`PIPESTATUS[0]` if a pipe is unavoidable); (b) after `append_record.py`, stage a path ONLY if that run printed `WROTE` for that path; (c) on an append-only record file, the pre-commit `diff-tree` must be asserted **insertions-only** — any deletion on LESSONS/DOCKET/NUMERICS/COST_CALIBRATION is a stale-base or truncation alarm, never a plausible edit (generalizes the chief's COST_CALIBRATION discipline to every record). Sibling of L-256 (masked failure between write and commit) and of the L-223/L-253 stale-base family — this instance adds the pipe as the mask and the shared worktree as the payload.

## L-264. A kernel-enforced memory cap cannot be denied, forgotten or armed late, and it fires at the byte — but a cap set for co-tenant safety is also a cap on what the item can measure, and when it binds the item returns PENDING, not an answer.

W4 O2 re-buy (`8d48fd46` → results committed by the supervisor after the lane's death): the cgroup
guard (`--memory=20g --memory-swap=20g --oom-score-adj=500`) replaced a watcher script whose start
command was under a permission denial. It worked perfectly — rc 137, `memory.peak` exactly
21,474,836,480 B, box undisturbed, no permission needed — **and** it is the sole reason the §3
decision was not bought: `splu` needed more than 20 GiB and was killed inside its first threshold.
The pre-registration registered that trade before the run (§7a), which is the only reason it can be
reported as a designed cost rather than discovered as a surprise. Register the cap, register the
outcome if it binds, and never call a censored peak a measurement of what the job needed.

## L-265. A spend prediction is only tested by a run that stops for the reason the prediction was about.

Same item. Both spend predictions — O2R-P5 (wall 1500–2700 s) and C-P1R (the scipy exact-LU exceeds
25.0 core-min) — are MISSes that measured a memory cap, not a factorization; the run ended at 900 s
because memory bound, so the 0.43× ratio measures an interruption. The C-P1 hypothesis is now two
attempts and zero tests old: first the factorization never ran (`W4_M1M2_RESULTS.md` §4f), then it
ran and never finished. A third attempt must change the binding constraint or it will produce a
third untested MISS. In the calibration ledger such a row attributes its gap to the misprediction
that truncated the run (here the memory band), never to the untested duration estimate.

## L-266. A registered exact-arithmetic rule implemented with a floating-point comparison can skip its own rung — dry-run the rule on its ladder before the freeze.

Curriculum D1 (`f07256fb`, addendum §16): the registered step rule reads `s_hi := smallest rung with
s_hi ≥ 3·s_lo`, so for `s_lo = 1e-4` the registered answer is the ladder's `3e-4`. In binary
`3 × 1e-4 = 3.0000000000000004e-04 > 3e-4`, and the comparison as first coded skipped the registered
rung and would have graded at `1e-3`. Found by the lane by checking the implementation against the
rule text before any FD ran — a `VERIFICATION_CHARTER.md` §2d.1-eligible repair, disclosed with md5s
— but it cost a voided arm (0.30 core-min, named waste) and a post-first-compute edit the
pre-registration's own §4.2(c) had forbidden. The whole class is closed by one habit: run the frozen
rule on its frozen ladder with a synthetic `|J|` and `η` **before the freeze**, and freeze the printed
selections beside the rule.
## L-267. A learning rate is not an optimiser — reproducing a paper's rate under a different update count is a different experiment, and a batch size chosen for the cost estimate silently changed the optimiser

**The rule.** When a pre-registration claims to run "the paper's own optimiser",
register the **update count and the update granularity** (per-point, mini-batch,
full-batch), not the epoch count — and cost *those*. Any batch-regime choice made
to fit a throughput estimate is an optimiser change and must be written down as
one, beside the departure it was meant to remove.

**Why.** The Ling2016 GPU arm registered ARM-A as "Ling's own SGD at 2.5e-7, 200,000
epochs, full batch by construction" — full batch chosen because a 7,000-parameter
network is launch-bound and the GPU-hour estimate needed it. The paper's own text
(sidecar l.131–132) says the weights were *updated after each training point*.
On 341,717 training cells that is ~3.4e5 more updates per epoch than the arm ran:
the arm removed the CPU lane's learning-rate departure (D3) by introducing an
update-count departure five orders of magnitude larger, and the registered
falsifier then fired on the wrong question. Measured: the TBNN's validation error
did not move in 200,000 full-batch updates (one seed's best epoch was epoch 0),
while the same optimiser at the paper's MLP rate trained the control to 0.30–0.37.
The gate is graded as written; the finding is that the experiment tested "the rate
at one update per epoch", not the paper.

**Where it fired.** `Ling2016_TBNN/gpu/RESULTS.md` D-1, §3; frozen file §6.
Docket D490.

## L-268. A detached job survives the fleet; the bill survives with it — the completion-to-stop path for a paid node must not depend on a live agent

**The rule.** Before launching a paid instance that a session cannot stop, register
who or what stops it *at batch completion* when no agent is alive — a durable
completion marker and a stop path that does not route through a live session —
and cost the idle interval you would otherwise pay as waste. The specific
mechanism is an instance-behaviour decision reserved to Sanaa; the chief has put
a proposal to her, and no lane proposes or implements one on its own.

**Why.** The Ling2016 GPU batch ran under `nohup` and completed cleanly at
08:03:58Z while the session limit had killed every agent overnight; nobody
reported completion until 15:56:45Z. The node idled **7.88 GPU-h = $6.34
derived** against the run's own **10.71 GPU-h = $8.62** — waste at 73 % of the
spend, entirely attributable to the report-then-ask-Sanaa path having a live
agent as its single point of failure. This box has no AWS CLI, so "stop it from
here" was never an option; the honest register was "who stops it when nobody is
awake", and no file asked that question before launch.

**Where it fired.** `Ling2016_TBNN/gpu/RESULTS.md` D-2, §5; `docs/COST_CALIBRATION.md`
C-16. Docket D490.

## L-269. A threshold is only as real as the instrument that will read it — dimension every registered number against its reader's resolution BEFORE the freeze, or the gate grades the instrument

One pre-registration, three registered clauses, and **not one of them could be
served by the instrument that had to read it.** All three were found *after* the
compute, two of them at close-out, and none could be repaired because gates close
at first compute (`CLAUDE.md` rule 2).

`Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md`, frozen `0ebc9d53`:

1. **G0a: threshold 1e-10, instrument resolution 4.00e-07.** The solver-identity
   gate compares two `U` fields written `ascii` at `writePrecision 6`. One ulp of
   that representation in the largest component is a rel-L2 of **4.002936e-07**;
   the half-ulp quantisation floor is **1.822069e-06**. The registered 1e-10 is
   **4,003x** below the first. The gate read `0.0` and passed — correctly, the
   files are byte-identical — but two solvers agreeing only to 1e-8 would have
   passed identically. **The gate proves agreement to < 4e-07 and no more.**
2. **H5: threshold 1e-3, against a normalisation the control itself fails.** On the
   registered `U_bulk/L` normalisation the zero-correction `NULL` control reads
   0.262 — 262x the threshold — and on the curved CBFS mesh the gradient estimator
   floors at ~5e-3, a level the shipped converged SST baseline **and the LES truth
   itself** both exceed. The threshold could not be met by any field on that mesh.
3. **§6 convergence: "sustained for 100 iterations", against a solver that stops
   at first satisfaction.** `residualControl` terminates the run the first
   iteration its test passes, so a criterion phrased as a 100-iteration run is
   unsatisfiable by construction on exactly the rows that converge. Its
   stagnation fallback is phrased over "the last 500 iterations" and
   `writeInterval` wrote checkpoints every 5,000, so that limb could not be
   measured at its registered window either.

**The common failure is not carelessness about the physics. Every one of these
thresholds is defensible as a statement about the world;** each is indefensible as
a statement about a *measurement*, because nobody asked what the reader could
resolve. A pre-registration's evidentiary content is that the gate could not have
been chosen to fit the answer — but a gate the instrument cannot evaluate has a
foreordained answer too, and it is not the one the registration was reaching for.

**The rule.** Before the freeze, for every registered number, write down the
instrument that will read it and its resolution, and assert the threshold sits
**above** that floor with margin. The check is cheap and it is arithmetic:
`writePrecision` for a field comparison; the estimator's calibration on a field of
known answer for a derived quantity — and the CONTROL row's own value, which must
pass before the treatment is graded; the checkpoint interval for anything phrased
over a window; the solver's own termination logic for anything phrased as a run of
iterations. A pre-registration that names a threshold should name, in the same
sentence, what would be measurable if the claim were false.

**The tell at grading time is a zero, or a floor that the truth also fails.** A
comparator returning exactly `0.0` and a control row failing the same gate as the
treatment are both the same signal: the number is about the instrument. Rule 3's
planted control answers *"can the reader see anything?"* — it does **not** answer
*"can the reader see the thing the threshold names?"* Here the plant passed (the
reader reported 4.002936e-07 for a planted perturbation) while the threshold
remained 4,003x out of reach. **Plant the zero, and then also dimension the
threshold; they are two different checks and the first does not imply the second.**

**And when the defect is found after the compute, it is disclosed and referred,
never repaired.** Nothing in that pre-registration was changed; the three defects
are recorded in `RESULTS.md` §5, §6 and the 2026-08-24 addendum §A.5, and
referred to verification as D492. A lane facing two readings of one frozen
clause may not take the softer one; the supervisor ruled the registered reading
governs (D492). Drafted by the close-out lane 2026-08-24T16:09:33Z; landed by
the closure supervisor 2026-08-24T16:15:11Z with the id re-derived at commit.

## L-270. A bit-identity checkpoint gate has no floor, so a solver that creeps at the write-precision digit can never satisfy it — register a bounded relative-change floor, a plateau reading, and enough retained checkpoints to measure the first crossing.

**Where it fired.** E4a (docket D493), the curriculum's first rung. The
pre-registration defined iterative convergence as p, U and φ value-for-value
identical between the last two written checkpoints at `writePrecision 12`.
All five cases finished rc=0 with residuals 1e-10…1e-14 — and every physics
row was NOT A RESULT, because the iterates still moved by ~6e-11 relative
(tens of units in the twelfth digit) over 5 000 iterations. The gate was
honoured as registered; that is what the record shows and what a closed
gate must show. The defect was in the criterion's shape, not the solver.

**The rule to carry.** A convergence gate must state a floor it can be
satisfied at: a registered maximum relative change between the last two
checkpoints, derived from (a) the write precision and (b) the largest change
that leaves every graded interval untouched — and it must be paired with a
plateau reading over at least three checkpoints (change flat or falling, not
growing: L-243's damping-vs-convergence trap) and a `purgeWrite` large
enough that the first crossing of the floor is measurable rather than
inferred (T3 ext1's over-shoot was unmeasurable by construction at
`purgeWrite 2`). "Identical" is a floor of zero, and zero is not a floor
a floating-point iteration can be asked to reach.

**Kin.** L-243 (change-based criteria), T1c §3 (endTime, not residuals),
T3 ext1 §2 (a flat residual is a floor, not slow decay).

## L-271. A per-cell-iteration cost basis is not portable across solver classes — E4a's estimate from a `buoyantBoussinesqSimpleFoam` basis over-predicted laminar 2D `simpleFoam` by 13.6×; measure the basis on the solver class being costed, or label the estimate cross-class.

**Where it fired.** E4a's pre-registration (§4) took 7.5e-6 s per
cell-iteration from T1c's measured `STATUS.L_Ts_P_*` replicates — coupled
energy + `alphat`/k/ω, on a contended box — and predicted 2 285 core-s.
The rung ran in 171 core-s: measured 5.50e-7 s per cell-iteration on the
momentum-only, laminar, 2D solver. Ratio 0.0748×, ledger C-21. Not waste,
not contention (three peer solvers were live and pushed the other way):
pure misprediction from a basis measured on a different solver class.

**The rule to carry.** A cost basis is a property of (solver class, physics,
dimensionality, contention), not of "OpenFOAM". Before registering a cost,
either cite a basis measured on the same solver class and physics, or state
the basis is cross-class and register the factor as unknown — a
conservative miss of 13× is harmless to the budget and useless to the
calibration ledger, which exists to make the next estimate better. The
calibration law (rule 12) turns this into a per-completion check; this
lesson names the first attribution it produced. **Proposed lab-wide** via
the chief: a line in `docs/COST_CALIBRATION.md`'s rules or the
`COMPUTE_BUDGET_CHARTER` requiring the solver class of the basis to be
stated in every pre-registration cost table.

## L-272. An aggregate cost ratio near 1.00 can be two large errors cancelling — read the per-row spread before calling a model calibrated, and never extrapolate a minutes-long contention window across a multi-day run

**The rule.** When a completed process is calibrated against its estimate
(CLAUDE.md rule 12), **the ratio of the totals is not the finding until the
per-row ratios have been read.** A total that lands on the prediction while its
rows scatter by 1.4–1.6× in one direction and 0.65–0.92× in the other is a
model with two defects, not a model that works. Two specific defects to look for,
because both were paid for here:

1. **A throughput model of the form `work ÷ rate` has no fixed-cost term**, so it
   under-predicts every short run by whatever the startup and IO cost is. Detect
   it with the **`ExecutionTime`/wall ratio per row**: where that ratio is well
   below 1, the missing fraction *is* the fixed cost the model omits. Add a fixed
   per-case term measured on the same mesh sizes before reusing the model.
2. **A contention penalty measured over minutes does not extrapolate over days.**
   A rate window taken while the box is saturated describes that moment. Re-measure
   on the long pole, or register the contended figure as an upper bound and the
   uncontended one as a lower bound — do not replace the pre-launch estimate with
   a short post-launch window and treat the replacement as better.

**Why.** T3's ext1 extension predicted **79.55 core-hours** before launch and
spent **79.968** — a headline **1.005×**, which read alone would have entered the
ledger as an accurate estimate. It was not. The three shortest runs came in at
**1.617× (`W_m`), 1.507× (`D_m`) and 1.404× (`R_c`)**, and their
`ExecutionTime`/wall ratios were **0.775, 0.778 and 0.858** — 14–23 % of their
wall was mesh read, field read, first write and wrapper, which the model has no
term for. Meanwhile the critical path `R_f` came in at **0.917×**, its
`ExecutionTime`/wall ratio **0.988**, because the pre-launch rates had themselves
been measured under contention. Separately, a **five-minute** window taken after
launch (2026-08-22 17:54–17:59Z, 15 of 16 cores committed) revised the estimate
*upward* to 108.3 core-hours on a 1.36× contention penalty; the contention
dissipated as siblings finished and the revision came in at **0.738×**, with
`R_f` finishing **24 h 1 min ahead** of the ETA that window produced. The
pre-launch estimate was the better one, and the "improved" measured-rate revision
was the worse one, because it generalised a minute-scale observation to a
45-hour run. Recording only the 1.005× would have taught the lab nothing and
would have carried both defects forward into the next rung's estimate.
*(`docs/COST_CALIBRATION.md` C-23; `docs/campaigns/T-family/T3_RESULTS.md` §14.7;
`docs/campaigns/T-family/T3_EXT1_AMENDMENT.md` §5, §10.4 and §15.)*

## L-273. A planted-zero control that plants into its own fixture proves the arithmetic and not the coupling — plant into a file the producer actually wrote.

Curriculum D1 arm C (`b10260a0` §8): the G5 control passed its zero-compute self-test and its
negative control (a deliberately blind reader refused with exit 2), then killed the arm at 14 s on
`KeyError: 'CD_final'` — the producer writes `"CD"` (`d1_opt_runScript.py:417`), the consumer reads
`"CD_final"` (`d1_fd_endpoint.py:110`). The self-test had planted into a hand-built dict carrying
the consumer's own key, so it verified the reader against a schema the pipeline never produces.
`CLAUDE.md` rule 3's logic applies to the control itself: a plant seen in a file no producer writes
is not the demonstration the rule asks for. Cost: 0.233 core-min of named waste and a `BLOCKED`
toolchain row a 2.0 core-min arm was bought to fill — and, because the frozen file's §4.2(c) voids
every prior arm on any edit, the repair could not be made in place: the shipped-row comparison is
re-registered as its own mini-item (Addendum §17). The habit that closes it: the pre-launch control
consumes a real artifact from the producing step — or, where none can exist before the run, asserts
the producer's key set against the consumer's in the invocation that freezes both. Same family as
L-266 on the same item: both defects were findable by dry-running the frozen code against its own
frozen inputs before the freeze.

## L-274. A short solver arm is startup-dominated, and a per-iteration cost basis prices its dominant term at zero

**The rule.** When an arm is order-10 iterations, **estimate the fixed harness
overhead FIRST and add the solve second.** A seconds-per-iteration rate borrowed
from a long neighbouring arm carries no fixed-cost term, so it under-prices a
short arm by roughly the whole overhead — and on a short arm the overhead is not
a correction to the bill, it *is* the bill.

**Why.** D460 sweep 1's ARM P-SM was priced at **1.5 core-min** from a
1,000-iteration neighbour's measured 0.95 s/iter × 10 iterations × a ~9×
`smoothSolver` sweep inflation. It cost **3.833 core-min**, a ratio of **2.56×**.
The solve was never the cost. Measured from the arm's own log: `ExecutionTime =
6.92 s`, `ClockTime = 7 s` for **all ten iterations** of a **230 s** wall. The
other **223 s — 97 % of the bill — was container start, `loadDAFoam.sh`, the
IDWarp import and its md5 assert, a whole-container-filesystem `find /` for
`libDASolverADF.so`, OpenMDAO/mphys setup, and the `mphys.html` + `reports/`
writes.** None of that is visible to a per-iteration basis, which assigns it
zero. The estimate was wrong in **structure, not in magnitude**: it modelled a
10-iteration arm as iteration-dominated when a 10-iteration arm is
startup-dominated.

**The transferable figure, with its honest limit.** Fixed harness overhead on
this DAFoam container measured **34–223 s per arm** — F-SM 34 s at `load1 =
4.31`, P-SM 223 s at `load1 = 14.50`, both `--cpus=1` and both running the
byte-identical launcher. A **6.6× overhead gap on a 3.4× load difference** says
some of the spread is host contention rather than intrinsic cost, but **no
per-phase instrumentation exists in this harness, so the split cannot be measured
and is not claimed.** The structural finding stands either way: whatever its
cause, the overhead is real and the estimate priced it at zero.

*(Sibling of L-272 from the other side: there a headline ratio of 1.005× hid
per-row scatter of 1.4–1.6× against 0.74–0.92×; here a headline of 0.940× hid
2.56× against 0.248×. Both defects are the same missing fixed-cost term in a
`work ÷ rate` model.)*
*Artifacts:* `/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/{psm.log,fsm.log,ledger.txt}`;
`cases/dafoam/d460_sweep1_solver_family/RESULTS.md` §7c item 1;
`docs/COST_CALIBRATION.md` C-22.

## L-275. A two-branch prediction registered as its maximum is an upper bound wearing a point estimate's clothes — register the interval and let the total carry both ends

**The rule.** When a cost estimate is **conditioned on the very outcome the
experiment exists to determine**, naming both branches is the honest move.
**Collapsing them into one number in the item total is not.** Register the
interval; carry both ends into the total; and when the item is calibrated, do not
count the resolved branch as a modelling error.

**Why.** D460 sweep 1 §9 priced ARM F-SM at **3.5 core-min**, written as *"if
healthy, as P-SM; if NaN-contaminated, the measured `s1b` cost … 5.383
core-min"*. The branch condition was precisely what the arm was built to decide —
whether the forward-AD build reaches NaN under `smoothSolver`. It resolved to the
cheap branch and came in at **0.867 core-min, 0.248×**. That **0.248× is not a
misprediction and must not be attributed as one** in the calibration ledger. What
it does mean is that the pre-registered item total of **5.0 core-min was an upper
bound presented as a point estimate**, and the aggregate ratio computed against
it (**0.940×**, which reads as near-perfect) is soft in one direction by
construction.
*Artifacts:* `cases/dafoam/d460_sweep1_solver_family/RESULTS.md` §7c item 2;
`docs/COST_CALIBRATION.md` C-22.

## L-276. Re-derive an append-only id for the COMMIT MESSAGE too, not only for the row — or put no id in the subject at all

**The rule.** `CLAUDE.md` rule 11 fixes the id at commit time, from the **maximum
existing number** in the committed blob, re-derived **in the same shell
invocation**. That discipline is routinely kept for the **row** and dropped for
the **subject line**, which gets composed earlier from a number read minutes
before. **Compose the subject from the same shell variable that numbers the row,
or leave the id out of the subject entirely.**

**Why.** The D460 sweep-1 lane re-derived the next `docs/COST_CALIBRATION.md` id
from the tail of `git show HEAD:docs/COST_CALIBRATION.md` inside its commit's own
shell invocation and got **C-22** — **four higher** than the **C-18** it had read
minutes earlier, because four peer rows (C-18 closure, C-19 closure, C-20
verification, C-21 heat-transfer) had landed in between. This is exactly the
collision rule 11 exists to catch, and it caught it: **the row is right — it is
C-22 and carries no other id.** But the subject line of commit **`f62ec7ed`** was
composed before the re-derivation and says **C-18**, which is now another team's
row. **The subject is wrong; the row it landed is right.** No correction row was
filed in the ledger, because that file's append rules call for one only when a
*row's data* is wrong, and this row's data is not; the commit message was left
unrewritten rather than amended, and annotated in the results file instead —
history is not rewritten to hide a mistake.

**The narrow lesson.** Re-deriving at commit time worked. The rule was simply not
applied to the one surface that also carries the id: the message.
*Artifacts:* `cases/dafoam/d460_sweep1_solver_family/RESULTS.md` §7c, disclosure
block; commit `f62ec7ed`.
## L-277. A planted-difference control turns "no difference found" into evidence — and the SAME comparator can produce a worthless zero and a load-bearing one on consecutive attempts of the same item

**The rule.** The discriminator for a null result is **never the guard's exit
code**. It is whether the guard was **given something to read**, and was **proved
able to read it in that session**. A zero from a reader that was handed nothing
is not a measurement of anything (`CLAUDE.md` rule 3).

**Why.** A3 rung 3, attempts 1 and 2, ran the **byte-identical** `identity_stop.sh`
comparator. **Attempt 1**: the arm was killed by its host-floor memory limb at 85 s
of a 2600 s budget, **0 of 11 identity checkpoints reached**; the comparator found
no difference, and the record correctly wrote *"this is explicitly not evidence
that it would not have fired"* — graded **NOT A RESULT**. **Attempt 2**: eleven
checkpoints printed, the same comparator's limb 7 had **already returned exit 6**
on rung 2's real path differing in the 5th significant figure, and the same zero
became the item's headline finding — **11 of 11 checkpoints bit-identical**,
verdict **GATE FAIL (adjoint, inherited)**.

**The narrow reading.** Two runs, one comparator, one exit code, two entirely
different evidentiary values. The positive leg is what separates them, and it has
to be demonstrated **in the session that reports the zero**, not inherited from
the script's design.
*Artifacts:* `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4/RESULTS.md:107`
(attempt 1, NOT A RESULT) against
`cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4_attempt2/RESULTS.md` §3.1
(attempt 2, 11/11); `CLAUDE.md` rule 3.

## L-278. A launch gate tight enough to protect its own memory floor SELECTS FOR A QUIET BOX — so any wall estimate carrying a contended-box contention multiplier is systematically high behind that gate

**The rule.** **Record the gate's own memory limb beside any contention
multiplier, and state which side of the gate the multiplier was measured on.** A
launch gate that refuses to open until the box is quiet is not a neutral
observer of contention: it is a filter that removes exactly the condition the
multiplier was calibrated on.

**Why.** A3 rung 3 attempt 2: Amendment 1 raised the launch gate's memory limb to
**25.0 GiB (82 % of `MemTotal`)**; the gate opened on **poll 1** at **27.19 GiB
with 13 free cores**. The realised contention factor was **1.1955×** against a
**1.7×** point taken from a rung-2 measurement made on a **contended** box. The
wall point estimate missed by **+42 %**, while the registered **1.0–2.6×** band
held.

**Relation to C-4.** This is C-4's lesson (*record the load average beside a
per-iteration cost basis*) arriving from the other direction: there a basis
measured under contention was carried onto a quiet box; here **the gate itself
made the box quiet**, and the same error follows.
*Artifacts:* `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4_attempt2/RESULTS.md`
§7 and §5; `docs/COST_CALIBRATION.md` C-29 (predicted 51.8 core-min, actual gross
36.733, ratio 0.709), C-4.
## L-279. A defect measured at one design point is a measurement AT THAT DESIGN POINT, not a property of the code — register any extrapolation of it as a falsifiable hypothesis with a discriminator

**The rule.** Before carrying a measured defect from the operating point where it
was measured to any other operating point, **register the carry as a hypothesis
with a named discriminator and a band**, and score it. A number measured at a
baseline is not a property of the library that produced it.

**Why.** The stock IDWarp warp-derivative error on A1 NACA0012 at np=1 reads
**640.3696 % with a sign flip** on `shape[6]` at the **undeformed** baseline
(`reverify_patched_idwarp_np1/RESULTS.md` §4.1) and **≤ 2.80e-06 relative —
unresolvable, at the cross-run noise floor** at arm O's converged design point,
same case, same two md5-identified images, both measurements pre-registered.
Curriculum mini-item D1-C′ registered two carries and **both were falsified**:
**H1** (the absolute defect carries to the endpoint) is out by **1.3e5**; **H2**
(the relative error carries) by **1.2e4**. The registered point verdict `P5 =
GATE FAIL` is a **MISS**, reported as one, and the gate it was registered against
(`G-C1`) reads **PASS**.

**What is NOT claimed.** No mechanism is inferred. Design-point dependence is the
*finding*, not the *explanation*; the candidate mechanism is registered as an
**untested hypothesis** with the arm that would test it, and it is not costed, not
registered and not launched. **The falsification is the load-bearing part** — the
predictions were wrong by four and five orders of magnitude, which is only visible
because they were written down first.
*Artifacts:* `cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md` §2, §7,
§8, §9 (prereg frozen `c19e0cbc`; graded `5bec45b7`, Addendum 1 `c4ce2b8f`);
`cases/dafoam/ladder-a/A1/reverify_patched_idwarp_np1/RESULTS.md` §4.1.

## L-280. A vendor verification table's ratio column measures agreement with a ROUNDED target, not with the reference solution — a tolerance drawn from that column is set wrong

**The rule.** In the Ansys Fluid Dynamics Verification Manual (VM2026R1) each
Results-Comparison table prints three columns — **Target**, **Ansys**, and
**Ratio = Ansys/Target** — and every one of those numbers is rounded to the
manual's reported significant figures (§1.2, p. 4: an ANSYS result "reported in
this manual as 0.01234 may very well show up in your printout as 0.012335271").
**The Ratio column therefore measures agreement between two rounded numbers, not
between the solver and the exact reference.** Do not set a lab tolerance from the
ratio column. Gate against the **printed Target** (that is the manual's own
claim, and it is what a re-run must reproduce), and print the **exact-formula
diagnostic beside it** so the rounding is visible rather than absorbed.

**The measurement that shows it.** VMFL001 (flow between rotating and stationary
concentric cylinders, p. 15) has a closed-form tangential-velocity solution
`v_θ(r) = Ω r_i²/(r_o²−r_i²)·(r_o²/r − r)` with `r_i = 17.8 mm`, `r_o = 46.28 mm`,
`Ω = 1 rad/s`. At **r = 35 mm** the exact value is **0.00454781 m/s**; the
manual's **printed Target is 0.0046** — already **+1.148 %** off the exact
solution purely from four-figure rounding. Ansys Fluent's own value **0.0045** is
**−1.05 %** from exact, yet the table shows it as **Ratio 0.978** (CFX 0.976),
i.e. a "2.2 %" disagreement — when Ansys's number is actually *closer* to the
exact solution than the printed target is. A 2 % tolerance drawn from "ratio
0.978" would be a tolerance against a rounded target, off in the wrong direction.

**What the lab did with it.** VMFL001's frozen pre-registration (`ffeed580`)
gates the lab velocity at **±2 % of the four printed Targets** — the manual's
reproducibility claim — and its comparator (`8cb29610`) prints, beside each gated
value, the deviation of the **exact formula** from the printed target
(−0.133 / −0.319 / +0.187 / +1.148 % at r = 20/25/30/35 mm; see N-AV3). The gate
is the manual's claim; the exact diagnostic is the honesty channel.

*Artifacts:* the manual sidecar
`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`
Table .01.1 (VMFL001, p. 16) and §1.2 (p. 4); `docs/NUMERICS_KNOWLEDGE.md`
N-AV2/N-AV3; VMFL001 pre-registration `ffeed580` (blob `e0afc259`), comparator
`8cb29610`.
## L-281. A gate that closes at the FIRST measurable interval has bought margin, not convergence — register `endTime` from a predecessor's measured first crossing times a stated multiple, and name that multiple as a cost decision

**The rule.** When a predecessor rung's retained change-series exists, **derive
`endTime` from its measured first crossing of the registered floor, times a
stated multiple, and record the multiple as a cost decision in the
pre-registration**. A run length carried over by habit, or picked as "3x the
last one", is a spend nobody has justified. And when a gate closes at the
earliest interval the checkpoint schedule can measure, **say so in the results**:
that reading is evidence about the run length, not about the convergence.

**Why.** E4a2 (prereg frozen `cd1f46e1`) registered `endTime` **60 000** — 3x
E4a's 20 000 — reasoning from E4a's flat floor that stationarity should be tested
over three times the span. The gate closed on all five cases, and **first
crossing of the `1e-8` floor was at iteration 4 000 on every one of them: the
first measurable interval in the series** (the `r_k` series begins with the
2 000 -> 4 000 pair, so no earlier reading exists). The floor was met as soon as
it could be observed. **60 000 iterations therefore bought ~15x margin rather
than convergence**, and the rung's solver cost — 491 core-s of a 497 core-s
total — is dominated by iterations after the answer had stopped moving. The
evidence that nothing was gained is in the rung itself: X1 recovered Q agreeing
with E4a's 20 000-iteration values **to ten significant figures**, gaps
**0.0000 pp** on all five cases.

**The contrasting case, and it is why this rule says "measured", not "shorter".**
T3 ext1 sized every extension from each case's own measured decay rate rather
than from a habit. `R_f`, the critical path, was granted **58 000** further
iterations and needed **57 713** of them — **99.5 % consumed, with margin only
from the round-up to `writeInterval`** (`T3_EXT1_AMENDMENT.md` §3: `T` must fall
a factor of 1 095 = 3.0394 decades at 0.05266 decades per 1 000 iterations ->
57 713; `20 000 + 57 713 = 77 713` -> `endTime` **78 000**). The same arithmetic
run on E4a's series would have exposed E4a2's 15x margin **before** the compute,
not after. **A registered `endTime` is a falsifiable prediction about a decay
rate, and it should be sized like one in both directions** — T3 ext1 sized it
tight and was nearly falsified; E4a2 sized it loose and paid for margin it
never used.

**What this lesson does NOT license.** It does not license shortening a run
after seeing where its gate closed. E4a2 §7 registered, before any solve, that
the rung has **no extension arm** precisely because a run length chosen after
seeing the numbers is what rule 2 exists to prevent; gates and caps are closed
after first compute. The rule binds the **successor's** pre-registration, and
the successor states the multiple and its cost basis in advance.

*Artifacts:* `docs/campaigns/T-family/E4a2_RESULTS.md` §2 (first crossing 4 000
on all five, and the `r_k` series in `log.analyse_e4a2.20260824T173504Z.txt`) and
§6 (cost); `docs/campaigns/T-family/E4a2_PREREGISTRATION.md` §2.4 (the 3x
reasoning) and §7 (no extension arm); `docs/campaigns/T-family/T3_EXT1_AMENDMENT.md`
§3 lines 157-176 and §5 line 326; ledger row `C-34`; docket `D505`.

## L-282. A "first timestep where the diagnostic fires" read point measures the initial transient, not the mechanism — register the read point at a matched time and pin the reference state to it

**The rule.** A clause of the form *"at the first timestep where `<indicator> > 0`,
for the worst cell"* lands on step one, where the indicator fires for reasons that
have nothing to do with the mechanism under study — an initial-condition
discontinuity, a first-solve transient, or the indicator simply firing everywhere.
**Register the read point at a matched time (the same `t*` the rest of the section
compares at), and pin the reference state to the read point rather than to the
first event.** A reference chosen for one population and applied to another is the
same defect either way round.

**The measurement that shows it.** F4 §8.3 read the first block with `nLow > 0`.
That is block 0, `t = 1.20003692e-09`, where the clamp fires on **all 29,700
cells** — the whole mesh. The interior is initialised uniform at freestream
(`0/U uniform (1274 0 0)`, `0/T uniform 81.2`) while the inlet carries the Table II
**boundary-layer** profile, so the amended §13.2 rule compared a still-freestream
cell against inlet face 108's `66.25 m/s` / `309.32 K` and returned `Δ|U| = +18.23`,
`Δρ = +2.80`. AMENDMENT 1 had removed the mirror artifact (an inlet-adjacent cell
judged against freestream) and, at the first timestep, re-created it pointing the
other way. `INDETERMINATE` was the literally correct label — both deviations are
outside band — for entirely the wrong reason. Gates close at first compute, so it
could not be repaired; it could only be disclosed.

*Artifacts:* `verification/campaign/F4_SIGFPE_STEP01_RESULTS.md` §3.4(a) (`5b5f5183`);
the clause and its amendment at `verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md`
§8.3 and §13.2 (`290fcff2`); `verification/runs/F4_runs/swbli_cylflare/GRADING_OUTPUT.txt`.

## L-283. A crash-detecting regex that matches the solver's own startup banner is a 100 %-false-positive detector — assert non-match on a clean log's banner in every such reader

**The rule.** Detectors for "did this run die?" are written from the crash text and
tested on a crash. They are almost never tested on a **clean** log, and the string
that names the exception usually appears in the startup banner of every run,
crashed or not. **Every crash detector asserts non-match against the banner, on a
log known to have completed** — that is standing rule 3 applied to the detector
itself: a `False` from a reader never shown able to return `True`, and a `True`
from one never shown able to return `False`, are both worthless.

**The measurement that shows it.** F4's reader carried
`RE_SIGFPE = r"Foam::sigFpe|Floating point exception|SIGFPE"`. Every OpenFOAM run on
this box prints `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`
at startup whenever `FOAM_SIGFPE` is set. Measured false-positive rate: **100 %** —
line 18 of the archived F4 crash log, line 18 of `F5_runs/re3900/log.pimpleFoam`
and line 29 of `F7_runs/damBreak_MM_a2p25in_medium/log.interFoam`, the latter two
having completed cleanly. The prereg's §7.3 would have labelled a perfectly
completed step `SIGFPE-RECURRENCE`. The replacement matches the backtrace frame
`Foam::sigFpe::sigHandler` (the ONLY in-log crash signal — the crash log carries no
bare `Floating point exception` line at the crash at all) and makes the kernel's
`rc == 136` the primary signal. The reader's `--selftest` now asserts non-match
against **two** banner wordings, so the guard does not depend on which one a future
build emits.

*Artifacts:* `verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md` §13.3
(`290fcff2`); `verification/runs/F4_runs/swbli_cylflare/analyse_f4_sigfpe_step01.py`
`RE_SIGFPE` and `selftest_sigfpe_regex()` (`4bf8138d`).

## L-284. A per-timestep diagnostic included twice per step emits two event sets per block — the pre-registration must name the ordinal it grades BEFORE compute, or the choice becomes a post-compute ruling disclosed against numbers already visible

**The rule.** Before freezing a clause that reads "the diagnostic line at time `t`",
**count how many times the emitting code runs per timestep.** If it is more than
once, name the ordinal in the frozen text. Left unnamed, the choice is still a
choice — it just gets made after the numbers are on disk, and then it can only be
*disclosed*, never *pre-registered*. Disclosure is the honest second-best, not an
equivalent.

**The measurement that shows it.** F4's `boundE.H` is included **twice per
timestep** — at `rhoCentralFoamBoundedDiag.C:267` (after the convective `rhoE`
solve, before `thermo.correct()`) and at `:282` (after the viscous `e`-diffusion
solve). All 2062 `Time =` blocks in each step carried **two** BOUND-family sets, and
§8 never said which it meant. **The choice was material**: at `t*` event 1 read
`2668/29700 = 8.98 %`, inside the registered `[6, 24] %` S0a band, and event 2 read
`749/29700 = 2.52 %`, outside it — so §8.1 returns `BASELINE-RECOVERED` on one
reading and `BASELINE-NOT-RECOVERED` on the other, and §9.1's fourth row would then
have made the whole discrimination question `NOT A RESULT`. The ruling (event 1,
the `:267` set) rests on mechanism — §8.3's `e = rhoE/rho − ½|U|²` cancellation and
§4.2's own frozen "`rho` and `U` are CURRENT … `T` is NOT current" comment are true
at `:267` and false at `:282` — but it was taken with both columns already on disk,
and ADDENDUM 2 says so in full and prints both.

*Artifacts:* `verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md` §14,
especially §14.3 (the ordinal rule: event `k` is the `k`-th set in log order, a
single-set block has event 2 **ABSENT not zero**, and a required-but-missing set
makes the reader refuse) and §14.4 (both-readings disclosure) — `d457f612`;
`verification/campaign/F4_SIGFPE_STEP01_RESULTS.md` §3.2 (`5b5f5183`).

## L-285. A build allowance cannot be closed out without a build-time artifact — time the build in the launch wrapper, or the ledger row reads ABSENT forever

**The rule.** A pre-registration that carries a **separate build allowance** must
also carry the instrument that measures it. Solver wall time comes free in the
log's `ExecutionTime`; **`wmake` wall time comes from nowhere unless something
times it.** Capture it in the launch wrapper alongside the solver. Otherwise the
allowance is registered, the compute is genuinely spent, and the calibration ledger
can never say whether it fitted — and the ledger's own append rule forbids
approximating the missing figure in, so the row reads **ABSENT** permanently.

**The measurement that shows it.** F4 §10.3 registered a **3 core-min BUILD
ALLOWANCE** separately from the 12 core-min run cap, plus an "≈2 core-min for
builds + control C0" estimate. At close-out the solver rows were exact from the
logs (295.55 s and 295.81 s) and the C0 twins exact (40.44 s and 40.31 s), but no
`wmake` timing existed anywhere on the box — the run tree, both `*_src/` trees,
`LAUNCH.txt`, `RC.txt`, `POSITIVE_CONTROL.txt` and `C0_RESULT.txt` were all
searched. Measured total **11.2018 core-min** with the builds absent; the
"≈2 core-min" estimate is recorded **NOT CLOSED OUT**. A relayed gross of
12.00 core-min could not be reproduced from disk, the ~0.80 gap being consistent
with exactly those two untimed builds — which is what an unmeasurable line looks
like from downstream.

*Artifacts:* `docs/COST_CALIBRATION.md` row `C-33` (`bb38504d`);
`verification/campaign/F4_SIGFPE_STEP01_RESULTS.md` §1 part 2 and part 6(d)
(`5b5f5183`); the registration at
`verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md` §10.3, §10.4.

## L-286. An empty commit with a claiming message — guard EVERY step of a commit chain explicitly, because `set -e` does not stop the harness tool shell

**The rule.** Every step of a private-index commit chain carries `|| exit 1` of its
own. Before `commit-tree`, **assert the written tree differs from the parent tree**,
and **assert the exact path list** the `diff-tree` prints. Read those assertions
*before* the commit, not after it. `set -e` inside a harness bash tool invocation
does **not** reliably abort the invocation, so an unguarded chain runs on past a
failed step and produces a commit whose message claims a write that is not in its
tree — the worst failure mode available to this protocol, because the message is
what a reader trusts.

**The measurement that shows it.** Commit `d99d82cd` (2026-08-24T17:35:52Z) carries
a message claiming a dafoam board write — the D1-C′ grading, the curriculum-D1
close, the C-31 calibration row. Its tree is `b2533d80`; `git rev-parse
d99d82cd^^{tree}` returns **the same** `b2533d80`, and `git diff-tree --stat
d99d82cd^ d99d82cd` prints **nothing**. The commit wrote no bytes. Cause: the
section-edit python step failed on a **pattern mismatch**, `set -e` did not abort
the invocation, and the chain then ran `write-tree` on the *unchanged* `read-tree`
and `commit-tree` on that tree. The evidence was already on the screen — the
chain's own `git diff-tree --stat $H $T` printed **EMPTY** — and was read too late
to stop the commit. A printed assertion nobody reads at the moment it can still
stop something is not a guard.

**The repair.** Nothing was reverted: rule 10 says an unexpected state is
**inspected, never reverted**, and that applies to one's own mistake as much as to
a peer's. The empty commit is disclosed **forward**, in the message of `ac19e210`
(2026-08-24T17:37:30Z, which carries the real board write) and on the dafoam board.
The history keeps an empty commit with a false-looking message and a successor that
says so; that is cheaper than a rewrite, and it is honest.

**Corollary — an anchor assertion must first assert the anchor is UNIQUE.** A check
that locates its edit point by substring can match the wrong occurrence and report
success. In this same session the sub-heading byte check first matched a mention of
`### O2 re-buy` **inside a stamp line** rather than the heading of that name. It was
caught by its own byte assertion before any commit, which is exactly what the
assertion is for — but the general form of the defect is that a non-unique anchor
turns a targeted edit into a silent misplacement.

*Artifacts:* `d99d82cd` — tree `b2533d80`, identical to its parent's, empty
`diff-tree --stat`; `ac19e210` — the forward disclosure and the board write that
`d99d82cd` claimed; CLAUDE.md rule 10, whose chain this lesson tightens.

## L-287. The docket maximum is read at LINE START — a loose `D[0-9]{3}` reader returns a phantom

**The rule.** Derive the maximum docket id from ids **at line start in their row
form** — `^\| D[0-9]+ ` for `docs/DOCKET.md` — and never from a `D`-number
*mention* anywhere in the prose. The same holds for `L-` (`^## L-[0-9]+`, the form
rule 11 already prints) and for the `N-D` series. A future id named in prose (the
dafoam board's `L-267+`) is not a row; neither is a number quoted inside another
row's body.

**The measurement that shows it.** Row **`D349`** of `docs/DOCKET.md` (line 714 at
`cc136f39`) narrates a citation-guard defect and, in doing so, names **`D901`** — an
*unallocated fixture constant*, a deliberately out-of-range synthetic value from a
`TempDocketRepo` test fixture, quoted inside the text of D349 itself. A reader
written as `grep -oE 'D[0-9]{3}' docs/DOCKET.md | sort -n | tail -1` therefore
returns **901**. It did, twice: the dafoam supervisor's own first read this session
returned 901, and the D1-C′ `RESULTS` §13 draft recorded it in writing —
`cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md:480`, "**`D` candidate
(max at drafting: `D901`)**". The true line-start maxima in that window were
**D498** (from `3f2480a1`, 17:11:23Z) and **D502** (from `dfe5292d`, 17:41:31Z).
Over the same `cc136f39` blob the line-start reader returns **505** while the loose
reader still returns **901** — the two readers disagree by 396 on the same bytes.

**Why no id was actually mis-assigned, and why that is not reassurance.** Rule 11
re-derives the id at commit time from **row** ids, in the same shell invocation, so
the phantom reached two drafts and no commit. The rule caught it; the reader is
still wrong, and a reader that is wrong everywhere except at the one gate that
happens to re-derive is a defect waiting for the gate to be skipped once.

*Artifacts:* `docs/DOCKET.md` row `D349` at line 714 of `cc136f39` (the D901
mention, the only one in the file); the true tail rows `D501`–`D505` at the same
rev; `cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md:480` (the recorded
phantom); CLAUDE.md rule 11.

## L-288. A comparator selftest that builds its own fixture verifies the comparator's BELIEF about the writer, never the writer — run the reader once against real solver output before the freeze

**The rule.** A selftest that writes its own input file and then reads it back is a
round-trip through one mind. It proves the reader is self-consistent. It cannot
prove the reader matches the **producer**, because the producer never appeared. So:
**before freezing a comparator, run its reader once against real output from the
real producer** — one throwaway coarse case, seconds of compute — and freeze only
after it has parsed something the solver actually wrote. If a producer's output
format is genuinely unavailable pre-freeze, the pre-registration must say so in the
words "this reader has never seen real output", and the first run must be treated as
an instrument shakedown whose grading is expected to be repeated.

**The measurement that shows it.** VMFL001 run 1. `grade_vmfl001.py` (blob
`8cb29610`) was frozen with a `--selftest` of **18 checks, all 18 passing** —
including a positive read of a synthetic `sets` file and, deliberately, a **refusal
on a headerless file**. The pre-registration disclosed honestly, in §9, that *"No
solver has run, so its OpenFOAM-output parsing has never seen real `simpleFoam`
output"*, and stated in advance that the comparator would refuse rather than guess.
Every one of those statements was true and the freeze was in good faith.

The fixture was still wrong in two ways at once, because the author wrote it from
the same belief the reader was written from:

| | the frozen comparator expected | OpenFOAM v2606 actually writes |
|---|---|---|
| filename | `U_gateAxis.*` — **field first** | `gateAxis_p_U.xy` — **set name first, then fields ALPHABETICALLY** |
| header | a `#` comment line naming the columns | **no header at all** |

At grading the comparator refused, exit 2, on the **coarsest** level:
`REFUSE: no sampled file for set 'gateAxis', field 'U' at time 3000`. It therefore
never reached L2, L3, its own planted-zero control, the grid triple or the gate. The
refusal was **correct behaviour** — it is what §9 promised and it is what stopped a
guessed column from becoming a lab value. The rung was lost anyway.

**Why the honest disclosure did not save it.** §9 said the reader had never seen
real output; the selftest's 18 green checks said the reader worked. Both were true,
and together they read as "unexercised but sound". They were not the same claim, and
only one of them was about OpenFOAM. **A disclosure that a check was not run is not
a substitute for running it when running it costs two seconds** — the L1 level here
takes **2 wall seconds**, and parsing its output before the freeze would have cost
0.033 core-minutes and caught both defects.

**The trap generalises past filenames.** Anything a comparator believes about a
producer — column order, units, sign convention, time-directory naming, header
presence, delimiter — is a belief until the producer has been observed. A fixture is
where those beliefs get written down twice and checked against each other.

**Not a licence to loosen the reader.** The repair is to teach the reader the true
convention and keep it refusing when it cannot identify a column. A reader made
tolerant enough that no fixture could have caught this would have produced a number
from run 1, and that number would have been worth nothing.

*Artifacts:* `cases/ansys_verification/VMFL001/RESULTS.md` §3 and §9;
`cases/ansys_verification/VMFL001/PREREGISTRATION.md` §9 (the honest pre-freeze
disclosure) and §10 (the planted-zero control that never fired);
`verification/runs/ansys_verification/VMFL001/GRADING_VMFL001.stdout.txt` (the
`REFUSE:` line) and `.../L*/postProcessing/radialProbes/3000/gateAxis_p_U.xy` (what
v2606 actually wrote), committed `ae30f914`; verdict commit `dee5870d`; register
row #1; the format itself is `N-AV4`.

## L-289. A single frozen iteration count across a grid triple is adequate at the coarse levels and inadequate at the fine one — register a per-level `endTime`, or a convergence-based stop the completion rule can still check

**The rule.** A Roache triple refines the mesh by 2 in every direction and holds
everything else fixed. **The iteration budget must not be one of the things held
fixed.** Iterative convergence at a fixed iteration count degrades with cell count,
so one `endTime` that comfortably converges the coarse level can leave the *fine*
level — the level the verdict is actually about — short of the registered residual
criterion. Register **per-level iteration budgets**, sized for the finest level, or
a **convergence-based stop**; and if you take the second, register the replacement
completion clause **in the same freeze**, because a solver that stops on
`residualControl` no longer satisfies "last time == `endTime`".

**The measurement that shows it.** VMFL001 run 1 froze `endTime = 3000` SIMPLE
iterations for all three levels at relaxation `p 0.3 / U 0.7`, and registered (§7)
that at **every** level the final-iteration initial residuals of `Ux`, `Uy`, `p` be
< 1e-6 and the plateau peak-to-peak of the r = 35 mm probe be < 1e-6 m/s over the
last 600 iterations:

| level | cells | Ux init. resid. @ 3000 | p init. resid. @ 3000 | plateau ptp (m/s) | §7 |
|---|---|---|---|---|---|
| L1 16×64 | 1,024 | 4.69187e-14 | 6.50871e-11 | 1.00e-14 | ✅ |
| L2 32×128 | 4,096 | 1.48771e-12 | 4.85296e-11 | 1.27e-11 | ✅ |
| **L3 64×256** | **16,384** | **1.19876e-06** | **2.89185e-06** | **2.77178e-05** | ❌ **both** |

L3 misses the residual clause by 1.20× on velocity and 2.89× on pressure, and the
plateau clause by **27.7×**. Under CLAUDE.md rule 5 step 1 the rung is
`NOT A RESULT` **before the triple is classified** — the verdict was decided by the
level the gate is defined on, and the two coarse levels passing tells you nothing.

**The triple is what exposed it, and it was cheap.** Total spend: **1.9833
core-minutes** (119 wall s serial), 0.661× the 3.0 core-min estimate, $0.0017
derived. A single-mesh run at L1 or L2 would have converged beautifully and taught
nothing about the mesh the verdict rests on. **Refining the mesh without refining
the iteration budget converts a discretisation study into an iterative-convergence
failure**, and the failure lands on exactly the level whose value is graded.

**The trade the repair has to make explicitly.** A per-level `endTime` keeps the
strict completion rule intact (`last time == endTime`, `ExecutionTime` count ==
`endTime`) and costs one more registered number per level. A `residualControl` stop
is better physics — it converges to a criterion instead of to a guess — but it
**breaks completion clause 3 by construction**, since the last time is then
deliberately less than `endTime`. If chosen, the replacement clause must be frozen
alongside it: last time < `endTime` **and** the `SIMPLE solution converged` line
present **and** `ExecutionTime` count == last time. Choose in the pre-registration,
before compute; a completion rule relaxed after a run that failed it is not a
completion rule.

**And it must be a new rung.** Changing `endTime` changes a registered quantity
after first compute, which CLAUDE.md rule 2 forbids in an addendum. The repair is a
**new pre-registration**, frozen by sha before any compute, landing as a **new
register row citing the old** (`ANSYS_VERIFICATION_CHARTER.md` §6). Run 1's
`NOT A RESULT` row is never removed, re-labelled or softened.

*Artifacts:* `cases/ansys_verification/VMFL001/RESULTS.md` §4, §6 and §9;
`PREREGISTRATION.md` §4 (verdict order), §7 (the convergence clauses), §8 (cost);
residuals in `verification/runs/ansys_verification/VMFL001/L*/log.simpleFoam` and the
3000-row plateau probes in `.../L*/postProcessing/gateProbes/0/U`, committed
`ae30f914`; verdict commit `dee5870d`; calibration row `C-37`; the measured
convergence degradation is `N-AV5`.
