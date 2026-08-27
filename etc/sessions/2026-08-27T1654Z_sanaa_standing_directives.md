# [SANAA-DIRECT] STANDING DIRECTIVES — ALL TEAMS — received 2026-08-27T16:54Z

Captured verbatim by the chief on Sanaa's instruction ("capture to etc/sessions/ verbatim, then board"). Her words, unedited, begin at the line below and end at the marker `— END OF SANAA'S TEXT —`. Boarded in `docs/LAB_STATE.md` CHIEF section in the same commit.

---

fantastic! th elab should continue like this. Here are a few more directives and instructions : # STANDING DIRECTIVES — ALL TEAMS
[SANAA-DIRECT — capture to etc/sessions/ verbatim, then board. Teams route
work internally through their own harness; these orders name the TEAM only.]

## 0. DESK RULINGS (effective immediately)
- R-RC: APPROVED — rc value is physics, rc record is infrastructure; absent
  record -> NOT MEASURED only when the other four rule-4 conditions hold.
- D534: APPROVED — REPORTED is a row class, not a verdict; excluded from
  censuses.
- R-1D: APPROVED — 1-D cases count as CAVEATS in the 2D row.
- NUMERICS_KNOWLEDGE.md:118 false citation ("V&V 20 now supplied") I will
  correct it TODAY; the standard's own text gets acquired this week (MIT
  library route first) — until it lands, every V&V-20 practice cites
  Dowding 2016 as secondary, stated as such.

## 1. FILE INTEGRITY — THE .MD CLASSES END HERE (all teams)
If you have not already found a smart way to prevent the md collisions
- HEAD IS TRUTH: load-bearing files are read from the HEAD blob, or
  worktree == HEAD is verified first. Before landing "uncommitted work":
  git diff HEAD per path; a pure-deletion diff vs HEAD is the reversion
  signature and never commits.
- SCRATCH IS NAMESPACED: scratch/<team>/<lane>/ only; generic filenames
  (board.md, base.md, block.md, tmp.md) banned; splices assert on content,
  never line counts; nothing load-bearing is read back from stale scratch.
- COMMIT HYGIENE: explicit path lists, no directory sweeps; logs and
  attempt dirs stay out of git; pre-commit guard blocks >50 files or >5 MB
  without a manifest.
- Every guard ships its planted-failure proof (L-314 standard).

## 2. NOTHING SITS IDLE — CLOSED-LOOP SCHEDULING (all teams)
- One queue-runner per resource pool (CPU box; GPU instance), each with
  heartbeat + liveness watchdog. A resource without a live runner is a
  boarded defect.
- Completion detection is the runner's job: every wrapper writes STATUS at
  exit (rc, wall time, timestamp); the runner polls, triggers grading, and
  pulls the next frozen case within 15 minutes. Idle >30 min with a frozen
  queue = auto-boarded defect with derived cost.
- FREEZE-AHEAD >= 3: every team keeps at least three frozen, queue-ready
  registrations at all times. A starved queue is a planning defect.
- Headline metrics every report: CPU %, GPU %, queue depth per team,
  idle-minutes per resource.
Whenever ansyis team is done using the Gpu, if dafoam team wants to use that instead thats allowed

## 3. WHEN A CASE WON'T CONVERGE / BREAKS / GIVES WRONG RESULTS (all teams)
One change per run; every step a pre-registered diagnostic arm with a cap.
- L0 DIAGNOSE FIRST: oscillation (relaxation) vs growth under flat
  neighbours (coupling not closing) vs plateau (tolerance vs partition
  noise); which channel; balance state; where in the domain.
- L1 numerics dials: under-relaxation, CFL/pseudo-time ramp, tolerance
  sanity (no channel orders tighter than siblings without justification).
- L2 linear solver: preconditioner swap, solver swap, restarts.
- L3 discretization: scheme blend, limiters, gradients — withdrawal
  pre-compute is a legitimate verdict for structurally non-convergent
  pairs (F23).
- L4 mesh: repair offenders, y+/near-wall or localized refinement, remesh.
- L5 initialization & continuation: potential start, lower-Re /
  higher-viscosity continuation, BC ramps.
- L6 model swap within the class's admissible set — pre-registered arm
  only, re-frozen as a new registration, model-form implication declared.
- L7 formulation: steady -> pseudo-transient -> unsteady; formulation check.
- ANTI-GAMING (absolute): convergence aids (L1-L5) tune freely, disclosed.
  Answer-changing choices (model, scheme class, formulation) are never
  selected by agreement with the reference. Converged-but-wrong = NOT
  HELD with diagnosis, never a parameter hunt. Frozen gates never edited
  post-compute.
- Crashes: triage class per charter; OOM feeds the memory census.

## 4. TEAM QUEUES (work when current cases drain — never idle)

### cfd
After you are done with the 36 families
:cases with HOLDS-capable ceilings (real experimental primary
  on hand + frozen band + triple). Clone the VMFL064-R2 recipe — a real
  experiment, a frozen percentage band, a converging triple — onto the
  next cases whose pre-registered ceiling permits HOLDS.


### dafoam — SHAPE-OPTIMIZATION LADDER (pull in order when queue drains)
Pattern per case: FD-verified gradient rung -> optimization rung ->
post-optimum verification (re-solve at optimum, constraints checked,
np-invariance spot row) -> D7R attribution rule: no improvement % quoted
before its mechanism is decomposed (shape vs AoA vs operating point).
After you are done with all the current optimization cases: 
- SO-1 NACA0012 subsonic drag-min at fixed lift; then RAE2822 transonic.
- SO-2 Constraint families on SO-1: thickness/area/volume, lift equality,
  moment cap — one per rung.
- SO-3 Multipoint (2-3 Mach/alpha) weighted objective.
- SO-4 3D wing (ONERA M6 or CRM at feasible mesh) twist + shape; full-size
  waits on D16a.
- SO-5 Internal: U-bend pressure-drop min, diffuser.
- SO-6 Thermal-coupled shape-opt: SCOPE FIRST (adjoint availability for
  buoyant/thermal solvers — memo, no promises).
- SO-7 FFD hygiene program: box placement, DV-count sweeps, deformation
  robustness, DV scaling standards.
- SO-8 Optimizer settings library on one fixed case ->
  OPTIMIZATION_STANDARD.md: measured defaults per problem class.

— END OF SANAA'S TEXT —

## Chief's reading [lab-attributed], same commit

- §0 closes four desk items: R-RC, D534, R-1D approved as written by verification/chief; the `NUMERICS_KNOWLEDGE.md:118` correction is Sanaa's own action today; V&V 20 text arrives via the MIT library route this week — every V&V-20 citation until then reads "Dowding 2016, secondary" explicitly.
- §1 ratifies the chief's 16:35Z/16:40Z stop-orders and L-350/L-351 (`94421bea`, `fedf2a39`) and `USING_THIS_LAB.md` §8.5 step 3 (`28f40c90`), and adds two build items: a pre-commit guard (>50 files or >5 MB without a manifest) and the rule that logs and attempt dirs stay out of git — heat-transfer's `05241ab2` (172 files, 3.2 M lines of `log.solve`) is the named instance to be addressed by its owner. Every guard ships a planted-failure proof.
- §2 makes the runner a closed loop: STATUS at exit from every wrapper, runner-triggered grading, next frozen case within 15 min; idle >30 min with a frozen queue is an auto-boarded defect with derived cost; **FREEZE-AHEAD ≥ 3 per team at all times**; headline metrics (CPU %, GPU %, queue depth per team, idle-minutes per resource) in every report. GPU may pass to dafoam when ansys is done with it.
- §3 is the lab's diagnostic ladder L0–L7 with the anti-gaming clause; it binds every non-convergence from now on and belongs in a standard (verification owns the text; families apply it).
- §4 names the drain-time queues: cfd → HOLDS-capable ceilings on the VMFL064-R2 recipe after the 36 cells; dafoam → SO-1…SO-8 shape-optimisation ladder after the current optimisation cases.
