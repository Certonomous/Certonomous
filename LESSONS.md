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
