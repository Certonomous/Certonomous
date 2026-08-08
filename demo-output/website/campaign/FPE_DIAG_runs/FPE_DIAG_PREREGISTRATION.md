# Paired k-family FPE diagnosis (bump + hills) — pre-registration

Written 2026-08-08 by the Cases family supervisor, **before any probe or
lever run is launched**. Docket item
`kfamily-fpe-shared-diagnosis-bump-and-hills` (filed `78495ab2`, approved,
25 core-min). Runner script: `FPE_DIAG_runs/run_fpe_diag.py` (committed with
this file). Per Verification Charter v1.5 §9: every case carries its
`log.checkMesh` beside it before launch (born clean), and solver logs carry
the mechanical lever echo via the shared `_foam` launcher, so
`levers_verified_active` is machine-built on each record.

## Phase 0 — zero-compute forensics, executed BEFORE this file closed

Read from the four archived crash logs (`MODEL_FORM_runs/{H_re10595_kEpsilon,
B_re1p2e7_{kEpsilon,kOmegaSST,realizableKE}}/log.simpleFoam[.gz]`):

| cell | crash iter | state before death | sigFpe site |
| --- | --- | --- | --- |
| hills kEpsilon | 13 | k and epsilon initial residuals pinned at 1.0 every iteration; U initial residuals ~1e-7 (frozen); then p GAMG Final residual 1.96e+17 at 200 sweeps | `GAMGSolver::scale` (pressure) |
| bump kEpsilon | 38 | momentum linear solves diverging (Ux 0.48 → 0.82 at 1000 sweeps) | `PCG::scalarSolve` in GAMG coarsest (pressure) |
| bump kOmegaSST | 44 | momentum linear solves converging; then pressure | `GAMGSolver::scale` (pressure) |
| bump realizableKE | 44 | momentum linear solves exploding (Final 2e+12) | PCG in GAMG coarsest (pressure) |

**The filing's shared-cause hypothesis is already HALF-FALSIFIED at zero
compute:** bump kOmegaSST carries no derived epsilon and no
`epsilonWallFunction`, yet crashes in the same class — so the derived-epsilon
construction cannot be the bump's cause. All four share only the death SITE
(sigFpe inside the GAMG pressure solve — a symptom, not a mechanism). The
refined question this arm decides: does the HILLS crash belong to the
derived turbulence initialization (its unique upstream signature: turbulence
residuals pinned at 1.0 with U frozen from the first iterations), and does
the BUMP class belong to the impulsive high-Re startup (nu = 8.3e-8, an
unresolvably thin startup boundary layer on 3,520 cells)?

## Phase 1 — instrumented probes (3 runs, seconds each)

Re-run three crashed configs bit-unchanged EXCEPT a `fieldMinMax` function
object printing per-iteration min/max WITH LOCATIONS (entry 9's per-quantity
monitoring design, applied as crash forensics):

- **HP1** hills kEpsilon (fields: p U k epsilon nut), endTime 100.
- **BP1** bump kOmegaSST — the class-defining derivation-free member
  (fields: p U k omega nut), endTime 200.
- **BP2** bump kEpsilon — the derived member (p U k epsilon nut), endTime 200.

Expected: each reproduces its archived crash within ±10 iterations; the
monitoring names the collapsing quantity and its region per geometry.

## Phase 2 — one lever per geometry, one variable each

- **HL1 (hills):** kEpsilon with the initial turbulence fields seeded
  per-cell from the converged same-case kOmegaSST solution (`medium/5997`):
  k = k_SST(cell), epsilon = 0.09 · k_SST · omega_SST (cell-wise — the same
  identity as the uniform derivation, evaluated on the converged field
  instead of the initial constants). Wall treatments, schemes, relaxation,
  solver settings unchanged. Cap 3,000 iterations (230× the crash point).
  **Survival criterion: no S1/S2 fatal through the cap.** Convergence is NOT
  sought and no band admission can follow from this arm (the filing's gate).
- **BL1 (bump):** kOmegaSST re1p2e7 with `potentialFoam` initialization —
  the family's precedented impulsive-start cure (F5b, B-52 convention; the
  F8 counter-precedent does not apply, no rotating frame here), single
  variable, `Phi` solver block added if absent (the F8 §12 mechanical
  lesson). Cap 2,000 iterations (45× the crash point). Same survival
  criterion.

## Verdict mapping, pre-stated (the filing's two signatures, refined by Phase 0)

- **SHARED root cause:** the probes name the same collapsing quantity in the
  same kind of region in both geometries, AND both levers are
  initialization-class changes that remove both crashes.
- **GEOMETRY-SPECIFIC:** the probes name different collapsing quantities or
  stages (the Phase-0 signatures already lean this way), or one lever works
  and the other does not.
- Rescued configurations re-enter bands only through the standing gate under
  their own future records — nothing here admits anything.

## Predictions, put at risk

- **D1:** all three probes reproduce their archived crashes (same fatal
  site, ±10 iterations).
- **D2:** the monitored collapse differs by geometry — hills: k/epsilon
  driven to their bounds with nut pathological BEFORE the pressure death;
  bump: U max exploding in the thin-boundary-layer/leading-edge region with
  turbulence secondary.
- **D3 (the discriminator):** HL1 SURVIVES its cap (initialization owns the
  hills crash) and BL1 STILL CRASHES (the bump class is regime-owned, not
  start-owned) → **verdict GEOMETRY-SPECIFIC.** Declared alternative: BL1
  also survives — then both crashes are initialization-class and the verdict
  moves to SHARED-BY-CLASS (initialization) even though the mechanisms
  differ in detail; stated now so the wording afterwards is not free.

## Budget

Measured basis: probes ≈ 0.1–0.2 core-min each; HL1 ≤ 3.5 (3,000 hills
iterations at the measured rate); BL1 ≤ 0.6. **Expected total ≈ 5 core-min
against the 25 approved.** All runs serial, one at a time, setsid-detached
via the arm script with per-run records in `FPE_DIAG_runs/<run>/record.json`;
watch handoff: the script and `FPE_DIAG_runs/driver.log` are the state.

*Nothing below this line existed when the arm was launched.*

## Outcome (2026-08-08, arm complete 23:14:50Z)

Pre-registration committed `0be92103`; first launch aborted on a driver bug
(the grading helper copied logs before creating its output directory — fixed,
zero solver loss, the probe had already run), relaunch 23:11Z clean.
**Total 3.54 of 25 core-min.**

| run | result | detail |
| --- | --- | --- |
| HP1 (hills kEpsilon, monitored) | crashed iter **13** | archived crash iter 13 — **exact** reproduction |
| BP1 (bump kOmegaSST, monitored) | crashed iter **44** | archived 44 — exact |
| BP2 (bump kEpsilon, monitored) | crashed iter **38** | archived 38 — exact |
| HL1 (hills lever: per-cell SST-seeded k/epsilon) | **SURVIVED** 3,000 | zero fatals, 230× past the crash point |
| BL1 (bump lever: potentialFoam init) | **SURVIVED** 2,000 | zero fatals, 45× past the crash point |

**What the monitoring named (D2's question):** two different roads to the
one death site. Hills: the **turbulence fields explode globally from the
uniform derived initialization** — at the crash, min(epsilon) = 4.96e+45
(the *minimum*, everywhere), max(k) = 4.7e+108, max(nut) = 2.4e+153 — the
absurd viscosity locks U (explaining the frozen ~1e-7 momentum residuals)
before the pressure solve dies. Bump: a **local momentum divergence** —
max|U| = 9.4e+22 at (x = 0.81, y = 0.046), the near-wall aft-bump region,
with k spiking locally (4.7e+6 near-wall at x = 0.6) and omega at 1.6e+11 —
the impulsive uniform start at nu = 8.3e-8, turbulence secondary.

**Verdict, per the pre-registered mapping: SHARED-BY-CLASS
(initialization)** — the declared alternative of D3, in its exact frozen
wording: both crashes are initialization-class and both levers remove them,
even though the mechanisms differ in detail (hills: the uniform
epsilon-from-constants derivation is the trigger, cured by evaluating the
same identity on the converged SST field per cell; bump: the impulsive
uniform start at the 20× Reynolds step, cured by the family's precedented
potentialFoam init). Not GEOMETRY-SPECIFIC as primarily predicted, and not
the filing's original single-shared-mechanism either.

**Predictions scored:** D1 HELD (three exact-iteration reproductions,
against a ±10 window). D2 HELD (different collapsing quantities and regions,
in the predicted directions). D3 FALSIFIED in its primary wording — BL1
survived — with the pre-declared alternative firing as written.

**Lever-activity proof:** every record carries the mechanical
`levers_verified_active` (launcher echo, hash-bound dictionaries) — the
first family records under the ea0f7d9d adoption; born-clean held on every
launch (checkMesh beside each case before its solver).

**What this buys, and what it does not:** four dead k-family cells across
two families now have named, tested, initialization-class cures — but per
this arm's own gate, nothing is admitted here. Recommended successor (for
the chief's docket pass, not run): re-run the four FPE cells through the
standing batch with the two seeding fixes as declared, pre-registered
initialization changes (`--redo-excluded`, own prereg), letting the standing
gate decide membership; family B's bands and family H's kEpsilon member
would be the payoff if they then converge.
