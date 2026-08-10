# Dead-lever audit, BATCH family — 2026-08-10 (L-40 / Verification Charter v1.5 §9)

Executed under the rule THE SWITCH YOU SET IS NOT THE SWITCH THAT RAN
(`LESSONS.md` L-40; charter §9 `levers_verified_active`): a solver option cited
by a conclusion's reasoning is evidence only when the archived RUNTIME LOG
proves it was active — presence in an input dictionary proves nothing.

Zero solver core-min. Read-only on every existing record; this file is the
audit's only write.

**Why this sweep exists.** The dead-lever audit of 2026-08-08
(`DEAD_LEVER_AUDIT_2026-08-08.md`, 946e4a26) covered DAFoam/adjoint, W4/W5,
ladder-b/S1/SPARTA, W1/W3/f6 and the family-N arms. It touched the batch family
in exactly two rows (`:306`, `:329`) and listed `MODEL_FORM_BATCH_DESIGN.md`
among the files it did **not** verify (`:347`). `docs/CAPABILITY_STRATEGY.md:148`
records the gap and orders this sweep:

> the finding that matters is that **the batch family was never swept by the
> dead-lever precedent**. That sweep is ordered (2026-08-10).

**Scope.** The `model_form_batch` / `mega_batch` workflows and their
conclusion-bearing records: the model-form band records, the `MODEL_FORM_runs`
cell records and ledger, the model-form pre-registrations, the mega_batch
ledgers and family reports, the R12 exemption decisions, the seeded-init rescue
records, and the y+ gate work.

---

## Method, and a methodological correction that changes the numbers

Two archive properties silently hide batch-family evidence from a naive sweep,
and both were hit during this audit before being caught. They are recorded here
because any re-run of this audit will hit them again:

1. **The MODEL_FORM solver logs are gzipped** (`log.simpleFoam.gz`). Plain
   `grep -r` matches none of the 36. Every count below uses `zgrep`/`zcat`.
2. **The shell's `grep` honours `.gitignore`**, so it skips the entire
   `mega-batch/work/` tree. Counts below use `command grep`.

The first parallel inventory of this audit reported that the N_a10 band's three
members carry "zero `Selecting RAS turbulence model` evidence and zero
LEVER-ECHO in their logs", and ranked that as the family's number-one dead
lever. **That reading was an artefact of gz-blind grep and is withdrawn.** The
banner is present in all 36 logs. The correction is stated here rather than
quietly dropped, because it is the difference between the family's flagship
conclusion being unproven and being proven.

Verification was done by direct decompression and cross-check, not by trusting
any record's self-description.

---

## Summary counts

| classification | pairs | note |
| --- | --- | --- |
| **VERIFIED** (log line quoted) | **165** | 162 MODEL_FORM/FPE + 3 mega-batch |
| **UNVERIFIABLE-FROM-LOGS** | **69** | 64 of them merge into ONE structural finding (U-1); 5 distinct others |
| **FOUND-DEAD** | **0** | no lever anywhere in the batch family was set-but-not-run |

**Headline: no dead lever was found in the batch family.** The two conclusions
that most needed proof — the model-form bands' closure attribution and the
N_a10 third member's admission — both verify cleanly and independently against
the archived logs. The audit's real product is the unverifiable list: **64 of
the 69 are one premise** (that the band's members differ only in closure), and
one is a live record whose corroborating log was destroyed by a later rerun.

---

## Dated correction, 2026-08-10 (same day, by the author of this file)

The counts above were corrected within hours of first publication, while
applying chief ruling 2 of 2026-08-10. **The first published version read 133
VERIFIED / 67 UNVERIFIABLE and described U-1 as affecting "31 of 36" cells. Both
were arithmetic errors in this audit, not new evidence.**

- Exactly **4** governing `record.json` files carry `levers_verified_active`
  (`B_re1p2e7_kEpsilon`, `B_re1p2e7_kOmegaSST`, `B_re1p2e7_realizableKE`,
  `H_re10595_kEpsilon`), not 5. The 5th echo record is
  `H_re10595_realizableKE/record_out_of_scope_…json` — the leaked rerun of U-2,
  which is not a governing record. So U-1 affects **32** cells, and the
  affected-cell list printed in U-1 always had 32 entries: the prose disagreed
  with this audit's own list.
- The VERIFIED total under-counted its own table: the rows sum to 162 for
  MODEL_FORM plus 3 for mega-batch. `residual_control_met` is true on 14 cells,
  not 15.

No classification changed and no conclusion moves. Recorded here rather than
silently repaired, on the same principle that put the withdrawn first-pass
headline on this file's face: an audit that hides its own corrections is asking
to be trusted on exactly the thing it failed at.

---

## FOUND-DEAD list

**Empty.** Every lever cited by a batch-family conclusion either verified in the
archived runtime log, or is unverifiable in both directions (no evidence that it
ran; equally no evidence that it did not). Nothing in this family matches the A3
`transonicPCOption 2` specimen, where the archive positively proved a cited
switch was dead code.

Two near-misses are recorded so they are not mistaken for clean bills:

- **N-1. The Ahmed refinement promotion has never fired in any archived run**
  (U-3 below). It is live, wired code — not dead — but the archive contains zero
  runs that exercised it. This is the closest thing in the family to a
  set-but-never-ran lever, and it is the one to watch.
- **N-2. `H_re10595_realizableKE`'s governing record is contradicted by the log
  sitting next to it** (U-2 below). The record is not wrong; its evidence was
  overwritten.

---

## VERIFIED — the table

### Group A/B: model-form bands and the 36 `MODEL_FORM_runs` cell records

Conclusions served: every `CONTAINED` / `NOT contained` / `no band` verdict in
`MODEL_FORM_BAND.md` (`:32`, `:63`, `:68`, `:108-109`) and `MODEL_FORM_BAND.json`,
the method claim in `models/curriculum/uq-studies/tmr_flatplate_modelform.json:4`,
and all 36 per-cell converged/excluded verdicts.

| lever | pairs | class | evidence |
| --- | --- | --- | --- |
| Closure / RAS model selection | **36** | VERIFIED | Every cell's `record.json` `"model"` matches the `Selecting RAS turbulence model X` banner in its own log, 36 for 36. `N_a10_SpalartAllmaras/log.simpleFoam.gz:45`, `N_a10_kEpsilon/log.simpleFoam.gz:45`, `N_a10_kOmegaSST/log.simpleFoam.gz:45`, `H_re10595_kEpsilon/log.simpleFoam.gz:31576`, `P_re5e6_kOmegaSST/log.simpleFoam.gz:45` |
| `printCoeffs` coefficient dump | 36 | VERIFIED | `P_re5e6_kOmegaSST/log.simpleFoam.gz:43-52` — `Selecting incompressible transport model Newtonian` (`:43`), `Selecting RAS turbulence model kOmegaSST` (`:45`), `printCoeffs on;` (`:51`), `alphaK1 0.85;` (`:52`) |
| Stop condition (backstop vs residualControl) | **36** → 35 | VERIFIED | Systematic cross-check of `record.json` `iterations` against the log's own last `Time = N`: **35 of 36 agree exactly.** The single mismatch is U-2. |
| `residualControl` convergence gate | 14 | VERIFIED | `SIMPLE solution converged in N iterations` matches the record's iteration count on every converged cell. `N_a10_kEpsilon/log.simpleFoam.gz:296323` (10431), `N_a10_kOmegaSST/log.simpleFoam.gz:229971` (8210), `H_re10595_kEpsilon/log.simpleFoam.gz:145855` (8780), `H_re10595_kOmegaSST/log.simpleFoam.gz:78269` (5997) |
| Iteration backstop 12,000, active and binding | 1 | VERIFIED | `N_a10_SpalartAllmaras/log.simpleFoam.gz:324077` reads `Time = 12000` with **no** convergence banner anywhere in the file; record carries `iterations: 12000`, `residual_control_met: false`. The backstop stopped the run. |
| Raised cap 30,000 (family-H extension) | 1 | VERIFIED | `H_re10595_SpalartAllmaras/log.simpleFoam.gz:148550` — `SIMPLE solution converged in 12361 iterations`. 12,361 lies beyond the old 12,000 cap, so the raised cap was necessarily active. Independently reproduces the prereg's own claim at `MODEL_FORM_H_EXTENSION_PREREGISTRATION.md:136-141`. |
| `potentialFoam` initialization | 15 | VERIFIED | A separate `log.potentialFoam` is archived per cell: 3 × `B_re1p2e7_*` and all 12 `N_a*_*`. |
| R12 mesh-gate exemption, factual basis | 12 | VERIFIED | The number the exemption was granted on is in the archived mesh log: `N_a10_SpalartAllmaras/log.checkMesh:94` — `Mesh non-orthogonality Max: 85.69872592 average: 15.01469094`, against the 70° hard gate. Carried on all 12 `N_a*` records. |

**The N_a10 adjusted settle criterion — recomputed, not taken on trust.**
`N_A10_THIRD_MEMBER_PREREGISTRATION.md:162-173` turns Cl from NOT contained
(n=2) to **CONTAINED** (n=3) by admitting `N_a10_SpalartAllmaras`, which failed
`residualControl` and was admitted instead under the pre-registered adjusted
settle rule (`MODEL_FORM_runs/adjusted_settle_n_a10.json`). Because that rule is
a post-hoc gate over the log's own history, its activity is directly
recomputable. Re-deriving the residual-plateau half straight from
`N_a10_SpalartAllmaras/log.simpleFoam.gz` (12,000 `Ux` and `nuTilda` initial
residuals, 24,000 for `p`):

| quantity | record | recomputed from the log | agreement |
| --- | --- | --- | --- |
| `Ux` median, final quarter | 5.508573643e-09 | 5.508320477e-09 | 5 s.f. |
| `Ux` median, previous quarter | 5.498467069e-09 | 5.498391446e-09 | 5 s.f. |
| `nuTilda` median, final quarter | 1.861528477e-08 | 1.861299497e-08 | 5 s.f. |

**VERIFIED.** The band's most load-bearing and most contestable admission
reproduces from the archived log.

### Group E: seeded-init rescue records

| lever | pairs | class | evidence |
| --- | --- | --- | --- |
| Seeded init `sst_seeded_kepsilon` (donor field, not a uniform seed) | 4 | VERIFIED | The launcher echo embeds the initial fields' full text in the log. `H_re10595_kEpsilon/log.simpleFoam.gz:242+` — `0/epsilon` is `nonuniform List<scalar>` of **15600** per-cell values; `:15861+` — `0/k` likewise. A uniform seed would read `uniform`. The donor is named at `H_re10595_kEpsilon/record.json` (`F6b_runs/medium/5997`). |
| `levers_verified_active`, hash-bound | 4 | VERIFIED (mechanical) | `H_re10595_kEpsilon/record.json:20-74`, basis `"launcher echo, hash-bound to the dictionaries that ran (Verification Charter v1.5 section 9)"`. Same on the 3 `B_re1p2e7_*` rescue records. A 5th echo record exists but is NOT a governing record: `H_re10595_realizableKE/record_out_of_scope_20260808T235259Z.json`, the leaked rerun of U-2. |

**This is the family's good news, and it is worth stating plainly.** The
lever-echo mechanism adopted at `ea0f7d9d` does not merely hash the dictionaries
— it writes their **entire text** into the solver log, delimited by
`==== LEVER-ECHO BEGIN ====` / `END`. For the four governing cells that carry it, levers
OpenFOAM structurally never echoes become log-provable:

```
H_re10595_kEpsilon/log.simpleFoam.gz:3      LEVER-ECHO file system/fvSchemes  sha256 b41b7447ec…
H_re10595_kEpsilon/log.simpleFoam.gz:83     LEVER-ECHO file system/fvSolution sha256 ff711586…
H_re10595_kEpsilon/log.simpleFoam.gz:181    LEVER-ECHO file constant/turbulenceProperties sha256 645a54d3…
H_re10595_kEpsilon/log.simpleFoam.gz:15855  bottomWall { type epsilonWallFunction; lowReCorrection true; … }
H_re10595_kEpsilon/log.simpleFoam.gz:31489  bottomWall { type nutLowReWallFunction; value uniform 0; }
H_re10595_kEpsilon/log.simpleFoam.gz:31504  bottomWall { type omegaWallFunction; value uniform 0.110227…; }
```

Those three wall-function lines verify, for these four governing cells only,
three of the four boundary-condition levers declared at
`MODEL_FORM_BATCH_DESIGN.md:335-338`.
**Where `levers_verified_active` is present the verification is mechanical and
this audit says so rather than re-deriving it.**

### Group F/G: mega_batch

| lever | pairs | class | evidence |
| --- | --- | --- | --- |
| F10 3-D viscous family closure `kOmegaSST` (serves the `Family-level validation gate: PASS` at `F10_3D_VISCOUS_FAMILY.md:147`) | 1 | VERIFIED | `mega-batch/work/ahmed-viscous/case-206927/log.simpleFoam:45` — `Selecting RAS turbulence model kOmegaSST`. 17 case dirs with 34 solver logs survive for this family. |
| Cylinder-unsteady laminar formulation (`PHYSICS_FAMILIES.md:18`) | 1 | VERIFIED | `mega-batch/work/cylinder-unsteady/case-206345/log.pimpleFoam:41-42` — `Selecting turbulence model type laminar` / `Selecting laminar stress model Stokes` |
| y+ band gate `[30, 500]` as applied pre-fix | 1 | VERIFIED | The gate's readings are on the ledger: all 52 `simplefoam-ahmed-3d-viscous` rows carry `yplus_avg`; the 28 rows above the Re threshold span 455.4–499.1, **none over 500**. Gate constants at `sdk/workflows/mega_batch.py:141-142`. |

---

## UNVERIFIABLE-FROM-LOGS — the list

### U-1. The band's "only the closure differs" premise, 32 of 36 members (64 pairs)

**This is the audit's principal finding.** A model-form band means nothing
unless its members differ *only* in the closure. That sameness is asserted in
three places:

- `models/curriculum/uq-studies/tmr_flatplate_modelform.json:4` — `"identical mesh, schemes and residual targets"`
- `MODEL_FORM_BATCH_DESIGN.md:339-341` — `**Schemes, relaxation and residual targets are held fixed across models.** The only things that change inside a (family, regime) group are the RASModel entry and the turbulence fields`
- `N_A10_THIRD_MEMBER_PREREGISTRATION.md:45-46` — `**Numerics, schemes, relaxation and residualControl targets are byte-for-byte the batch's own — nothing about the solve changes.**`

OpenFOAM's steady `simpleFoam` **never echoes fvSchemes, fvSolution or boundary
condition types**. Measured directly:

```
zgrep -c "WallFunction|lowReCorrection"  N_a10_kEpsilon/log.simpleFoam.gz  →  0
zgrep -c "linearUpwind|Gauss|divScheme"  N_a10_kEpsilon/log.simpleFoam.gz  →  0
```

For the 4 lever-echo cells the premise is fully proven (above). For the other
**32** it cannot be proven or disproven from the logs — 32 cells × 2 lever
classes (schemes/solution; wall-function BCs) = **64 pairs**. Nothing suggests
the premise is false; it is simply unevidenced, and per charter §9 it must ride
on the bands' faces as unverifiable-from-logs.

The 32 predate `ea0f7d9d` (2026-08-08 22:59:34Z) and **can never be repaired
retroactively** — `sdk/chief_engineer/lever_echo.py`'s own docstring concedes
that for these classes "no discipline at record-writing time can recover the
evidence afterwards." The only route to proof is re-running the cells under the
echo. That is a chief's call, not this audit's.

Affected: `B_re1p2e7_SpalartAllmaras`, all 4 `B_re3e6_*`, `H_re10595_{SpalartAllmaras,kOmegaSST,realizableKE}`, all 4 `N_a0_*`, all 4 `N_a10_*`, all 4 `N_a15_*`, all 4 `P_re1e6_*`, all 4 `P_re2e7_*`, all 4 `P_re5e6_*`.

### U-2. `H_re10595_realizableKE` — the governing record's log was overwritten

The live `record.json` reads `iterations: 30000`, `iteration_backstop: 30000`,
excluded on `residualControl not met (stopped on the backstop)`. **The
`log.simpleFoam.gz` sitting beside it ends at `Time = 12000`.** It is the only
record/log mismatch in all 36 cells.

The cause is on the record and is not a defect in the conclusion: the FPE-rescue
launch filter's family×regime×model cross-product leaked this cell
(`MODEL_FORM_FPE_RESCUE_PREREGISTRATION.md:127-136`), and the leaked 12,000-iteration
rerun **overwrote the 30,000-iteration run's log in place** on 2026-08-08 at
23:52. The directory still holds both `12000/` and `30000/` time directories, so
the fields survive; the log does not. The rescue honestly retained its own
result as `record_out_of_scope_20260808T235259Z.json`.

**Impact: bounded, and the conclusion stands.** `MODEL_FORM_H_EXTENSION_PREREGISTRATION.md:117,145-147`
excludes realizableKE and concludes `Family-H membership final: n = 1`. Both the
30,000 record and the 12,000 rerun exclude the cell for the *same two reasons*
(backstop stop, plus `no steady bubble: 0 skin-friction sign changes`), so the
membership verdict is robust to which run one believes. What is lost is the
ability to corroborate the 30,000-cap stop from its own log.

**Lesson for the chief, not written into any record by this audit:** a rerun
that lands in an existing case directory destroys the prior run's L-40 evidence
even when its own record-keeping is impeccable. The rescue's leak was caught and
disclosed; the log overwrite it caused was not.

### U-3. The Ahmed refinement promotion has never been exercised in the archive

`F10_YPLUS_FIX.md:26-28,86-89` concludes the gate was correct and the design
space was wrong, and rests on a promotion lever: `AHMED_REFINEMENT_HIGH_RE = 3`
above `AHMED_REFINEMENT_RE_THRESHOLD = 2.8e6`
(`sdk/workflows/mega_batch.py:122-123`).

The lever is **live code, not dead code** — `mega_batch.py:594`
`refinement = _ahmed_refinement_for_reynolds(reynolds)`, consumed four lines
later by `build_case(..., refinement=refinement, ...)` at `:601-602`. It is not
an A3-class specimen.

But no archived run has ever exercised it:

- The fix landed in `a75e1fa1` at **2026-07-29 18:25:47Z**. The **last** of the
  52 archived `simplefoam-ahmed-3d-viscous` ledger rows is **2026-07-29T11:16:13Z**
  — seven hours earlier. Every archived ahmed row is pre-fix.
- All 52 rows carry `cells` ∈ {45760, 45813}, i.e. refinement 2 — **including all
  28 rows above the 2.8e6 threshold**, which is correct pre-fix behaviour and
  proves only that the promotion was not yet in force.
- `metrics.mesh_refinement` — which `F10_YPLUS_FIX.md:43` promises is "now
  recorded per row … for auditability" — appears on **0 of 52** rows. The code
  does write it (`mega_batch.py:236`, `:712`); there is simply no post-fix ahmed
  row in the archive to carry it.
- The document's own BEFORE/AFTER verification points are indices **1715, 419,
  3215, 239**. None has a surviving case directory, and none appears in the
  ledger. **The load-bearing measurement — y+ avg 463.89 at refinement 3, 79,439
  cells — cannot be checked against any archived log.**

Classification: unverifiable-from-logs, not dead. The promotion's correctness
rests entirely on the table inside `F10_YPLUS_FIX.md` itself.

### U-4. Transonic family gate — 280 passing rows, zero surviving logs

`PHYSICS_FAMILIES.md:167` states `VALIDATION GATE RESULT: PASS (banded, shock
position) — CORRECTED 2026-07-30`, reasoning from `:95` `**Solver**:
rhoSimpleFoam (compressible, steady SIMPLE), kOmegaSST`. The ledger holds **280**
`rhosimplefoam-naca0012-transonic` rows, all `ok: true`. `mega-batch/work/transonic-naca0012/`
exists and contains **0 case directories**. Neither the solver identity nor the
closure can be verified from any archived log.

### U-5. Steady-cylinder laminar lever — logs present but restart-collided

`PHYSICS_FAMILIES.md:18` reasons from `**Solver**: pimpleFoam, laminar`. 16
steady-cylinder logs survive, but they are corrupted by the restart-collision
pattern: `mega-batch/work/cylinder/case-059901/log.simpleFoam` opens mid-file
with `--> FOAM FATAL IO ERROR … Cannot open file postProcessing/forceCoeffs1/0/coefficient.dat`
before the next run's header, and carries no selection banner. The unsteady
sibling verifies (above); the steady family's own banner does not survive.

### U-6. Wing family — 11 logs against 69,149 rows

`COST_SCALING.md:75` concludes `**vspaero-wing clears it 6,457 times in a row
with an R2 of 0.0002.**` `mega-batch/work/wing/` holds 557 case dirs and **11**
`log.vspaero` files against 69,149 ledger rows. The solver-identity lever behind
the cost-scaling conclusions is unverifiable at population scale.

---

## What this audit did NOT cover — stated, not silently truncated

1. **The 38 superseded `record_superseded_*.json` files** under
   `MODEL_FORM_runs/` were not individually swept. They are superseded by
   design and no conclusion cites them. The one `record_out_of_scope_*.json`
   **was** swept (U-2).
2. **The reduced-order mega-batch family (69,007 ledger rows)** has no
   `work/reduced-order` directory and never produced solver logs — it is an
   analytic/reduced-order model, so there is no solver lever to verify. Its
   conclusions in `learned_study.json` and `COST_SCALING.md:130` are outside
   L-40's reach rather than failing it.
3. **`COST_SCALING.md` and `LEDGER_DUPLICATES.md` reason statistically over
   ledger rows** and cite no solver option, scheme, model or gate setting beyond
   solver *identity* (covered at U-6). They are not lever-bearing and were not
   forced into the table.
4. **`GEN_ALT_runs/`** carries `log.blockMesh` + `log.checkMesh` only — mesh
   stage, no solver run, no solver lever. Adjacent to the family, not in it.
5. **The two batch rows already verified by the 2026-08-08 audit** (`:306`,
   `:329`) were not redone, per that audit's own precedent of citing prior
   activity proof rather than repeating it.
6. **No mega_batch ledger row was re-derived.** `ledger.jsonl` (208,194 rows) is
   untracked by git (`.gitignore:24-25,39-44`) and exists only on this machine's
   disk. That is a durability finding rather than an L-40 one, and it is flagged
   here because the batch family's largest conclusion corpus has no
   version-controlled backup.

---

## For the chief

- **Nothing is reopened by this audit.** No FOUND-DEAD lever, therefore no
  conclusion loses its footing. The N_a10 band and the H membership verdict both
  survive direct verification.
- **U-1 is a labelling job, not an investigation**: 31 of 36 model-form cells
  owe an unverifiable-from-logs caveat on the sameness premise, per charter §9.
  Re-running them under the lever echo is the only route to proof and is a cost
  decision.
- **U-3 is the one to watch**: the Ahmed refinement promotion is correct-looking
  live code that no archived run has ever exercised. The first post-fix ahmed
  batch will settle it, and will carry `metrics.mesh_refinement` automatically.
- **U-2 names a process hazard worth a lesson**: a rerun into an existing case
  directory silently destroys the previous run's L-40 evidence. The seeded-init
  rescue disclosed its leak honestly and still cost the archive a log.
