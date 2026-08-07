# Standing model-form batch — design and pre-registration

Written 2026-08-05 UTC, before any cell of this batch executed. Machine
runner: `sdk/scripts/model_form_batch.py`. Per-cell records and the ledger:
`demo-output/website/campaign/MODEL_FORM_runs/`. Band artifact:
`demo-output/website/campaign/MODEL_FORM_BAND.json` (+ `.md`).

## 1. What this batch is for

The uncertainty doctrine's model channel (`docs/UNCERTAINTY-DOCTRINE.md`,
channel 3) is the lab's weakest measured channel: it is either *direct* (the
case has its own reference) or *transferred* (estimated from validation
history). The NASA hump headline established a third, measured mechanism —
**inter-model spread as a pre-registered containment band** — and it is
currently a sample of one case:

> Inter model spread alone, all four models converged: 1.0722 to 1.2503,
> contains the experiment 1.100. As first reported, with one model
> unconverged: 1.1299 to 1.2534, did not contain it.
> (`demo-output/website/ACTIVE_RESEARCH.md`, headline table)

Two lessons from that headline are load-bearing here and are written into the
gate below, not left to judgement:

1. **An unconverged cell is not evidence.** The band that failed to contain
   the experiment was the band containing a run that had not met its own
   convergence standard. One unconverged member moved the whole verdict.
2. **The band is min/max over CONVERGED members only**, and the excluded
   members are recorded by name with their verdict, never dropped silently.

This batch turns that one case into a standing, resumable population: the same
four closures, on validated cases, across regimes, with the convergence gate
applied mechanically instead of by hand.

**Slot-filler status.** This is the LOWEST-priority work on the machine. Every
launch is gated (section 6) and every cell is small.

## 2. Model availability, verified before design

Checked on this host 2026-08-05, both toolchains:

| Model | native OpenFOAM v2606 (`openfoam2606` launcher) | DAFoam image `dafoam/opt-packages:latest`, OpenFOAM **v2506** |
| --- | --- | --- |
| kOmegaSST | present | present |
| SpalartAllmaras | present | present |
| kEpsilon | present | present |
| realizableKE | present | present |

Native v2606 availability is additionally established by *use*, not by symbol
inspection: `demo-output/website/campaign/RANS_MODEL_COMPARISON.md` (2026-07-28)
solved the square duct under all four of these plus kOmega and LienCubicKE on
this box. The v2506 image's list was read from
`$FOAM_LIBBIN/libincompressibleTurbulenceModels.so` inside a `--cpus=2`
container.

**This batch runs native v2606**, because every case family below is a native
TMR ladder case that the lab has already validated on that toolchain. The
container check is recorded because the docket asked for it and because the
DAFoam families (A1-class NACA0012 tutorial) would need it — see section 7.

## 3. The matrix

Three validated case families x four RANS models x a regime axis per family.
Every family is a case this lab has already run and reported.

### Family P — TMR 2-D zero-pressure-gradient flat plate

- Case: `sdk/workflows/tmr_verification.py` flat-plate ladder, **medium** rung,
  3264 cells (TMR 69x49). Validated: `demo-output/website/tmr/runs/medium`,
  Cd 0.00278117 against CFL3D SST-V 0.00278507 at the same cell count (−0.14%).
- Regime axis: **Re per unit length** 1e6, 5e6 (the TMR reference condition),
  2e7 — a factor-20 sweep, set by nu at U=1. Freestream turbulence is carried
  with it: omega_inf = 1e-6 a^2/nu, nut_inf = 0.009 nu, k_inf unchanged
  (TMR's own scaling).
- QoI: **Cd** (plate drag, Aref = plate area 2) and **Cf at x = 0.970084071**
  (the TMR reporting station).
- Cells: 4 x 3 = 12. Measured baseline cost: 23.9 s wall for the SST cell.
- **Family cap: 20 core-min.**

### Family B — TMR 2-D bump-in-channel

- Case: same module, bump ladder, **coarse** rung, 3520 cells (TMR 89x41).
  Validated: `demo-output/website/tmr/runs/bump-coarse`, Cd 0.00344302 with the
  pressure/viscous split recorded.
- Regime axis: **Re per unit length** 3e6 (the TMR reference condition) and
  1.2e7. Two regimes, not three, because this family is 4x the flat plate's
  per-cell cost.
- Why it earns its place: it is the same wall-bounded family as P but with a
  streamwise pressure gradient, which is where linear eddy-viscosity closures
  begin to disagree with each other. P and B together separate "the models
  disagree about skin friction" from "the models disagree about pressure
  gradient response".
- QoI: **Cd**, with the pressure and viscous components carried separately.
- Cells: 4 x 2 = 8. Measured baseline cost: 101.9 s wall for the SST cell.
- **Family cap: 30 core-min.**

### Family N — TMR NACA 0012 airfoil (A1-class, C-grid)

- Case: same module, `run_naca_level`, **coarse** TMR C-grid 113x33 (3584
  cells), solved on the TMR-distributed PLOT3D grid with a potential-flow
  initialisation. Validated: `demo-output/website/tmr/runs/naca-a10-coarse`,
  Cl 1.11644 / Cd 0.00449485 against CFL3D SST 1.07781 / 0.01236 on the finest
  published grid.
- Regime axis: **angle of attack** 0, 10, 15 degrees, at Re 6e6 / M 0.15 (the
  TMR validation conditions, published CFL3D and FUN3D values for all three).
- QoI: **Cl** and **Cd**.
- Cells: 4 x 3 = 12. Measured baseline cost: 95.2 s wall for the SST alpha=10
  cell.
- **Family cap: 60 core-min.**
- **Known hazard, pre-registered:** the module's own record states the steady
  coarse-rung C-grid runs carry "a sustained wake-driven force oscillation".
  A cell that oscillates fails the gate in section 4 and is EXCLUDED. That is
  the expected, correct outcome, not a defect of the batch, and family N may
  legitimately produce a band from fewer than four members — or no band at all.

**Total design: 32 cells, 110 core-min if every cell runs to its cap.** The
session budget is separate and is passed on the command line
(`--max-core-min`), so a session never exceeds what its owner allowed.

## 4. The convergence gate — pre-registered, applied mechanically

A cell is **CONVERGED** (admitted to the band) only if all four hold:

1. **The solver exited 0** and its log carries no FATAL monitor signature —
   `Foam::sigFpe::sigHandler` (Monitor Standard S1) or a NaN on a residual line
   (S2). Either one is FATAL and the cell is excluded.
2. **The case's own `residualControl` was met**: the log ends with
   `SIMPLE solution converged in N iterations`. The targets are the flat-plate
   ladder's own, unchanged: `p 1e-06`, `U 1e-08`, `(k|omega|epsilon|nuTilda)
   1e-08` (`fv_solution` in `tmr_verification.py`). A run that stopped on its
   iteration backstop is UNCONVERGED by definition.
3. **The quoted quantity has settled**, judged by the Monitor Standard's **S12
   unsettled stop** on the QoI history itself: relative drift < 1e-3 or monotone
   fraction < 0.90 over the trailing window. S12 is used because it is
   scale-free — it grades a Cl of 1.1 and a Cd of 0.0028 against their own
   scales, which the charter's absolute `SETTLE_TOL = 3e-7` cannot do. L-24:
   a run is not converged, a *quantity* is.
4. **Mesh gates pass** (`docs/standards/MESH_STANDARD.md`): max
   non-orthogonality <= 70, max skewness <= 4, read from that cell's own
   `log.checkMesh`. Aspect ratio is advisory on these wall-resolved grids and
   is recorded, never a rejection (Mesh Standard 3.3).

Anything else — cap-stopped, drifting, FPE, mesh-gated — is recorded in the
ledger with `converged: false` and its reason, and is **named in the band
artifact as excluded**. The hump lesson is that the exclusion list is part of
the result.

## 5. What the band is

For each (family, regime) group, over its **converged cells only**:

- `band = [min, max]` of each QoI across the models present,
- `n_converged`, `n_excluded`, and the excluded cells by name with reasons,
- `spread_abs`, `spread_rel = spread_abs / |mean|`,
- the reference value where the family has one (TMR CFL3D/FUN3D), and whether
  the band contains it.

**A group with fewer than 2 converged cells has NO band** and says so. The band
is an interval, carried per the doctrine's model channel alongside u_val, and
**never converted to a sigma or folded into the RSS quadrature** — the same
discipline the closure-coefficient envelope already follows
(`docs/UNCERTAINTY-DOCTRINE.md`, channel 3).

Containment of the reference is reported, never claimed as sufficient: the hump
record's own caution ("the band is wide, a factor of roughly 2.4; containment
is necessary, it is not sufficient on its own") binds here too.

## 6. Queueing discipline — this batch yields to everything

Before each cell launches, the runner:

1. Runs `sudo docker ps` and counts running containers whose image or name
   marks them as dafoam/openfoam work. **If 3 or more are live, the runner
   waits** (60 s poll) and launches nothing.
2. Runs **one cell at a time**, single-rank (`simpleFoam` serial, 1 core). The
   docket's `--cpus=2` ceiling is a container flag; these cells are native, so
   the equivalent is enforced by concurrency: never more than one solve of this
   batch on the machine, i.e. never more than 1 core, which is stricter.
3. Stops before starting a cell that would take the session past
   `--max-core-min`.

## 7. What is NOT in this batch, and why

- **RAE2822 (transonic, case 9).** `sdk/workflows/rae2822_case9.py` exists, but
  the family is compressible (`rhoSimpleFoam`) and the lab's measured transonic
  costs (`rhosimplefoam-naca0012-transonic` p50 29.6 s, p99 69.9 s per solve at
  2000 iterations, Monitor Standard S9 envelope) are per-*evaluation* numbers on
  a much smaller case. A shock-carrying family also changes what "converged"
  means. It is deferred to a later session with its own pre-registration, not
  quietly attempted.
- **The A1-class DAFoam NACA0012 tutorial** (4032 cells, 3.51 core-min): a
  container family. It would need the `--cpus=2` container path, which the
  runner does not implement yet. Family N covers the airfoil regime natively.
- **Nonlinear and RSM closures** (LienCubicKE, LRR, SSG, EBRSM). The docket's
  matrix is the four linear closures. The square-duct sweep already showed the
  linear/nonlinear split is a *structural* question, not a spread question
  (`RANS_MODEL_COMPARISON.md`); mixing a structurally different class into a
  min/max band would make the band mean two things at once.

## 8. Continuation — how the next session picks this up cold

Everything needed is on disk; nothing lives in an agent's head.

- **Runner:** `sdk/scripts/model_form_batch.py`, resumable and idempotent.
  - `python3 sdk/scripts/model_form_batch.py --list` prints every cell and its
    state (done / excluded / pending).
  - `python3 sdk/scripts/model_form_batch.py --family P --max-core-min 40`
    runs pending cells of one family, skipping any cell that already has a
    `record.json`. Re-running it is a no-op on completed cells.
  - `--band` recomputes the band artifact from the ledger alone, with no solve.
- **State:** one directory per cell under
  `demo-output/website/campaign/MODEL_FORM_runs/<cell_id>/` holding
  `record.json` (the cell's own verdict, QoI, timings, gate detail) and its
  `log.simpleFoam` / `log.checkMesh`. **The record.json is the unit of truth**;
  the ledger `ledger.jsonl` is an append-only convenience index rebuilt from
  the records by `--band`.
- **Detachment:** the runner is meant to be launched detached
  (`setsid nohup ... &`) and writes each cell's record as that cell finishes, so
  a fleet death loses at most the one cell in flight. Its own progress log is
  `MODEL_FORM_runs/runner.log`.
- **Cell ids** are stable and deterministic: `P_re5e6_kOmegaSST`,
  `B_re3e6_kEpsilon`, `N_a10_SpalartAllmaras`. A cell is never renamed; adding
  a regime adds ids and leaves the existing ones alone.

## 8a. Addendum, 2026-08-07: what the first twenty cells taught

Written after families P and B ran (20 of 32 cells), across two usage-limit
kills (2026-08-05 ~17:20Z and ~17:45Z) and one two-day power-cycle gap. The
design above is unchanged; these are measured corrections to the runner, each
carried in `sdk/scripts/model_form_batch.py` with its reason.

1. **The ladder's iteration cap is a settle-watcher number, not a
   residualControl allowance.** `iteration_backstop()` returns 3000 on these
   grids because the TMR ladder stops on coefficient flatness; this batch's
   gate is `residualControl`, and at 3000 nine of the first twenty cells were
   guillotined mid-descent. The batch now carries its own
   `BATCH_BACKSTOP = 12000` (`--iteration-backstop`). Re-runs at 12000
   converted first-pass exclusions into 4 more converged cells.
2. **An excluded record is superseded, never deleted.** `--redo-excluded`
   renames the old record to `record_superseded_<stamp>.json` beside the new
   one, so the reason a cell was once excluded survives its rehabilitation.
3. **The bump family fails its gate honestly, and the failure stands.** At
   12000 iterations every B_re3e6 cell is S12-settled on Cd but still above
   the U 1e-08 target (U initial residual ~2.4e-06 and crawling), so all four
   are EXCLUDED and B_re3e6 has **no band** — the pre-registered gate applied
   to a case whose own archived rung also never met residualControl (the
   bump-coarse archive is a 4000-iteration cap stop). At Re 1.2e7 the three
   k-family models FPE within ~45 iterations (S1 FATAL); only SA runs, and it
   stalls. Family B is evidence about the gate, not a band, and is recorded
   as such rather than re-run on softer terms.
4. **SA on the flat plate converges but its `coefficient.dat` does not
   survive collection** — reproduced twice; the log carries the full Cd
   table each iteration while the copied postProcessing tree has yPlus and
   wallShearStress but no forceCoeffs output. The runner now falls back to
   parsing the coefficient history from the solver log and stamps
   `qoi_source` on the record, so the cell is graded on the same S12 test
   either way. Root cause not yet identified; filed as an observation.
4b. **The realizableKE members deserve a raised eyebrow, stated here rather
   than discovered later.** Its one converged flat-plate cell (re1e6) reads
   Cd 0.000935, 3.9x below the SST member, and its other two regimes stall.
   realizableKE is a high-Re formulation and these are y+ < 1 wall-resolved
   grids; `epsilonWallFunction lowReCorrection` is the standard treatment but
   the combination is delicate. The cell met the mechanical gate, so it is in
   the band per the pre-registration — and it is the reason the re1e6 spread
   is 156% of the mean. A follow-up that runs realizableKE on a wall-function
   mesh of the same case would say whether that member is model-form spread
   or wall-treatment artifact; filed as the batch's first ambition item.
5. **Resumability is proven, three times.** Both kills and the power cycle
   cost zero completed cells: every finished cell had already written its
   `record.json`, and the restarted runner skipped them. The one cell a kill
   can cost is the one in flight, as designed.

## 8b. Launch log

- **2026-08-07 20:10:20Z — family N launched detached** (`setsid`, PID 10186):
  `python3 sdk/scripts/model_form_batch.py --family N --max-core-min 60
  --max-queue-wait 3600`. 12 cells in scope, queue gate open (0 solver
  containers live at launch), first cell `N_a0_kOmegaSST` solving at 20:10:22Z.
  Runner log: `MODEL_FORM_runs/runner.log`. Expected to finish or exhaust its
  60 core-min budget within roughly an hour of wall clock (single core);
  whichever session comes next collects with `--list` then `--band` /
  `--study` — no reattachment needed, every completed cell self-ledgers.

## 9. Deviations recorded up front

1. **SA freestream is the TMR SA specification, not the SST one.** SpalartAllmaras
   carries no k or omega, so its freestream is `nuTilda = 3 nu` (the TMR value),
   while the k-family cells carry k_inf and omega_inf/epsilon_inf at the
   published eddy-viscosity ratio 0.009. The cells are therefore matched on the
   *case*, on the mesh, on the schemes and on the convergence gate, and each
   closure is given its own standard freestream — which is what an inter-model
   band is supposed to compare.
2. **epsilon_inf is derived, not invented:** `eps = C_mu k^2 / nut` with the
   family's own k_inf and nut_inf, so the k-epsilon cells start from the same
   physical freestream eddy viscosity as the k-omega cells.
3. **Wall treatment is the ladder's own low-Re treatment** on every model
   (`kLowReWallFunction`, `nutLowReWallFunction`, `omegaWallFunction blended`,
   and `epsilonWallFunction` with `lowReCorrection`), because these are
   wall-resolved grids (y+ < 1). No cell switches to a high-Re wall function.
4. **Schemes, relaxation and residual targets are held fixed across models.**
   The only things that change inside a (family, regime) group are the RASModel
   entry and the turbulence fields that model requires. A band whose members
   differ in discretisation would not be a model-form band.
