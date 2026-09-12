# VMFL072-R5 — PRE-REGISTRATION

**FREEZE STATUS: FROZEN 2026-09-12. THE COMMIT CONTAINING THIS LINE IS THE FREEZE.** Frozen by the ansys-verification-supervisor after personal check 1 (comparator verdict block read as a diff: survival `try` catches ONLY completion+C-08b, FilmRun built outside it so an instrument fault hard-refuses; plant fires BEFORE any number; verdict() one-way, no PASS; R4A_BLOB_SHA pinned and refused before the AST compare) and check 4 (run root `verification/runs/ansys_verification/VMFL072-R5` ABSENT, re-asserted in the committing invocation; launcher aborts if the film fvSolution names DILU/PBiCGStab/PCG -- it cannot re-enter the reciprocal-diagonal path that produced all five crashes). Every core-min figure in sec.6 is a CALIBRATION PREDICTION, NOT A CAP-STOP (Sanaa 2026-09-12); no timeout, no drawdown, no kill.
This file is the lane's draft for the `ansys-verification-supervisor`. It becomes
the freeze only when the supervisor, having done the `SUPERVISION_CHARTER` §3
check-1 (comparator read as a diff), check-3 (cost) and check-4 (committed before
compute) **personally**, commits it together with its comparator, driver, apply
script and `base/` inputs (`CLAUDE.md` rule 2). **The committing supervisor MUST,
in that same commit, replace the line above with**
`FREEZE STATUS: FROZEN <commit-sha> <date>` **and record the prereg sha in the
launch record.** This header is written to state its status truthfully *now*; it
must not reach a freeze commit still reading "DRAFT" (the defect carried in
VMFL072-R4-A's frozen header, which this file does not reproduce).

Authored by an `ansys-lane-opus48` lane. This document redesigns nothing on its
own authority: the strategy (move to `kinematicSingleLayer`, VOF held as named
fallback) is the supervisor's ruling of 2026-09-12; this file pins the numbers the
freeze requires and records the evidence for and against that ruling.

---

## §0. THE RULING, THE EVIDENCE, AND ONE CORRECTION THE SUPERVISOR IS OWED

**Ruling implemented:** VMFL072-R5 drives the finite-volume single-layer film
`regionModels::surfaceFilmModels::kinematicSingleLayer` with `reactingParcelFoam`,
run inert (no chemistry, no combustion, no radiation, cloud inactive). VOF
(`interFoam`) is the registered fallback (§7).

**The corrected reason (the supervisor's own correction of 2026-09-12, verified
here from v2606 source and a positive-path smoke).** The SIGFPE that killed five
runs (VMFL072 R2-L3, R3-L3, R4-A A1/A2/A3 — the 17-frame trace is byte-identical
across all five) is raised at `DILUPreconditioner::calcReciprocalD` in **core
`libOpenFOAM.so`**, while *constructing* the preconditioner — a reciprocal of a
zero/denormal matrix diagonal, before any solve iteration. That core code is shared
by **every** solver, `kinematicSingleLayer` included. So the ruling does **not**
rest on "leaving the failing library." It rests on two things, one of which I must
qualify:

1. **A different film-model implementation** — frame #10 of the crash is
   `regionModels::areaSurfaceFilmModels::kinematicThinFilm` in
   `libregionFaModels.so` (the **finite-area** thin-film shell driven through
   `velocityFilmShellFvPatchVectorField::updateCoeffs()`). `kinematicSingleLayer`
   is a **finite-volume** model in `libsurfaceFilmModels.so` with its own
   assembly and degeneracy handling. Confirmed distinct in source (§1.2).

2. **⚠ HONESTY CORRECTION THE SUPERVISOR IS OWED — the two models share the
   thickness-scaled momentum-diagonal STRUCTURE; `kinematicSingleLayer` is NOT
   immune by virtue of a "different diagonal".** Both assemble a momentum matrix
   whose transient diagonal scales with film thickness and vanishes as the film
   dewets:
   - finite-area (the crasher): `kinematicThinFilm.C:59` `fam::ddt(h_, U)` and the
     `Uf_` solve at `:110–118` → diagonal `h·V/dt → 0` as `h→0`;
   - single-layer (R5): `kinematicSingleLayer.C:~294` `fvm::ddt(deltaRho_, U_)` →
     diagonal `delta·rho·V/dt → 0` as `delta→0`.
   What actually differs, and what breaks the five-crash chain, is (a) the **wall
   friction regularisation** in the FV model and (b) the **linear-solver choice**,
   NOT the ddt term. These are stated precisely in §1.2–§1.3 and are the reason R5
   is expected to survive dewetting where the finite-area path could not.

**If §1.2's distinction is wrong — if the two share the degenerate-matrix path in a
way I have not seen — the ruling breaks and I would want that known before the
freeze.** I do not find that; my reading and the smoke both say the FV path is
conditioned at `delta=0`. But I flag the shared ddt structure so the claim is not
overclaimed: the escape is verified by observers at run time (§5), never assumed.

---

## §1. WHY kinematicSingleLayer IS CONDITIONED AT DEWETTING — SOURCE + SMOKE

### §1.1 The driving solver, and that there is no lighter one

Exactly three installed solvers instantiate the standalone region-model film via
`regionModels::surfaceFilmModel::New(mesh, g)`:

- `reactingParcelFoam` — `applications/solvers/lagrangian/reactingParcelFoam/createSurfaceFilmModel.H:5`
- `fireFoam` — `applications/solvers/combustion/fireFoam/createSurfaceFilmModel.H:5`
- `compressibleInterFilmFoam` — `applications/solvers/multiphase/compressibleInterFoam/compressibleInterFilmFoam/createSurfaceFilmModel.H:6`

There is **no film-only solver** in this installation (`surfaceFilmModel::New` has
no other caller in `applications/` or `src/`; verified by grep). `fireFoam` adds
pyrolysis + combustion + radiation; `compressibleInterFilmFoam` adds a compressible
two-phase VOF primary. **`reactingParcelFoam` is the lightest of the three for an
isothermal, non-reacting film**, because its extra machinery can all be made inert:
this is not speculative — the shipped tutorial
`tutorials/lagrangian/reactingParcelFoam/rivuletPanel` (a laminar **water** film on
a panel) runs with `combustionModel none`, `chemistry off`
(`noChemistrySolver`), `radiation off`, and cloud `active no`. That tutorial is the
design and cost anchor for R5.

Honest cost caveat: "lightest available" is not "light". `reactingParcelFoam` still
stands up a **compressible thermo primary region** (T, p, p_rgh, species) even
though the air is quiescent. R5 accepts this because the primary is a passive
ambient (§1.4) and the alternative solvers are strictly heavier.

### §1.2 The two film models are distinct implementations (source)

`kinematicSingleLayer` registers to a different runtime table in a different library:
`kinematicSingleLayer.C:55` `addToRunTimeSelectionTable(surfaceFilmRegionModel, kinematicSingleLayer, mesh)`
(`libsurfaceFilmModels.so`), versus the finite-area `kinematicThinFilm`
(`libregionFaModels.so`). The FV thickness equation
(`kinematicSingleLayer.C:~369`) is
`fvm::ddt(rho_, delta_) + fvm::div(phid, delta_) - fvm::laplacian(ddrhorUAppf, delta_) == -rhoSp_`
— its diagonal is `rho·V/dt`, **independent of thickness**, so the *thickness*
solve (the direct analog of the crashing `hf_film` solve) is unconditionally
well-conditioned. Post-solve `delta_.clamp_min(0)` (`:401`) bounds thickness at
**zero** (not at an `h0` floor).

### §1.3 The momentum diagonal is kept finite and positive by the friction Sp term

The momentum ddt diagonal vanishes as `delta→0` (§0 item 2), but the laminar wall
friction adds a bounded positive diagonal contribution. `laminar.C:123–130`:

```
Cs = Cf * rhop * mag(Up - U);                        // air-side (Up≈0 here)
Cw = mu / ((1.0/3.0)*(delta + film.deltaSmall()));   // wall-side
Cw.clamp_max(5000.0);
return  - fvm::Sp(Cs, U) + Cs*Up   - fvm::Sp(Cw, U) + Cw*Uw;
```

`-fvm::Sp(Cw, U)` adds `+Cw·V` to the momentum diagonal. As `delta→0`, `Cw` rises
but is **clamped at 5000** (`laminar.C:125`) and its denominator carries
`deltaSmall` (`= SMALL ≈ 1e-15`, hardcoded constructor default
`kinematicSingleLayer.C:437`; NOT dictionary-exposed, so it cannot be
mis-configured), while `delta` is clamped `≥ 0` before it re-enters. The
denominator therefore **cannot go negative** — unlike the finite-area path, whose
`Cw = 3·mu/((h+h0)·rho)` R4-A diagnosed as able to go negative on a transient
undershoot below `−h0`, poisoning the diagonal. Result: the FV momentum diagonal
`delta·rho·V/dt + (Cs+Cw)·V` stays **strictly positive and finite at `delta=0`**.

### §1.4 Positive-path smoke — the model+solver survive dewetting on this box

Answer-blind smoke, in scratch, this exact model+solver+physics (rivuletPanel,
laminar water film), single rank, load 56.7, `FOAM_SIGFPE` trapping ON:
- 20 fixed steps (`deltaT 1e-4`), **rc=0, no SIGFPE**;
- `min/max(delta) = 0, 4.60e-05` — **dewetted cells (delta=0) present and the run
  did not fault** — the positive path exercised, not inferred;
- `Courant Number mean/max = 0` — the quiescent primary imposes **no**
  convective/acoustic dt limit (pressure-based PIMPLE), so R5's dt is set by film
  stability, not primary acoustics (bears on §6);
- film Info per step prints `min/max(mag(U))`, `min/max(delta)`, `coverage`, and
  `smoothSolver: Solving for Ufx/Ufy/Ufz` / `deltaf … Final residual` — the exact
  channels R5's observer and NaN/inf guard read (§5).

Artifacts (scratch, ephemeral): `…/scratchpad/rp/log.rp`. This smoke created no run
root under `verification/runs/`.

---

## §2. WHAT R5 REUSES FROM R4-A, AND WHAT MUST CHANGE

**REUSED (carried over verbatim — not rediscovered):**

| quantity | value | source |
|---|---|---|
| film inlet thickness `H_IN` | `7.1084204656e-04` m | R4-A `LEVEL_APPLIED.txt` |
| film inlet velocity `U_IN` | `0.537381243` m/s (downslope) | R4-A `LEVEL_APPLIED.txt` |
| ⇒ inlet mass flux Γ = ρ·H_IN·U_IN | `0.381995` kg/m/s (per width) | derived, ρ=1000 |
| domain | 500 × 100 × 100 mm | manual p.211 |
| gravity (40° incline) | g=(6.305746, 0, −7.514896) m/s² | manual p.211–212 |
| water properties | ρ=1000, μ=1e-3, σ=0.07 | R4-A / rivuletPanel constantCoeffs |
| manual reference | 0.555 mm (Roy & Jain 1989) | manual Table .72.1 |
| Ansys Fluent (context only) | 0.5497 mm, ratio 0.99 | manual Table .72.1 |
| Limb-A band | `[0.543234, 0.566766]` mm (±2.12%) | R4-A §5 |
| monitor window | x∈[0.440,0.460], y∈[0.025,0.075] m, area-weighted | R4-A §6 |
| admissibility floor `D_MIN_ADMISSIBLE` | `1e-06` m | R4-A §6 |
| plant machinery / rule-3 control | `PLANT = 1.234e-05` m, read-back-or-refuse | R4-A §6 |
| single-grid stance (no Roache triple in R5) | — | R4-A §6; §5 below |

**MUST CHANGE (because the film model changed):**

1. **Film model & library.** `velocityFilmShell` (finite-area, `libregionFaModels.so`)
   → `kinematicSingleLayer` (finite-volume, `libsurfaceFilmModels.so`).
2. **Driver.** `pimpleFoam` + film-shell patch BC → `reactingParcelFoam` (inert).
3. **The `h0` knob is RETIRED.** R4-A's entire ladder swept the precursor
   thickness `h0` of the finite-area shell. `kinematicSingleLayer` has **no `h0`**;
   its dewetting is handled by `delta_.clamp_min(0)` + the bounded `Cw` (§1.3), not
   a precursor floor. R5 is therefore **not** a ladder — it is one case.
4. **Mesh.** faMesh on the wall patch → a 3D primary box mesh (`blockMesh`) plus a
   **mapped film region** extruded from the plate patch (`topoSet` +
   `extrudeToRegionMesh`, exactly rivuletPanel's `Allrun.pre` path).
5. **Film fields.** `hf_film`, `Uf_film` (faMesh) → `deltaf`, `Uf`, `Tf`
   (film region; thickness is written to disk as `deltaf`,
   `kinematicSingleLayer.C:487`).
6. **Film inlet mechanism.** A film-region `inlet` patch (top strip of the plate)
   with `deltaf` `fixedValue = H_IN` and `Uf` `fixedValue = U_IN` downslope —
   directly reproducing rivuletPanel's inlet pattern and delivering Γ above. This
   is the clean reuse of R4-A's `H_IN`/`U_IN` in the new model.
7. **Film linear solver — now a FROZEN setting (§3).**

---

## §3. THE FROZEN FILM LINEAR SOLVER — a pre-registered choice, not an inherited default

Per the supervisor's design requirement of 2026-09-12: the film linear solver and
preconditioner are dictionary settings, therefore ours to freeze.

**FROZEN (film-region `system/wallFilmRegion/fvSolution`):**
```
solvers { "(Uf|deltaf.*)" { solver smoothSolver; smoother symGaussSeidel;
                             tolerance 1e-10; relTol 0; } }
PISO { momentumPredictor yes; nCorr 1; nNonOrthCorr 0; }
```
Justification (three parts, the third answering the supervisor's warning):
1. It is the **validated tutorial solver** for this exact model (rivuletPanel), and
   the smoke ran clean with it (§1.4).
2. `smoothSolver`/`symGaussSeidel` is a **relaxation** solver: it calls neither
   `lduMatrix::preconditioner::New` nor `DILUPreconditioner::calcReciprocalD`. So
   the **exact frame-#3 fault that killed all five prior runs cannot fire** —
   structurally, not probabilistically. R4-A used `DILU`/`PBiCGStab`; DILU is
   precisely the algorithm that inverts the diagonal and cannot survive a zero one.
3. **This is NOT "buy a number instead of a crash".** A genuinely singular momentum
   diagonal would still produce a NaN/inf in the Gauss–Seidel sweep. R5 does **not**
   swallow that: the survival gate (§5, C-08b) **refuses** on any NaN/inf film
   residual and on `max|Uf|` exceeding a physical bound. A run that only *completes*
   because the solver limped past a degenerate matrix is graded **`NOT A RESULT`**,
   never `GATE REACHED`. The tolerant solver is paired with a hard observer so that
   escape is *measured*, not assumed.

---

## §4. THE CASE — MESH, BCs, TIMING (all frozen, prediction-first)

**Primary mesh (`base/system/blockMeshDict`).** Box 0.5 × 0.1 × 0.1 m. x =
along-plate (downslope, +g_x), y = plate-transverse (100 mm width), z = plate-normal
(quiescent air). Cells: **256 (x) × 64 (y) × 4 (z) = 65,536**. **The primary is a CARRIER MESH, not
a resolved physics domain** (supervisor ruling Q3, 2026-09-12): the air is quiescent
(`Co≈0`, §1.4), so it exists only to supply the film's near-wall p/U/rho, and the
film answer is insensitive to its plate-normal (z) count. z=4 is the passive-ambient
minimum. **This is WHY no primary-side grid convergence is claimed** — a reader must
not mistake 4 cells for under-resolution of a physics domain. Plate-patch resolution
256×64 **matches R4-A's resolved grid** so the film discretisation is comparable
across the model change.

**Film region.** Built by `topoSet` (select the plate wall faceSet) +
`extrudeToRegionMesh -overwrite` (rivuletPanel `Allrun.pre` path) → a single-layer
`wallFilmRegion` of **256×64 = 16,384** film cells over the plate.

**Boundary conditions.**
- Primary: plate = wall (film-coupled mapped patch `region0_to_wallFilmRegion_…`);
  the three open box faces = `pressureInletOutletVelocity`/`totalPressure` ambient
  (quiescent air, zero gauge); top (z=0.1) = slip/ambient. Air `U` internal `(0 0 0)`.
- Film `deltaf`: `inlet` (top x=0 strip, 5 mm injection width per manual)
  `fixedValue H_IN`; `outlet` (bottom x=0.5) `zeroGradient`; sides `zeroGradient`;
  top free surface `zeroGradient`; wall-coupled `zeroGradient`.
- Film `Uf`: `inlet` `fixedValue (U_IN 0 0)` (downslope +x); `outlet` `zeroGradient`;
  wall-coupled `noSlip`; free surface `slip`; sides `noSlip`.
- Film `Tf`: `fixedValue 300 K` throughout (isothermal; `filmThermoModel constant`,
  so `Tf` is inert — carried only because the region model constructs the field).

**⚠ THE BC SET IS A FROZEN MODELLING CHOICE (supervisor ruling Q2, 2026-09-12), read
as a diff at check-1.** The manual specifies "air flow zero" but names no boundary
set, so the quiescent-air ambient conditions above are **frozen explicitly, not
defaulted** — the manual's silence is exactly why they must be pinned. One-line
justification: quiescent isobaric air is represented by zero-gauge open ambient
boundaries (`pressureInletOutletVelocity`/`totalPressure`) that neither drive nor
resist the film; the film is forced only by gravity and its inlet Γ. The freeze does
not happen until the supervisor has read this set.

**Film model dict (`base/constant/surfaceFilmProperties`).**
`surfaceFilmModel kinematicSingleLayer; region wallFilmRegion; active true;`
`kinematicSingleLayerCoeffs { filmThermoModel constant; constantCoeffs { specie water;
rho0 1000; mu0 1e-3; sigma0 0.07; } injectionModels (); turbulence laminar;
laminarCoeffs { Cf 0; } forces (); }`. **`Cf = 0`** (air-side friction; carried over
from R4-A §3.3 — quiescent air exerts no surface drag). `forces ()` empty (no
thermocapillary, no contact-angle distribution — VMFL072 is a plain gravity film).

**Timing (`base/system/controlDict`).** `application reactingParcelFoam;`
`deltaT 1.0e-03;` **`adjustTimeStep no;`** (deterministic cost and an exact
`ExecutionTime` count for the rule-4 completion check); `endTime 8.0;` →
**8,000 steps** (matches R4-A's step budget for comparability); `writeControl
timeStep; writeInterval 50;` → **160 written dirs**; `writeFormat ascii;
writePrecision 10;`. Inert sub-dicts copied from rivuletPanel: `combustionModel
none`, `chemistry off`, `radiation off`, cloud `active no`.

**No grid triple in R5 (rule 5, stated explicitly).** R5 is **single-grid**
(256×64 film). It establishes survival + retention in the new model on one mesh; it
does **not** establish grid convergence. A Roache triple L1/L2/L3 (128×32 / 256×64 /
512×128 film) is **R5-B**, a separate freeze, launched only if R5 reaches
`GATE REACHED` (§6, §7). Its cost is presented in §6 for the supervisor's decision;
it is not authorised by this freeze.

---

## §5. THE GATE (verdict vocabulary only; prediction-first)

**Step 1 — SURVIVAL (both conjuncts required):**

- **C-08a — Completion (rule 4):** `rc==0`; an `End` line; last time `== endTime
  8.0`; fields `deltaf Uf Tf` (film) and `U p p_rgh T` (primary) present at
  `endTime`; **160 written dirs**; **8,000 `ExecutionTime` lines** (exact, since
  `adjustTimeStep no`; rule-4 clause-5); age guard (every `endTime` field newer than
  the case's `0/` launch marker). The comparator **refuses (exit 2)** on any failed
  clause.
  **⚠ rc semantics re-derived for R5's cap-free launcher (do NOT copy R4-A's note).**
  R4-A wrapped each rung in `timeout 2400`, so `rc=124` there *meant* "cap reached".
  R5's launcher has **no `timeout`** (§6), so `rc=124` carries **no cap meaning**: a
  nonzero rc is a genuine solver failure or an external kill, and any `rc!=0` fails
  C-08a exactly as `rc=136` (SIGFPE) or `rc=1` would. The only "took too long"
  signal is the STALL_ALERT marker (§6), which is an escalation, not an rc.
- **C-08b — BOUNDED OBSERVER (the escaped-or-postponed instrument):** at every
  logged step, from the film Info `min/max(mag(U))` line, the maximum film speed
  must satisfy **`MAGUF_MAX_BOUND = 50 m/s`**, AND **no film residual (Ufx, Ufy,
  Ufz, deltaf) may be NaN or Inf** at any step. Rationale (answer-blind): physical
  film speed is `U_IN = 0.537` m/s and terminal velocity is O(1) m/s, so 50 m/s is
  ~two decades above physical and cannot false-fire on a bounded transient; the
  finite-area runaway floor was ≥ 4e13 m/s (R3-L3), i.e. the bound sits in an empty
  gap. A run that **completes with rc==0 but breached `MAGUF_MAX_BOUND` or emitted a
  NaN/inf residual** is the defect **postponed/disguised**, not escaped, and is
  graded **`NOT A RESULT`** (§3 justification 3). `min/max(delta)` and `coverage`
  are recorded as **context only, never a gate** — a dry patch off the monitor is
  legitimate physics.

A run failing **either** conjunct is **`NOT A RESULT`** on the film-thickness
answer; its observer trace (`max|Uf|`, residual health, `delta`, `coverage`) is
reported as the mechanism datum.

**Step 2 — ANSWER-RETENTION (surviving runs only):**

- **Admissibility:** monitor-window `min(deltaf) ≥ D_MIN_ADMISSIBLE = 1e-06` m. A
  dewetted monitor ⇒ **`NOT A RESULT`** (the thickness reading needs a wetted
  monitor).
- **Plateau (FROZEN before compute, per charter v1.11 §16):** over the **last 20%
  of written times** (times ≥ 6.4 s), the area-weighted `monitor_mean(deltaf)`
  peak-to-peak must be `≤ T_FLOOR = 2.7750e-07` m (R4-A instrument floor). Not
  plateaued ⇒ **`NOT A RESULT`** (never "run it longer").
- **Limb A (vs manual, the only retention gate in R5):**
  `e_A = |δ_mon − 0.555 mm| / 0.555 mm ≤ 2.12 %`, i.e. `δ_mon ∈ [0.543234,
  0.566766]` mm → **`GATE REACHED`** (its ceiling — single-grid validation against a
  benchmark, never `PASS`); outside → **`GATE FAIL`**; either overridden to
  **`NOT A RESULT`** by any completion / observer / plant / admissibility / plateau
  refusal.

**No Limb B in R5, and why (stated so the omission is not silent).** R4-A's Limb B
compared against the *finite-area solver's own exact discrete steady state*
`dN*(h0)` — a reference specific to that model and its `h0`. It does not transfer to
`kinematicSingleLayer` (different model, no `h0`). A model-independent **analytical
Nusselt** code-verification (`δ_N = (3μΓ/(ρ²g_s))^{1/3}`) is legitimate but is
**deferred to R5-B**, where a converged L1/L2/L3 triple makes a GCI meaningful; a
`PASS` from a single grid would be uninterpretable (rule 5). R5's ceiling is
therefore `GATE REACHED`.

**Planted-zero control (rule 3):** the comparator plants `PLANT = 1.234e-05` m into
a copy of the read-back `deltaf` sub-region, re-reads from disk, and **refuses**
(exit 2) if the reader cannot see it. A comparator without a fired plant has
produced no number.

**The gate cannot be widened.** A failing limb is worked/re-registered, never
softened.

---

## §6. COST (`CLAUDE.md` rule 12) — a MEASURED anchor and a SCENARIO FAMILY

**⚠ NO CAP KILLS A RUN (owner directive, 2026-09-12, verbatim relayed: "dont
forget i dont want any cap on any run, and that i bumped the volume to 1000 gib";
lab-attributed ruling by the supervisor).** The figures in this section are
**registered as CALIBRATION PREDICTIONS, never as kill thresholds.** Rule 12 still
requires every run costed before launch and the estimate compared against actual at
completion (§8); it does not require a `timeout` that kills. **The launcher wraps
the solver in NO `timeout <cap>`** — there is no construct whose effect is "the
solve dies because it spent too much" (R4-A's `timeout 2400`/rung and 120-core-min
family refusal are DISARMED and not reproduced). No later reader may re-arm these
numbers as kill thresholds.

**Cap-kill is replaced by a STALL OBSERVER (an instrument, not a cap).** A run with
no timeout can hang and hold a core silently — a real failure mode. The launcher
therefore carries a passive watcher: **if no new `Time =` line appears in the
solver log for `STALL_INTERVAL = 600 s` (10 min)**, the watcher **writes a
`STALL_ALERT` marker and escalates to the supervisor — it never kills the solver.**
A watcher that kills is a cap; a watcher that reports is an instrument. 600 s is ~2
decades above a healthy step's wall time even under heavy contention, so it will not
false-fire on a merely slow box.

**Why this is a family and not one number (the R4-A defect, applied).** R4-A
anchored its estimate to an `n=1` point and scaled by the very variable it was
sweeping; two errors cancelled to a plausible-looking `0.883` that hid a 3.99×
scenario miss. R5 avoids this: the per-step rate is **measured on this solver**
(§1.4), the load at measurement is stated, and the estimate is a family over the
two axes that actually move cost — **survival outcome** and (for the deferred
triple) **mesh level** — each with a predicted (not enforced) figure.

**MEASURED anchor (rivuletPanel, `reactingParcelFoam`, serial, load 56.7):**
steady-state **0.12 CPU-s/step at 43,200 primary cells** (successive `ExecutionTime`
samples 0.87→0.99→1.11 … 3.06→3.19→3.31 s, uniform +0.12; startup ≈ 0.75 CPU-s).
Unit work: **2.78e-06 CPU-s per (primary-cell · step)**. This is a *same-solver,
different-mesh* anchor: **predicted, not measured, for R5's own mesh** — a completed
R5 run would be the first clean measurement, recorded in the calibration row (§8).

**⚠ A RATE MUST SAY WHAT IT IS A RATE OF (chief, 2026-09-12).** The anchor above is
a **CPU-s** rate (from `ExecutionTime`). Core-minute **actuals and ETAs are WALL
quantities** (`ClockTime`, ÷60 for a serial run). The two differ by the contention
factor **`ClockTime/ExecutionTime`**, which is **per-run, never lab-wide**: measured
tonight VMFL017-R3 (1 rank) = 1.0185, VMFL078-L3 (4 ranks) = 1.347. R5's factor is
**MEASURED on R5's own log** at completion (`ClockTime/ExecutionTime` from the tail of
`log.reactingParcelFoam`) and named **separately** in the §8 calibration row — never
assumed from another run. The 31.6 core-min figure is the CPU-s prediction; the WALL
actual = that × R5's own measured factor, the gap named as contention per
`COMPUTE_BUDGET_CHARTER` §6.

**R5 = single grid, 65,536 primary cells + 16,384 film cells, 8,000 steps, serial
(RANKS=1).** Per-step primary work `65,536 × 2.78e-06 = 0.182 CPU-s`; + ~30% for the
film solve, mapping and function objects ⇒ **≈ 0.237 CPU-s/step**; × 8,000 =
**≈ 31.6 CPU-min work-limited** (serial ⇒ core-min = wall-min at load→1).

| scenario | steps reached | **PREDICTED core-min (calibration, NOT a kill cap)** | predicted wall-s (serial, load→1) |
|---|---|---|---|
| **S — survives to endTime** | 8,000 | 31.6 | ~1,900 |
| **C — crashes/stalls early** (regression) | ~800 (10%) | ~3.2 | ~190 |
| **expected-actual bracket (for the §8 ratio)** | — | 32–65 (load 1× → ~2×) | — |

- **These are predictions the completion calibration is graded against (§8), not
  thresholds that stop the run.** The 31.6 core-min work-limited figure, bracketed
  to ~65 core-min under ~2× contention, is what actual/predicted is computed from.
  There is no re-budgeting question because there is no cap to overrun.
- **Liveness** is judged by the `ExecutionTime`/step increment (≈ constant ≈ 0.24 s)
  and by the STALL_INTERVAL=600 s watcher above — never by a total-wall cap.
  **Launched by hand when load drops, not filed for a daemon** so it never takes a
  core from Sanaa's-priority 3D/multipoint work at load 3.5×.
- **Dollars — DERIVED, never measured** (box cannot read billing,
  `COMPUTE_BUDGET_CHARTER` §5): expected (scenario S) 31.6 core-min = 0.527 core-h ×
  $0.0513/core-h = **$0.027 derived**; contention-bracketed ~65 core-min →
  **$0.056 derived**. CPU only. (No $ pre-authorisation gate is asserted as a cap;
  the figure is stated for the calibration record.)
- **Deferred R5-B triple, costed for the supervisor's decision (NOT authorised
  here):** L1 (24,576 primary) ≈ 12 core-min; L2 (65,536) ≈ 32; L3 (524,288) ≈ 253
  core-min work-limited; triple ≈ **300 core-min work-limited**, ≈ **600 core-min
  (10 core-h, $0.51 derived) at ~2× contention** — a prediction, not a cap. Heavy on
  a 3.5×-oversubscribed box — the supervisor rules whether/when to authorise it.
- **Calibration at completion (rule 12):** actual core-min from the logs vs the 31.6
  estimate; the row states the ratio, the **load at launch and at grade**, and
  attributes the gap (contention / waste / misprediction — waste named separately per
  `COMPUTE_BUDGET_CHARTER` §6); lands in `docs/COST_CALIBRATION.md`.

---

## §7. THE REGISTERED PREDICTIONS, AND THE ABANDONMENT / VOF ESCALATION (in advance)

**Answer-blind predictions (recorded before the run):**
- R5 **survives** (completion + C-08b): expected, on the §1 evidence (conditioned FV
  diagonal + non-preconditioner solver + positive-path smoke).
- If it survives, `δ_mon → ` the laminar film thickness for Γ = 0.382 kg/m/s at
  g_s = 6.306, expected **near 0.55 mm and in band** — but the model change is a
  genuine test and the outcome is **not asserted**. A survival that lands materially
  out of band refutes our reading of the FV film model — a finding worth more than a
  passing row.

**Registered escalation (prediction-first, cannot be chosen after the fact):**
- **If R5 does NOT survive** (C-08a completion fail, OR C-08b `max|Uf|`/NaN breach) →
  the **`kinematicSingleLayer` approach is ABANDONED for VMFL072** and the successor
  is the **VOF re-formulation (`interFoam`)**, anchored to VMFL069-R2's completed
  L1/L2/L3 `interFoam` triple on this box. Registered in
  `docs/ansys_verification/FIX_SUCCESSOR_REGISTRY.md`.
- **If R5 survives but `GATE FAIL`** (δ_mon out of band, monitor wetted, plateaued)
  → **not** abandonment; a mesh/parameter question carried to R5-B (triple), which
  tests grid convergence before any conclusion about the model's accuracy.
- **If R5 survives `GATE REACHED`** → its setup is carried to **R5-B** (the 256×64→
  512×128 Roache triple, separate freeze) for grid convergence and the analytical
  Nusselt Limb-B code-verification.

**The escaped-vs-postponed partition, stated honestly (supervisor refinement,
2026-09-12).** `FOAM_SIGFPE` trapping is **ON** — confirmed from the smoke log
(`trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)`; check-1 will
re-confirm for the frozen launch). So the partition is:
- **ESCAPED:** `rc=0` **and** `max|Uf| ≤ 50 m/s` at every step **and** zero NaN/inf
  film residuals across all 8,000 steps.
- **POSTPONED = `rc=136` (SIGFPE):** the **same crash signature as the five-crash
  chain**, graded **`NOT A RESULT`** via the completion clause C-01 exactly as R4-A
  graded its rungs. With trapFpe ON, a zero-diagonal division in the Gauss–Seidel
  sweep (`GaussSeidelSmoother.C:164`, `psii /= diagPtr[celli]`) raises SIGFPE itself,
  so this is the main postponement mode.

**The PRIMARY protection is not the NaN guard — it is the bounded-positive friction
diagonal (§1.3).** At `delta=0`, `Cw = 3·mu/deltaSmall` is finite-positive
(`deltaSmall>0`), clamped to 5000, added to the momentum diagonal, so the diagonal is
strictly `> 0` and no singular matrix arises in the first place. The C-08b NaN/inf
guard is therefore a **narrow middle-case** belt-and-braces (an Inf produced without
tripping trapFpe), **not** a claimed escape route that trapFpe would pre-empt — the
prereg does not claim a NaN-completion escape. `min(delta)=0` off the monitor is NOT
a failure signal here (clamp at zero + regularised friction represent dewetting, not
fault it) — the precise inverse of R4-A, where `min_h` was blind at the floor.

---

## §8. GRADING PATH, COMPARATOR PLAN (to build only AFTER the supervisor rules on §4)

Per the supervisor's instruction, the comparator is **not built until the design is
ruled on** (R4-A cost a freeze/edit collision from a comparator edited during a
freeze). Planned `compare_vmfl072_r5.py`, for the supervisor's check-1 (read as a
diff):

- **REUSE byte-faithfully from `compare_vmfl072_r3.py`/`r4a`:** the geometry/area
  readers, `window_mask`, `area_mean`, `monitor_mean`, the plant machinery
  (`PLANT = 1.234e-05`), `T_FLOOR`, `D_MIN_ADMISSIBLE`, band constants. These read
  the film thickness field — now **`deltaf`** on the `wallFilmRegion` — so the
  field-name and region-path bindings change but the reduction does not.
- **⚠ THE FAMILY'S LIVE-PLANT DEBT, DISCHARGED BY DESIGN (supervisor directive
  2026-09-12).** Across five crashes and three freezes (R2/R3/R4-A) the answer-reading
  path never ran, so the rule-3 planted control has **never fired live** in this
  family's history — every refusal so far was a completion refusal that never reached
  the reader. R5's comparator is therefore built so that **a surviving run
  necessarily exercises the live plant**: the plant is injected into the
  read-back copy of the real `deltaf` field the survivor wrote to disk (not a
  synthetic fixture), re-read, and the run's number is not emitted unless that live
  read-back sees the perturbation. If R5 survives, that firing is the **first live
  plant in the family** — designed in deliberately, ordered so the reader cannot
  produce `δ_mon` without the plant having been seen and removed.
- **NEW, isolated in one `# ==== R5 kinematicSingleLayer VERDICT ====` block:**
  (1) `observe(log)` — parse `min/max(mag(U))`, `min/max(delta)`, `coverage`, and
  the `Ufx/Ufy/Ufz/deltaf … Final residual` values into `film_observer.tsv`;
  `max|Uf|` feeds C-08b, residual NaN/inf feeds C-08b, `delta`/`coverage` are
  context. (2) `check_completion` retargeted to `deltaf/Uf/Tf` + 160 dirs + 8,000
  `ExecutionTime` lines + age guard. (3) `check_survival` = C-08a AND C-08b.
  (4) `verdict` = survival → admissibility → plateau → Limb A, per §5. Every refusal
  is explicit `refuse()/sys.exit(2)`, never a bare `assert`.
- **`--selftest`** green under `python3` and `python3 -O`, with mutants: completion
  fail → NOT A RESULT; **the C-08b `max|Uf|` gate and the NaN/inf residual guard —
  each with a mutation control that goes RED when the guard is removed** (the
  supervisor's warning-3 instrument); admissibility; plateau; Limb-A band edges both
  sides; plant firing. ⚠ **Do NOT run `--selftest` on this comparator or any
  descendant until the L-548 footprint bound is in place** (unbounded fixture trees,
  31.6 GiB/h).
- **Comparator pin:** `git hash-object` recorded at freeze, verified by the driver
  against the committed blob before launch.
- **DECLARED TRANSITIVE DEPENDENCY (check-1 finding, 2026-09-12).** The comparator
  reads and `ast.parse`s the frozen `compare_vmfl072_r4a.py` at run time (the AST
  reuse guard) — a FILE-READ dependency no import scan sees, so the freeze must
  declare it. Its frozen git blob is **`ca2c73c70ce72a9aa12cf436a482ba83246158f1`**
  (`= git hash-object = HEAD blob`, verified three ways). `compare_vmfl072_r5.py`
  pins this as `R4A_BLOB_SHA` and, in `_assert_reuse_faithful()`, hashes the on-disk
  r4a and **refuses (exit 2) BEFORE the AST comparison** on any mismatch — closing
  the AST guard's one blind spot (r4a drifting on disk while this copy drifts
  identically). A selftest control confirms the blob pin fires when the pinned sha
  is wrong. The freeze covers the transitive closure of what executes: r5 + r4a@blob.
- **Driver + apply + base:** driver mirrors R4-A's pre-launch guards (freeze-sha
  verify, VMFL017 no-touch, load/`free -g` read), retargeted to R5 paths, single run
  (no rung loop). **NO `timeout` and NO core-min kill accounting** (§6, owner
  directive) — R4-A's `TOTAL_CORE_MIN`/`min(cap,…)` construct is removed, not
  carried. The mesh path is `blockMesh` → `topoSet` (plate faceSet) →
  `extrudeToRegionMesh -overwrite`. The driver spawns the STALL_INTERVAL=600 s
  watcher (report-only, §6) alongside the solver. `apply_level.sh` tokenises
  `@H_IN@`, `@U_IN@`, `@NX@ @NY@ @NZ@`, `@DELTAT@`, `@ENDTIME@`, `@WRITEINT@` into
  `base/`. All frozen files committed in the SAME commit as this doc.

---

## §9. WHAT I COULD NOT VERIFY / OPEN CAVEATS

1. **The finest-grid conditioning of the FV momentum diagonal is argued, and the
   smoke confirms it on rivuletPanel's mesh at `delta=0`, but not on VMFL072's
   256×64 mesh at VMFL072's Γ.** C-08b exists precisely to catch it at run time if
   the argument is wrong.
2. **The per-step rate is measured on a different mesh** (43,200 vs 65,536 primary
   cells); §6 scales it linearly in cell count, which is the standard assumption for
   a fixed solver but is itself unverified for this mesh — the completion calibration
   row is the first clean check.
3. **`endTime = 8.0 s` is assumed sufficient for the monitor film to plateau**; the
   frozen plateau criterion (§5) enforces this — if not plateaued, `NOT A RESULT`,
   not a longer run.
4. **The open-boundary ambient BCs for the quiescent primary are a modelling choice**
   (the manual specifies zero air flow, not a boundary set); they are registered
   here and are the supervisor's to challenge at check-1.
